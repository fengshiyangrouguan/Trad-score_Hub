from dataclasses import dataclass, field, asdict
from typing import List, Union, Optional


@dataclass
class Node:
    """
    抽象基类，所有 AST 节点继承自此类
    """
    def accept(self, visitor):
        """支持 Visitor 模式"""
        method_name = f"visit_{self.__class__.__name__}"
        visit = getattr(visitor, method_name, visitor.generic_visit)
        return visit(self)

    def to_dict(self):
        """便于调试/序列化"""
        return asdict(self)


@dataclass
class TextNode(Node):
    """
    乐谱中的文本信息节点。
    """
    type: str
    text: str



@dataclass
class ScoreUnitNode(Node):
    """
    谱字单元节点（包括一个音符及其所有修饰符）。
    """  
    main_score_character: str                             # 主音符（谱字，e.g., "一", "二", "丁"）
    modifiers: List[str] = field(default_factory=list)    # 附加的小字号音符组


@dataclass
class SectionNode(Node):
    """
    乐部节点
    """
    title: Optional[str] = None
    mode: str               # 可临时转调，None 表示继承 Document 的调式
    elements: List[Union[ScoreUnitNode, TextNode]] = field(default_factory=list)        # 可包含谱字，文本



@dataclass
class ScoreDocumentNode(Node):
    """
    乐谱文档根节点
    """
    title: Optional[str] = None
    mode: Optional[str] = None
    source: Optional[str] = None
    transcriber: Optional[str] = None
    proofreader: Optional[str] = None
    date: Optional[str] = None
    elements: List[Union[SectionNode, TextNode]] = field(default_factory=list) # 可包含文本，乐部
