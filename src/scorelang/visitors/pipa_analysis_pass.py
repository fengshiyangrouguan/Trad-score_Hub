import toml
from pathlib import Path
from typing import Dict

from .base_visitor import BaseVisitor
from ..ast_score.nodes import ScoreDocumentNode,SectionNode,ScoreUnitNode,TextNode



class PipaTheoryAnalysisPass(BaseVisitor):
    """
    语义分析 Pass：负责推导和注入乐谱中省略的时值标记。
    核心逻辑：基于乐拍计数（beats）和规则（如四分音符推导）。
    """
    
    def __init__(self):
        super().__init__()
        current_file = Path(__file__).resolve()
        config_path = current_file.parent.parent / "config" / "pipa_map.toml"

        # 2. 从配置文件加载数据
        try:
            self.config = toml.load(config_path)    
        except FileNotFoundError:
            raise FileNotFoundError(f"Parser config file not found at: {config_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load/parse TOML config: {e}")
        
        self.duration_map: Dict[str, float] = self.config["duration_modifier_map"]
        print("初始化无误")

    def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
        """
        从根节点开始遍历所有 Section。
        """
        # 依赖 generic_visit 自动遍历到 Sections
        print("开始遍历根节点并处理模式继承")

        # 1. 强制设置 Document 的默认模式
        if not node.mode:
            node.mode = '黄钟调' 
            
        current_inherited_mode = node.mode
        # 2. 遍历所有直接元素，为未指定 mode 的 SectionNode 继承模式
        for element in node.elements:
            if isinstance(element, SectionNode):
                if not element.mode: 
                    # 设置为上一次设置的调式类型
                    element.mode = current_inherited_mode
                # 更新调式定义
                current_inherited_mode = element.mode
                
        # 3. 继续遍历子节点以进行后续的语义分析
        self.generic_visit(node)
        
    def visit_SectionNode(self, node: SectionNode):
        """
        在 Section 级别进行时值推导的上下文初始化。
        """
        # print(f"-> PipaTimingPass: Processing Section {node.section_id}")
        self.generic_visit(node)

    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        """
        在 ScoreUnit 级别进行实际的时值注入。
        """
        if node.time_modifier != None:
            node.time *= self.duration_map[node.time_modifier]
        if node.time_modifier == "/hh":
            node.time_modifier = None

        # print(f"   [Unit] Inferred time at beat {self.current_beat_index}: {node.main_character}")
        return
    





# class PipaTheoryAnalysisPass(BaseVisitor):
#     """
#     语义分析 Pass：负责推导和注入乐谱中省略的时值标记。
#     核心逻辑：基于乐拍计数（beats）和规则（如四分音符推导）。
#     """
    
#     def __init__(self):
#         # # 初始化 Pass 的状态和上下文
#         # self.current_beat_index: int = 0      # 当前 Section 内已消耗的拍位
#         # self.beats_per_measure: int = 4       # 默认每小节拍数（例如 4/4 拍）
#         # self.rhythm_units_per_beat: int = 1   # 每个乐拍内默认推导的音符数量

#         current_file = Path(__file__).resolve()
#         config_path = current_file.parent.parent / "config" / "pipa_map.toml"

#         # 2. 从配置文件加载数据
#         try:
#             self.config = toml.load(config_path)    
#         except FileNotFoundError:
#             raise FileNotFoundError(f"Parser config file not found at: {config_path}")
#         except Exception as e:
#             raise RuntimeError(f"Failed to load/parse TOML config: {e}")
        
#         self.duration_map: Dict[str, float] = self.config["duration_modifier_map"]

#     def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
#         """
#         从根节点开始遍历所有 Section。
#         """
#         # 依赖 generic_visit 自动遍历到 Sections
#         self.generic_visit(node)
        
#     def visit_SectionNode(self, node: SectionNode):
#         """
#         在 Section 级别进行时值推导的上下文初始化。
#         """
#         print(f"-> PipaTimingPass: Processing Section {node.section_id}")
        
#         # # 1. 初始化 Section 状态
#         # self.current_beat_index = 0
#         # # self.beats_per_measure = node.time_signature.beats # 实际代码中应从节点读取
        
#         # 2. 遍历子节点（ScoreUnitNodes）
#         self.generic_visit(node)
        
#         # # 3. Section 结束，检查乐拍是否匹配
#         # if self.current_beat_index % self.beats_per_measure != 0:
#         #     print(f"Warning: Section {node.section_id} has an incomplete measure.")

#     def visit_ScoreUnitNode(self, node: ScoreUnitNode):
#         """
#         在 ScoreUnit 级别进行实际的时值注入。
#         """
#         # 只有当节点没有明确的时值标记（如 /h, /y, /q 等）时才进行推导
#         if not node.time_rhythm_markers:
            
#             # --- 核心时值推导逻辑骨架 ---
            
#             # 1. 默认推导为四分音符（假设每拍一个音符）
#             # TODO: 这里需要更复杂的逻辑来处理八分音符等情况
            
#             # 2. 注入时值标记（例如 '/q' 代表四分音符）
#             node.time *= self.duration_map[node.time_modifier]
#             if node.time_modifier == "/hh":
#                 node.time_modifier = ""

            
#             # # 3. 更新乐拍计数
#             # self.current_beat_index += 1 # 假设推导出了一个一拍的音符
            
#             print(f"   [Unit] Inferred time at beat {self.current_beat_index}: {node.main_character}")
            
#         else:
#             # 如果已有标记，则直接消耗乐拍，但不进行推导
#             # 假设标记的时值已通过 Lexer 转换成标准化的 'duration_value'
#             # self.current_beat_index += node.duration_value
#             pass
            
#         # 注意：ScoreUnitNode 是叶子节点，不需要调用 generic_visit。
#         return