import os
from typing import List, Optional,Tuple
from PIL import Image, ImageDraw, ImageFont
from ..domain.models import ScoreDocument, ScoreUnit, TextUnit

#TODO: 加上log！！！

class PNGGenerator:
    """
    测试工具类
    负责将 ScoreUnit 数据结构渲染为 PNG 图像的生成器。
    字体和基础配置在初始化时加载。
    """
    def __init__(self, font_path: str, char_size: int = 48, canvas_size: Tuple[int, int] = (150, 150)):
        self.char_size = char_size
        self.canvas_size = canvas_size
        self.font_path = font_path
        self.main_font: ImageFont.ImageFont = None
        self.mod_font: ImageFont.ImageFont = None
        
        # 尝试加载字体
        try:
            self.main_font = ImageFont.truetype(font_path, char_size)
            self.mod_font = ImageFont.truetype(font_path, char_size // 3)
            print(f"PNGGenerator 初始化成功，已加载字体: {font_path}")
        except IOError:
            print(f"错误：无法加载字体文件 '{font_path}'。请确保路径正确且文件存在。")
            raise

    def generate_png(self, unit: ScoreUnit, filename: str):
        """
        将单个 ScoreUnit 渲染为 PNG 图像。

        Args:
            unit: 要渲染的 ScoreUnit 实例。
            filename: 输出 PNG 文件的名称。
        """
        if not self.main_font:
            print("错误：字体未加载，无法渲染。")
            return

        # 图像配置
        bg_color = (255, 255, 255) # 白色背景
        text_color = (0, 0, 0)      # 黑色文字

        # 创建图像和绘图对象
        img = Image.new('RGB', self.canvas_size, bg_color)
        draw = ImageDraw.Draw(img)

        # --- 1. 绘制主音符 (居中) ---
        main_char = unit.main_score_character
        
        # 测量主字符大小
        try:
            bbox = draw.textbbox((0, 0), main_char, font=self.main_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(main_char, font=self.main_font)
        
        # 计算居中位置
        x_center = (self.canvas_size[0] - text_width) / 2
        y_center = (self.canvas_size[1] - text_height) / 2
        
        # 绘制主字符
        draw.text((x_center, y_center), main_char, fill=text_color, font=self.main_font)

        # --- 2. 绘制小字号修饰符 (上方和右方) ---
        # 假设所有 small_modifiers 都是文本
        mod_x_start = x_center + text_width + 5
        mod_y_start = y_center - 10 # 放在主音符的上方偏右

        current_mod_x = mod_x_start

        for mod in unit.small_modifiers:
            mod_text = mod
            
            # 针对 '/h' (火) 和 '/y' (引) 进行特殊渲染（如果需要）
            if mod == '/h':
                mod_text = '火' # 渲染为汉字
            elif mod == '/y':
                mod_text = '引' # 渲染为汉字
            
            # 绘制修饰符
            draw.text((current_mod_x, mod_y_start), mod_text, fill=(150, 0, 0), font=self.mod_font)
            
            # 移动下一个修饰符的位置 (简单的水平堆叠)
            try:
                mod_bbox = draw.textbbox((0, 0), mod_text, font=self.mod_font)
                mod_width = mod_bbox[2] - mod_bbox[0]
            except AttributeError:
                mod_width = draw.textsize(mod_text, font=self.mod_font)[0]
                
            current_mod_x += mod_width + 2

        # --- 3. 绘制节奏修饰符 (下方和右方点) ---
        
        # 绘制 '/zp' (下方点)
        if unit.bottom_rhythm_modifier == '/zp':
            # 放置在主音符正下方
            dot_radius = 5
            dot_x = int(x_center + text_width / 2)
            dot_y = int(y_center + text_height + 5)
            draw.ellipse((dot_x - dot_radius, dot_y - dot_radius, 
                          dot_x + dot_radius, dot_y + dot_radius), 
                         fill=text_color, outline=text_color)

        # 绘制 '/yp' (右方点)
        if unit.right_rhythm_modifier == '/yp':
            # 放置在主音符右侧中间
            dot_radius = 5
            dot_x = int(x_center + text_width + 15)
            dot_y = int(y_center + text_height / 2)
            draw.ellipse((dot_x - dot_radius, dot_y - dot_radius, 
                          dot_x + dot_radius, dot_y + dot_radius), 
                         fill=text_color, outline=text_color)
        
        # 绘制 '/r' (休止符线)
        if unit.bottom_rhythm_modifier == '/r':
            # 放置在主音符下方作为休止线
            line_y = int(y_center + text_height + 5)
            line_x1 = int(x_center - 10)
            line_x2 = int(x_center + text_width + 10)
            draw.line((line_x1, line_y, line_x2, line_y), fill=text_color, width=3)


        # 保存图像
        img.save(filename)
        print(f"成功生成文件: {filename}")


