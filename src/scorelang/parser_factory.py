from typing import TypeVar

from .parsers.pipa_parser import PipaParser
from .parsers.base_parser import BaseParser


# 定义一个泛型，表示所有 Parser 都继承自 BaseParser
P = TypeVar('P', bound=BaseParser)

class ParserFactory:
    """
    根据乐谱类型返回正确的 Parser 实例。
    """
    @staticmethod
    def get_parser(score_type: str) -> P:
        """选择并返回具体乐谱的 Parser 实例。"""
        if score_type.lower() == 'pipa':
            return PipaParser()
        # elif score_type.lower() == 'guzheng':
        #     return GuzhengParser()
        else:
            raise ValueError(f"Unsupported score type: {score_type}. Please check configuration.")