import logging
from typing import Dict, Tuple, Optional
from src.scorelang.visitors.base_visitor import BaseVisitor
# 假设的 AST 节点
from src.scorelang.ast_score.nodes import ScoreDocumentNode, SectionNode, ScoreUnitNode, TextRenderInfo
from src.scorelang.config.layout_config import PipaLayoutConfig
# 初始化 Logger

# --- 假设的全局排版常量 (在实际项目中应从配置文件加载) ---
COLUMN_SPACING = 50.0   # 列间距
UNIT_NUM = 4       # 硬编码 每一列的只拍子单元数量


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
            page_dimensions: Tuple[int, int] = (2160, 1280), 
            margin: Dict[str, int] = {
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
        # 当前排版流程的 X/Y 起始点（注意：X从右往左递减）
        # current_x: 当前列的起始X坐标 (排版从右侧页边距开始)
        self.current_x: int = page_dimensions[0] - margin['right']
        # current_y: 当前行内元素的起始Y坐标 (排版从顶部页边距开始)
        self.current_y: int = margin['top']
        
        # 跟踪上一个元素占用的高度，以便在 Y 轴上堆叠
        self.last_element_height: float = 0.0
        
        effective_y_height = (
            self.page_dimensions[1] - margin['top'] - margin['bottom']
        )

        self.scoreunit_height = int(effective_y_height/ UNIT_NUM)
        self.scoreunit_counter: int = 0  # 计数当前列已排版的单元数量
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
        
        if node.title:
            title_w = self.layout_config.title_space[0]
            title_unit_h = self.layout_config.title_space[1]
            title_indentation = self.current_y + title_unit_h # 硬编码一格缩进
            # 1. 确定 Section 的起始 X/Y 坐标 (承接 Document 的流控)
            node.title_pos = (self.current_x, title_indentation)
            self.current_x -= mode_w
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
        if self.unit_counter >= SCOREUNIT_NUM:
            self._do_column_break(node)

        # --- 2. 计算绝对定位和尺寸 ---
        
        # X 坐标：继承自当前 X (self.current_x)
        unit_abs_x = self.current_x - self.layout_config.scoreunit_x_offset # 向左平移
        # Y 坐标：继承自当前 Y (self.current_y)
        unit_abs_y = self.current_y
        
        # 尺寸：基于时值或固定单元宽度计算，并更新 self.last_element_height
        unit_width = self.layout_config.main_char_space[0]
        unit_height = self.scoreunit_height
        
        node.main_char_pos = (unit_abs_x, unit_abs_y)
        node.dimensions = (unit_width, unit_height)
        
        # 计算小字组的相对位置 (依赖于数量和间距)
        self.layout_small_modifiers(node, unit_width, unit_height)
        
        # ... (计算其他修饰符的相对位置) ...
        
        # --- 3. 更新 X/Y 流控 ---
        # Y 轴向下递增，准备下一个单元
        self.current_y += unit_height 
        self.unit_counter += 1  
        # 竖排排版中，每处理一个单元，Y 坐标向下递增
        self.current_y += unit_height 
        self.last_element_height = unit_height
        
        # [TODO: 检查是否到达当前列底部，如果到达，则更新 self.current_x 和重置 self.current_y]

    def layout_small_modifiers(self, node: ScoreUnitNode, unit_width: float, unit_height: float):
        """计算小字组的相对位置，并注入 AST"""
        
        # 假设所有小字都紧靠在主音符的左侧
        fixed_x_offset = - (UNIT_WIDTH / 2 + 5.0) 
        
        # Y 轴起始点：从小字的中心开始
        start_y_offset = unit_height / 2 - (len(node.small_modifier) * SMALL_CHAR_FONT_SIZE / 2)
        
        node.small_mod_pos_offsets = []
        current_y = start_y_offset
        
        for _ in node.small_modifier:
            # 这里的 Y 坐标是相对于 unit_abs_y 的偏移
            node.small_mod_pos_offsets.append((fixed_x_offset, current_y))
            current_y += SMALL_CHAR_FONT_SIZE + SMALL_CHAR_SPACING_Y