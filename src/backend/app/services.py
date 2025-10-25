# app/services.py

from typing import Any, Dict, Optional
from pathlib import Path
from src.scorelang.parser_factory import ParserFactory
from src.scorelang.visitor_manager import VisitorManager
from src.scorelang.ast_score.nodes import ScoreDocumentNode

ROOT_PATH = str(Path(__file__).parent.parent.parent.parent / "new_system_test.png")

class ScoreService:
    """
    ScoreService 负责接收输入、驱动编译管道，并返回最终结果。
    它负责编排 Parser, VisitorManager 和 RendererFactory (隐式)。
    """
    
    def __init__(self):
        # 初始化时加载配置，以便后续使用
        self.visitor_manager = VisitorManager

    def process_score(self, score_text: str, score_type: str) -> ScoreDocumentNode:
        """
        核心管道方法：解析文本，运行所有语义 Visitor，返回处理后的 AST。
        """
        score_type = score_type.lower()
        
        # --- 1. 解析阶段 ---
        try:
            parser = ParserFactory.get_parser(score_type)
            # 处理元输入文本
            ast_root: ScoreDocumentNode = parser.parse(score_text)
        except Exception as e:
            raise RuntimeError(f"Parsing failed for {score_type} score: {e}")

        # --- 2. 语义分析与转换阶段 (Visitor Passes) ---
        
        # 委托给 VisitorManager 运行所有配置好的 Pass
        print("开始运行visit")
        VisitorManager.run_pipeline(
            ast_root, 
            score_type, 
        )

        # 返回语义完整的 AST 根节点
        return ast_root

    def render_score(self, ast_root: ScoreDocumentNode, score_type: str, format: str, save_dir: str = ROOT_PATH) -> Any:
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
            if format == 'pillow':
                from src.scorelang.renderers.pipa_pillow_renderer import PipaPillowRenderer
                RendererClass = PipaPillowRenderer
            else:
                 # 模拟动态加载失败
                # raise NotImplementedError(f"Renderer for {renderer_path} not implemented.")
                raise NotImplementedError(f"Renderer not implemented.")
            
            renderer = RendererClass()
            renderer.render(ast_root,save_dir)
            return
            
        except (ImportError, AttributeError, NotImplementedError) as e:
            #raise RuntimeError(f"Failed to load or run renderer '{renderer_path}': {e}")
            raise RuntimeError(f"Failed to load or run renderer: {e}")