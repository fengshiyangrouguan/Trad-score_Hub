from typing import Literal, Optional, Tuple, Dict, Any, Union


# 文本类渲染类型
TextType = Literal[
    "DOCUMENT_TITLE",
    "SECTION_TITLE",
    "MODE",
    "MAIN_CHAR",
    "SMALL_MODIFIER",
    "TEXT_BLOCK",
]

# 标记类渲染类型
MarkerType = Literal[
    "DOT_MARKER",
    "CIRCLE_MARKER",
    "LINE_MARKER",
    "CHECK_MARKER",
]

# 符号字符映射 (定制字库)
Text_Map: Dict[MarkerType, str] = {
    "DOT_MARKER": "乐", 
    "CIRCLE_MARKER": "只", 
    "LINE_MARKER": "段", 
    "CHECK_MARKER": "拨",
    "BAI_MARKER": "百"
}

# 所有渲染类型（联合类型）
RenderType = Union[TextType, MarkerType]

# 避免循环引用，如果需要 PipaLayoutPass 实例的类型提示
# if TYPE_CHECKING:
#     from visitors.pipa_layout_pass import PipaLayoutPass 
#     LayoutPassInstance = PipaLayoutPass
# else:
#     LayoutPassInstance = Any


class RenderListBuilder:
    """
    负责封装所有 Render Command 生成逻辑的构建器类。
    它持有一个对 Layout Pass 实例的引用，以写入指令。
    """
    def __init__(self, render_list):
        """初始化时，保存对 Layout Pass 的引用，并直接访问指令列表。"""
        # 保存对指令列表的引用
        self._target_list = render_list

    # --- A. 底层私有封装方法 (不包含 dimension) ---

    def _add_raw_command(
        self,
        type: RenderType,
        position: Tuple[float, float],
        text: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """将数据打包成 Render Command 字典并加入到目标列表。"""
        command = {
            "type": type,
            "position": list(position),
            "text": text,
            # 根据您的要求，不包含 dimension 字段
            "metadata": metadata if metadata else {}
        }
        
        self._target_list.append(command) # 直接写入目标列表


    # --- B. 对外公共语义API ---
    
    # 拆分 add_text() 为具体的语义函数，但仍接收 type 作为参数
    
    def add_document_title(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加文档标题命令 (type="DOCUMENT_TITLE")。"""
        self._add_raw_command(
            type="DOCUMENT_TITLE",
            position=position,
            text=text,
            metadata=metadata
        )

    def add_section_title(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加章节标题命令 (type="SECTION_TITLE")。"""
        self._add_raw_command(
            type="SECTION_TITLE",
            position=position,
            text=text,
            metadata=metadata
        )

    def add_mode(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加文档标题命令 (type="DOCUMENT_TITLE")。"""
        self._add_raw_command(
            type="MODE",
            position=position,
            text=text,
            metadata=metadata
        )

    def add_main_char(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加主谱字命令 (type="MAIN_CHAR")。"""
        self._add_raw_command(
            type="MAIN_CHAR",
            position=position,
            text=text,
            metadata=metadata
        )
        
    def add_text_block(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加多行文本块命令 (type="TEXT_BLOCK")。"""
        # metadata 通常需要包含 chars_per_column 等分列规则
        self._add_raw_command(
            type="TEXT_BLOCK",
            position=position,
            text=text,
            metadata=metadata
        )
        
    def add_small_modifier(
        self, 
        text: str,
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加小修饰字命令 (type="SMALL_MODIFIER")。"""
        self._add_raw_command(
            type="SMALL_MODIFIER",
            position=position,
            text=text,
            metadata=metadata
        )


    # Marker 标记函数使用硬编码 Type，并查找 Text_Map
    def add_dot_marker(
        self, 
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加实心圆点标记 (type="DOT_MARKER")。"""
        self._add_raw_command(
            type="DOT_MARKER",
            position=position,
            text=Text_Map["DOT_MARKER"],
            metadata=metadata
        )

    def add_circle_marker(
        self, 
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加空心圆点标记 (type="CIRCLE_MARKER")。"""
        self._add_raw_command(
            type="CIRCLE_MARKER",
            position=position,
            text=Text_Map["CIRCLE_MARKER"],
            metadata=metadata
        )
        
    def add_line_marker(
        self, 
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加直线标记 (type="LINE_MARKER")。"""
        self._add_raw_command(
            type="LINE_MARKER",
            position=position,
            text=Text_Map["LINE_MARKER"],
            metadata=metadata
        )

    def add_check_marker(
        self, 
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加勾号标记 (type="CHECK_MARKER")。"""
        self._add_raw_command(
            type="CHECK_MARKER",
            position=position,
            text=Text_Map["CHECK_MARKER"],
            metadata=metadata
        )

    def add_bai_marker(
        self, 
        position: Tuple[float, float], 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加百标记 (type="BAI_MARKER")。"""
        self._add_raw_command(
            type="BAI_MARKER",
            position=position,
            text=Text_Map["BAI_MARKER"],
            metadata=metadata
        )
        
    # ... 您可以仿照上面的模式继续添加 add_circle_marker, add_check_marker 等