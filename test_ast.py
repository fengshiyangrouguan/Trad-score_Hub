# test.py
import json
from pathlib import Path
from src.backend.app.services import ScoreService
from src.scorelang.ast_score.nodes import ScoreDocumentNode


def main():
    sample_score_text = (
"""
# 最凉州
@ 沙陀调
% 来源：三五要录
% 录入：冯氏羊肉馆
% 审校：冯氏羊肉馆
% 日期：2025.10.12
= 凉或作梁 拍子廿 可弹四反 合拍子八十
= 终帖加拍子 南宫横笛谱云打三度拍子
= 中曲 古乐 南宫谱同    龙吟抄云内宴？
= 音声 用之
## 第一段
@ 沙陀调
{二}
{也/pz}
{七}
{言（七言）/pz}
{一/y/b/pz}
{之}
{四/pz}
{之}
{合（八）/h}
{之/hh/pz}
{七（三七）}
{之/hh}
{四/hh/pz}
{言（七言）/b}
{言/h}
{言（七）/hh/pz}
{言(七言)}
{八/pz}
{五}
{八/pz}
{二}
{也/pz}
{言（七）/b}
{七/h}
{七（三）/hh/pz}
{七（三七）/y/pz}
{之}
{四/h}
{七（三）/hh/pz}
{二}
{也/h}
{七（三）/hh/pz}
{二/b}
{也/pz}
{也/y/r}

## 第二段
@ 盘涉调
{二}
{也/pz}
{七}
{言（七言）/pz}
{一/b/y/pz}
{之}
{四/pz}
{之}
{合（八）/h}
{之/hh/pz}
{七（三七）}
{之/hh}
{四/hh/pz}
{言（七言）/b}
{言/h}
{言（七）/hh/pz}
{言（七言）}
{八/pz}
{言（七言）}
{五/hh}
{八/hh/pz}
{八/y/pz}
{言（七言）/b}
{之/hh}
{四/hh/pz}
{合（八）}
{一/hh}
{之/hh/pz}
{之/y/pz}
{八}
{合（八合）/pz}
{一/b}
{之/pz}
{之/y/pz}
{之}
{四/r}
## 第三段


"""
    )
    sample_score_text_2 = (
"""
# 字体测试范例
@ 沙陀调
% 来源：三五要录
% 录入：冯氏羊肉馆
% 审校：冯氏羊肉馆
% 日期：2025.10.12
= 用于测试字体
= 这一行用于测试文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行文本换行换行
## 主谱字展示
{一}
{二}
{三}
{四}
{五}
{六/pz}
{七}
{八/pz}
{九}
{十/pz}
{匕}
{卜/pz}
{敷}
{乙/pz}
{言}
{合/pz}
{斗}
{乞/pz}
{之}
{也/pz}

## 小谱字展示
{一/h}
{二/hh}
{三/pz}
{四/y/pz}
{五/b}
{六（五六）/h/py}
{七/hh/pz}
{八/py}
{九/pz/py}


"""
    )



    # 初始化解析器
    service = ScoreService()

    # 解析成 AST
    score_document: ScoreDocumentNode = service.process_score(sample_score_text,"pipa")

    # 3.输出到控制台
    print("=== AST ===")
    #print(score_document)

    # 4.保存为 JSON
    json_data = json.dumps(score_document.to_dict(), ensure_ascii=False, indent=2)

    with open("score_document.json", "w", encoding="utf-8") as f:
        f.write(json_data)

    print("=== 已保存 score_document.json ===")
    file_name = "new_system_test.png"
    save_path = str(Path(__file__).parent / file_name)
    # 5.渲染为图片
    service.render_score(score_document,"pipa","pillow",save_path)


if __name__ == "__main__":
    main()
