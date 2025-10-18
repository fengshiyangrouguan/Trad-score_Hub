from dataclasses import dataclass, field, asdict
from typing import List, Union, Optional, Dict, Tuple


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

    # 几何属性已改为 float
    position: Tuple[float, float] = field(default=(0.0, 0.0))
    width_dimension: float = field(default=0.0)


@dataclass
class ScoreUnitNode(Node):
    """
    谱字单元节点（包括一个音符及其所有修饰符）。
    """ 
    main_score_character: str                                   # 主音符（谱字，e.g., "一", "二", "丁"）
    small_modifier: List[str] = field(default_factory=list)     # 附加的小字号音符组（谱字）
    time_modifier: Optional[str] = None                         # 时值符号（引，火）
    right_rhythm_modifier: Optional[str] = None                 # 右侧的节奏修饰符（e.g., "百","乐拍子" ）
    bottom_rhythm_modifier: Optional[str] = None                # 正下方的节奏修饰符（e.g., "只拍子","-"）
    time: float = 1.0                                           # 时值 (1.0, 0.5, 2.0)

    main_char_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    small_mod_pos: List[Tuple[float, float]] = field(default_factory=list)
    time_mod_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    right_rhythm_mod_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    bottom_rhythm_mod_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    dimensions: Tuple[float, float] = field(default=(0.0, 0.0))


@dataclass
class SectionNode(Node):
    """
    乐部节点
    """
    title: Optional[str] = None
    mode: Optional[str] = None      # 可临时转调，None 表示继承 Document 的调式
    elements: List[Union[ScoreUnitNode, TextNode]] = field(default_factory=list) # 可包含谱字，文本

    title_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    mode_display_flag: bool = field(default=False) 
    mode_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    width_dimension: float = field(default=0.0)


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
    elements: List[Union[SectionNode, TextNode]] = field(default_factory=list) # 可包含谱字，文本，乐部

    page_dimensions: Tuple[float, float] = field(default=(2160.0, 1280.0))
    title_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    mode_pos: Tuple[float, float] = field(default=(0.0, 0.0))
    width_dimension: float = field(default=0.0)
    margin: Dict[str, float] = field(default_factory=lambda: {
        "top": 20.0, 
        "left": 20.0, 
        "right": 20.0, 
        "bottom": 20.0
    })