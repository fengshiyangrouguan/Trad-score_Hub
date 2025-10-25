import math
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple, Union, Callable
# 确保导入了正确的 AST 节点和 BaseVisitor
from ..visitors.base_visitor import BaseVisitor
from ..ast_score.nodes import ScoreDocumentNode, SectionNode, ScoreUnitNode, TextNode
from ..config.layout_config import PipaLayoutConfig


class PipaPillowRenderer(BaseVisitor):
    
    def __init__(self):
        """
        初始化渲染器。
        """
        # 修正 BaseVisitor 的初始化调用
        super().__init__()
        self.config = PipaLayoutConfig()
        self._font_cache = {}
        
        # 声明画布和绘图上下文
        self.canvas: Optional[Image.Image] = None
        self.draw: Optional[ImageDraw.ImageDraw] = None
        self.page_width: int = 0
        self.page_height: int = 0
        
        # 存储根节点和输出路径，供 traversal 期间使用
        self.document_node: Optional[ScoreDocumentNode] = None
        self.output_path: Optional[str] = None
        
        # 处理映射表
        print("Pipa Pillow Renderer initialized.")

    # -----------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------

    def _get_font(self, size: float, font_type: str) -> ImageFont.FreeTypeFont:
        """根据配置加载或从缓存中获取字体对象。"""
        key = (size, font_type)
        if key not in self._font_cache:
            font_path = self.config.get_font_path(font_type)
            # Pillow 需要整数大小
            self._font_cache[key] = ImageFont.truetype(font_path, int(size))
        return self._font_cache[key]

    def _draw_text(self, text: str, pos: List[float], size: float, font_type: str = 'text', color: str = "black"):
        """
        绘制文本。
        """
        if not self.draw: return
        # 假设 pos 是 [x, y]
        x, y = pos[0], pos[1]
        font = self._get_font(size, font_type)

        self.draw.text(
            (x, y), 
            text, 
            fill= color, 
            font=font, 
            # 使用 'ra' (Right-Top/Ascender) 锚点
            anchor="ra" 
        )


    def _draw_vertical_text(
        self, 
        text: str, 
        start_pos: Tuple[float, float], 
        size: float, 
        font_type: str
    ) -> float:
        """
        将字符串中的每个字符从上到下逐个绘制。
        
        参数:
        - text: 要绘制的字符串。
        - start_pos: 第一个字符的 (X, Y) 起始坐标。
        - size: 字体大小。
        - font_type: 字体类型（用于获取空间度量）。
        
        返回:
        - 最后一个字符的 Y 轴结束位置（下一个元素应开始的位置）。
        """
        
        start_x, current_y = start_pos
        
        # 1. 根据 font_type 获取对应的 Y 轴空间占用
        if font_type == 'title':
            # 假设 title_space 是 (X_占用, Y_占用)
            _, char_y_space = self.config.title_space
        elif font_type == 'mode':
            _, char_y_space = self.config.mode_space
        else:
            # 对于其他类型，可能需要更通用的逻辑
            return
            
        
        # 2. 逐字符绘制
        for char in text:
            # 绘制当前字符
            self._draw_text(
                char, 
                (start_x, current_y), 
                size, 
                font_type
            )
            
            # 更新 Y 轴：向下移动一个字符的 Y 空间
            current_y += char_y_space
            
        # 3. 返回最终 Y 坐标，供下一个元素继续向下排版
        return current_y
    
    def _draw_hollow_circle(
        self,
        center_pos: Tuple[float, float], 
        radius: float, 
        color: Union[str, Tuple[int, int, int]] = 'black', 
        line_width: int = 1
    ):
        """
        使用 Pillow 的 ImageDraw 对象绘制一个空心圆圈。
        
        参数:
        - draw: ImageDraw.Draw 实例，用于在图像上绘图。
        - center_pos: 圆心的 (x, y) 坐标元组。
        - radius: 圆的半径（以像素为单位）。
        - color: 圆圈的轮廓颜色，可以是字符串（如 'black'）或 RGB 元组。
        - line_width: 圆圈边框的宽度（以像素为单位）。
        """
        if not self.draw: return
        center_x, center_y = center_pos
        
        # 计算圆的边界框 (Bounding Box): [x1, y1, x2, y2]
        # Pillow 的 ellipse 方法需要的是边界矩形的左上角和右下角坐标。
        x1 = center_x - radius
        y1 = center_y - radius
        x2 = center_x + radius
        y2 = center_y + radius
        
        bbox = (x1, y1, x2, y2)
        
        # 使用 draw.ellipse() 绘制无填充的椭圆（当边界框是正方形时即为圆）
        self.draw.ellipse(
            bbox, 
            outline=color, 
            width=line_width
            # 注意：不设置 fill 参数，或设置为 None，即为空心
        )
    def _draw_line(
        self, 
        start_pos: Tuple[float, float], 
        end_pos: Tuple[float, float], 
        line_width: int = 1,
        color: Union[str, Tuple[int, int, int]] = 'black'
        ):
        """
        使用 Pillow 的 ImageDraw 对象绘制一条线段。
        
        参数:
        - draw: ImageDraw.Draw 实例，用于在图像上绘图。
        - start_pos: 线段的起点 (x1, y1) 坐标元组。
        - end_pos: 线段的终点 (x2, y2) 坐标元组。
        - color: 线段的颜色，可以是字符串（如 'black'）或 RGB 元组。
        - line_width: 线段的宽度（以像素为单位）。
        """
        
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Pillow 的 line 方法接受一个坐标序列，这里传入 (x1, y1, x2, y2)
        coordinates = [(x1, y1), (x2, y2)]
        
        # 使用 draw.line() 绘制线段
        self.draw.line(
            coordinates, 
            fill=color,       # 对于 line 方法，使用 fill 参数设置颜色
            width=line_width
        )
    

    # -----------------------------------------------------------
    # 绘图方法 (接收 AST 节点对象)
    # -----------------------------------------------------------

    def _draw_metadata(self, node: ScoreDocumentNode):
        """绘制标题、调式等页眉信息，使用节点中计算好的 pos 属性。"""
        
        # 1. 绘制 Title
        if node.title and hasattr(node, 'title_pos'):
            self._draw_vertical_text(
                node.title, 
                node.title_pos, 
                self.config.title_size,
                'title'
            )
        
        # 2. 绘制 Mode
        if node.mode and hasattr(node, 'mode_pos'):
            self._draw_vertical_text(
                node.mode, 
                node.mode_pos, 
                self.config.mode_size, 
                'mode'
            )
            
    def _draw_score_unit(self, unit_node: ScoreUnitNode):
        """绘制一个乐谱单元及其所有修饰符。现在接收 ScoreUnitNode 对象。"""
        
        # 1. 绘制主字符 (使用节点中的属性)
        if hasattr(unit_node, 'main_char_pos'):
             self._draw_text(
                 unit_node.main_score_character, 
                 unit_node.main_char_pos, 
                 self.config.main_char_size, 
                 'score'
            )
        
        # 2. 绘制小修饰符 (使用节点中的属性)
        if unit_node.small_modifier and hasattr(unit_node, 'small_mod_pos'):
            for i, mod_char in enumerate(unit_node.small_modifier):
                if len(unit_node.small_mod_pos) > i:
                    self._draw_text(
                        mod_char, 
                        unit_node.small_mod_pos[i], 
                        self.config.small_char_size, 
                        'score'
                    )

        # 3. 绘制右侧节奏修饰符 (检查属性是否存在)
        if unit_node.right_rhythm_modifier and hasattr(unit_node, 'right_rhythm_mod_pos'):
            if unit_node.right_rhythm_modifier == "/py":
                radius = self.config.small_char_size / 5
                width: int = int(radius*2)
                self._draw_hollow_circle(
                    unit_node.right_rhythm_mod_pos, 
                    radius, 
                    color='red', 
                    line_width = width
                )
            elif unit_node.right_rhythm_modifier == "/b":
                pos = (unit_node.right_rhythm_mod_pos[0] + self.config.small_char_size/2,
                       unit_node.right_rhythm_mod_pos[1] - self.config.small_char_size/2,)
                self._draw_text(
                    "百", 
                    pos, 
                    self.config.small_char_size, 
                    'score',
                    "red"
                )

        # 4. 绘制底部节奏修饰符
        if unit_node.bottom_rhythm_modifier and hasattr(unit_node, 'bottom_rhythm_mod_pos'):
            if unit_node.bottom_rhythm_modifier == "/pz":
                radius = self.config.small_char_size / 5
                width: int = int(radius / 2)
                          
                # 3. 调用函数绘制空心圆
                self._draw_hollow_circle(
                    unit_node.bottom_rhythm_mod_pos, 
                    radius, 
                    color='red', 
                    line_width = width
                )
            elif unit_node.bottom_rhythm_modifier == "/r":
                pos = (unit_node.bottom_rhythm_mod_pos[0]+self.config.small_char_size,unit_node.bottom_rhythm_mod_pos[1]-self.config.small_char_space[1]/2)
                self._draw_text(
                    "一",
                    pos,
                    self.config.small_char_size,
                    "score",
                    "red"
                )

                    
        # 5. 绘制时值修饰符
        if unit_node.time_modifier and hasattr(unit_node, 'time_mod_pos'):
            if unit_node.time_modifier == "/h":
                self._draw_text(
                    "火", 
                    unit_node.time_mod_pos, 
                    self.config.small_char_size, 
                    'score',
                    "red"
                )
            elif unit_node.time_modifier == "/y":
                self._draw_text(
                    "引", 
                    unit_node.time_mod_pos, 
                    self.config.small_char_size, 
                    'score',
                    "red"
                )

    def _draw_comment_textunit(self, node: TextNode, doc_node: ScoreDocumentNode):
        """
        绘制具有换行特性的竖排注释文本。
        现在接收 TextNode 和 ScoreDocumentNode 对象。
        """
        text = node.text or ""
        if not text or not hasattr(node, 'position'):
            return
            
        # 假设 PositionPass 已经将 position 注入到 TextNode 中
        start_x, start_y = node.position[0], node.position[1]
        
        # 获取配置
        font_size = self.config.textunit_size
        x_space = self.config.textunit_space[0] 
        y_space = self.config.textunit_space[1] 
        
        # 获取页边距 (从 ScoreDocumentNode 属性获取)
        margin = doc_node.margin # 假设 margin 是一个字典属性
        left_margin = margin.get('left', 0)
        
        # 1. 计算纵向可用空间
        available_height = node.dimensions[1]
        if available_height <= 0:
            print(f"Warning: Not enough vertical space for comment at Y={start_y}")
            return
            
        # 2. 计算每列最大字符数
        max_chars_per_col = math.floor(available_height / y_space)
        
        if max_chars_per_col <= 0:
            print("Warning: Max chars per column is zero, skipping comment.")
            return

        # 3. 开始迭代绘制
        current_x = start_x
        current_y = start_y
        char_count = 0

        for char in text:
            # 绘制当前字符
            self._draw_text(char, [current_x, current_y], font_size, 'textunit')
            
            char_count += 1
            current_y += y_space
            
            # 检查是否达到列最大字符数
            if char_count >= max_chars_per_col:
                current_x -= x_space # 换列：X 坐标向左移动
                current_y = start_y  # Y 坐标回到初始位置
                char_count = 0
                
                # 检查是否超出左侧边距
                if current_x < left_margin:
                    print("Comment text ran out of horizontal space.")
                    break
                    
    # -----------------------------------------------------------
    # VISTOR 核心方法
    # -----------------------------------------------------------

    def render(self, ast_root: ScoreDocumentNode, output_path: str):
        """
        公共入口方法，负责设置上下文并启动 AST 遍历。
        """
        self.output_path = output_path
        # BaseVisitor 的 visit 方法会启动遍历，然后调用 visit_ScoreDocumentNode
        self.visit(ast_root)
        
    def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
        """
        AST 遍历的入口：初始化画布、绘制元数据，然后递归遍历子节点。
        """
        self.document_node = node # 存储根节点，供子节点（如 TextNode）获取全局信息
        
        # --- 1. 初始化画布 ---
        page_dims = node.page_dimensions # 假设 page_dimensions 现在是节点属性
        if not page_dims or len(page_dims) < 2:
             raise ValueError("AST root node is missing valid 'page_dimensions' attribute.")
             
        self.page_width = int(page_dims[0])
        self.page_height = int(page_dims[1])
        
        self.canvas = Image.new('RGB', (self.page_width, self.page_height), 'white')
        self.draw = ImageDraw.Draw(self.canvas)
        
        print(f"Canvas created: {self.page_width}x{self.page_height}")
        print("Starting Pillow render via Visitor pattern...")

        # --- 2. 绘制元数据 ---
        self._draw_metadata(node)
        
        # --- 3. 递归遍历内容 ---
        # BaseVisitor 会负责遍历 node.sections (或其他子节点列表)
        self.generic_visit(node)
        
        # --- 4. 保存文件 (遍历结束时执行) ---
        if self.canvas and self.output_path:
             self.canvas.save(self.output_path, 'PNG') 
             print(f"Pillow score saved successfully to {self.output_path}")

    def visit_SectionNode(self, node: SectionNode):
        """
        处理 Section 节点。
        通常 Section 只需要绘制标题，然后继续遍历内部的 ScoreUnit。
        """
        # TODO: 绘制 Section 标题 (使用 node.title 和 node.position_x/y 属性)
        # 例如: self._draw_text(node.title, [node.position_x, node.position_y], ...)
                # 1. 绘制 Title
        if node.title and hasattr(node, 'title_pos'):
            self._draw_vertical_text(
                node.title, 
                node.title_pos, 
                self.config.title_size,
                'title'
            )
        
        # 2. 绘制 Mode
        if node.mode and node.mode_display_flag and hasattr(node, 'mode_pos'):
            self._draw_vertical_text(
                node.mode, 
                node.mode_pos, 
                self.config.mode_size, 
                'mode'
            )
        # 继续遍历 Section 内部的 ScoreUnitNode/TextNode
        self.generic_visit(node)
        
    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        """
        处理 ScoreUnit 节点：执行核心乐谱单元的绘制。
        """
        self._draw_score_unit(node)
        
        # ScoreUnit 是叶子节点，不需要继续 generic_visit
        return 
        
    def visit_TextNode(self, node: TextNode):
        """
        处理 TextNode (CommentNode) 节点：执行注释文本的绘制。
        """
        if self.document_node:
            self._draw_comment_textunit(node, self.document_node)
        
        # TextNode 是叶子节点，不需要继续 generic_visit
        return
