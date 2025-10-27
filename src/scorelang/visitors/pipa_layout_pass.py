import logging
import math
from typing import Dict

from ..visitors.base_visitor import BaseVisitor
from ..ast_score.nodes import ScoreDocumentNode, SectionNode, ScoreUnitNode, TextNode
from ..config.layout_config import PipaLayoutConfig
from ..visitors.utils.render_commands import RenderListBuilder
from ..core.pipeline_context import PipelineContext
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
            context
        ):
        super().__init__(context)
        
        # --- 全局状态 (用于 X/Y 流控制) ---
        self.layout = PipaLayoutConfig()
        self.page_dimensions =self.layout.page_dimensions
        self.margin = self.layout.margin
        

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

        self.scoreunit_height = effective_y_height/ self.layout.UNIT_NUM
        self.scoreunit_counter: int = 0  # 计数当前列已排版的单元数量
        self.time_counter: int = 0 # 用于排版的时值计数器
        self.unit_temp_y = 0

        #计算每列可容纳最大内容文本字数
        self.text_column = effective_y_height - (2 * self.layout.main_char_space[1])
        self.max_text_per_column = math.floor(self.text_column / self.layout.textunit_space[1])

        #上一个字是否是乐谱的标志位
        self._is_score_unit = False

        self.all_page_render_lists = [] # 存储所有页面的主列表
        self.current_page_render_list = [] # 存储当前页面的绘制指令
        self.page_number = 1
        self.command = RenderListBuilder(self.current_page_render_list)

        self.current_display_mode = None

        print("PipaLayoutPass initialized.")

    def _do_page_break(self):
        # 1. 结束当前页，将指令列表添加到总列表
        self.all_page_render_lists.append(list(self.current_page_render_list))

        # 2. 准备新页
        self.page_number += 1
        self.current_page_render_list = []
        self.command = RenderListBuilder(self.current_page_render_list)

        # 3. 重置 X/Y 流控到新页的顶部和右侧
        self.current_x = self.page_dimensions[0] - self.margin['right']
        self.current_y = self.margin['top']
        # TODO: 处理跨页元素，如页眉/页码的绘制指令。

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
            title_w = self.layout.title_space[0]
            
            # 添加指令
            title_pos = (self.current_x, self.current_y)
            self.command.add_document_title(text=node.title,position=title_pos)

            # 更新 X 流控：向左移动
            self.current_x -= title_w
            header_width_acc += title_w

        # --- 3. 处理 Mode 元数据 ---
        if node.mode:
            mode_w = self.layout.mode_space[0]
            title_unit_h = self.layout.title_space[1]
            mode_indentation = self.current_y + title_unit_h # 硬编码一格缩进

            # 添加指令
            mode_pos = (self.current_x, mode_indentation)
            self.command.add_mode(text=node.mode,position=mode_pos)
            
            # 更新 X 流控：向左移动
            self.current_x -= mode_w
            header_width_acc += mode_w

        
        # 5. 更新 Y 流控：乐谱主体仍然从顶部的 Y 坐标开始
        # 但 X 坐标需要跳过页首区域，从新的 self.current_x 开始
        # 这里不需要更新 self.current_y，因为页首信息和乐谱主体在 X 轴上是平行的。

        self.current_display_mode = node.mode
        
        self.generic_visit(node)

        # 确保将最后一页的指令列表也添加到总列表
        if self.current_page_render_list:
            self.all_page_render_lists.append(list(self.current_page_render_list))

        print("--- Layout Completed ---")
        print(self.all_page_render_lists)

        self.context.node = node
        self.context.layout_config=self.layout
        self.context.add_render_artifact("png",self.all_page_render_lists)
        
    def visit_SectionNode(self, node: SectionNode):
        """处理乐部节点，设置起始 X/Y 坐标，并开始列排版。"""
        print(f"Visiting SectionNode: {node.title}")

        self.current_y = self.margin['top']

        useable_space = self.current_x - self.margin["left"]
        if useable_space < self.layout.title_space[0]:
            self._do_page_break()

        if self._is_score_unit == True:
            self.current_x -= (self.layout.main_char_space[0] + self.layout.scoreunit_x_offset)
            self.scoreunit_counter = 0
            self.time_counter = 0
            self._is_score_unit = False
        header_width_acc = 0.0 # 页首总宽度累加器
        
        if node.title:
            title_w = self.layout.title_space[0]
            title_unit_h = self.layout.title_space[1]
            title_indentation = self.current_y + title_unit_h # 硬编码一格缩进

            # 添加命令
            title_pos = (self.current_x, title_indentation)
            self.command.add_section_title(text=node.title,position=title_pos)

            self.current_x -= title_w
            header_width_acc += title_w

        # 3. 处理转调文本 (mode_display_flag)
        if node.mode != self.current_display_mode:
            mode_w = self.layout.mode_space[0]
            mode_indentation = self.current_y + title_unit_h # 一格缩进
            # X 坐标：当前列的起始点 (是上一个元素计算后的新 current_x)
            
            # 添加命令
            mode_pos = (self.current_x, mode_indentation)
            self.command.add_mode(text=node.mode,position=mode_pos)

            header_width_acc += mode_w
            
            # 更新 X 流控：向左移动
            self.current_x -= mode_w
            header_width_acc += mode_w    
            self.current_display_mode = node.mode  

        # 4. 遍历 Section 内部元素 (elements)
        self.generic_visit(node)
    
    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        """处理谱字单元，计算其绝对位置和内部组件的相对位置。"""
        # --- 1. 检查是否需要换列 (Column Break) ---

        if self._is_score_unit == False:
            self._is_score_unit = True
        if self.scoreunit_counter >= self.layout.UNIT_NUM:
            self.scoreunit_counter = 0
            self._do_column_break()

        unit_x = self.current_x - self.layout.scoreunit_x_offset # 向左平移
        useable_space = unit_x - self.margin["left"]
        if useable_space < self.layout.main_char_space[0]:
            self._do_page_break()
        # --- 2. 计算绝对定位和尺寸 ---
        
        # X 坐标：继承自当前 X (self.current_x)
        unit_x = self.current_x - self.layout.scoreunit_x_offset # 向左平移
        # Y 坐标：继承自当前 Y (self.current_y)
        


        # 尺寸：基于时值或固定单元宽度计算，并更新 self.last_element_height
        unit_height = self.scoreunit_height
        
        # 添加命令
        main_char_pos = (unit_x, self.current_y)
        self.command.add_main_char(text=node.main_score_character,position=main_char_pos)
        
        # 缓存当前只拍子起始位置，用于当时值为整数时执行缩进
        if self.time_counter == 0:
            self.unit_temp_y = self.current_y

        # 计算小谱字+引/火的位置
        small_mod_y = self._layout_small_modifiers(node,unit_x)

        # 计算右边符号位置
        self._layout_right_rhythm_modifier(node, unit_x)

        
        # --- 3. 更新 X/Y 流控 ---
        # 先计算时值累加
        self.time_counter += node.time

        # 从同一起点计算，防止float累计误差
        if self.time_counter == 1:            
            self.current_y = self.unit_temp_y + (unit_height * 0.4)
        elif self.time_counter == 2:            
            self.current_y = self.unit_temp_y + (unit_height * 0.8) + (unit_height * 0.1)
            self._layout_bottom_rhythm_modifier(node, unit_x)
            self.current_y = self.unit_temp_y + unit_height
            # 更新计数器
            self.time_counter = 0
            self.scoreunit_counter += 1  
        else:
            self.current_y = small_mod_y

        # 处理底部符号位置


        #TODO 如果想让只拍子或其他底部符号可以出现在一个只拍子内部，让layout_bottom_rhythm_modifier移到第二步中，返回一个偏移值（0.2unitheight），第三步里，如果存在则加上，不存在则返回0
        return

    def visit_TextNode(self,node: TextNode):
        """处理文本单元，计算其绝对位置"""
        title_unit_h = self.layout.title_space[1]
        text_indentation = self.current_y + (2 * title_unit_h) # 硬编码两格缩进
        if self._is_score_unit == True:
            self.current_x -= (self.layout.main_char_space[0] + self.layout.scoreunit_x_offset)
            self.scoreunit_counter = 0
            self.time_counter = 0
            self._is_score_unit = False
            self.current_y = self.margin["top"]
            text_indentation = self.current_y

        
        # 添加命令
        text_pos = (self.current_x, text_indentation)
        self.command.add_text_block(text=node.text,position=text_pos)

        total_texts = len(node.text)
        total_columns = math.ceil(total_texts / self.max_text_per_column)
        dimensions = (total_columns * self.layout.textunit_space[0], self.text_column)
        self.current_x -= dimensions[0]
        return
    
 

    def _layout_small_modifiers(self, node: ScoreUnitNode,unit_x):
        """计算小字组的相对位置，并注入 AST"""
        
        # 所有小字都紧靠在主音符的右下侧，向下排版，时值符号紧跟小字继续向下排版
        small_mod_x = unit_x
        
        # 初始化 Y 轴起始点：
        small_mod_y = self.current_y + self.layout.main_char_space[1]

        if node.small_modifier is not None:
            for text in node.small_modifier:
                # 添加命令
                small_mod_pos=(small_mod_x, small_mod_y)
                self.command.add_small_modifier(text=text,position=small_mod_pos)

                # 更新流控
                small_mod_y += self.layout.small_char_space[1]

        if node.time_modifier is not None:
            # 添加命令
            for text in node.time_modifier:
                time_mod_pos = (small_mod_x,small_mod_y)
                if text == '/h':
                    self.command.add_small_modifier(text="火",position=time_mod_pos)
                if text == '/y':
                    self.command.add_small_modifier(text="引",position=time_mod_pos)
                if text == '/ls':
                    pos = (small_mod_x,self.current_y)
                    self.command.add_main_char(text="连", position=pos)
                    continue
                if text == '/f':
                    pos = (small_mod_x,self.current_y)
                    self.command.add_main_char(text="反", position=pos)
                    continue

                # 更新流控
                small_mod_y += self.layout.small_char_space[1]
            
        return small_mod_y

    def _layout_bottom_rhythm_modifier(self, node: ScoreUnitNode, unit_x):
        """计算底部符号的相对位置，并注入 AST"""
        if node.bottom_rhythm_modifier == None:
            return
        bottom_mod_x = unit_x - (self.layout.main_char_size / 2)
        bottom_mod_y = self.current_y
        bottom_rhythm_mod_pos = (bottom_mod_x, bottom_mod_y)
        
        # TODO: 改parser，在创建AST时就直接把符号存储标准化,而不是改了指令在这里也处理
        if node.bottom_rhythm_modifier == "/pz":
            self.command.add_circle_marker(position=bottom_rhythm_mod_pos)
        elif node.bottom_rhythm_modifier == "/r":
            self.command.add_line_marker(position=bottom_rhythm_mod_pos)
        return
 
    def _layout_right_rhythm_modifier(self,node: ScoreUnitNode,unit_x):
        """计算右边符号的相对位置，并注入 AST"""
        right_mod_x = unit_x + (0.5 * self.layout.small_char_space[0])
        right_mod_y = self.current_y + (0.5 * self.layout.main_char_size)

        right_rhythm_mod_pos = (right_mod_x,right_mod_y)
        if node.right_rhythm_modifier == "/b":
            self.command.add_bai_marker(position=right_rhythm_mod_pos)
        elif node.right_rhythm_modifier == "/py":
            self.command.add_dot_marker(position=right_rhythm_mod_pos)

        return
    
    def _do_column_break(self):
        self.current_x -= (self.layout.main_char_space[0] + self.layout.scoreunit_x_offset)

        # 从页顶部开始
        self.current_y = self.margin['top']
