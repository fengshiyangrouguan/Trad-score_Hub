import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from src.frontend.main_windows import MainWindow


def check_env():
    root_dir = Path.cwd()
    os.makedirs(root_dir / "data/scores_saved", exist_ok=True)
    os.makedirs(root_dir / "data/scores_image", exist_ok=True)

def main():
    
    check_env()
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_red.xml',css_file='custom.css')

    extra_css = """
/* ------------------------------------------- */
/* 1. 文本输入框 (QPlainTextEdit) 样式 */
/* ------------------------------------------- */
QPlainTextEdit {
    /* 背景色 (保持您选择的浅暗灰) */
    background-color: #ffffff; 
    /* 文字颜色 */
    color: #3c3c3c;
    
    /* ------------------------------------------------ */
    /* 🌟 内陷边框效果设置 */
    /* ------------------------------------------------ */
    /* 1. 设置边框样式为 groove (内凹槽) */
    border-style: groove;
    /* 2. 设置边框宽度 */
    border-width: 4px;
    /* 3. 设置边框颜色，使用不同的灰度来模拟光影 */
    border-color: #c9c9c9 #c9c9c9 #c9c9c9 #c9c9c9;
    /* ^ 顶部     ^ 右侧     ^ 底部     ^ 左侧   */
    /* 注意：暗色 (#c9c9c9) 放在顶部和左侧，亮色 (#f5f5f5) 放在右侧和底部，以创建光源在左上角的内陷效果。*/
    
    padding: 8px; /* 调整内边距，适应 2px 的边框 */
    border-radius: 8px; /* 轻微圆角 */
    selection-background-color: #ff616f;
}

/* ------------------------------------------- */
/* 2. 按钮 (QPushButton) 样式 */
/* ------------------------------------------- */
QPushButton {
    /* 主色调 (primaryColor) */
    background-color: #ff1744;
    /* 文字颜色 (secondaryLightColor) */
    color: #ffffff;
    /* 字体加粗、大小 */
    font-weight: bold;
    font-size: 14px;
    /* 边框和内边距 */
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
}

/* 按钮悬停状态 (鼠标移动到按钮上) */
QPushButton:hover {
    /* 亮红色 (primaryLightColor) */
    background-color: #ff616f;
}

/* 按钮按下状态 (点击瞬间) */
QPushButton:pressed {
    /* 略微变暗，增加点击反馈 */
    background-color: #d1002d; /* #ff1744 稍微变暗 */
    padding-top: 11px; /* 实现轻微的“按下”效果 */
}

/* 按钮禁用状态 (如翻页按钮禁用时) */
QPushButton:disabled {
    background-color: #aaaaaa; /* 灰色 */
    color: #e6e6e6;
}
    """

    window = MainWindow()

    current_style = app.styleSheet()
    app.setStyleSheet(current_style + extra_css)

    window.show()
    app.exec()



if __name__ == "__main__": 
    main()