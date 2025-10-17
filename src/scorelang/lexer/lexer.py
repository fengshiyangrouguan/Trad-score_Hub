import re
import toml
from typing import List, Dict, Any

#TODO: 优化一下扫描速度

class Lexer:
    """
    记谱语言词法分析器（支持状态机 + 整行扫描）
    - 支持 { ... } scoreunit 块
    - 支持 next_state / pop_state
    - 每行可多 token
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.token_rules = self._load_rules()
        self.state_stack = ["normal"]

    # ---------------------------------------------
    # 载入 TOML 配置
    # ---------------------------------------------
    def _load_rules(self) -> List[Dict[str, Any]]:
        data = toml.load(self.config_path)
        rules = []
        for token in data.get("TOKENS", []):
            pattern = token["pattern"]
            flags = 0
            if "IGNORECASE" in token.get("flags", "").upper():
                flags |= re.IGNORECASE
            compiled = re.compile(pattern, flags)
            rules.append({
                "name": token["name"],
                "compiled": compiled,
                "semantic": token.get("semantic"),
                "group1": token.get("group1", False),
                "group2": token.get("group2", False),
                "state": token.get("state", "any"),
                "next_state": token.get("next_state"),
                "pop_state": token.get("pop_state", False),
            })
        return rules

    # ---------------------------------------------
    # 主体词法扫描逻辑
    # ---------------------------------------------
    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        tokens = []
        self.state_stack = ["normal"]
        lines = text.splitlines()

        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            pos = 0
            while pos < len(line):
                remaining = line[pos:]
                current_state = self.state_stack[-1]
                matched = False

                # 遍历全部规则
                for rule in self.token_rules:
                    if rule["state"] not in ("any", current_state):
                        continue

                    m = rule["compiled"].match(remaining)
                    if not m:
                        continue

                    # 构造 token
                    token_data = {
                        "type": rule["name"],
                        "semantic": rule.get("semantic"),
                        "value": m.group(1) if rule.get("group1") else m.group(0),
                        "lineno": line_no,
                    }
                    if rule.get("group2") and m.lastindex and m.lastindex >= 2:
                        token_data["extra"] = m.group(2)

                    tokens.append(token_data)

                    # --- 状态控制 ---
                    if rule.get("next_state"):
                        self.state_stack.append(rule["next_state"])
                    elif rule.get("pop_state"):
                        if len(self.state_stack) > 1:
                            self.state_stack.pop()

                    # ✅ 核心变化：
                    # 在 scoreunit 状态下，继续扫描这一行（不 break）
                    pos += m.end()
                    matched = True

                    if current_state != "scoreunit":
                        # 普通状态匹配一个 token 就跳出规则循环
                        break
                    # 否则继续扫描同一行下一个 token（不 break）

                if not matched:
                    # 未匹配任何规则
                    pos += 1  # 跳过一个字符，防止死循环

        return tokens
