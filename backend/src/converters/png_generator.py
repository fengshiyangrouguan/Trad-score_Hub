import os
from typing import List, Optional,Tuple
from PIL import Image, ImageDraw, ImageFont
from ..domain.models import ScoreDocument, ScoreUnit, TextUnit

#TODO: 加上log！！！

DEFAULT_FONT_PATH = r"C:\Windows\Fonts\FZYanZQKSJF.TTF"

class PNGGenerator:
    """
    测试工具类
    负责将 ScoreUnit 数据结构渲染为 PNG 图像的生成器。
    字体和基础配置在初始化时加载。
    """
    def __init__(self, font_path: str = DEFAULT_FONT_PATH, char_size: int = 48, canvas_size: Tuple[int, int] = (150, 3000)):
        self.char_size = char_size
        self.sub_char_size = char_size // 2
        self.canvas_size = canvas_size
        self.font_path = font_path
        self.main_font: ImageFont.ImageFont = None
        self.mod_font: ImageFont.ImageFont = None
        
        # 尝试加载字体
        try:
            self.main_font = ImageFont.truetype(font_path, self.char_size)
            self.mod_font = ImageFont.truetype(font_path, self.sub_char_size)
            print(f"PNGGenerator 初始化成功，已加载字体: {font_path}")
        except IOError:
            print(f"错误：无法加载字体文件 '{font_path}'。请确保路径正确且文件存在。")
            raise


    def generate_scoredocument_image(self, score_doc: ScoreDocument, filename: str = 'test.png'):
        """
        根据ScoreDocument生成整张乐谱图像。
        """
        # 创建大画布
        total_height = 3000  # 总高度初始化为0
        max_width = self.canvas_size[0]  # 假设所有单元宽度相同且等于canvas_size的宽度
               
        img = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 第二步：在大画布上依次绘制每个ScoreUnit
        current_y = 3
        for element in score_doc.elements:
            if not isinstance(element, ScoreUnit):
                continue  # 跳过非ScoreUnit元素
            
            # 更新current_y以反映当前单元的实际高度
            current_y = self.generate_scoreunit_png(unit=element, filename=None, current_y=current_y, img=img)

            # 在两个单元之间添加20像素的间距
            current_y += 20
        
        # 保存最终的大图
        img.save(filename)
        print(f"成功生成文件: {filename}")


    def generate_scoreunit_png(self, unit: ScoreUnit, filename: str, current_y: Optional[int] = 0, img: Optional[Image.Image] = None) -> int:
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

        draw = ImageDraw.Draw(img)

        # --- 1. 绘制主音符 (居中) ---

        main_char = unit.main_score_character
        
        # 测量主字符大小
        bbox = draw.textbbox((0, 0), main_char, font=self.main_font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        
        # 计算竖直靠上，水平居中的坐标
        x_main_draw = (self.canvas_size[0] - char_width) / 2 #x宽带-字符宽度除以二得到绘制起点
        y_main_draw = current_y
        
        # 绘制主字符
        draw.text((x_main_draw, y_main_draw), main_char, fill=text_color, font=self.main_font)

        # --- 2. 绘制小字号修饰符 (下方和右方) ---
        # 假设所有 small_modifiers 都是文本
        mod_x_start = x_main_draw + (char_width//2) + 10 # 放在主音符的中间偏右侧
        mod_y_start = y_main_draw + char_height + 10 # 放在主音符的下方

        current_mod_y = mod_y_start

        for mod in unit.small_modifiers:
            mod_text = mod
            
            # 针对 '/h' (火) 和 '/y' (引) 进行特殊渲染（如果需要）
            if mod == '/h':
                 mod_text = '火' # 渲染为汉字
            elif mod == '/y':
                mod_text = '引' # 渲染为汉字
            
            # 绘制修饰符
            draw.text((mod_x_start, current_mod_y), mod_text, fill=(150, 0, 0), font=self.mod_font)
            
            # 移动下一个修饰符的位置 (简单的竖直堆叠)
            mod_bbox = draw.textbbox((0, 0), mod_text, font=self.mod_font)
            mod_height = mod_bbox[3] - mod_bbox[1]
                
            current_mod_y += mod_height + 2

        # --- 3. 绘制节奏修饰符 (下方和右方点) ---
        
        # 绘制 '/zp' (下方圆圈)
        if unit.bottom_rhythm_modifier == '/pz':
            # 放置在主音符正下方
            dot_radius = 5
            dot_x = self.canvas_size[0] // 2
            dot_y = current_mod_y + 20  # 放在所有下方修饰符的下方
            # 使用draw.ellipse方法绘制圆圈
            draw.ellipse(
                (
                    dot_x - dot_radius, dot_y - dot_radius, 
                    dot_x + dot_radius, dot_y + dot_radius
                ), 
                outline=(0, 0, 0), fill=None  # 绘制空心圆，根据需要调整颜色
            )
            current_mod_y += 20  # 更新current_mod_y以避免重叠


        # 绘制 '/r' (休止符线)
        if unit.bottom_rhythm_modifier == '/r':
            # 放置在主音符下方作为休止线
            line_y = current_mod_y + 5
            line_x1 = self.canvas_size[0] // 2
            line_x2 = line_x1 + (char_width // 2)
            draw.line((line_x1, line_y, line_x2, line_y), fill=text_color, width=3)

        # 绘制 '/yp' (右方点)
        if unit.right_rhythm_modifier == '/py':
            # 放置在主音符右侧中间
            dot_radius = 5
            dot_x = int(x_main_draw + char_width + 20)
            dot_y = int((y_main_draw + char_height) / 2)
            draw.ellipse((dot_x - dot_radius, dot_y - dot_radius, 
                          dot_x + dot_radius, dot_y + dot_radius), 
                         fill=text_color, outline=text_color)
            
        # 绘制 '/b' (右方“百”字)
        if unit.right_rhythm_modifier == '/b':
            text = '百'
            text_bbox = draw.textbbox((0, 0), text, font=self.mod_font)
            text_height = text_bbox[3] - text_bbox[1]
            text_x = int(x_main_draw + char_width + 10)
            text_y = int(y_main_draw + (char_height/ 2))
            draw.text((text_x, text_y), text, fill=text_color, font=self.mod_font)

        return current_mod_y


