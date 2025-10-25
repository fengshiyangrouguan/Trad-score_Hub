from dataclasses import dataclass, field
from typing import Tuple, Dict

@dataclass
class PipaLayoutConfig:
    # --- 字体配置参数 ---
    
    # 字体大小
    main_char_size: float = 40
    title_size: float = 60
    
    # 字符（Char/符号）的度量系数
    CHAR_METRICS: Tuple[float, float] = (2.0, 1.05)  # (width_per_pt, height_per_pt)
    # 文本（Text/描述）的度量系数
    TEXT_METRICS: Tuple[float, float] = (1.5, 1.2)  # (width_per_pt, height_per_pt)
    
    # 乐谱单元宽度系数
    scoreunit_width_per_pt: float = field(init=False)
    
    # --- 布局常量 ---
    UNIT_NUM: int = 4

    # --- 派生字号/空间 (在 __post_init__ 中计算) ---
    small_char_size: float = field(init=False)
    mode_size: float = field(init=False)
    textunit_size: float = field(init=False)
    
    # 将派生空间定义为通用的场，其具体赋值在 post_init 中完成
    main_char_space: Tuple[float, float] = field(init=False)
    small_char_space: Tuple[float, float] = field(init=False)
    title_space: Tuple[float, float] = field(init=False)
    mode_space: Tuple[float, float] = field(init=False)
    textunit_space: Tuple[float, float] = field(init=False)
    
    # 对于谱字的向左位移数值
    scoreunit_x_offset: float = field(init=False)


    def __post_init__(self):
        
        # 1. 计算派生字号
        self.small_char_size = self.main_char_size / 2.0
        self.mode_size = self.title_size / 2.0
        self.textunit_size = self.title_size / 2.0

        # 计算派生空间参数
        self.scoreunit_width_per_pt = self.CHAR_METRICS[0] - 1
        # 2. 定义一个通用的计算函数
        def _calculate_space(size: float, metrics: Tuple[float, float]) -> Tuple[float, float]:
            """计算单个元素的 (X 占用, Y 占用)，使用传入的乘数"""
            width_multiplier, height_multiplier = metrics
            x_space = size * width_multiplier
            y_space = size * height_multiplier
            return (x_space, y_space)

        # 3. 计算字体空间参数
        
        # 定义一个映射，包含所有需要计算的 (字号属性名, 空间属性名, 度量组)
        # 这里我们使用 self._get_size_name 是一种更安全的方式来获取 size 属性
        calculations_map = [
            # (空间属性名, 字号属性名, 度量乘数)
            ("main_char_space", "main_char_size", self.CHAR_METRICS),
            ("small_char_space", "small_char_size", self.CHAR_METRICS),
            ("title_space", "title_size", self.TEXT_METRICS),
            ("mode_space", "mode_size", self.TEXT_METRICS),
            ("textunit_space", "textunit_size", self.TEXT_METRICS),
        ]
        
        for space_attr, size_attr, metrics in calculations_map:
            # 获取对应的字号
            size = getattr(self, size_attr)
            # 计算空间
            space = _calculate_space(size, metrics)
            # 赋值给对应的 space 属性
            setattr(self, space_attr, space)
        
        # 4. 计算 ScoreUnit X 偏移量
        self.scoreunit_x_offset = self.main_char_size * self.scoreunit_width_per_pt

    def get_font_path(self, font_type: str) -> str:
        """
        **关键：返回你系统中中文字体文件的绝对路径。**
        你需要根据你的开发环境来设置这个路径！
        """
        if font_type == 'score':
             return r"E:\project\Trad-score_Hub\pipa.ttf" # 假设主要内容字体
        return r"E:\project\Trad-score_Hub\text.ttf"   # 假设标题字体
        