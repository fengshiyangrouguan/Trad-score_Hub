# ast/visitor.py
from abc import ABC,abstractmethod

from ..ast_score.nodes import Node

class BaseVisitor(ABC):
    """
    抽象 Visitor 基类。
    提供默认递归遍历逻辑（generic_visit）。
    """
    @abstractmethod
    def __init__(self):
        """强制子类初始化，用于设置 Pass 的状态和上下文。"""
        pass

    def visit(self, node: Node):
        """
        外部入口点：启动双重分派。
        将控制权交给 Node 上的 accept 方法。
        """
        # node.accept(self) 将启动查找 visit_NodeName 或 fallback 到 generic_visit
        return node.accept(self)
    

    def generic_visit(self, node: Node):
        """
        默认递归遍历方法：在没有特定 visit_NodeName 方法时被调用。
        它负责确保遍历继续深入到所有子节点。
        """
        # 使用 vars(node).values() 或 node.__dict__.values() 来遍历所有字段的值
        for value in vars(node).values():
            if isinstance(value, Node):
                # 如果是单个子节点，继续调用 accept
                value.accept(self)
            elif isinstance(value, list):
                # 如果是节点列表，遍历并对每个节点调用 accept
                for item in value:
                    if isinstance(item, Node):
                        item.accept(self)
                        
        return None 