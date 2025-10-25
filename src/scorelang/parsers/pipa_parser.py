from pathlib import Path
from typing import Dict, List, Callable,Union
import toml

# 假设的导入路径
from .base_parser import BaseParser 
from ..lexer.lexer import Lexer
from ..ast_score.nodes import (
    ScoreDocumentNode, SectionNode, TextNode, 
    ScoreUnitNode
)


class PipaParser(BaseParser):
    
    def __init__(self):
        # 1. 初始化 Lexer
        current_file = Path(__file__).resolve()
        config_path = current_file.parent.parent / "config" / "pipa_map.toml"
        self.lexer = Lexer(config_path)

        # 2. 从配置文件加载数据
        try:
            self.config = toml.load(config_path)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Parser config file not found at: {config_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load/parse TOML config: {e}")
        
        # 3. 从配置加载数据
        self.meta_field_map: Dict[str, str] = self.config["document_meta_map"]

        # 4. 初始化状态
        self.score_document: ScoreDocumentNode = None
        self.current_section: SectionNode = None
        self.current_unit: ScoreUnitNode = None
        
        # 5. 动态构建方法分发映射
        self._dispatch_map: Dict[str, Callable] = self._build_dispatch_map(
            self.config["parser_dispatch"]
        )

    def _build_dispatch_map(self, dispatch_config: Dict[str, str]) -> Dict[str, Callable]:
        """动态地将配置中的字符串方法名映射到类实例的方法。"""
        dispatch_map = {}
        for semantic_key, method_name in dispatch_config.items():
            handler = getattr(self, method_name, None)
            
            if handler is None or not callable(handler):
                raise AttributeError(f"PipaParser is missing required handler: {method_name}")
            
            dispatch_map[semantic_key] = handler
        return dispatch_map

    # --- 主要解析入口 ---

    def parse(self, text: str) -> ScoreDocumentNode:
        tokens = self.lexer.tokenize(text)
        
        # 重置状态
        self.score_document = ScoreDocumentNode()
        self.current_section = None
        self.current_unit = None
        
        for token in tokens:
            semantic = token.get("semantic")
            
            handler = self._dispatch_map.get(semantic)
            
            if handler:
                handler(token)
            elif token["type"] not in ["SKIP_SPACE"]:
                # 忽略空格，对所有未处理的语义或Token发出警告
                print(f"Warning: Token type '{token['type']}' (semantic: {semantic}) was skipped.")
        
        return self.score_document





    # --- 状态管理/辅助方法 ---
    
    def _get_current_container(self) -> Union[SectionNode, ScoreDocumentNode]:
        """返回当前应该添加元素的容器（Section 或 Document 根）"""
        # 注意：这里需要确保返回的是可附加elements的容器
        return self.current_section or self.score_document

    # --- 语义处理方法 ---

    def _handle_document_meta(self, token):
        """处理 #SCORE_DOCUMENT, @MODE, %DOCUMENT_META"""
        ttype = token["type"]
        val = token["value"]
        
        if ttype == "SCORE_DOCUMENT":
            self.score_document.title = val
                
        elif ttype == "DOCUMENT_META":
            # 字段名是 token["value"]，字段值是 token["extra"]（假设 Lexer 约定）
            key = token["value"] 
            value = token.get("extra") 
            mapped_attr = self.meta_field_map.get(key)
            if mapped_attr:
                setattr(self.score_document, mapped_attr, value)

    def _handle_mode(self,token):
        target = self.current_section if self.current_section else self.score_document
        target.mode = token["value"]

    def _handle_section(self, token):
        """处理 SECTION (##) 启动新的乐段"""
        val = token["value"]
             
        self.current_section = SectionNode(title=val, mode=None)
        self.score_document.elements.append(self.current_section)


    def _handle_control(self, token):
        """处理 { 和 } UNIT_START 和 UNIT_END"""
        ttype = token["type"]
        
        if ttype == "UNIT_START":
            # 检查：在创建unit前当前没有活动的 SectionNode (即 current_section 为 None)
            if self.current_section is None:

                # 创建虚拟 SectionNode
                virtual_section = SectionNode(
                    title = None,  # 文本设置为 "None"
                    mode = None, # 继承根节点的 mode
                    mode_display_flag = False   # 设置 display_flag 为 False
                )
                # 将虚拟 Section 添加到 Document
                self.score_document.elements.append(virtual_section)
                # 将其设置为当前的 Section
                self.current_section = virtual_section
            # 必须创建 PipaScoreUnitNode 实例
            self.current_unit = ScoreUnitNode(main_score_character=None) 
            self._get_current_container().elements.append(self.current_unit)

        elif ttype == "UNIT_END":
            # 可以在这里做最终的校验或清理工作
            self.current_unit = None

    
    def _handle_main_char(self, token):
        """处理 MAIN_CHAR 主音符"""
        if self.current_unit:
            self.current_unit.main_score_character = token["value"]
        # else: 生产环境中应抛出语法错误


    def _handle_time_modifier(self, token):
        """处理 TIME_MOD (/y, /h, /hh) 专用于 time_multiplier 字段"""
        if self.current_unit:
            self.current_unit.time_modifier = token["value"]


    def _handle_small_modifier(self, token):
        """处理 SUB_CHAR (附加的小字号音符)"""
        if self.current_unit:
            mod_text = token["value"].strip("（）()") 
            self.current_unit.small_modifier.extend(list(mod_text))


    def _handle_right_rhythm_modifier(self, token):
        """处理 RHYTHM_MOD (节奏技巧) 和琵琶谱特有的汉字节奏"""
        if self.current_unit:
            self.current_unit.right_rhythm_modifier = token["value"]
    
    def _handle_bottom_rhythm_modifier(self, token):
        """处理 RHYTHM_MOD (节奏技巧) 和琵琶谱特有的汉字节奏"""
        if self.current_unit:
            self.current_unit.bottom_rhythm_modifier = token["value"]


    def _handle_text_unit(self, token):
        """处理 COMMENT (=) 等文本单元"""
        node = TextNode(text=token["value"],type="COMMENT")
        self._get_current_container().elements.append(node)