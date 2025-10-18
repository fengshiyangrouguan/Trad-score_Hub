import importlib
from typing import Dict, Any

from src.scorelang.ast_score.nodes import ScoreDocumentNode
from src.scorelang.visitors.base_visitor import BaseVisitor # 假设你已定义这个基类


# TODO:# 现硬编码,可能在 __init__ 或配置中心加载它
PIPELINE_CONFIG: Dict[str, Any] = {
    "pipa": {
        "visitors": [
            "src.scorelang.visitors.pipa_analysis_pass.PipaTheoryAnalysisPass",
            "src.scorelang.visitors.pipa_layout_pass.PipaLayoutPass", # 占位
        ],
        "renderers": {
            #"svg": "scorelang.renderers.pipa_svg_renderer.PipaSVGRenderer",
            "text": "src.scorelang.renderers.pipa_text_renderer.PipaTextRenderer",
        }
    }
}

class VisitorManager:
    """
    VisitorManager 负责根据配置动态加载 Visitor 类，
    并按正确的顺序对 AST 执行转换 Pass。
    
    这个管理器将整个编译管道的编排逻辑从 ScoreService 中分离出来。
    """
    
    @staticmethod
    def run_pipeline(ast_root: ScoreDocumentNode, score_type: str) -> ScoreDocumentNode:
        """
        加载并按顺序运行 Visitor 链。
        
        Args:
            ast_root: 要修改的 AST 根节点。
            score_type: 乐谱类型（例如 'pipa'）。
            config: 包含该 score_type 的 'visitors' 路径列表的配置字典。
            
        Returns:
            经过所有 Pass 转换后的 AST 根节点。
        """
        
        score_type = score_type.lower()
        # 从配置中获取 Visitor 类的完全限定路径列表
        score_config = PIPELINE_CONFIG.get(score_type)
        visitor_paths: list = score_config.get('visitors', [])
        
        if not visitor_paths:
            print(f"Warning: No Visitors defined for score type '{score_type}'. Skipping pipeline run.")
            return ast_root

        print(f"--- Running Visitor Pipeline for {score_type} ({len(visitor_paths)} Passes) ---")

        for visitor_path in visitor_paths:
            try:
                # 1. 解析路径：将 'module.submodule.ClassName' 拆分为路径和类名
                module_path, class_name = visitor_path.rsplit('.', 1)
                
                # 2. 动态导入模块
                module = importlib.import_module(module_path)
                
                # 3. 获取 Visitor 类对象
                VisitorClass = getattr(module, class_name)

                # TODO这里将配置字典作为参数传递给 Visitor 的 __init__ 方法
                # 5. 实例化并运行 Visitor Pass
                visitor_instance: BaseVisitor = VisitorClass()
                print(f"   -> Executing Pass: {class_name}...")
                
                # Visitor Pass 在原地 (in-place) 修改 ast_root
                visitor_instance.visit(ast_root)
                
            except Exception as e:
                # 捕获任何加载或执行错误，并抛出清晰的运行时错误
                raise RuntimeError(f"Pipeline failed at Visitor Pass '{visitor_path}'. Error: {e}")

        print("--- Visitor Pipeline Completed ---")
        return ast_root