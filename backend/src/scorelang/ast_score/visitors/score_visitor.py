from typing import List

from ..base_visitor import BaseVisitor
from ..nodes import ScoreDocumentNode,SectionNode,ScoreUnitNode,TextNode
# -------------------------------
# 示例 1：分析 / 调式继承 / 统计 Visitor
# -------------------------------
class ScoreVisitor(BaseVisitor):
    """
    对 AST 执行分析、计算和调式继承。
    """

    def __init__(self):
        # 用于统计
        self.total_score_units = 0
        self.current_mode_stack: List[str] = []

    def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
        # 文档级默认调式
        if node.mode:
            self.current_mode_stack.append(node.mode)
        else:
            self.current_mode_stack.append("C")  # 默认调式
        self.generic_visit(node)
        self.current_mode_stack.pop()

    def visit_SectionNode(self, node: SectionNode):
        # Section 内可能临时转调
        if node.mode:
            self.current_mode_stack.append(node.mode)
        else:
            self.current_mode_stack.append(self.current_mode_stack[-1])
        self.generic_visit(node)
        self.current_mode_stack.pop()

    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        # ScoreUnit 的实际调式继承自当前栈顶
        node.effective_mode = node.mode or self.current_mode_stack[-1]
        self.total_score_units += 1

    def visit_TextNode(self, node: TextNode):
        pass  # 默认不做操作


# -------------------------------
# 示例 2：文本渲染 Visitor
# -------------------------------
class TextRenderVisitor(BaseVisitor):
    """
    将 AST 渲染为文本树（可用于 debug / CLI 输出）。
    """

    def __init__(self):
        self.level = 0
        self.lines: List[str] = []

    def visit_ScoreDocumentNode(self, node: ScoreDocumentNode):
        header = f"ScoreDocument: {node.title or 'Untitled'} (mode={node.mode})"
        self.lines.append(header)
        self.level += 1
        self.generic_visit(node)
        self.level -= 1

    def visit_SectionNode(self, node: SectionNode):
        line = "  " * self.level + f"Section: {node.title or 'Unnamed'} (mode={node.mode})"
        self.lines.append(line)
        self.level += 1
        self.generic_visit(node)
        self.level -= 1

    def visit_ScoreUnitNode(self, node: ScoreUnitNode):
        modifiers = ",".join(node.modifiers) if hasattr(node, "modifiers") else ""
        line = "  " * self.level + f"ScoreUnit: {node.main_score_character} [{modifiers}]"
        self.lines.append(line)

    def visit_TextNode(self, node: TextNode):
        line = "  " * self.level + f"TextNode: {node.type} -> {node.text}"
        self.lines.append(line)

    def get_text(self) -> str:
        return "\n".join(self.lines)


# -------------------------------
# 节点 accept 方法示例
# -------------------------------
# 假设你的 Node 类中有 accept 方法：
# def accept(self, visitor: Visitor):
#     method_name = f"visit_{self.__class__.__name__}"
#     visit = getattr(visitor, method_name, visitor.generic_visit)
#     visit(self)
