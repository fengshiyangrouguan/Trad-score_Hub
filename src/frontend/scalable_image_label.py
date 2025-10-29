# scalable_image_label.py (或直接放在 main_windows.py 顶部)

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize

class ScalableImageLabel(QLabel):
    """
    一个自定义的 QLabel，用于在尺寸变化时自动等比例缩放图片。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._current_pixmap = QPixmap() 

    def set_score_pixmap(self, pixmap: QPixmap):
        """设置新的原始图片，并触发缩放更新"""
        self._current_pixmap = pixmap
        self.update_scaled_image() 

    def resizeEvent(self, event):
        """当控件尺寸变化时自动触发缩放"""
        super().resizeEvent(event)
        self.update_scaled_image()

    def update_scaled_image(self):
        """执行等比例缩放操作"""
        if self._current_pixmap.isNull():
            self.setText("乐谱图片显示区域")
            return
        
        # 1. 获取 QLabel 的当前可用尺寸
        label_size = self.size()
        
        # 2. 缩放图片，保持宽高比，并平滑处理
        scaled_pixmap = self._current_pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio, # 保持宽高比
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 3. 设置到 QLabel
        self.setPixmap(scaled_pixmap)
        
    def minimumSizeHint(self) -> QSize:
        """
        覆盖此方法，明确告诉布局管理器，这个标签可以缩小到 1x1 像素。
        """
        # 如果没有图片，返回一个默认值，或者返回最小允许尺寸
        if self._current_pixmap.isNull():
             # 返回 QWidget 的默认最小尺寸提示
             return super().minimumSizeHint()

        # 核心：为了允许 QSplitter 自由拖动，我们将最小尺寸设得很小
        return QSize(1, 1)
# ----------------------------------------------------------------------