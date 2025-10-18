from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class PipaLayoutConfig:
    # --- 基础配置参数 ---
    
    # 字体大小
    main_char_size: float = 18.0
    
    # 派生字号（将在 __post_init__ 中计算）
    title_size: float = field(init=False)
    mode_size: float = field(init=False)
    small_char_size: float = field(init=False)
    textunit_size: float = field(init=False)
    

    # 字体度量：字体实际要占用的空间的乘数
    width_per_pt: float = 1.5 
    height_per_pt: float = 1.2
    
    # 乐谱单元宽度系数
    scoreunit_width_per_pt: float = 0.5

    # --- 派生布局值 (将在 __post_init__ 中计算) ---
    
    # 单个字符在 X/Y 轴上的占用空间 (W, H)
    main_char_space: Tuple[float, float] = field(init=False)
    small_char_space: Tuple[float, float] = field(init=False)
    title_space: Tuple[float, float] = field(init=False)
    mode_space: Tuple[float, float] = field(init=False)
    textunit_space: Tuple[float, float] = field(init=False)
    
    # ScoreUnit 主音符的 X 轴偏移量
    scoreunit_x_offset: float = field(init=False)

    def __post_init__(self):
        """
        在对象初始化后执行，用于计算依赖于其他字段的派生值。
        """
        # 1. 计算派生字号 (必须先完成)
        self.title_size = self.main_char_size
        self.small_char_size = self.main_char_size / 2.0
        self.mode_size = self.title_size / 2.0
        self.textunit_size = self.title_size / 2.0

        # 2. 定义一个通用的计算函数
        def _calculate_space(size: float) -> Tuple[float, float]:
            """计算单个字符的 (X 占用, Y 占用)"""
            # X 占用 (Column Width) = 字号 * X 系数
            x_space = size * self.width_per_pt
            # Y 占用 (Character Height) = 字号 * Y 系数
            y_space = size * self.height_per_pt
            return (x_space, y_space)

        # 3. 计算所有元素的空间占用
        self.main_char_space = _calculate_space(self.main_char_size)
        self.small_char_space = _calculate_space(self.small_char_size)
        self.title_space = _calculate_space(self.title_size)
        self.mode_space = _calculate_space(self.mode_size)
        self.textunit_space = _calculate_space(self.textunit_size)
        
        # 4. 计算 ScoreUnit X 偏移量
        self.scoreunit_x_offset = self.main_char_size * self.scoreunit_width_per_pt