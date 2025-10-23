import logging
import math
from typing import Dict, Tuple, Optional

from ..visitors.base_visitor import BaseVisitor
from ..ast_score.nodes import ScoreDocumentNode, SectionNode, ScoreUnitNode, TextNode
from ..config.layout_config import PipaLayoutConfig
#TODO: 初始化 Logger

class PipaLayoutPass(BaseVisitor):
    """
    负责计算所有 AST 元素的精确几何位置和尺寸。
    
    核心职责：
    1. 计算 ScoreDocumentNode 的页首元数据位置 (X, Y) 和总宽度。
    2. 计算 SectionNode 的起始位置。
    3. 计算 ScoreUnitNode 的绝对位置和内部组件的相对位置。
    4. 驱动 X 轴（列）和 Y 轴（行）的流式排版。
    """
    
    def __init__(
            self, 
            page_dimensions = (2160, 1280), 
            margin: Dict[str, float] = {
                "top": 20, 
                "left": 20, 
                "right": 20, 
                "bottom": 20
            }
        ):
        super().__init__()
        
        # --- 全局状态 (用于 X/Y 流控制) ---
        self.page_dimensions = page_dimensions
        self.margin = margin
        self.layout_config = PipaLayoutConfig()

        # current_x: 当前列的起始X坐标 (排版从右侧页边距开始)
        self.current_x = self.page_dimensions[0] - self.margin['right']
        # current_y: 当前行内元素的起始Y坐标 (排版从顶部页边距开始)
        self.current_y = self.margin['top']
        
        # 跟踪上一个元素占用的高度，以便在 Y 轴上堆叠
        self.last_element_height: float = 0.0
        
        # 实际可用的y高度
        effective_y_height = (
            self.page_dimensions[1] - self.margin['top'] - self.margin['bottom']
        )

        self.scoreunit_height = effective_y_height/ self.layout_config.UNIT_NUM
        self.scoreunit_counter: int = 0  # 计数当前列已排版的单元数量
        self.time_counter: int = 0 # 用于排版的时值计数器
        self.unit_temp_y = 0

        #计算每列可容纳最大内容文本字数
        self.text_column = effective_y_height - (2 * self.layout_config.main_char_space[1])
        self.max_text_per_column = math.floor(self.text_column / self.layout_config.textunit_space[1])
        print("PipaLayoutPass initialized.")


    # --- 辅助方法 (用于测量) ---

    # --- 核心 visit 方法 ---

    def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
        """处理文档根节点，计算页首元数据并确定乐谱主体的起始点。"""
        print("Visiting ScoreDocumentNode: Calculating Header Layout.")
        
        # 1. 初始化 X/Y 流控起始点
        self.current_x: float = self.page_dimensions[0] - self.margin['right']
        self.current_y = self.margin['top']
        header_width_acc = 0.0 # 页首总宽度累加器

        # --- 2. 处理 Title 元数据 ---
        if node.title:
            title_w = self.layout_config.title_space[0]
            
            # X 坐标：当前列的起始点
            node.title_pos = (self.current_x, self.current_y)
            
            # 更新 X 流控：向左移动
            self.current_x -= title_w
            header_width_acc += title_w

        # --- 3. 处理 Mode 元数据 ---
        if node.mode:
            mode_w = self.layout_config.mode_space[0]
            mode_unit_h = self.layout_config.mode_space[1]
            mode_indentation = self.current_y + mode_unit_h # 一格缩进
            # X 坐标：当前列的起始点 (是上一个元素计算后的新 current_x)
            node.mode_pos = (self.current_x, mode_indentation)

            # 更新 X 流控：向左移动
            self.current_x -= mode_w
            header_width_acc += mode_w

        # 4. 注入最终总宽度
        node.width_dimension = header_width_acc
        
        # 5. 更新 Y 流控：乐谱主体仍然从顶部的 Y 坐标开始
        # 但 X 坐标需要跳过页首区域，从新的 self.current_x 开始
        # 这里不需要更新 self.current_y，因为页首信息和乐谱主体在 X 轴上是平行的。
        
        self.generic_visit(node)
        
    def visit_SectionNode(self, node: SectionNode):
        """处理乐部节点，设置起始 X/Y 坐标，并开始列排版。"""
        print(f"Visiting SectionNode: {node.title}")

        header_width_acc = 0.0 # 页首总宽度累加器
        
        if node.title:
            title_w = self.layout_config.title_space[0]
            title_unit_h = self.layout_config.title_space[1]
            title_indentation = self.current_y + title_unit_h # 硬编码一格缩进
            # 1. 确定 Section 的起始 X/Y 坐标 (承接 Document 的流控)
            node.title_pos = (self.current_x, title_indentation)
            self.current_x -= title_w
            header_width_acc += title_w

            # 3. 处理转调文本 (mode_display_flag)
        if node.mode_display_flag:
            mode_w = self.layout_config.mode_space[0]
            mode_unit_h = self.layout_config.mode_space[1]
            mode_indentation = self.current_y + mode_unit_h # 一格缩进
            # X 坐标：当前列的起始点 (是上一个元素计算后的新 current_x)
            node.mode_pos = (self.current_x, mode_indentation)
            header_width_acc += mode_w
            # 更新 X 流控：向左移动
            self.current_x -= mode_w
            header_width_acc += mode_w      
        # 4. 遍历 Section 内部元素 (elements)
        node.width_dimension = header_width_acc
        self.generic_visit(node)
    
    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        """处理谱字单元，计算其绝对位置和内部组件的相对位置。"""
        # --- 1. 检查是否需要换列 (Column Break) ---
        if self.scoreunit_counter >= self.layout_config.UNIT_NUM:
            self._do_column_break()

        # --- 2. 计算绝对定位和尺寸 ---
        
        # X 坐标：继承自当前 X (self.current_x)
        self.current_x -= self.layout_config.scoreunit_x_offset # 向左平移
        # Y 坐标：继承自当前 Y (self.current_y)

        # 尺寸：基于时值或固定单元宽度计算，并更新 self.last_element_height
        unit_width = self.layout_config.main_char_space[0]
        unit_height = self.scoreunit_height
        
        # 设置主谱字位置
        node.main_char_pos = (self.current_x, self.current_y)
        
        # 缓存当前只拍子起始位置，用于当时值为整数时执行缩进
        if self.time_counter == 0:
            self.unit_temp_y = self.current_y

        # 计算小谱字+引/火的位置
        small_mod_y = self._layout_small_modifiers(node)

        # 计算右边符号位置
        self._layout_right_rhythm_modifier(node)

        
        # --- 3. 更新 X/Y 流控 ---
        # 先计算时值累加
        self.time_counter += node.time

        # 从同一起点计算，防止float累计误差
        if self.time_counter == 1:            
            self.current_y = self.unit_temp_y + (unit_height * 0.4)
        elif self.time_counter == 2:            
            self.current_y = self.unit_temp_y + (unit_height * 0.8)
        else:
            self.current_y = small_mod_y

        # 处理底部符号位置
        self._layout_bottom_rhythm_modifier(node, unit_width, unit_height)

        #TODO 如果想让只拍子或其他底部符号可以出现在一个只拍子内部，让layout_bottom_rhythm_modifier移到第二步中，返回一个偏移值（0.2unitheight），第三步里，如果存在则加上，不存在则返回0，

        # 更新计数器
        self.scoreunit_counter += 1  

        return

    def visit_TextNode(self,node: TextNode):
        """处理文本单元，计算其绝对位置"""
        text_indentation = self.current_y + (2 * self.layout_config.main_char_space[1]) # 硬编码两格缩进
        node.position = (self.current_x, text_indentation)
        total_texts = len(node.text)
        total_columns = math.ceil(total_texts / self.max_text_per_column)
        node.width_dimension = total_columns * self.layout_config.textunit_space[0]
        self.current_x -= node.width_dimension
        return
    
 

    def _layout_small_modifiers(self, node: ScoreUnitNode):
        """计算小字组的相对位置，并注入 AST"""
        
        # 假设所有小字都紧靠在主音符的左侧
        small_mod_x = self.current_x 
        
        # 初始化 Y 轴起始点：
        small_mod_y = self.current_y + self.layout_config.main_char_space[1]

        node.small_mod_pos = []
        if node.small_modifier is not None:
            for _ in node.small_modifier:
                node.small_mod_pos.append((small_mod_x, small_mod_y))
                small_mod_y += self.layout_config.small_char_space[1]
        if node.time_modifier is not None:
            for _ in node.time_modifier:
                node.time_mod_pos = (small_mod_x,small_mod_y)
                small_mod_y += self.layout_config.small_char_space[1]
            
        return small_mod_y

    def _layout_bottom_rhythm_modifier(self, node: ScoreUnitNode, unit_width, unit_height):
        """计算底部符号的相对位置，并注入 AST"""
        if node.bottom_rhythm_modifier == None:
            return
        bottom_mod_x = self.current_x - (unit_width / 2)
        bottom_mod_y = self.current_y + (unit_height * 0.1)
        node.bottom_rhythm_mod_pos = (bottom_mod_x, bottom_mod_y)
        self.current_y = self.unit_temp_y + unit_height
        return
 
    def _layout_right_rhythm_modifier(self,node: ScoreUnitNode):
        """计算右边符号的相对位置，并注入 AST"""
        right_mod_x = self.current_x + (0.5 * self.layout_config.scoreunit_x_offset)
        right_mod_y = self.current_y + (0.5 * self.layout_config.main_char_size)

        node.right_rhythm_mod_pos = (right_mod_x,right_mod_y)
        return
    
    def _do_column_break(self):
        self.current_x -= self.layout_config.main_char_space[0]

        # 从页顶部开始
        self.current_y = self.margin['top']
