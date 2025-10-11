import os
import textwrap
from typing import List, Optional,Tuple
from PIL import Image, ImageDraw, ImageFont
from ..domain.models import ScoreDocument, ScoreUnit, TextUnit

#TODO: 加上log！！！

DEFAULT_FONT_PATH = r"C:\Windows\Fonts\FZYanZQKSJF.TTF"
# --- 布局配置 ---
IMG_WIDTH = 2160 
IMG_HEIGHT = 1280
MARGIN_X = 30
MARGIN_Y = 30
EDGE_MAX_Y = 50 #靠近边缘警戒值
COLUMN_WIDTH = 80 # 每个乐谱单元列的固定宽度
UNIT_SPACING_Y = 20 # 乐谱单元之间的垂直间距
COLUMN_SPACING_X = 40 # 乐谱列之间的水平间距
TEXT_PADDING_Y = 10 # 文本行之间的垂直间距

# 定义 TextUnit 绘制配置
TEXT_CONFIG = {
    'TITLE': {'font_size_ratio': 1.5, 'fill_width': True, 'leading_space': 0},  # 顶格写满一行
    'SOURCE': {'font_size_ratio': 0.8, 'fill_width': False, 'leading_space': 2},
    'MODE': {'font_size_ratio': 0.8, 'fill_width': False, 'leading_space': 2},  # 向下两格
    'SECTION': {'font_size_ratio': 1.0, 'fill_width': False, 'leading_space': 2}, # 向下两格
    #'COMMENT': {'font_size_ratio': 0.6, 'fill_width': True, 'leading_space': 4}, # 向下四格
    'COMMENT': {'font_size_ratio': 0.6, 'fill_width': False, 'leading_space': 4}, # 向下四格(测试用comment) 
}

class PNGGenerator:
    """
    测试工具类
    负责将 ScoreDocument 数据结构渲染为 PNG 图像的生成器。
    实现了多列布局和文本排版。
    """
    def __init__(self, font_path: str = DEFAULT_FONT_PATH, char_size: int = 48, canvas_size: Tuple[int, int] = (IMG_WIDTH, IMG_HEIGHT)):
        self.char_size = char_size
        self.sub_char_size = char_size // 2
        self.canvas_size = canvas_size
        self.font_path = font_path
        self.main_font: ImageFont.ImageFont = None
        self.sub_font: ImageFont.ImageFont = None
        
        # 尝试加载字体
        try:
            self.main_font = ImageFont.truetype(font_path, self.char_size)
            self.sub_font = ImageFont.truetype(font_path, self.sub_char_size)
            print(f"PNGGenerator 初始化成功，已加载字体: {font_path}")
        except IOError:
            print(f"错误：无法加载字体文件 '{font_path}'。请确保路径正确且文件存在。")
            raise


    def generate_scoredocument_image(self, score_doc: ScoreDocument, filename: str = 'score_output.png'):
        """
        根据ScoreDocument生成整张乐谱图像。
        """
        # 创建大画布
        total_height = self.canvas_size[1]  # 总高度初始化为0
        max_width = self.canvas_size[0]  # 假设所有单元宽度相同且等于canvas_size的宽度
               
        img = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 边界设置
        draw_area_height = IMG_HEIGHT - 2 * MARGIN_Y
        
        # 初始化绘制起点（）
        current_x = IMG_WIDTH - MARGIN_X - COLUMN_WIDTH
        current_y = MARGIN_Y

        # 使用 while 循环和索引，以便在 TextUnit 跨列时可以重新绘制当前元素
        elements_list = score_doc.elements
        element_index = 0


        while element_index < len(elements_list):
            element = elements_list[element_index]            
            
            # --- 边界检查 ---
            if current_x < MARGIN_X:
                print("Warning: Score exceeds page capacity. Stopping rendering.")
                break 
    
            if isinstance(element, ScoreUnit):
               # ScoreUnit预检查：如果只剩下一个单元的绘制空间，就直接换列，避免绘制在警戒区
                if current_y > MARGIN_Y + draw_area_height - EDGE_MAX_Y:
                    # 触发换列
                    current_x -= (COLUMN_WIDTH + COLUMN_SPACING_X)
                    current_y = MARGIN_Y
                    # 再次检查边界，虽然上面检查过，但安全起见
                    if current_x < MARGIN_X: break
                
                # 绘制 ScoreUnit
                current_y = self._draw_score_unit(draw=draw, unit=element, current_x=current_x, current_y=current_y)
                current_y += UNIT_SPACING_Y  # 在 ScoreUnit 后面添加垂直间距
                element_index += 1           # 完成绘制，推进索引

            elif isinstance(element, TextUnit):
                text_col_width = COLUMN_WIDTH

                # 绘制 TextUnit，它会处理自身的跨列逻辑
                # **关键修复：这里必须接收 (current_y, remaining_text) 元组**
                current_y, remaining_text = self._draw_text_unit(
                    draw, 
                    element, 
                    current_x, 
                    current_y, 
                    text_col_width,
                )

                # **关键修复：处理换列信号**
                if remaining_text:
                    # TextUnit 被中断，需要换列并在新列顶部继续绘制
                    
                    # 1. 将剩余文本替换当前元素，以便重新绘制
                    elements_list[element_index] = TextUnit(text=remaining_text, type=element.type)
                    # 2. 触发换列
                    current_x -= (COLUMN_WIDTH + COLUMN_SPACING_X)
                    current_y = MARGIN_Y
                    
                    # 3. DO NOT 推进 element_index，以便在下一轮循环中，新的 current_x/y 下重新处理剩余的文本
                else:
                    # 这解决了 TextUnit (如标题) 后面紧跟 ScoreUnit 导致未换列的问题。
                    if TEXT_CONFIG[element.type]['fill_width'] == False:
                        current_x -= (COLUMN_WIDTH + COLUMN_SPACING_X)
                        current_y = MARGIN_Y
                    # ------------------------------------------------
                    
                    # TextUnit 完整绘制完成
                    element_index += 1 # 完成绘制，推进索引


        # 保存最终的大图
        img.save(filename)
        print(f"成功生成文件: {filename}")


    def _draw_text_unit(self, draw: ImageDraw.ImageDraw, unit: TextUnit, x: int, y: int, col_width: int) -> int:
        """
        绘制 TextUnit，处理不同类型文本的字号、缩进和换行。
        返回绘制所占用的总高度。
        """
        
        config = TEXT_CONFIG.get(unit.type, {'font_size_ratio': 1.0, 'fill_width': False, 'leading_space': 0})
        
        #前置强制换列检查
        if (config['fill_width'] == False) and y > MARGIN_Y:
            # 返回原始 Y 和全部文本，强制主循环换列（这是“换列信号”）
            return y, unit.text 
        
        # 字体和颜色
        text_color = (0, 0, 0)
        font_size = self.char_size * config['font_size_ratio'] # 默认使用修饰符字体大小
        font = ImageFont.truetype(self.font_path, font_size)

        # 1. 应用前置缩进 (Leading Space)
        current_y = MARGIN_Y + font_size*config['leading_space']
        total_height = config['leading_space']
        char_block_height = font_size + TEXT_PADDING_Y
        
        # 2. 计算实际可绘制宽度
        # 文本从当前列的左侧边缘开始绘制
        draw_start_x = x
        draw_area_width = col_width 
        
        # 3. 文本换行处理
        # if config['fill_width']:
        #     # 计算每行可容纳的字符数
        #     try:
        #         avg_char_width = font.getbbox("测")[2] - font.getbbox("测")[0]
        #         max_chars = int(draw_area_width / avg_char_width)
        #         if max_chars < 1: max_chars = 1
        #     except Exception:
        #         max_chars = 10 # 容错
            
        #     wrapper = textwrap.TextWrapper(width=max_chars, subsequent_indent='', initial_indent='')
        #     lines = wrapper.wrap(text=unit.text)
        # else:
        #     # 不填满宽度，只作为一行输出 (如 @调名)
        #     lines = [unit.text]

        # 4. 逐行绘制
        for i, char in enumerate(unit.text):
            next_y = current_y + char_block_height
            
            # 绘制单个字符 (从上到下)
            draw.text((draw_start_x, current_y), char, fill=text_color, font=font)
            
            # 移动到下一个字符的 Y 坐标
            current_y = next_y
                
        remaining_text = None

        # 5. 返回结果
        if remaining_text:
            # 文本被分页或预检查触发了换列
            return current_y, remaining_text
        else:
            # 绘制完毕
            return current_y, None 



    def _draw_score_unit(self, draw: ImageDraw.ImageDraw, unit: ScoreUnit, current_x: Optional[int] = 0, current_y: Optional[int] = 0) -> int:
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
        sub_color = (255,0,0)

        draw = draw

        # --- 1. 绘制主音符 (居中) ---

        main_char = unit.main_score_character
        
        # 测量主字符大小
        bbox = draw.textbbox((0, 0), main_char, font=self.main_font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        
        # 计算起始坐标
        x_main_draw = current_x
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
            draw.text((mod_x_start, current_mod_y), mod_text, fill= sub_color , font=self.sub_font)
            
            # 移动下一个修饰符的位置 (简单的竖直堆叠)
            mod_bbox = draw.textbbox((0, 0), mod_text, font=self.sub_font)
            mod_height = mod_bbox[3] - mod_bbox[1]
                
            current_mod_y += mod_height + 2

        # --- 3. 绘制节奏修饰符 (下方和右方点) ---
        
        # 绘制 '/zp' (下方圆圈)
        if unit.bottom_rhythm_modifier == '/pz':
            # 放置在主音符正下方
            dot_radius = 5
            dot_x = current_x + self.char_size // 2
            dot_y = current_mod_y + 20  # 放在所有下方修饰符的下方
            # 使用draw.ellipse方法绘制圆圈
            draw.ellipse(
                (
                    dot_x - dot_radius, dot_y - dot_radius, 
                    dot_x + dot_radius, dot_y + dot_radius
                ), 
                outline=sub_color, fill=None  # 绘制空心圆，根据需要调整颜色
            )
            current_mod_y += 20  # 更新current_mod_y以避免重叠


        # 绘制 '/r' (休止符线)
        if unit.bottom_rhythm_modifier == '/r':
            # 放置在主音符下方作为休止线
            line_y = current_mod_y + 5
            line_x1 = current_x + char_width // 2
            line_x2 = line_x1 + (char_width // 2)
            draw.line((line_x1, line_y, line_x2, line_y), fill=sub_color, width=3)

        # 绘制 '/yp' (右方点)
        if unit.right_rhythm_modifier == '/py':
            # 放置在主音符右侧中间
            dot_radius = 5
            dot_x = int(x_main_draw + char_width + 20)
            dot_y = int((y_main_draw + char_height) / 2)
            draw.ellipse((dot_x - dot_radius, dot_y - dot_radius, 
                          dot_x + dot_radius, dot_y + dot_radius), 
                         fill=sub_color, outline=sub_color)
            
        # 绘制 '/b' (右方“百”字)
        if unit.right_rhythm_modifier == '/b':
            text = '百'
            text_bbox = draw.textbbox((0, 0), text, font=self.sub_font)
            text_height = text_bbox[3] - text_bbox[1]
            text_x = int(x_main_draw + char_width + 10)
            text_y = int(y_main_draw + (char_height/ 2))
            draw.text((text_x, text_y), text, fill=sub_color, font=self.sub_font)

        return current_mod_y


