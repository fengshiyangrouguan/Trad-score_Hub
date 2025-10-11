from typing import List, Union
from ..domain.models import ScoreDocument, ScoreUnit, TextUnit

#TODO: 加上log！！！

ScoreElement = Union[ScoreUnit, TextUnit] 
class TermuxedGenerator:
    """
    测试工具类
    负责将 ScoreDocument 模型对象转换为适合终端显示的调试格式。
    它输出了每个元素的内部变量及其值。
    """
    
    def generate_output(self, score_document: ScoreDocument) -> str:
        """
        遍历 ScoreDocument 中的所有元素，将每个 ScoreUnit 和 TextUnit
        的内部变量及其值格式化为字符串输出，每行一个实例。
        """
        output_lines = []
        output_lines.append("\n--- ScoreDocument 元素详细输出 (DEBUG) ---")
        
        for element in score_document.elements:
            element_type = element.__class__.__name__
            
            # 使用 vars() 获取实例变量字典 (适用于 dataclass)
            attrs = vars(element)
            
            # 格式化属性字符串，使列表、数字和字符串的显示更清晰
            attr_strings = []
            for k, v in attrs.items():
                # 对于字符串，我们用引号包裹
                if isinstance(v, str):
                    attr_strings.append(f"{k}='{v}'")
                else:
                    attr_strings.append(f"{k}={v}")
            
            # 打印当前元素的类型和所有属性，在一行内显示
            output_lines.append(f"[{element_type}]: {', '.join(attr_strings)}")
        
        output_lines.append("------------------------------------------")
        
        # 返回完整的字符串，让调用者 (ExportService) 决定是打印还是返回
        return "\n".join(output_lines)
