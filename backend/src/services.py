from typing import Literal, List, Union

from .domain.models import TextUnit, ScoreUnit, ScoreDocument
from .core.parser import ScoreParser
from .converters.termuxed_generator import TermuxedGenerator


class ScoreService:
    """
    应用服务层：负责协调整个乐谱解析和转换的业务流程。
    将解析器、数据模型和生成器连接起来。
    """

    def __init__(self):
        """初始化所需的依赖组件。"""
        # 实例化核心解析器(Markdown to DataModel)
        self.parser = ScoreParser()
        # 实例化不同的生成器/导出器
        self.termuxed_generator = TermuxedGenerator()

    def process_parsing(self, full_score_text: str) -> ScoreDocument:
        """
        处理乐谱解析请求。
        将包含所有元数据和乐谱符号的完整文本流转换为结构化的 ScoreDocument 数据模型。
        
        Args:
            full_score_text: 包含所有信息（#标题、@子标题、乐谱符号）的完整文本。

        Returns:
            ScoreDocument: 包含所有元素（TextUnit 和 ScoreUnit）的对象。
        """
        # 1. 解析：Parser 现在处理所有信息，并返回包含混合元素的 ScoreDocument
        # Parser 负责预处理、分词、后向关联和元素排序
        score_document: ScoreDocument = self.parser.parse(full_score_text)
        
        # 2. 验证或进一步处理
        # 可以在这里添加验证逻辑，例如检查时值计算是否有效等。
        
        return score_document

    def process_export(self, score_model: ScoreDocument, format: Literal['debug', 'png', 'txt', 'musicxml', 'midi']) -> str:
        """
        处理乐谱导出请求。
        
        Args:
            score_model: 结构化的 ScoreDocument 数据模型。
            format: 目标导出格式 ('txt', 'musicxml', 'midi')。

        Returns:
            str: 导出的文本内容。
        """
        if format == 'debug':
            return self.termuxed_generator.generate_output(score_model)
        elif format == 'png':
            return self.png_generator.generate_image(score_model)

    def debug_print_document(self, score_document: ScoreDocument):
        """
        将 'debug' 格式的输出打印到终端，用于调试。
        """
        # 调用 process_export 并打印结果
        output = self.process_export(score_document, 'debug')
        print(output)

# --- 测试代码块（更新以匹配新的模型和流程） ---
def test_service():
    """ 简单的服务层测试，演示解析和导出流程。 """

    # 假设的完整输入数据
    sample_full_score = (
"""
# 凉州
@ 沙陀调
% 来源: 三五要录
= This is a sample score with mixed content.
【入破第一】
{二}
{也/zp}
{七}
{言（七言）/zp}
{一/y/b}
{之}
{四/zp}
{之}
{合（八）/h}
{之/h/zp}
"""
    )
    
    service = ScoreService()
    
    # 1. 处理解析
    try:
        print("ScoreService 初始化成功，准备处理解析请求...")
        
        # 处理成score document model
        score_document_model = service.process_parsing(sample_full_score)
        
        print(f"解析完成。元素数量: {len(score_document_model.elements)}")
        service.debug_print_document(score_document_model)

    except Exception as e:
        print(f"处理错误: {e}")