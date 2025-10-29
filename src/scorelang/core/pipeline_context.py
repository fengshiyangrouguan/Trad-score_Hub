# src/scorelang/pipeline_context.py

from typing import Dict, Any, List, Optional
from ..ast_score.nodes import ScoreDocumentNode
# 假设这些依赖类已在其他模块定义


# 定义 RenderArtifact 的类型结构
RenderArtifact = Dict[str, Any] 

class PipelineContext:
    """
    编译/渲染管道的共享上下文。
    它负责存储全局配置依赖项 (StyleManager, LayoutMetrics)
    和 Pass 之间的共享输出 (Render List)。
    """
    
    def __init__(
        self, 
        node = None
    ):
        """
        初始化 Context，注入必要的全局配置。
        
        Args:
            style_manager: 负责所有视觉表现属性和符号字符映射。
            layout_metrics: 负责所有几何约束、尺寸常量和乐理意图映射。
        """
        # --- 原始输入文本 ---
        self.raw_score_text: str = ""
        # --- 当前处理的 AST 节点 ---
        self.node: ScoreDocumentNode = node
        # --- 依赖配置 (全局共享，只读) ---
        self.layout_config = None
        
        # --- Pass 之间的共享数据/输出 (可变) ---
        
        # 用于存储 Layout Pass 的主要输出 (Render List)
        # 结构示例: {'pipa': {'pages': [...], 'metadata': {...}}}
        self.render_artifact: Dict[str, RenderArtifact] = {} 
        
        # 用于存储管道中所有 Pass 的通用日志和警告信息
        self.log_messages: List[str] = []

    # --- 辅助方法 (可选，但推荐) ---

    def add_render_artifact(self, data_type: str, artifact_data: RenderArtifact):
        """将 Layout Pass 的最终输出 (Render List) 存储到 Context 中。"""
        self.render_artifact[data_type.lower()] = artifact_data
        
    def log(self, message: str):
        """记录管道运行中的信息或警告。"""
        self.log_messages.append(message)

    def set_raw_text(self, text: str):
        """设置原始输入文本。"""
        self.raw_score_text = text
# ----------------------------------------------------------------------
# 外部使用示例 (在 ScoreService 或主程序中):
# ----------------------------------------------------------------------
"""
# 1. 实例化依赖项
layout_metrics = LayoutMetrics.create_from_config(style_mgr, 'layout.yaml')

# 2. 实例化上下文
context = PipelineContext(
    style_manager=style_mgr,
    layout_metrics=layout_metrics
)

# 3. 运行管道 (VisitorManager.run_pipeline)
# VisitorManager.run_pipeline(ast_root, 'pipa', context)

# 4. 获取输出
# render_list = context.render_artifact.get('pipa')
"""