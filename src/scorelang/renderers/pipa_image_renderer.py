import math
import os
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont # 导入 Pillow 核心模块

# 假设 PipaLayoutConfig 路径和结构已知
from ..config.layout_config import PipaLayoutConfig # 使用你更新后的类名
from ..core.pipeline_context import PipelineContext

# --- 临时配置替代品 (同上，用于快速验证) ---
TEMP_STYLES_MAP = {
    "DOCUMENT_TITLE": {"font_size_key": "title_size", "color": "darkblue", "font_type": "title", "font_path_key": "text"},
    "SECTION_TITLE":  {"font_size_key": "title_size", "color": "darkblue", "font_type": "title", "font_path_key": "text"},
    "MODE":           {"font_size_key": "mode_size", "color": "gray", "font_type": "mode", "font_path_key": "text"},
    "MAIN_CHAR":      {"font_size_key": "main_char_size", "color": "black", "font_type": "main_char", "font_path_key": "score"},
    "SMALL_MODIFIER": {"font_size_key": "small_char_size", "color": "black", "font_type": "small_char", "font_path_key": "score"},
    "TEXT_BLOCK":     {"font_size_key": "textunit_size", "color": "black", "font_type": "textunit", "font_path_key": "text"},
    "DOT_MARKER":     {"font_size_key": "main_char_size", "color": "red", "font_type": "main_char", "font_path_key": "score"},
    "CIRCLE_MARKER":  {"font_size_key": "main_char_size", "color": "red", "font_type": "main_char", "font_path_key": "score"},
    "LINE_MARKER":    {"font_size_key": "small_char_size", "color": "red", "font_type": "small_char", "font_path_key": "score"},
    "CHECK_MARKER":   {"font_size_key": "small_char_size", "color": "red", "font_type": "small_char", "font_path_key": "score"},
    "BAI_MARKER":     {"font_size_key": "small_char_size", "color": "red", "font_type": "small_char", "font_path_key": "score"},
}


class PipaImageRenderer:
    """
    基于 Render List 命令的 Pillow 图像渲染器 (快速验证版)。
    """
    def __init__(self, context:PipelineContext):
        self.context = context
        self.config:PipaLayoutConfig = self.context.layout_config
        self.styles = TEMP_STYLES_MAP
        self._font_cache: Dict[Tuple[str, float], ImageFont.FreeTypeFont] = {}
        
        # 声明画布和绘图上下文
        self.canvas: Optional[Image.Image] = None
        self.draw: Optional[ImageDraw.ImageDraw] = None
        self.page_width: int = int(self.config.page_dimensions[0])
        self.page_height: int = int(self.config.page_dimensions[1])
        
        print("Pipa Image Renderer initialized with Render List interface.")

    # -----------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------

    def _get_font(self, size: float, font_type: str) -> ImageFont.FreeTypeFont:
        """根据配置加载或从缓存中获取字体对象。"""
        key = (size, font_type)
        if key not in self._font_cache:
            font_path = self.config.get_font_path(font_type)
            try:
                # Pillow 需要整数大小
                self._font_cache[key] = ImageFont.truetype(font_path, int(size))
            except IOError:
                print(f"Warning: Font {font_path} not found. Using default.")
                self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]

    def _draw_text(self, text: str, pos: List[float], size: float, font_type: str = 'text', color: str = "black"):
        """
        绘制文本。
        """
        if not self.draw: return
        # 假设 pos 是 [x, y]
        x, y = pos[0], pos[1]
        font = self._get_font(size, font_type)

        # 使用 'ra' (Right-Top/Ascender) 锚点，符合竖排排版习惯
        self.draw.text(
            (x, y), 
            text, 
            fill=color, 
            font=font, 
            anchor="ra" 
        )

    def _get_space_metrics(self, font_type: str) -> Tuple[float, float]:
        """根据 font_type 查找对应的空间度量 (x_space, y_space)。"""
        if font_type == 'title':
            return self.config.title_space
        elif font_type == 'mode':
            return self.config.mode_space
        elif font_type == 'textunit': # 用于 TextBlock/普通文本
            return self.config.textunit_space
        elif font_type == 'main_char':
            return self.config.main_char_space # 主字符空间
        elif font_type == 'small_char':
            return self.config.small_char_space # 主字符空间
    
    def _draw_vertical_string(
        self, 
        text: str, 
        start_pos: Tuple[float, float], 
        size: float, 
        font_type: str,
        color: str = 'black'
    ) -> float:
        """
        将字符串中的每个字符从上到下逐个绘制（用于标题/调式）。
        
        返回: 最后一个字符的 Y 轴结束位置（下一个元素应开始的位置）。
        """
        
        start_x, current_y = start_pos
        
        # 根据 font_type 获取对应的 Y 轴空间占用
        _, char_y_space = self._get_space_metrics(font_type)
        
        # 逐字符绘制
        for char in text:
            # 绘制当前字符
            self._draw_text(
                char, 
                [start_x, current_y], 
                size, 
                font_type,
                color
            )
            
            # 更新 Y 轴：向下移动一个字符的 Y 空间
            current_y += char_y_space
        return
    
    def _draw_text_block(
        self, 
        text: str, 
        start_pos: Tuple[float, float], 
        font_size: float, 
        font_type: str, 
        dimensions: Tuple[float, float],
        color: str
    ):
        """
        绘制具有换行特性的竖排注释文本块。
        """
        if not text: return
            
        start_x, start_y = start_pos
        
        # 获取空间度量 (假设 text/textunit 字体类型)
        x_space, y_space = self._get_space_metrics(font_type)
        
        # dimensions: (width_available, height_available)
        available_height = self.config.page_dimensions[1] - start_y - self.config.margin["bottom"]
        
        if available_height <= 0:
            print("Warning: Not enough vertical space for text block.")
            return
            
        # 计算每列最大字符数
        max_chars_per_col = math.floor(available_height / y_space)
        
        if max_chars_per_col <= 0:
            print("Warning: Max chars per column is zero, skipping text block.")
            return

        # 开始迭代绘制
        current_x = start_x
        current_y = start_y
        char_count = 0

        for char in text:
            # 绘制当前字符
            self._draw_text(char, [current_x, current_y], font_size, font_type, color)
            
            char_count += 1
            current_y += y_space
            
            # 检查是否达到列最大字符数
            if char_count >= max_chars_per_col:
                current_x -= x_space # 换列：X 坐标向左移动
                current_y = start_y  # Y 坐标回到初始位置
                char_count = 0


    # -----------------------------------------------------------
    # 核心命令处理和渲染入口
    # -----------------------------------------------------------

    def _handle_command(self, command: Dict[str, Any]):
        """根据命令类型分发绘制操作。"""
        cmd_type = command['type']
        pos:Tuple = command['position']
        text:str = command.get('text', '')
        metadata:Dict = command.get('metadata', {})
        
        style = self.styles.get(cmd_type, {})
        size_key = style.get('font_size_key', 'main_char_size')
        font_type = style.get('font_type', 'title')
        color = style.get('color', 'black')
        
        font_size = getattr(self.config, size_key, self.config.main_char_size)

         
        if cmd_type == "TEXT_BLOCK":
            dimensions = metadata.get('dimensions', (self.page_width, self.page_height)) # 假设 Layout Pass 提供了可用尺寸
            self._draw_text_block(text, pos, font_size, font_type, dimensions, color)
            return

        if cmd_type in ["DOCUMENT_TITLE", "SECTION_TITLE", "MODE"]:
            self._draw_vertical_string(text, pos, font_size, font_type, color)
            return
        
        self._draw_text(text, pos, font_size, font_type, color)
       

    def render(self, output_path: str) -> str:
        """
        公共入口：接收 Render Artifact (包含 pages)，初始化画布，并遍历绘制所有命令。
        
        Args:
            render_artifact: Layout Pass 的最终输出。
            output_path: 图像保存路径。
            
        Returns:
            保存图像的文件路径。
        """
        render_artifact = self.context.render_artifact["png"]
        if not render_artifact:
            print("Render Artifact is invalid or empty.")
            return ""
            
        # 1. 确定文件夹名称（使用第一页第一个命令的 text 值）
        first_command = render_artifact[0][0]
        folder_name = first_command.get('text', 'untitled_score').strip()
        
        # 清理文件夹名中的非法字符
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '_')).rstrip()
        if not folder_name:
            folder_name = 'untitled_score'

        # 2. 构造完整的保存目录路径
        save_dir = os.path.join(output_path, folder_name)
        
        # 3. 创建目录（如果不存在）
        try:
            os.makedirs(save_dir, exist_ok=True)
            print(f"Saving to directory: {save_dir}")
        except OSError as e:
            print(f"Error creating directory {save_dir}: {e}")
            return ""

        # 4. 遍历并渲染所有页面
        rendered_pages = []
        
        for page_index, page_commands in enumerate(render_artifact):
            # --- 初始化画布 ---
            self.canvas = Image.new('RGB', (self.page_width, self.page_height), 'white')
            self.draw = ImageDraw.Draw(self.canvas)
            print(f"Rendering Page {page_index + 1}...")

            num_x = 2*self.config.margin["left"]
            num_y = self.config.page_dimensions[1] - 0.6* self.config.margin["bottom"]
            num_pos = (num_x,num_y)
            # --- 遍历并处理当前页面的所有命令 ---
            for command in page_commands:
                # num = 1
                # text = "page" + "_" + str(num)
                # font = self._get_font(25,"text")
                try:
                    self._handle_command(command)
                except Exception as e:
                    print(f"Error processing command {command.get('type')} on page {page_index + 1}: {e}")
            # self.draw.text(
            #     num_pos, 
            #     text, 
            #     fill="grey", 
            #     font=font, 
            #     anchor="ra" 
            # )
            
            # --- 5. 保存当前页面文件 ---
            file_name = f"page_{page_index + 1:03d}.png" # 格式化为 page_001.png, page_002.png
            page_save_path = os.path.join(save_dir, file_name)

            # num += 1
            
            try:
                self.canvas.save(page_save_path, 'PNG')
                print(f"Saved page {page_index + 1} to {page_save_path}")
            except Exception as e:
                print(f"Error saving image page {page_index + 1}: {e}")
                # 如果一页保存失败，不影响继续渲染下一页

        print("--- Pipa Image Rendering Completed ---")
        return save_dir # 返回最终保存的目录路径