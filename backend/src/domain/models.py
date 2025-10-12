# app-backend/src/domain/models.py

from typing import List, Any, Dict, Optional,Union
from dataclasses import dataclass, field,asdict

@dataclass
class MetaUnit:
    """
    存储本乐谱的基本信息
    """
    title: str          # 标题
    source: str         # 源
    mode: str           # 调式
    transcriber: str    # 录入者
    proofreader: str    # 审校
    date: str           # 录入日期


@dataclass
class TextUnit:
    """
    乐谱中的文本信息（标题、注释、乐部、调式等）的标准数据结构。
    """
    type: str      # 文本类型 (e.g., 'TITLE', 'COMMENT', 'SECTION', 'MODE')
    text: str      # 文本内容 (e.g., '春莺啭', '越调')


@dataclass
class ScoreUnit:
    """
    单个乐谱单元（包括一个音符及其所有修饰符）的标准数据结构。
    """  
    main_score_character: str                                   # 主音符（谱字，e.g., "一", "二", "丁"）
    small_modifiers: List[str] = field(default_factory=list)    # 附加的小字号音符组
    right_rhythm_modifier: Optional[str] = None                 # 右侧的节奏修饰符（e.g., "百","乐拍子" ）
    bottom_rhythm_modifier: Optional[str] = None                # 正下方的节奏修饰符（e.g., "只拍子","-"）
    time_multiplier: float = 1.0                                # 时值修饰符的乘数 (1.0, 0.5, 2.0)


@dataclass
class ScoreDocument:
    """
    解析后的完整乐谱数据。包含所有 ScoreUnit 和 TextUnit 的有序流。
    """
    elements: List[Union[TextUnit, ScoreUnit]] = field(default_factory=list) 
        
    def to_dict(self) -> Dict[str, Any]:
        """
        整个乐谱数据转换为可序列化的字典，用于 API 响应。
        """
        return asdict(self)