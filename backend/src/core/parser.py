import re
from typing import List, Tuple, Dict, Any, Optional, Union

from ..domain.models import ScoreUnit, TextUnit, ScoreDocument
from .lexer import Lexer 

#TODO: 和lexer使用一个统一的MAP文件
#TODO: 加上log！！！

# 配置数据 (Token 类型定义)
# 修饰符 Token 类型，需要附加到 ScoreUnit 上
MODIFIER_TYPES = [
    'TIME_MOD',       # (/y, /h)
    'RHYTHM_MOD',     # (/b, /zp, /yp, /r)
    'SUB_CHAR',       # (小字号音符组)
]

# 文本信息 Token 类型，需要创建 TextUnit
TEXT_TYPES = [
    'TITLE',          # # 主标题
    'SOURCE',         # %来源
    'COMMENT',        # = 插入文本
    'SECTION',        # [乐部] 或 【乐部】
    'MODE',           # @调式
]


class ScoreParser:
    """
    核心解析器：负责将预处理后的文本 Token 流转换为 ScoreDocument 对象。
    实现了后向关联算法和琵琶谱的火标记过滤。
    """
    
    def __init__(self):
        self.lexer = Lexer()  
        
    # --- 阶段 1: 预处理 ---
    
    def _preprocess_score_text(self, text: str) -> str:
        """
        将多行输入合并为单行，并用空格分隔所有符号，使其适应 Lexer。
        """
        # 合并所有行，\n替换为空格
        text_single_line = text.replace('\n', ' ')
        
        # 先把括号整体分割
        unified_text = re.sub(r'([（\(][^（\）\(\)]+?[）\)])', r' \1 ', text_single_line)

        # 分割方法
        modifiers_to_space = [
            '{', '}',                   # 结构符
            '/y', '/h',                 # 时值修饰符
            '/b', '/pz', '/py', '/r',   # 节奏修饰符
        ]

        # 符号空格分隔
        for mod in modifiers_to_space:
             unified_text = unified_text.replace(mod, f' {mod} ')

        # 多余空格全变成单个空格，返回
        return re.sub(r'\s+', ' ', unified_text).strip()

    # --- 阶段 2 : 词法分析与解析 ---

    def parse(self, text: str) -> ScoreDocument:
        """
        从原始输入文本中解析出完整的 ScoreDocument 对象。
        """
        # 1. 预处理文本
        processed_text = self._preprocess_score_text(text)
        
        # 2. str to tokens
        tokens: List[Tuple[str, str]] = self.lexer.tokenize(processed_text) 

        # 3. 初始化混合数据结构
        elements: List[Union[TextUnit, ScoreUnit]] = [] # 最终的元素流
        current_unit: Optional[ScoreUnit] = None          # 最近的主音符单元

        # 4. 遍历 Tokens 并执行解析逻辑
        for token_type, content in tokens:
            
            # --- 边界和结构处理: 任何单元边界和文本Token都会结束当前单元 ---
            # 这包括 UNIT_START, UNIT_END, MAIN_CHAR, 以及所有 TEXT_TYPES
            is_boundary_or_text = token_type in ['UNIT_START', 'UNIT_END', 'MAIN_CHAR'] or token_type in TEXT_TYPES
            if is_boundary_or_text:
                # 无论遇到何种边界，都结束并保存当前的 ScoreUnit
                if current_unit is not None:
                    elements.append(current_unit)
                    current_unit = None

            # --- A. 文本处理：创建 TextUnit (已移除冗余 if/elif 链) ---
            if token_type in TEXT_TYPES:
                # 直接使用 token_type 作为 TextUnit 的类型 (例如 'TITLE', 'AUTHOR')
                text_unit = TextUnit(type=token_type, text=content)
                elements.append(text_unit)

            # --- B. 乐谱单元处理 (MAIN_CHAR) ---
            elif token_type == 'MAIN_CHAR':
                # 创建新的 ScoreUnit，并设置为当前单元 (它会取代前面被结束的 current_unit)
                current_unit = ScoreUnit(
                    main_score_character=content, 
                )
    
            # --- C. 修饰符处理 (后向关联) ---
            elif token_type in MODIFIER_TYPES:
                if current_unit is None:
                    # 错误处理：修饰符前面没有主音符，跳过
                    print(f"Warning: Modifier '{content}' found without preceding main PU. Skipping.")
                    continue
                
                # 分派给 ScoreUnit 的相应属性
                self._assign_modifier(current_unit, token_type, content)

        # 5. 循环结束后，确保最后一个单元被存储
        if current_unit is not None:
            elements.append(current_unit)
            
        # 6. 节奏标记过滤 (Fire Mark Filtering Pass)
        self._filter_fire_marks(elements)

        # 7. 返回 ScoreDocument
        return ScoreDocument(elements=elements)
        
    
    def _assign_modifier(self, unit: ScoreUnit, token_type: str, content: str):
        """
        根据 Token 类型将修饰符内容附加到 ScoreUnit 的正确属性上。
        现在使用 SYMBOL_MAP 进行转译，并使用查表分配节奏修饰符。
        """
        
        # 1. 时值乘数计算 (基于原始 Token content)
        # 必须在转译前执行，确保 '/y' 和 '/h' 被正确识别
        if content == '/y': 
            unit.time_multiplier *= 2.0 
        elif content == '/h':
            unit.time_multiplier *= 0.5
        
        # 3. 小字号/时值修饰符 (加入 small_modifiers 列表)
        # '火' 和 '引' (转译后) 也会被加入此列表
        if token_type in ['TIME_MOD']: 
            unit.small_modifiers.append(content)
            
        # 4. 节奏/排版相关的修饰符(以后再使用map移除硬编码)
        if token_type == 'RHYTHM_MOD':
            if content in ['/b', '/py']: 
                unit.right_rhythm_modifier = content
            elif content in ['/pz', '/r']:
                unit.bottom_rhythm_modifier = content

        # 3. 小字号/时值修饰符 (SUB_CHAR)
        if token_type == 'SUB_CHAR': 
            # 按照用户要求：将小字号音符组的内容按字符拆分并分别存储
            # 例如：'七言' 现在被存储为 ['七', '言']，以提供最高的粒度控制
            for char in content:
                unit.small_modifiers.append(char)

    def _filter_fire_marks(self, elements: List[Union[TextUnit, ScoreUnit]]):
        """
        遍历元素流，移除连续的 '火' 标记中除第一个以外的所有 '火' 符号。
        """
        is_in_fire_chain = False 
        
        for element in elements:
            
            # 只对 ScoreUnit 进行操作
            if isinstance(element, ScoreUnit):
                
                # 检查当前单元是否包含 '火' 符号，且时值被设为 0.5
                has_fire_symbol = '/h' in element.small_modifiers
                is_half_time = (element.time_multiplier == 0.5)
                
                # 只有当符号存在且时值确实被减半时，才认为它是一个“火”单元
                if has_fire_symbol and is_half_time:
                    if is_in_fire_chain:
                        # 处于连续减半链中，这不是第一个，应该移除 '火' 标记
                        element.small_modifiers.remove('/h')
                        
                    # 标记下一轮循环为“处于减半链中”
                    is_in_fire_chain = True
                else:
                    # 当前音符不满足条件，链条断开
                    is_in_fire_chain = False

            else:
                # 遇到 TextUnit 或其他非 ScoreUnit 元素，链条断开
                is_in_fire_chain = False
