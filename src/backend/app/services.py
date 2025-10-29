# app/services.py

from typing import Any, Dict, Optional
from pathlib import Path
from src.scorelang.core.parser_factory import ParserFactory
from src.scorelang.core.visitor_manager import VisitorManager
from src.scorelang.ast_score.nodes import ScoreDocumentNode
from src.scorelang.core.pipeline_context import PipelineContext


ROOT_PATH = str(Path(__file__).parent.parent.parent.parent / "new_system_test.png")

class ScoreService:
    """
    ScoreService 负责接收输入、驱动编译管道，并返回最终结果。
    它负责编排 Parser, VisitorManager 和 RendererFactory (隐式)。
    """
    
    def __init__(self):
        # 初始化时加载配置，以便后续使用
        self.visitor_manager = VisitorManager
        self.context = PipelineContext()

    def process_score(self, score_context: PipelineContext, score_type: str) -> ScoreDocumentNode:
        """
        核心管道方法：解析文本，运行所有语义 Visitor，返回处理后的 AST。
        """
        self.context = score_context
        score_type = score_type.lower()
        
        # --- 1. 解析阶段 ---
        try:
            parser = ParserFactory.get_parser(score_type)
            # 处理元输入文本
            score_text = self.context.raw_score_text
            ast_root: ScoreDocumentNode = parser.parse(score_text)
        except Exception as e:
            raise RuntimeError(f"Parsing failed for {score_type} score: {e}")

        # --- 2. 语义分析与转换阶段 (Visitor Passes) ---
        
        # 委托给 VisitorManager 运行所有配置好的 Pass
        print("开始运行visit")

        self.context.node = ast_root
        VisitorManager.run_pipeline(
            self.context, 
            score_type, 
        )

        # 返回上下文
        return self.context

    def render_score(self, context, score_type: str, format: str, save_dir: str = ROOT_PATH) -> Any:
        """
        渲染方法：查找正确的 Renderer，生成最终格式的输出。
        """
        score_type = score_type.lower()
        format = format.lower()
        
        # renderer_path = self.pipeline_config.get(score_type, {}).get('renderers', {}).get(format)

        # if not renderer_path:
        #     raise ValueError(f"Unsupported rendering format '{format}' for score type '{score_type}'.")

        # --- 动态加载和运行 Renderer ---
        try:
            # 实际项目中，这里会使用反射 (importlib)
            # 占位：假设我们只关心 TextRenderer
            if format == 'image':
                from src.scorelang.renderers.pipa_image_renderer import PipaImageRenderer
                RendererClass = PipaImageRenderer
            else:
                 # 模拟动态加载失败
                # raise NotImplementedError(f"Renderer for {renderer_path} not implemented.")
                raise NotImplementedError(f"Renderer not implemented.")
            
            renderer = RendererClass(context)
            renderer.render(save_dir)
            return
            
        except (ImportError, AttributeError, NotImplementedError) as e:
            #raise RuntimeError(f"Failed to load or run renderer '{renderer_path}': {e}")
            raise RuntimeError(f"Failed to load or run renderer: {e}")