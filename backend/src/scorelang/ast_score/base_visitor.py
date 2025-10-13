# ast/visitor.py
from abc import ABC

from .nodes import Node

class BaseVisitor(ABC):
    """
    抽象 Visitor 基类。
    提供默认递归遍历逻辑（generic_visit）。
    """

    def generic_visit(self, node: Node):
        """
        默认遍历逻辑：
        如果节点有 `elements` 属性，则递归访问子节点。
        """
        if hasattr(node, "elements") and isinstance(node.elements, list):
            for child in node.elements:
                child.accept(self)
