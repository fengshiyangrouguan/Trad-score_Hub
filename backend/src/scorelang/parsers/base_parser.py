from abc import ABC, abstractmethod

class BaseParser(ABC):
    def __init__(self):
        self.lexer = None
    @abstractmethod
    def parse(self, text: str):
        """
        核心接口：输入原始文本，输出 AST（ScoreDocumentNode）
        """
        pass
