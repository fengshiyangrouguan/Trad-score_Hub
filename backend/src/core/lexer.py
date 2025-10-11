import re
from typing import List, Tuple

#TODO: 需要把这些规则和类型定义移到单独的配置文件中，解除硬编码
#TODO：定义更精细的编辑输入规则，MAIN_CHAR必须只有一个，且必须在句首等等……
#TODO: 需要增加对错误输入的处理和报告机制
#TODO: 插入文本的规则需要改进，可能会包含STOP_CHARS,需要一个专用停止符号“；”
#TODO: 也许应该简化火的处理？输入时输入/h意味着显示的火，输入/hd意味时值减半但不渲染该字符，删去火链的逻辑处理
#TODO: 使用<>添加一个扫弦连音符号判定，归类为textunit    
#FIXED: 调整规则顺序


# TOKEN规则配置
STOP_CHARS = r'[#%@=\[【\{]' 
# 匹配直到遇到停止符或换行符
TEXT_CONTENT_PATTERN = r'([^\n]*?)(?=' + STOP_CHARS + r'|\s*$)';
# 文本规则
TEXT_RULES: List[Tuple[str, str, int]] = [
    # 匹配 #标题内容
    ('TITLE', r'^#\s*'+ TEXT_CONTENT_PATTERN, re.IGNORECASE), 
    
    # 匹配 %来源
    ('SOURCE', r'^%\s*'+ TEXT_CONTENT_PATTERN, re.IGNORECASE),
    
    # 匹配 [乐部] 或 【乐部】
    ('SECTION', r'^【(.+?)】', re.IGNORECASE), 
    ('SECTION', r'^\[(.+?)\]', re.IGNORECASE),
    # 匹配 @调名
    ('MODE', r'^@\s*'+ TEXT_CONTENT_PATTERN, re.IGNORECASE), 
    
    # 匹配 =插入文本/注释
    ('COMMENT', r'^=\s*'+ TEXT_CONTENT_PATTERN, re.IGNORECASE),
]

# 乐谱符号规则
SCORE_RULES: List[Tuple[str, str, int]] = [
    # 匹配主音符: 所有琵琶谱使用谱字加一个休止符（丁）
    ('MAIN_CHAR', r'^(一|二|三|四|五|六|七|八|九|十|匕|卜|敷|乙|言|合|斗|乞|之|也|丁)', re.IGNORECASE),

    # 匹配节奏修饰符: '百:/b', '。:/zp', ',:/yp', '-:/r', 以及标准符号
    ('RHYTHM_MOD', r'^(\/b|\/pz|\/py|\/r)', re.IGNORECASE), 

    # 匹配时值修饰符: '引:/y', '火:/h'
    ('TIME_MOD', r'^(\/y|\/h)', re.IGNORECASE), # 增加标准符号的兼容性
   
    # 匹配小字号音符组: 必须是 (内容) 或 （内容）
    ('SUB_CHAR', r'^[（\(]([^（\）\(\)]*?)[）\)]', re.IGNORECASE),
]

# 结构/边界规则
STRUCTURE_RULES: List[Tuple[str, str, int]] = [
    # 匹配单元开始/结束符
    ('UNIT_START', r'^{', re.IGNORECASE),
    ('UNIT_END', r'^}', re.IGNORECASE),
    
    # 匹配空格(跳过)
    ('SKIP_SPACE', r'^\s+', re.IGNORECASE),
]


class Lexer:
    """
    词法分析器，将字符串输入转换为有序的 Tokens 列表。
    """
    def __init__(self):
        # 将所有规则合并并编译正则表达式
        all_rules_data = TEXT_RULES + STRUCTURE_RULES + SCORE_RULES
        
        self.compiled_rules = []
        for name, pattern, flags in all_rules_data:
            # 编译时传入 flags
            self.compiled_rules.append((name, re.compile(pattern, flags)))

        # 定义需要从 group(1) 提取内容的 Token 类型列表
        self.GROUP_1_CONTENT_TOKENS = [r[0] for r in TEXT_RULES] + ['SUB_CHAR', 'RHYTHM_MOD', 'TIME_MOD']

    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        """
        将预处理后的文本流分解为 (TOKEN_TYPE, CONTENT) 的 Tokens 列表。
        """
        tokens: List[Tuple[str, str]] = []
        remaining_text = text

        while remaining_text:
            match = None
            
            # 遍历所有规则，寻找最先匹配的 Token
            for token_type, pattern in self.compiled_rules:
                m = pattern.match(remaining_text)
                if m:
                    match = m
                    break
            
            if match:         
                # 对于 TEXT_RULES，内容在捕获组 1 中，排除了前缀字符
                if token_type in self.GROUP_1_CONTENT_TOKENS:
                    content = match.group(1) 
                else:
                    # 对于其他规则（结构、乐谱），内容是整个匹配项
                    content = match.group(0)

                # 跳过纯空格 Token
                if token_type == 'SKIP_SPACE':
                    remaining_text = remaining_text[match.end():]
                    continue
                
                # Strip() 移除内容两侧可能有的空格
                tokens.append((token_type, content.strip()))
                
                # 移动到文本的下一部分，并移除匹配内容后的所有前导空格
                remaining_text = remaining_text[match.end():].lstrip()
            else:
                # 无法匹配任何规则
                print(f"Lexer Error: Unrecognized token starting with '{remaining_text[:20]}...'")
                break 
                
        return tokens
