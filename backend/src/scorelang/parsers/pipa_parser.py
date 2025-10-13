from pathlib import Path

from .base_parser import BaseParser
from ..lexer.lexer import Lexer
from ..ast_score.nodes import ScoreDocumentNode, SectionNode, ScoreUnitNode, TextNode


class PipaParser(BaseParser):
    
    def __init__(self):
        current_file = Path(__file__).resolve()
        config_path = current_file.parent.parent / "config" / "pipa_map.toml"
        self.lexer = Lexer(config_path)
        self.meta_field_map = {
            "来源": "source",
            "录入": "transcriber",
            "审校": "proofreader",
            "日期": "date"
        }

    def parse(self, text: str) -> ScoreDocumentNode:
        tokens = self.lexer.tokenize(text)
        score_document = ScoreDocumentNode()
        current_section = None
        current_unit = None

        for token in tokens:
            ttype = token["type"]
            val = token["value"]

            if ttype == "SCORE_DOCUMENT":
                score_document.title = val

            elif ttype == "MODE":
                if current_section:
                    current_section.mode = val
                else:
                    score_document.mode = val

            elif ttype == "DOCUMENT_META":
                key = token["value"]      # 来源 / 审校 / 录入
                value = token.get("extra")
                mapped = self.meta_field_map.get(key)
                if mapped:
                    setattr(score_document, mapped, value)

            elif ttype == "SECTION":
                current_section = SectionNode(title=val, mode=score_document.mode)
                score_document.elements.append(current_section)

            elif ttype == "UNIT_START":
                current_unit = ScoreUnitNode()
                if current_section:
                    current_section.elements.append(current_unit)
                else:
                    score_document.elements.append(current_unit)

            elif ttype == "UNIT_END":
                current_unit = None

            elif ttype == "MAIN_CHAR":
                if current_unit:
                    current_unit.main_score_character = val

            elif ttype in ["TIME_MOD", "RHYTHM_MOD", "SUB_CHAR"]:
                if current_unit:
                    current_unit.modifiers.append(val)

            elif ttype in ["COMMENT", "UNKNOWN"]:
                node = TextNode(type="COMMENT", text=val)
                if current_section:
                    current_section.elements.append(node)
                else:
                    score_document.elements.append(node)

        return score_document
