import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize
from pathlib import Path


from src.frontend import Ui_main_windows 
from src.frontend.scalable_image_label import ScalableImageLabel 
from src.backend.app.services import ScoreService
from src.scorelang.core.pipeline_context import PipelineContext

sample_score_text_2 = (
"""# 乐谱数字化小测试
@这里写调式
## 主谱字
@支持临时转调

{一/py}
{二/py/pz}
{三/py}
{四/py/pz}
{五/b}
{六/py/pz}
{七/py}
{八/py/pz}
{九/py}
{十/py/pz}
{匕/py}
{卜/py/pz}
{敷/b}
{乙/py/pz}
{言/py}
{合/py/pz}
{斗/py}
{乞/py/pz}
{之/py}
{也/py/pz}
{也/b}
{丁/py/r}

## 修饰符号展示

{一/py/h}
{二/hh}
{乙/ls/py}
{三/le/pz}
{四/f/py}
{五/pz/py}
{六/y/b/pz}
{七（三七）/py}
{卜（八）/h/py}
{八/hh/pz}
{九/f/py}
{十/r}


"""
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. 初始化 UI
        self.ui = Ui_main_windows.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("乐谱数字化平台")
        self.service = ScoreService()
        self.context = PipelineContext()
        self.ui.text_input.setPlaceholderText("在此输入唐代琵琶谱文本，点击“生成乐谱”按钮开始处理...")
        self.ui.text_input.setPlainText(sample_score_text_2)
        self.ui.text_input.setReadOnly(False)


        # current_file_dir = Path(__file__).resolve().parent
        # self.project_root = current_file_dir.parent.parent
        self.project_root =  Path.cwd()
        self.image_save_root = self.project_root / "data" / "scores_image"
        self.text_save_root = self.project_root / "data" / "scores_saved"
        
        try:
            # 找到原始 QLabel
            old_label = self.ui.label_image 
            # 找到 QLabel 所在的布局
            image_vbox_layout = self.ui.layout_vbox_image
            
            # 记录旧控件的位置索引
            old_label_index = image_vbox_layout.indexOf(old_label)
            
            # 移除旧的 QLabel
            image_vbox_layout.removeWidget(old_label)
            old_label.deleteLater()
            
            # 创建并插入新的 ScalableImageLabel
            self.image_display = ScalableImageLabel()
            # 插入到原来的位置，并确保它能拉伸 (stretch=1)
            image_vbox_layout.insertWidget(old_label_index, self.image_display, 1) 
            
        except AttributeError:
            print("⚠️ UI 文件中的控件名称或布局结构可能与预期不符。")
            print("请确认 QLabel 命名为 'label_image'，并且其 QVBoxLayout 命名为 'layout_vbox_image'。")
            # 降级处理：直接使用 Designer 中的 QLabel
            self.image_display = self.ui.label_image
            self.image_display.setScaledContents(True)


        # 3. 业务数据初始化
        # 示例图片路径，请替换为您的资源路径或模拟数据
        self.image_paths = []
        self.current_index = 0
        
        
        # 初始化显示
        self.update_image_display()
        self.update_navigation_buttons()

        self.start_digitization()
        
        # 4. 信号槽连接
        self.ui.btn_generate.clicked.connect(self.start_digitization)
        self.ui.btn_input.clicked.connect(self.input_score)
        self.ui.btn_save.clicked.connect(self.save_score)
        self.ui.btn_prev.clicked.connect(lambda: self.navigate_image(-1))
        self.ui.btn_next.clicked.connect(lambda: self.navigate_image(1))

    # -----------------------------------------------------------
    # 5. 业务逻辑方法
    # -----------------------------------------------------------

    def update_image_display(self):
        """根据当前索引更新显示的图片"""
        if not self.image_paths:
            self.image_display.setText("数字化结果图片序列为空")
            return
        
        path = self.image_paths[self.current_index]
        try:
            pixmap = QPixmap(path) 
            
            if pixmap.isNull():
                 # 替换为占位图或错误信息
                self.image_display.setText(f"图片文件未找到: {path}")
                return
            
            # 使用自定义 ScalableImageLabel 的方法来设置图片并触发缩放
            if isinstance(self.image_display, ScalableImageLabel):
                self.image_display.set_score_pixmap(pixmap)
            else:
                 # 降级处理
                self.image_display.setPixmap(pixmap)

        except Exception as e:
            self.image_display.setText(f"图片加载失败: {path}\n错误: {e}")
            
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """更新翻页按钮的可用状态"""
        count = len(self.image_paths)
        
        # 假设翻页按钮命名为 prev_button 和 next_button
        self.ui.btn_prev.setEnabled(self.current_index > 0)
        self.ui.btn_next.setEnabled(self.current_index < count - 1)

        # 提示：可以在某个 Label 中显示页码，例如 self.ui.page_count_label.setText(...)

    def navigate_image(self, step: int):
        """翻页逻辑"""
        new_index = self.current_index + step
        if 0 <= new_index < len(self.image_paths):
            self.current_index = new_index
            self.update_image_display()

    def start_digitization(self):
        """点击数字化按钮后的处理逻辑"""
        input_text = self.ui.text_input.toPlainText()
        if not input_text.strip():
            QMessageBox.warning(self, "输入错误", "请输入乐谱文本后再进行数字化生成。")
            return
            
        # QMessageBox.information(self, "数字化", f"开始处理以下文本:\n{input_text[:50]}...")
        
        # 1. 处理乐谱逻辑
        context: PipelineContext = PipelineContext()
        context.set_raw_text(input_text)
        try:
            context = self.service.process_score(context,"pipa")
        except Exception as e:
            QMessageBox.critical(self, "处理错误", f"乐谱文本处理失败\n错误: {e}")
            return

        # 2. 提取乐谱名
        score_dict = context.node.to_dict()
        score_name = score_dict.get('title', 'untitled_score')

        
        # 3. 确定项目根目录和保存路径


        self.service.render_score(context,"pipa","image",str(self.image_save_root))

        final_score_dir = self.image_save_root / score_name
        self.image_paths = []
        for image_path in sorted(final_score_dir.glob("page_*.png")):
            # 将 Path 对象转换为字符串，以便 PySide6 的 QPixmap() 使用
            self.image_paths.append(str(image_path))
            
        # 检查是否生成了图片
        if not self.image_paths:
            QMessageBox.warning(self, "渲染失败", f"未在目录 {final_score_dir} 中找到生成的乐谱图片。")
            return
        
        self.current_index = 0
        self.update_image_display()

    def input_score(self):
        """
        打开文件选择对话框，选择乐谱文件，将内容加载到 QPlainTextEdit，并运行生成。
        """
        # 1. 打开文件对话框
        file_dialog = QFileDialog(self)
        
        # 设置打开的起始目录
        initial_dir = str(self.text_save_root)
        
        # 过滤器：只显示 .score 文件，或所有文件
        filter_str = "乐谱文件 (*.score);;所有文件 (*)"
        
        # 弹出文件打开对话框
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "打开已保存的乐谱文件", 
            initial_dir,
            filter_str
        )

        if file_path:
            try:
                # 2. 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 3. 将文本显示到 QPlainTextEdit
                self.ui.text_input.setPlainText(content)
                
                # 4. 运行生成逻辑 (您之前定义的 start_digitization)
                self.start_digitization() 
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"读取文件失败: {e}")
                
    def save_score(self):
        """
        保存 QPlainTextEdit 中的文本到 data/scores_saved/{score_name}.score。
        """
        # 1. 获取当前编辑框中的文本
        content = self.ui.text_input.toPlainText()

        if not content.strip():
            QMessageBox.warning(self, "保存失败", "当前文本输入框内容为空，无法保存。")
            return
            
        # 2. 运行生成逻辑以获取 score_name (必须先运行，因为 score_name 依赖 context)
        
        # 警告：这里我们只运行获取 score_name 必要的业务逻辑，不渲染图片
        # 理论上，您应该封装一个方法专门用于解析文本获取 context，而不是调用 start_digitization

        try:
            # 简化操作：假设您的 service.process_score 可以在不影响 UI 的情况下运行
            context = PipelineContext()
            context.set_raw_text(content)
            context = self.service.process_score(context,"pipa")
            score_dict = context.node.to_dict()
            score_name = score_dict.get('title', 'untitled_score')
        
        except Exception as e:
            QMessageBox.critical(self, "解析错误", f"无法从文本中解析出乐谱名称，保存失败。\n错误: {e}")
            score_name = "error_untitled" # 使用默认值以防万一
        
        # 3. 构造保存的文件路径
        file_name = f"{score_name}.score"
        save_path = self.text_save_root / file_name

        # 4. 写入文件
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            QMessageBox.information(self, "保存成功", f"乐谱已保存到:\n{save_path}")

        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"写入文件失败: {e}")


