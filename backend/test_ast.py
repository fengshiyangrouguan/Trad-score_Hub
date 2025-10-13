# test.py
import json
from src.scorelang.parsers.pipa_parser import PipaParser
from src.scorelang.ast_score.nodes import ScoreDocumentNode

def main():
    sample_score_text = (
"""
# 凉州
@ 沙陀调
% 来源：三五要录
% 录入：冯氏羊肉馆
% 审校：冯氏羊肉馆
% 日期：2025.10.12
= 简单测试一下注释，冯氏羊肉馆冯氏羊肉馆
## 入破第一
{二}
{也/pz}
{七}
{言（七言）/pz}
{一/y/b}
{之}
{四/pz}
{之}
{合（八）/h}
{之/h/pz}
{七（三七）}
{之/h}
{四/h/pz}
{言（七言）/b}
{言/h}
{言（七）/h/pz}
{言(七言)}
{八/pz}
{五}
{八/pz}
{二}
{也/pz}
{言（七）/b}
{七/h}
{七（三）/h/pz}
{七（三七）/y/pz}
{之}
{四/h}
{七（三）/pz}
{二}
{也/h}
{七（三）/pz}
{二/b}
{也/pz}
{也/y/r}
"""
    )

    # 初始化解析器
    parser = PipaParser()

    # 解析成 AST
    score_document: ScoreDocumentNode = parser.parse(sample_score_text)

    # 3️⃣ 输出到控制台
    print("=== AST ===")
    print(score_document)

    # 4️⃣ 保存为 JSON
    json_data = json.dumps(score_document.to_dict(), ensure_ascii=False, indent=2)

    with open("score_document.json", "w", encoding="utf-8") as f:
        f.write(json_data)

    print("=== 已保存 score_document.json ===")

if __name__ == "__main__":
    main()
