from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class PipaLayoutConfig:
    # --- 字体配置参数 ---
    
    # 字体大小
    main_char_size: float = 18.0
    title_size: float = 18.0
    
    # 字体度量：字体实际要占用的空间的乘数
    width_per_pt: float = 1.5 
    height_per_pt: float = 1.2
    
    # 乐谱单元宽度系数（使其字体在一列中心生成，也就是一列有2.0倍数宽度）
    scoreunit_width_per_pt: float = 0.5
    
    # --- 布局常量 ---
    UNIT_NUM: int = 4            # 每一列的标准只拍子单元数量
    
    # 内部布局比例
    SEGMENT_ONE_RATIO: float = 0.4    # 第一个子单元（Time=1）占比
    SEGMENT_TWO_RATIO: float = 0.4    # 第二个子单元（Time=2）占比
    MODIFIER_RATIO: float = 0.2       # 底部修饰符区域占比

    # --- 派生字号/空间 (在 __post_init__ 中计算) ---
    small_char_size: float = field(init=False)
    mode_size: float = field(init=False)
    textunit_size: float = field(init=False)
    
    main_char_space: Tuple[float, float] = field(init=False)
    small_char_space: Tuple[float, float] = field(init=False)
    title_space: Tuple[float, float] = field(init=False)
    mode_space: Tuple[float, float] = field(init=False)
    textunit_space: Tuple[float, float] = field(init=False)
    
    scoreunit_x_offset: float = field(init=False)


    def __post_init__(self):
        """
        在对象初始化后执行，用于计算依赖于其他字段的派生值。
        """
        # 1. 计算派生字号
        self.small_char_size = self.main_char_size / 2.0
        self.mode_size = self.title_size / 2.0
        self.textunit_size = self.title_size / 2.0

        # 2. 定义一个通用的计算函数
        def _calculate_space(size: float) -> Tuple[float, float]:
            """计算单个字符的 (X 占用, Y 占用)"""
            x_space = size * self.width_per_pt
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
        
    def get_font_path(self, font_type: str) -> str:
        """
        **关键：返回你系统中中文字体文件的绝对路径。**
        你需要根据你的开发环境来设置这个路径！
        """
        # ⚠️ 必须替换为你的实际字体路径！
        if font_type == 'title':
             return r"C:\Windows\Fonts\FZYanZQKSJF.TTF"  # 假设标题字体
        return r"C:\Windows\Fonts\FZYanZQKSJF.TTF" # 假设主要内容字体