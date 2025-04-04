import sys
import os
import zipfile
import json
import shutil
import winreg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QButtonGroup,
    QGroupBox, QRadioButton, QStackedWidget, QDialog, QScrollArea, QCheckBox, QMessageBox,
    QLineEdit, QTextBrowser, QGraphicsOpacityEffect, QProgressBar
)
from PySide6.QtGui import QPixmap, QIcon, QDesktopServices, QCursor, QFont
from PySide6.QtCore import Qt, QSize, QUrl, QPropertyAnimation, QEasingCurve, QPoint, QTimer

# 定义全局版本变量
APP_VERSION = "2.1.3.50404 Alpha"

# 内测码
BETA_CODE = ""

class ToastNotification(QWidget):
    def __init__(self, parent=None, title="", message="", toast_type="tip"):
        super().__init__(parent)
        self.setFixedSize(400, 80)

        # 外层布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 外层无边距

        # 创建一个容器 QWidget，用于统一背景
        container = QWidget()
        container.setStyleSheet("background-color: #3D3D3D; border-radius: 10px;")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)  # 容器内边距
        container_layout.setSpacing(15)  # 设置间距为 15

        # 左侧图标
        self.icon_label = QLabel()
        base_path = os.path.dirname(os.path.abspath(__file__))
        if toast_type == "tip":
            icon_path = os.path.join(base_path, "assets/icon/tip.png")
        elif toast_type == "error":
            icon_path = os.path.join(base_path, "assets/icon/error.png")
        elif toast_type == "warning":
            icon_path = os.path.join(base_path, "assets/icon/warning.png")
        else:
            icon_path = os.path.join(base_path, "assets/icon/tip.png")  # 默认使用提示图标

        pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setStyleSheet("background-color: transparent; margin: 0px; padding: 0px;")  # 移除可能存在的边距和填充
        self.icon_label.setFixedSize(40, 40)  # 固定图标大小，避免自动调整
        container_layout.addWidget(self.icon_label)

        # 右侧文字（两行：标题和内容）
        text_widget = QWidget()
        text_widget.setStyleSheet("background-color: transparent; margin: 0px; padding: 0px;")  # 移除可能存在的边距和填充
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)  # 确保文字控件内部无边距
        text_layout.setSpacing(5)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: white; margin: 0px; padding: 0px;")  # 移除边距和填充
        text_layout.addWidget(self.title_label)

        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Microsoft YaHei", 10))
        self.message_label.setStyleSheet("color: #AAAAAA; margin: 0px; padding: 0px;")  # 移除边距和填充
        self.message_label.setWordWrap(True)
        text_layout.addWidget(self.message_label)

        container_layout.addWidget(text_widget)

        # 确保布局中没有拉伸因子干扰
        container_layout.setStretch(0, 0)  # 图标不拉伸
        container_layout.setStretch(1, 1)  # 文字部分占剩余空间

        # 将容器添加到主布局
        main_layout.addWidget(container)

        # 设置透明度效果，用于动画
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # 动画：从底部滑入并淡入
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")

        # 定时器：3秒后自动消失
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)

    def show_toast(self):
        # 设置初始位置（窗口底部外）
        parent_height = self.parent().height()
        self.move(200, parent_height)  # 初始位置在窗口底部外

        # 滑入动画
        self.slide_animation.setDuration(500)
        self.slide_animation.setStartValue(QPoint(200, parent_height))
        self.slide_animation.setEndValue(QPoint(200, parent_height - 100))
        self.slide_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 淡入动画
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.show()
        self.slide_animation.start()
        self.fade_animation.start()

        # 3秒后自动消失
        self.timer.start(3000)

    def hide_toast(self):
        # 滑出并淡出动画
        parent_height = self.parent().height()
        self.slide_animation.setStartValue(QPoint(200, parent_height - 100))
        self.slide_animation.setEndValue(QPoint(200, parent_height))
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)

        self.slide_animation.start()
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.deleteLater)

class PluginItem(QWidget):
    def __init__(self, name, description, icon_path, has_subpack, parent=None, main_window=None):
        super().__init__(parent)
        self.has_subpack = has_subpack
        self.main_window = main_window
        self.initUI(name, description, icon_path)
        self.setStyleSheet("background-color: transparent;")

    def initUI(self, name, description, icon_path):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(4)
        self.setFixedSize(500, 70)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 30px; }")
        layout.addWidget(self.checkbox)

        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(50, 50)
        layout.addWidget(self.icon_label)

        self.mix_text_box = QWidget()
        mix_text_layout = QHBoxLayout(self.mix_text_box)  # 修改为水平布局以添加图标
        mix_text_layout.setContentsMargins(0, 0, 0, 15)
        mix_text_layout.setSpacing(8)  # 设置图标和文字之间的间距

        # 文字部分（垂直布局）
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        text_layout.addWidget(self.name_label)

        self.description_label = QLabel(description)
        self.description_label.setFont(QFont("Microsoft YaHei", 10))
        text_layout.addWidget(self.description_label)

        mix_text_layout.addWidget(text_widget)
        layout.addWidget(self.mix_text_box)
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        layout.setStretchFactor(self.mix_text_box, 1)
        if self.main_window:
            self.checkbox.stateChanged.connect(self.main_window.toggle_apply_button)

class UserAgreementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户协议&更新日志")
        self.setGeometry(575, 150, 750, 800)
        self.setStyleSheet("QDialog { background-color: rgb(45, 45, 45); }")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 20)
        main_layout.setSpacing(0)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 20)
        self.title_label = QLabel("用户协议&更新日志")
        self.title_label.setStyleSheet("QLabel { color: white; font-size: 24px; font-weight: bold; background-color: transparent; }")
        title_layout.addWidget(self.title_label)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 5)

        self.agreement_widget = QWidget()
        agreement_layout = QVBoxLayout(self.agreement_widget)
        self.agreement_title = QLabel("用户协议")
        self.agreement_title.setStyleSheet("QLabel { color: #A8B4D4; font-size: 20px; margin-bottom: 10px; background-color: transparent; }")
        agreement_layout.addWidget(self.agreement_title)

        self.agreement_text = QTextBrowser()
        self.agreement_text.setStyleSheet("QTextBrowser { background-color: rgb(55, 55, 58); color: #DCDDDE; border: 1px solid #36393F; border-radius: 8px; padding: 15px; font-size: 14px; line-height: 1.6; min-height: 300px; } QScrollBar:vertical { background-color: transparent; width: 0px; }")
        self.agreement_text.setReadOnly(True)
        agreement_layout.addWidget(self.agreement_text)

        self.update_log_widget = QWidget()
        update_log_layout = QVBoxLayout(self.update_log_widget)
        self.update_log_title = QLabel("更新日志")
        self.update_log_title.setStyleSheet("QLabel { color: #A8B4D4; font-size: 20px; margin-bottom: 10px; background-color: transparent; }")
        update_log_layout.addWidget(self.update_log_title)

        self.update_log_text = QTextBrowser()
        self.update_log_text.setStyleSheet("QTextBrowser { background-color: rgb(55, 55, 58); color: #DCDDDE; border: 1px solid #36393F; border-radius: 8px; padding: 15px; font-size: 14px; line-height: 1.6; min-height: 160px; } QScrollBar:vertical { background-color: transparent; width: 0px; }")
        self.update_log_text.setReadOnly(True)
        update_log_layout.addWidget(self.update_log_text)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; } QScrollBar:vertical { background-color: transparent; width: 0px; }")
        scroll_area.setWidgetResizable(True)

        content_container = QWidget()
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.addWidget(self.agreement_widget)
        content_container_layout.addWidget(self.update_log_widget)
        content_container_layout.addStretch()

        scroll_area.setWidget(content_container)
        content_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()

        self.close_button = QPushButton("关闭")
        self.close_button.setStyleSheet("QPushButton { background-color: rgb(135, 153, 255); color: white; border: none; border-radius: 5px; padding: 10px 20px; font-size: 14px; } QPushButton:hover { background-color: rgb(145, 163, 255); }")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(title_layout)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.load_content()

    def load_content(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        lang_path = os.path.join(base_path, "assets/text", "zh_cn.lang")
        print(f"Attempting to load language file from: {lang_path}")  # 调试信息
        if not os.path.exists(lang_path):
            print(f"Language file not found at: {lang_path}")
            self.agreement_text.setText("无法加载用户协议，语言文件不存在。")
            self.update_log_text.setText("无法加载更新日志，语言文件不存在。")
            toast = ToastNotification(self, "错误", "语言文件不存在！", "error")
            toast.show_toast()
            return
        try:
            with open(lang_path, "r", encoding="utf-8") as file:
                lang_data = {}
                for line in file:
                    line = line.strip()
                    #print(f"Processing line: {line}")  # 调试信息
                    if line and not line.startswith("#"):
                        if "=" not in line:
                            print(f"Skipping invalid line (no '=' found): {line}")
                            continue
                        parts = line.split("=", 1)
                        if len(parts) != 2:
                            print(f"Skipping invalid line (incorrect format): {line}")
                            continue
                        key, value = parts
                        if not value:
                            print(f"Skipping line with empty value: {line}")
                            continue
                        lang_data[key] = value

                user_agreement_title = lang_data.get("user_agreement.title", "欢迎您使用Lerio!")
                user_agreement_content = lang_data.get("user_agreement.content", "用户协议内容未加载")
                update_log_title = lang_data.get("update_log.title", "更新日志")
                update_log_Launcher_version = lang_data.get("update_log.client_version", "客户端版本 {version}").format(version=APP_VERSION)
                update_log_changes = lang_data.get("update_log.changes", "更新日志未加载")

                sections = ["免责声明", "适用范围", "主要规定", "转载规定", "分享规定", "协议变更", "其他"]
                for section in sections:
                    user_agreement_content = user_agreement_content.replace(f"| {section}", f"<b>| {section}</b>")

                user_agreement_content = user_agreement_content.replace("\\n", "<br>")
                update_log_changes = update_log_changes.replace("\\n", "<br>")

                self.agreement_text.setHtml(f"<h3 style='color: #A8B4D4;'>{user_agreement_title}</h3><p>{user_agreement_content}</p>")
                self.update_log_text.setHtml(f"<h3 style='color: #A8B4D4;'>{update_log_title}</h3><h4 style='color: #A8B4D4;'>{update_log_Launcher_version}</h4><p>{update_log_changes}</p>")
        except Exception as e:
            print(f"Error loading lang file: {e}")
            self.agreement_text.setText("无法加载用户协议，请检查语言文件是否正确。")
            self.update_log_text.setText("无法加载更新日志，请检查语言文件是否正确。")
            toast = ToastNotification(self, "错误", f"加载语言文件失败：{e}", "error")
            toast.show_toast()
         
class BetaVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lerio Launcher Start")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: transparent;")

        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 800, 600)
        self.background_label.lower()

        base_path = os.path.dirname(os.path.abspath(__file__))
        background_path = os.path.join(base_path, "assets/images/background")
        background_pixmap = QPixmap(background_path)
        if not background_pixmap.isNull():
            self.background_label.setPixmap(background_pixmap)
            self.background_label.setScaledContents(True)
        else:
            print(f"背景图片加载失败: {background_path}")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)

        self.logo_icon = QLabel()
        self.logo_icon.setStyleSheet("background-color: transparent;")
        icon_path = os.path.join(base_path, "assets/icon/lerio_high.png")
        lerio_pixmap = QPixmap(icon_path)
        if not lerio_pixmap.isNull():
            lerio_pixmap = lerio_pixmap.scaled(128, 128, Qt.KeepAspectRatio)
            self.logo_icon.setPixmap(lerio_pixmap)
            self.logo_icon.setFixedSize(128, 128)
        else:
            print(f"Lerio图标加载失败: {icon_path}")
        logo_layout.addWidget(self.logo_icon)

        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background-color: transparent; color: white; font-size: 48px; font-weight: bold;")
        self.logo_label.setText(f"Lerio \n{APP_VERSION}")
        logo_layout.addWidget(self.logo_label)

        main_layout.addLayout(logo_layout)

        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)
        input_layout.setSpacing(20)

        self.code_label = QLabel("内测码:")
        self.code_label.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
        input_layout.addWidget(self.code_label)

        self.code_input = QLineEdit()
        self.code_input.setStyleSheet("background-color: rgb(50, 50, 50); color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.code_input.setFixedWidth(400)
        input_layout.addWidget(self.code_input)

        checkbox_button_layout = QHBoxLayout()
        checkbox_button_layout.setAlignment(Qt.AlignCenter)
        checkbox_button_layout.setSpacing(20)

        self.agree_checkbox = QCheckBox("")
        self.agree_checkbox.setStyleSheet("background-color: transparent; color: white; font-size: 14px;")
        checkbox_button_layout.addWidget(self.agree_checkbox)

        self.agree_link = QLabel('同意' + '<a href="user_agreement">《LerioLauncher使用协议》</a>')
        self.agree_link.setStyleSheet("background-color: transparent; color: rgb(255, 255, 255); font-size: 14px;")
        self.agree_link.linkActivated.connect(self.show_user_agreement)
        checkbox_button_layout.addWidget(self.agree_link)

        self.confirm_button = QPushButton("确定")
        self.confirm_button.setStyleSheet("background-color: rgb(135, 153, 255); color: white; font-size: 16px; padding: 10px 20px; border-radius: 5px; border: none;")
        self.confirm_button.clicked.connect(self.verify)
        checkbox_button_layout.addWidget(self.confirm_button)

        input_layout.addLayout(checkbox_button_layout)

        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setSpacing(20)

        self.qq_button = QPushButton()
        self.qq_button.setIcon(QIcon(os.path.join(base_path, "assets/icon/QQ.png")))
        self.qq_button.setIconSize(QSize(40, 40))
        self.qq_button.setStyleSheet("QPushButton { background-color: transparent; border: none; border-radius: 20px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
        self.qq_button.clicked.connect(self.open_qq_link)
        icon_layout.addWidget(self.qq_button)

        self.github_button = QPushButton()
        self.github_button.setIcon(QIcon(os.path.join(base_path, "assets/icon/Github.png")))
        self.github_button.setIconSize(QSize(40, 40))
        self.github_button.setStyleSheet("QPushButton { background-color: transparent; border: none; border-radius: 20px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
        self.github_button.clicked.connect(self.open_github_link)
        icon_layout.addWidget(self.github_button)

        input_layout.addLayout(icon_layout)
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def verify(self):
        input_code = self.code_input.text().strip()
        if input_code == BETA_CODE:
            if self.agree_checkbox.isChecked():
                self.accept()
            else:
                toast = ToastNotification(self, "警告", "请先同意《Lerio使用协议》", "warning")
                toast.show_toast()
        else:
            toast = ToastNotification(self, "错误", "内测码错误!", "error")
            toast.show_toast()

    def show_user_agreement(self):
        dialog = UserAgreementDialog(self)
        dialog.exec()

    def open_qq_link(self):
        QDesktopServices.openUrl(QUrl("https://qm.qq.com/q/9Lov0aVmZa"))

    def open_github_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/ZNink/Lerio"))

class InstallProgressWidget(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window  # 保存对 MainWindow 的引用
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #2D2D2D; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.progress_label = QLabel("安装进度")
        self.progress_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.progress_label.setStyleSheet("color: white;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #36393F;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #8799FF;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("正在安装...")
        self.status_label.setStyleSheet("color: #AAAAAA;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress = 0

    def start_progress(self):
        self.progress = 0
        self.progress_bar.setValue(0)
        self.status_label.setText("正在安装...")
        self.timer.start(12)

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        #print(f"Progress: {self.progress}%")  # 调试信息
        if self.progress >= 100:
            self.timer.stop()
            self.status_label.setText("即将安装完成")
            print("Progress reached 100%")  # 调试信息
            # 不再在这里调用 installation_finished，交给 perform_installation 处理
            QApplication.processEvents()  # 强制刷新界面

class InstallCompleteWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置主布局为垂直布局，并确保居中对齐
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)  # 确保整个布局内容居中

        # 图标
        icon_label = QLabel()
        icon_path = os.path.join(parent.base_path, "assets/icon/complete.png")
        pixmap = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)  # 图标居中
        layout.addWidget(icon_label)

        # 文字
        complete_label = QLabel("安装完成")
        complete_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        complete_label.setStyleSheet("color: white;")
        complete_label.setAlignment(Qt.AlignCenter)  # 文字居中
        layout.addWidget(complete_label)

        # 增加行距
        layout.addSpacing(50)  # 在文字和按钮之间增加间距

        # 完成按钮
        self.finish_button = QPushButton("完成")
        self.finish_button.setFixedSize(150, 40)
        self.finish_button.setStyleSheet("QPushButton { background-color: #8799FF; color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: #97A9FF; }")
        self.finish_button.clicked.connect(lambda: parent.stacked_widget.setCurrentWidget(parent.install_page))
        # 将按钮包装在一个 QWidget 中以控制对齐
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()  # 左侧填充
        button_layout.addWidget(self.finish_button)
        button_layout.addStretch()  # 右侧填充
        layout.addWidget(button_container)

        # layout.addStretch()  # 移除底部填充，确保内容整体居中
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files_to_delete = []
        self.setWindowTitle(f"Lerio Launcher Release {APP_VERSION}")
        self.setGeometry(550, 250, 800, 700)
        self.setFixedSize(800, 700)
        #self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("MainWindow { background-color: #2D2D2D; border-radius: 20px; }")
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.import_button = QPushButton("导入")
        self.import_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "import.png")))
        self.import_button.setIconSize(QSize(32, 32))
        self.import_button.clicked.connect(self.import_plugin)
        self.import_button.setFixedSize(100, 40)
        self.import_button.setStyleSheet("QPushButton { background-color: #404040; color: white; border: none; border-radius: 5px; font-size: 16px; padding: 10px; } QPushButton:hover { background-color: #505050; }")

        self.delete_button = QPushButton("删除")
        self.delete_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "delete.png")))
        self.delete_button.setIconSize(QSize(32, 32))
        self.delete_button.clicked.connect(self.delete_plugin)
        self.delete_button.setFixedSize(100, 40)
        self.delete_button.setStyleSheet("QPushButton { background-color: #723131; color: white; border: none; border-radius: 5px; font-size: 16px; padding: 10px; } QPushButton:hover { background-color: #824141; }")

        self.next_button = QPushButton("下一步")
        self.next_button.setStyleSheet("QPushButton { background-color: #7289DA; color: white; border: none; border-radius: 5px; font-size: 16px; padding: 10px; } QPushButton:hover { background-color: #677BC4; }")
        self.next_button.setFixedSize(100, 40)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.init_top_bar()
        self.main_content = QStackedWidget()
        self.main_content.setStyleSheet("background-color: #2D2D2D; border: none;")
        self.main_layout.addWidget(self.main_content)
        self.init_tabs()
        self.plugin_path = os.path.join(os.path.expandvars("%appdata%"), "LerioLauncher", "addons")
        if not os.path.exists(self.plugin_path):
            os.makedirs(self.plugin_path)
        self.plugin_path_input.setText(self.plugin_path)
        self.load_plugins()
        self.update_button_style(0)
        self.draggable = False
        self.drag_start_position = QPoint()
        self.current_page = None
        self.next_page = None
        self.fade_out_animation = None
        self.fade_in_animation = None
        self.selected_client_path = None  # 存储导入的客户端文件路径
        self.install_options = {"textures": True, "ui": True, "texts": True}  # 自定义安装选项

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.top_bar.rect().contains(self.top_bar.mapFromGlobal(QCursor.pos())):
                self.draggable = True
                self.drag_start_position = QCursor.pos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.draggable:
            self.move(QCursor.pos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            event.accept()

    def init_top_bar(self):
        self.top_bar = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(10, 10, 10, 10)
        top_bar_layout.setSpacing(10)
        self.top_bar.setLayout(top_bar_layout)
        self.top_bar.setStyleSheet("background-color: rgb(36, 36, 36);")

        left_container = QWidget()
        left_container.setStyleSheet("background-color: rgb(40, 40, 40); border-radius: 10px; padding: 0px;")
        left_layout = QHBoxLayout(left_container)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.lerio_icon = QLabel()
        icon_path = os.path.join(self.base_path, "assets", "icon", "lerio.png")
        pixmap = QPixmap(icon_path).scaled(48, 48, Qt.KeepAspectRatio)
        self.lerio_icon.setPixmap(pixmap)
        self.lerio_icon.setStyleSheet("border-radius: 4px;")
        left_layout.addWidget(self.lerio_icon)

        self.button_group = QButtonGroup(self)
        self.install_button = QPushButton(" 安装")
        self.install_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "setup.png")))
        self.install_button.setIconSize(QSize(24, 24))
        self.install_button.setFixedHeight(40)
        self.install_button.setFont(QFont("Microsoft YaHei", 12))
        self.install_button.setStyleSheet(self.get_button_style(False))

        self.plugin_button = QPushButton(" 插件")
        self.plugin_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "plugin.png")))
        self.plugin_button.setIconSize(QSize(24, 24))
        self.plugin_button.setFixedHeight(40)
        self.plugin_button.setFont(QFont("Microsoft YaHei", 12))
        self.plugin_button.setStyleSheet(self.get_button_style(False))

        self.tools_button = QPushButton(" 工具")
        self.tools_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "tools.png")))
        self.tools_button.setIconSize(QSize(24, 24))
        self.tools_button.setFixedHeight(40)
        self.tools_button.setFont(QFont("Microsoft YaHei", 12))
        self.tools_button.setStyleSheet(self.get_button_style(False))

        self.settings_button = QPushButton(" 设置")
        self.settings_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "settings.png")))
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedHeight(40)
        self.settings_button.setFont(QFont("Microsoft YaHei", 12))
        self.settings_button.setStyleSheet(self.get_button_style(False))

        self.about_button = QPushButton(" 关于")
        self.about_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "about.png")))
        self.about_button.setIconSize(QSize(24, 24))
        self.about_button.setFixedHeight(40)
        self.about_button.setFont(QFont("Microsoft YaHei", 12))
        self.about_button.setStyleSheet(self.get_button_style(False))

        self.button_group.addButton(self.install_button, 0)
        self.button_group.addButton(self.plugin_button, 1)
        self.button_group.addButton(self.tools_button, 2)
        self.button_group.addButton(self.settings_button, 3)
        self.button_group.addButton(self.about_button, 4)
        self.button_group.buttonClicked.connect(self.switch_tab)

        left_layout.addWidget(self.install_button)
        left_layout.addWidget(self.plugin_button)
        left_layout.addWidget(self.tools_button)
        left_layout.addWidget(self.settings_button)
        left_layout.addWidget(self.about_button)

        right_container = QWidget()
        right_container.setStyleSheet("background-color: rgb(40, 40, 40); border-radius: 8px; padding: 5px;")
        right_layout = QHBoxLayout(right_container)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(15, 15, 15, 15)

        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "minimize.png")))
        self.minimize_button.setIconSize(QSize(24, 24))
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.setStyleSheet("QPushButton { background-color: transparent; border-radius: 4px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
        self.minimize_button.clicked.connect(self.showMinimized)

        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "close.png")))
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setFixedSize(40, 40)
        self.close_button.setStyleSheet("QPushButton { background-color: transparent; border-radius: 4px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }")
        self.close_button.clicked.connect(self.close)

        right_layout.addWidget(self.minimize_button)
        right_layout.addWidget(self.close_button)

        top_bar_layout.addWidget(left_container)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(right_container)
        self.main_layout.addWidget(self.top_bar)

    def get_button_style(self, is_active):
        if is_active:
            return "QPushButton { background-color: rgb(135, 153, 255); color: white; border: none; border-radius: 4px; padding: 5px 10px; font-size: 14px; } QPushButton:hover { background-color: rgb(145, 163, 255); }"
        else:
            return "QPushButton { background-color: transparent; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-size: 14px; } QPushButton:hover { background-color: rgba(90, 90, 90, 0.5); }"

    def init_tabs(self):
        self.install_tab = QWidget()
        install_layout = QVBoxLayout(self.install_tab)
        install_layout.setContentsMargins(20, 10, 20, 10)

        self.stacked_widget = QStackedWidget()
        install_layout.addWidget(self.stacked_widget)

        self.install_page = self.create_install_page()
        self.custom_setup_page = self.create_custom_setup_page()
        self.other_setup_page = self.create_import_client_page()
        self.install_location_page = self.create_install_location_page()
        self.install_progress_page = self.create_install_progress_page()
        self.install_complete_page = self.create_install_complete_page()

        self.stacked_widget.addWidget(self.install_page)
        self.stacked_widget.addWidget(self.custom_setup_page)
        self.stacked_widget.addWidget(self.other_setup_page)
        self.stacked_widget.addWidget(self.install_location_page)
        self.stacked_widget.addWidget(self.install_progress_page)
        self.stacked_widget.addWidget(self.install_complete_page)

        self.plugins_tab = QWidget()
        plugins_layout = QVBoxLayout(self.plugins_tab)
        plugins_layout.setContentsMargins(20, 20, 20, 20)

        top_button_layout = QHBoxLayout()
        
        # 创建一个新的 QWidget 来包含图标和“插件”文字
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)  # 设置图标和文字之间的间距
        title_layout.setAlignment(Qt.AlignVCenter)

        # 添加插件图标
        plugin_icon = QLabel()
        icon_path = os.path.join(self.base_path, "assets/icon/plugin.png")
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio)  # 调整图标大小为 32x32
            plugin_icon.setPixmap(pixmap)
            plugin_icon.setAlignment(Qt.AlignCenter)
        else:
            print(f"加载插件图标失败: {icon_path}")
        title_layout.addWidget(plugin_icon)

        # 添加“插件”文字
        self.addons_label = QLabel("插件 Plugin")
        self.addons_label.setFont(QFont("Microsoft YaHei", 18))
        self.addons_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.addons_label.setStyleSheet("color: #FFFFFF;")
        title_layout.addWidget(self.addons_label)

        top_button_layout.addWidget(title_widget)
        top_button_layout.addStretch()
        top_button_layout.addWidget(self.import_button)
        top_button_layout.addWidget(self.delete_button)
        top_button_layout.addWidget(self.next_button)
        plugins_layout.addLayout(top_button_layout)

        self.plugins_scroll_area = QScrollArea()
        self.plugins_scroll_area.setWidgetResizable(True)
        self.plugins_scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; } QScrollBar:vertical { width: 0px; } QScrollBar:horizontal { height: 0px; }")
        self.plugins_widget = QWidget()
        self.plugins_widget.setStyleSheet("background-color: rgb(64, 64, 64); border-radius: 10px;")
        self.plugins_layout = QVBoxLayout(self.plugins_widget)
        self.plugins_layout.setContentsMargins(5, 5, 5, 5)
        self.plugins_layout.setSpacing(10)
        self.plugins_layout.setAlignment(Qt.AlignTop)  # 确保插件项目从顶部对齐
        self.plugins_scroll_area.setWidget(self.plugins_widget)
        plugins_layout.addWidget(self.plugins_scroll_area)

        self.tools_tab = QWidget()
        tools_layout = QVBoxLayout(self.tools_tab)
        tools_layout.setContentsMargins(20, 20, 20, 20)
        tools_label = QLabel("✨ 杀EN \n 杀EN前请确认已下载服务器资源包")
        tools_label.setFont(QFont("Microsoft YaHei", 20, QFont.Light))
        tools_label.setStyleSheet("color: #FFFFFF;")
        tools_layout.addWidget(tools_label)

        options = QGroupBox("杀EN选项")
        options.setStyleSheet("QGroupBox { border: 1px solid #404040; border-radius: 5px; }")
        options_layout = QVBoxLayout()
        self.radio_full_kill = QRadioButton("全杀-布吉岛")
        self.radio_simplified_kill = QRadioButton("简杀-EaseCation")
        self.radio_full_kill.setChecked(True)
        font = QFont("Microsoft YaHei", 18)
        self.radio_full_kill.setFont(font)
        self.radio_simplified_kill.setFont(font)
        self.radio_full_kill.setStyleSheet("color: #FFFFFF;")
        self.radio_simplified_kill.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(self.radio_full_kill)
        options_layout.addWidget(self.radio_simplified_kill)
        options.setLayout(options_layout)
        tools_layout.addWidget(options)

        self.kill_en_button = QPushButton("确定")
        self.kill_en_button.setStyleSheet("QPushButton { background-color: #7289DA; color: white; border: none; border-radius: 5px; font-size: 16px; padding: 10px 20px; } QPushButton:hover { background-color: #677BC4; }")
        self.kill_en_button.clicked.connect(self.confirm_kill_en)
        tools_layout.addWidget(self.kill_en_button)

        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_label = QLabel("✨ 设置")
        settings_label.setFont(QFont("Microsoft YaHei", 20, QFont.Light))
        settings_label.setStyleSheet("color: #FFFFFF;")
        settings_layout.addWidget(settings_label)

        self.plugin_path_label = QLabel("插件路径:")
        self.plugin_path_label.setStyleSheet("color: #AAAAAA;")
        settings_layout.addWidget(self.plugin_path_label)

        self.plugin_path_input = QLineEdit()
        self.plugin_path_input.setReadOnly(True)
        self.plugin_path_input.setStyleSheet("QLineEdit { background-color: #36393F; color: white; border: 1px solid #404040; border-radius: 5px; padding: 10px; }")
        settings_layout.addWidget(self.plugin_path_input)

        self.plugin_path_button = QPushButton("更改路径")
        self.plugin_path_button.setStyleSheet("QPushButton { background-color: #404040; color: white; border: none; border-radius: 5px; font-size: 14px; padding: 10px 20px; } QPushButton:hover { background-color: #505050; }")
        self.plugin_path_button.clicked.connect(self.change_plugin_path)
        settings_layout.addWidget(self.plugin_path_button)

        self.about_tab = QWidget()
        about_layout = QVBoxLayout(self.about_tab)
        about_layout.setContentsMargins(20, 20, 20, 20)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setScaledContents(False)
        self.icon_label.setPixmap(QPixmap(os.path.join(self.base_path, "assets", "icon", "lerio.png")))
        about_layout.addWidget(self.icon_label)

        about_label = QLabel("Lerio Launcher ")
        about_label.setFont(QFont("Microsoft YaHei", 20, QFont.Light))
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet("color: #FFFFFF;")
        about_layout.addWidget(about_label)

        about_content = QLabel(f"Lerio Launcher {APP_VERSION}\nDeveloper: ZNi\nGitHub: github.com/ZNink/Lerio")
        about_content.setFont(QFont("Microsoft YaHei", 16))
        about_content.setAlignment(Qt.AlignCenter)
        about_content.setStyleSheet("color: #AAAAAA;")
        about_layout.addWidget(about_content)

        self.main_content.addWidget(self.install_tab)
        self.main_content.addWidget(self.plugins_tab)
        self.main_content.addWidget(self.tools_tab)
        self.main_content.addWidget(self.settings_tab)
        self.main_content.addWidget(self.about_tab)

        for i in range(self.main_content.count()):
            widget = self.main_content.widget(i)
            opacity_effect = QGraphicsOpacityEffect(widget)
            opacity_effect.setOpacity(1.0 if i == 0 else 0.0)
            widget.setGraphicsEffect(opacity_effect)


    def switch_tab(self, button):
        if button == self.install_button:
            self.switch_page_with_animation(0)
        elif button == self.plugin_button:
            self.switch_page_with_animation(1)
        elif button == self.tools_button:
            self.switch_page_with_animation(2)
        elif button == self.settings_button:
            self.switch_page_with_animation(3)
        elif button == self.about_button:
            self.switch_page_with_animation(4)

    def switch_page_with_animation(self, index):
        if self.main_content.currentIndex() == index:
            return
        self.current_page = self.main_content.currentWidget()
        self.next_page = self.main_content.widget(index)
        if self.fade_out_animation:
            self.fade_out_animation.stop()
        if self.fade_in_animation:
            self.fade_in_animation.stop()
        current_opacity_effect = self.current_page.graphicsEffect()
        self.fade_out_animation = QPropertyAnimation(current_opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        next_opacity_effect = self.next_page.graphicsEffect()
        self.fade_in_animation = QPropertyAnimation(next_opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.main_content.setCurrentIndex(index)
        self.update_button_style(index)
        self.fade_out_animation.start()
        self.fade_in_animation.start()

    def update_button_style(self, active_index):
        self.install_button.setStyleSheet(self.get_button_style(active_index == 0))
        self.plugin_button.setStyleSheet(self.get_button_style(active_index == 1))
        self.tools_button.setStyleSheet(self.get_button_style(active_index == 2))
        self.settings_button.setStyleSheet(self.get_button_style(active_index == 3))
        self.about_button.setStyleSheet(self.get_button_style(active_index == 4))

    def create_install_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)  # 改为水平布局
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 左侧部分：图标和标题
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        setup_icon = QLabel()
        setup_icon_path = os.path.join(self.base_path, "assets/icon/setup.png")
        setup_pixmap = QPixmap(setup_icon_path)
        if not setup_pixmap.isNull():
            setup_pixmap = setup_pixmap.scaled(100, 100, Qt.KeepAspectRatio)  # 调整图标大小
            setup_icon.setPixmap(setup_pixmap)
        else:
            print(f"加载顶部图标失败: {setup_icon_path}")
        left_layout.addWidget(setup_icon)

        setup_label = QLabel("安装 Setup")
        setup_label.setFont(QFont("Microsoft YaHei", 18))
        setup_label.setStyleSheet("color: white;")
        left_layout.addWidget(setup_label)

        # 右侧部分：选项和按钮
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        options_group = QGroupBox()
        options_group.setStyleSheet("QGroupBox { border: none; }")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(15)

        self.install_radio_group = QButtonGroup(self)
        self.radio_buttons = []
        options_data = [
            ("快速安装Lerio", "快速安装完整LerioClient", "assets/icon/fast_setup.png"),
            ("自定义安装Lerio", "自定义安装LerioClient的部份内容", "assets/icon/custom_setup.png"),
            ("安装其他Client", "通过导入其他Client的压缩包或文件进行安装", "assets/icon/setup_other.png")
        ]

        for i, (title, desc, icon_rel_path) in enumerate(options_data):
            option_widget = QWidget()
            option_widget.setStyleSheet("background-color: rgb(64, 64, 64); border-radius: 10px; padding: 10px;")
            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(10, 0, 0, 0)

            radio = QRadioButton()
            radio.setStyleSheet("color: white;")
            if i == 0:
                radio.setChecked(True)
            self.radio_buttons.append(radio)
            self.install_radio_group.addButton(radio)
            option_layout.addWidget(radio)

            icon = QLabel()
            icon_path = os.path.join(self.base_path, icon_rel_path)
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio)
                icon.setPixmap(pixmap)
            else:
                print(f"加载图标失败: {icon_path}")
            option_layout.addWidget(icon)

            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(0)
            title_label = QLabel(title)
            title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
            text_layout.addWidget(title_label)
            spacer = QWidget()
            spacer.setFixedHeight(0)
            text_layout.addWidget(spacer)
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 14px;")
            desc_label.setWordWrap(True)
            desc_label.setFixedWidth(400)
            text_layout.addWidget(desc_label)
            option_layout.addWidget(text_widget)
            option_layout.addStretch()
            options_layout.addWidget(option_widget)

        right_layout.addWidget(options_group)

        next_button = QPushButton("下一步")
        next_button.setFixedSize(120, 40)
        next_button.setStyleSheet("QPushButton { background-color: rgb(135, 153, 255); color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: rgb(145, 163, 255); }")
        next_button.clicked.connect(self.switch_install_page)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(next_button)
        right_layout.addLayout(button_layout)

        right_layout.addStretch()

        # 将左右部分添加到主布局
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        return page

    def create_custom_setup_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        icon_label = QLabel()
        icon_path = os.path.join(self.base_path, "assets/icon/custom_setup.png")
        pixmap = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        left_layout.addWidget(icon_label)

        title_label = QLabel("自定义安装Lerio")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        left_layout.addWidget(title_label)

        desc_label = QLabel("选择需要安装的LerioClient内容")
        desc_label.setFont(QFont("Microsoft YaHei", 12))
        desc_label.setStyleSheet("color: #AAAAAA;")
        left_layout.addWidget(desc_label)

        right_widget = QWidget()
        right_LAYOUT = QVBoxLayout(right_widget)
        right_LAYOUT.setSpacing(15)

        self.textures_checkbox = QCheckBox("材质")
        self.textures_checkbox.setChecked(True)
        self.textures_checkbox.setFont(QFont("Microsoft YaHei", 14))
        self.textures_checkbox.setStyleSheet("color: white;")
        self.textures_checkbox.stateChanged.connect(lambda state: self.install_options.update({"textures": state == Qt.Checked}))
        textures_icon = QLabel()
        textures_icon.setPixmap(QPixmap(os.path.join(self.base_path, "assets/icon/textures.png")).scaled(24, 24, Qt.KeepAspectRatio))
        textures_layout = QHBoxLayout()
        textures_layout.addWidget(textures_icon)
        textures_layout.addWidget(self.textures_checkbox)
        textures_layout.addStretch()
        textures_widget = QWidget()
        textures_widget.setLayout(textures_layout)
        textures_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_LAYOUT.addWidget(textures_widget)

        self.ui_checkbox = QCheckBox("UI")
        self.ui_checkbox.setChecked(True)
        self.ui_checkbox.setFont(QFont("Microsoft YaHei", 14))
        self.ui_checkbox.setStyleSheet("color: white;")
        self.ui_checkbox.stateChanged.connect(lambda state: self.install_options.update({"ui": state == Qt.Checked}))
        ui_icon = QLabel()
        ui_icon.setPixmap(QPixmap(os.path.join(self.base_path, "assets/icon/ui.png")).scaled(24, 24, Qt.KeepAspectRatio))
        ui_layout = QHBoxLayout()
        ui_layout.addWidget(ui_icon)
        ui_layout.addWidget(self.ui_checkbox)
        ui_layout.addStretch()
        ui_widget = QWidget()
        ui_widget.setLayout(ui_layout)
        ui_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_LAYOUT.addWidget(ui_widget)

        self.texts_checkbox = QCheckBox("文本")
        self.texts_checkbox.setChecked(True)
        self.texts_checkbox.setFont(QFont("Microsoft YaHei", 14))
        self.texts_checkbox.setStyleSheet("color: white;")
        self.texts_checkbox.stateChanged.connect(lambda state: self.install_options.update({"texts": state == Qt.Checked}))
        texts_icon = QLabel()
        texts_icon.setPixmap(QPixmap(os.path.join(self.base_path, "assets/icon/texts.png")).scaled(24, 24, Qt.KeepAspectRatio))
        texts_layout = QHBoxLayout()
        texts_layout.addWidget(texts_icon)
        texts_layout.addWidget(self.texts_checkbox)
        texts_layout.addStretch()
        texts_widget = QWidget()
        texts_widget.setLayout(texts_layout)
        texts_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_LAYOUT.addWidget(texts_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        prev_button = QPushButton("上一步")
        prev_button.setFixedSize(120, 40)
        prev_button.setStyleSheet("QPushButton { background-color: #505050; color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: #606060; }")
        prev_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.install_page))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("下一步")
        next_button.setFixedSize(120, 40)
        next_button.setStyleSheet("QPushButton { background-color: rgb(135, 153, 255); color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: rgb(145, 163, 255); }")
        next_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.install_location_page))
        button_layout.addWidget(next_button)

        right_LAYOUT.addLayout(button_layout)
        right_LAYOUT.addStretch()

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        return page

    def create_import_client_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        icon_label = QLabel()
        icon_path = os.path.join(self.base_path, "assets/icon/setup_other.png")
        pixmap = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        left_layout.addWidget(icon_label)

        title_label = QLabel("安装其他Client")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        left_layout.addWidget(title_label)

        desc_label = QLabel("导入压缩包格式的客户端文件")
        desc_label.setFont(QFont("Microsoft YaHei", 12))
        desc_label.setStyleSheet("color: #AAAAAA;")
        left_layout.addWidget(desc_label)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        import_button = QPushButton("导入客户端")
        import_button.setIcon(QIcon(os.path.join(self.base_path, "assets/icon/client_import.png")))
        import_button.setIconSize(QSize(24, 24))
        import_button.setStyleSheet("QPushButton { background-color: #404040; color: white; border: none; border-radius: 5px; font-size: 16px; padding: 10px; } QPushButton:hover { background-color: #505050; }")
        import_button.clicked.connect(self.import_client)
        right_layout.addWidget(import_button)

        self.client_file_label = QLabel("未选择文件")
        self.client_file_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        right_layout.addWidget(self.client_file_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        prev_button = QPushButton("上一步")
        prev_button.setFixedSize(120, 40)
        prev_button.setStyleSheet("QPushButton { background-color: #505050; color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: #606060; }")
        prev_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.install_page))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("下一步")
        next_button.setFixedSize(120, 40)
        next_button.setStyleSheet("QPushButton { background-color: rgb(135, 153, 255); color: white; font-size: 16px; border-radius: 8px; padding: 5px 15px; } QPushButton:hover { background-color: rgb(145, 163, 255); }")
        next_button.clicked.connect(self.check_and_switch_to_install_location)
        button_layout.addWidget(next_button)

        right_layout.addLayout(button_layout)
        right_layout.addStretch()

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        return page

    def create_install_location_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        icon_label = QLabel()
        icon_path = os.path.join(self.base_path, "assets", "icon", "lerio.png")
        pixmap = QPixmap(icon_path).scaled(100, 100, Qt.KeepAspectRatio)
        icon_label.setPixmap(pixmap)
        left_layout.addWidget(icon_label)

        title_label = QLabel("选择路径")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        left_layout.addWidget(title_label)

        subtitle_label = QLabel("选择一个路径以安装")
        subtitle_label.setFont(QFont("Microsoft YaHei", 12))
        subtitle_label.setStyleSheet("color: #AAAAAA;")
        left_layout.addWidget(subtitle_label)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        self.location_button_group = QButtonGroup(self)

        self.option1 = QRadioButton("163目录")
        self.option1.setFont(QFont("Microsoft YaHei", 14))
        self.option1.setStyleSheet("color: white;")
        self.option1.setChecked(True)
        self.location_button_group.addButton(self.option1)
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Netease\MCLauncher', 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, 'MinecraftBENeteasePath')
                option1_path_text = value
        except FileNotFoundError:
            option1_path_text = "未找到路径"
        self.option1_path = QLabel(option1_path_text)
        self.option1_path.setFont(QFont("Microsoft YaHei", 10))
        self.option1_path.setStyleSheet("color: #AAAAAA;")
        option1_layout = QHBoxLayout()
        option1_layout.addWidget(self.option1)
        option1_layout.addWidget(self.option1_path)
        option1_layout.addStretch()
        option1_widget = QWidget()
        option1_widget.setLayout(option1_layout)
        option1_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_layout.addWidget(option1_widget)

        self.option2 = QRadioButton("4399目录")
        self.option2.setFont(QFont("Microsoft YaHei", 14))
        self.option2.setStyleSheet("color: white;")
        self.location_button_group.addButton(self.option2)
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Netease\PC4399_MCLauncher', 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, 'MinecraftBENeteasePath')
                option2_path_text = value
        except FileNotFoundError:
            option2_path_text = "未找到路径"
        self.option2_path = QLabel(option2_path_text)
        self.option2_path.setFont(QFont("Microsoft YaHei", 10))
        self.option2_path.setStyleSheet("color: #AAAAAA;")
        option2_layout = QHBoxLayout()
        option2_layout.addWidget(self.option2)
        option2_layout.addWidget(self.option2_path)
        option2_layout.addStretch()
        option2_widget = QWidget()
        option2_widget.setLayout(option2_layout)
        option2_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_layout.addWidget(option2_widget)

        self.option3 = QRadioButton("自定义目录")
        self.option3.setFont(QFont("Microsoft YaHei", 14))
        self.option3.setStyleSheet("color: white;")
        self.location_button_group.addButton(self.option3)
        self.option3_path = QLabel("未选择路径")
        self.option3_path.setFont(QFont("Microsoft YaHei", 10))
        self.option3_path.setStyleSheet("color: #AAAAAA;")
        self.custom_path_button = QPushButton()
        folder_icon_path = os.path.join(self.base_path, "assets", "icon", "folder.png")
        self.custom_path_button.setIcon(QIcon(folder_icon_path))
        self.custom_path_button.setIconSize(QSize(24, 24))
        self.custom_path_button.setStyleSheet("QPushButton { background-color: #3D3D3D; border-radius: 5px; padding: 5px; } QPushButton:hover { background-color: #505050; }")
        self.custom_path_button.clicked.connect(self.select_custom_path)
        option3_layout = QHBoxLayout()
        option3_layout.addWidget(self.option3)
        option3_layout.addWidget(self.option3_path)
        option3_layout.addWidget(self.custom_path_button)
        option3_layout.addStretch()
        option3_widget = QWidget()
        option3_widget.setLayout(option3_layout)
        option3_widget.setStyleSheet("background-color: #3D3D3D; border-radius: 5px; padding: 10px;")
        right_layout.addWidget(option3_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(120, 40)  # 调整为与安装界面的“下一步”按钮相同大小
        cancel_button.setFont(QFont("Microsoft YaHei", 14))
        cancel_button.setStyleSheet("QPushButton { background-color: #505050; color: white; border: none; padding: 10px 20px; border-radius: 5px; } QPushButton:hover { background-color: #606060; }")
        cancel_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.install_page))
        button_layout.addWidget(cancel_button)

        install_button = QPushButton("确定")
        install_button.setFixedSize(120, 40)  # 调整为与安装界面的“下一步”按钮相同大小
        install_button.setFont(QFont("Microsoft YaHei", 14))
        install_button.setStyleSheet("QPushButton { background-color: #8799FF; color: white; border: none; padding: 10px 20px; border-radius: 5px; } QPushButton:hover { background-color: #97A9FF; }")
        install_button.clicked.connect(self.start_installation)
        button_layout.addWidget(install_button)

        right_layout.addLayout(button_layout)
        right_layout.addStretch()

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        self.custom_path = ""
        return page

    def create_install_progress_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        self.progress_widget = InstallProgressWidget(self, main_window=self)  # 传递 MainWindow 引用
        layout.addWidget(self.progress_widget)
        self.progress_widget.show()

        layout.addStretch()
        return page

    def create_install_complete_page(self):
        page = QWidget()
        self.install_complete_widget = InstallCompleteWidget(self)
        layout = QVBoxLayout(page)
        layout.addWidget(self.install_complete_widget)
        return page

    def switch_install_page(self):
        for i, radio in enumerate(self.radio_buttons):
            if radio.isChecked():
                if i == 0:
                    self.stacked_widget.setCurrentWidget(self.install_location_page)
                elif i == 1:
                    self.stacked_widget.setCurrentWidget(self.custom_setup_page)
                elif i == 2:
                    self.stacked_widget.setCurrentWidget(self.other_setup_page)
                break

    def check_and_switch_to_install_location(self):
        if not self.selected_client_path:
            self.show_toast("提示", "请先导入客户端文件！", "warning")
        else:
            self.stacked_widget.setCurrentWidget(self.install_location_page)

    def select_custom_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择安装路径")
        if path:
            self.custom_path = path
            self.option3_path.setText(path)

    def get_selected_path(self):
        if self.option1.isChecked():
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Netease\MCLauncher', 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, 'MinecraftBENeteasePath')
                    target_dir = os.path.join(value, "x64_mc", "data", "resource_packs")
                    if not os.path.exists(os.path.join(value, "x64_mc")):
                        target_dir = os.path.join(value, "windowsmc", "data", "resource_packs")
                    return target_dir
            except FileNotFoundError:
                self.show_toast("错误", "未找到163安装路径!", "error")
                return None
        elif self.option2.isChecked():
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Netease\PC4399_MCLauncher', 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, 'MinecraftBENeteasePath')
                    target_dir = os.path.join(value, "windowsmc", "data", "resource_packs")
                    if not os.path.exists(os.path.join(value, "windowsmc")):
                        target_dir = os.path.join(value, "x64_mc", "data", "resource_packs")
                    return target_dir
            except FileNotFoundError:
                self.show_toast("错误", "未找到4399安装路径!", "error")
                return None
        elif self.option3.isChecked():
            if not self.custom_path:
                self.show_toast("错误", "请先选择自定义路径!", "error")
                return None
            return os.path.join(self.custom_path, "data", "resource_packs")
        return None

    def start_installation(self):
        install_path = self.get_selected_path()
        if not install_path:
            print("No valid install path selected")
            return

        print("Switching to install_progress_page")
        self.stacked_widget.setCurrentWidget(self.install_progress_page)
        print(f"Current widget: {self.stacked_widget.currentWidget()}")
        self.progress_widget.start_progress()

        QTimer.singleShot(1200, lambda: self.perform_installation(install_path))

    def perform_installation(self, install_path):
        print(f"Starting installation at path: {install_path}")
        try:
            if not os.path.exists(install_path):
                os.makedirs(install_path)
                print(f"Created directory: {install_path}")

            if self.stacked_widget.currentWidget() == self.install_progress_page:
                print("Installing from install_progress_page")
                if self.option1.isChecked() or self.option2.isChecked() or self.option3.isChecked():
                    source_path = os.path.join(self.base_path, "assets", "client")
                    print(f"Copying from {source_path} to {install_path}")
                    shutil.copytree(source_path, install_path, dirs_exist_ok=True)
                    print("Copy completed")
            elif self.stacked_widget.currentWidget() == self.custom_setup_page:
                print("Installing from custom_setup_page")
                source_path = os.path.join(self.base_path, "assets", "client")
                for folder in ["vanilla", "vanilla_netease"]:
                    if not os.path.exists(os.path.join(install_path, folder)):
                        os.makedirs(os.path.join(install_path, folder))
                if self.install_options["textures"]:
                    shutil.copytree(os.path.join(source_path, "vanilla", "textures"), os.path.join(install_path, "vanilla", "textures"), dirs_exist_ok=True)
                if self.install_options["ui"]:
                    shutil.copytree(os.path.join(source_path, "vanilla_netease", "ui"), os.path.join(install_path, "vanilla_netease", "ui"), dirs_exist_ok=True)
                if self.install_options["texts"]:
                    shutil.copytree(os.path.join(source_path, "vanilla_netease", "texts"), os.path.join(install_path, "vanilla_netease", "texts"), dirs_exist_ok=True)
            elif self.stacked_widget.currentWidget() == self.other_setup_page and self.selected_client_path:
                print("Installing from other_setup_page")
                with zipfile.ZipFile(self.selected_client_path, 'r') as zip_ref:
                    for folder in ["vanilla", "vanilla_netease", "vanilla_base"]:
                        if folder in zip_ref.namelist():
                            zip_ref.extractall(install_path, members=[f for f in zip_ref.namelist() if f.startswith(folder)])
            print("Installation completed successfully")
            # 安装完成后直接跳转到安装完成页面
            self.installation_finished()
        except Exception as e:
            print(f"Error during installation: {e}")
            self.show_toast("错误", f"安装过程中发生错误: {e}", "error")

    def installation_finished(self):
        print("Switching to install_complete_page")
        self.stacked_widget.setCurrentWidget(self.install_complete_page)
        print(f"Current widget: {self.stacked_widget.currentWidget()}")
        QApplication.processEvents()

    def import_client(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择客户端文件", "", "压缩文件 (*.zip *.rar *.7z *.mclient)")
        if file_path:
            temp_dir = os.path.expandvars("%temp%")
            target_path = os.path.join(temp_dir, os.path.basename(file_path))
            shutil.copy(file_path, target_path)
            self.selected_client_path = target_path
            self.client_file_label.setText(os.path.basename(file_path))

    def show_toast(self, title, message, toast_type="tip"):
        toast = ToastNotification(self, title, message, toast_type)
        toast.show_toast()

    def import_plugin(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择插件", "", "ZIP 文件 (*.zip)")
        if file_path:
            self.save_plugin(file_path)
            self.load_plugins()

    def save_plugin(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                if 'manifest.json' not in zip_ref.namelist():
                    self.show_toast("错误", "插件包中缺少 manifest.json 文件", "error")
                    return
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    with zip_ref.open('manifest.json') as manifest_file:
                        manifest = json.load(manifest_file)
                        uuid = manifest['header']['uuid']
                        version = ".".join(map(str, manifest['header']['version']))
                existing_plugin_path = self.find_plugin_by_uuid(uuid)
                if existing_plugin_path:
                    existing_version = self.get_plugin_version(existing_plugin_path)
                    if self.compare_versions(version, existing_version) <= 0:
                        self.show_toast("提示", "已存在相同或更高版本的插件包", "warning")
                        return
                    else:
                        os.remove(existing_plugin_path)
                plugin_name = os.path.basename(file_path)
                target_path = os.path.join(self.plugin_path, plugin_name)
                shutil.copy(file_path, target_path)
                self.show_toast("提示", "插件已成功更新为最新版本", "tip")
        except Exception as e:
            self.show_toast("错误", f"处理插件时发生错误: {e}", "error")

    def find_plugin_by_uuid(self, uuid):
        if not os.path.exists(self.plugin_path):
            return None
        for file_name in os.listdir(self.plugin_path):
            if file_name.endswith(".zip"):
                file_path = os.path.join(self.plugin_path, file_name)
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        if 'manifest.json' in zip_ref.namelist():
                            with zip_ref.open('manifest.json') as manifest_file:
                                manifest = json.load(manifest_file)
                                if manifest['header']['uuid'] == uuid:
                                    return file_path
                except Exception as e:
                    print(f"Error checking plugin {file_name}: {e}")
        return None

    def get_plugin_version(self, plugin_path):
        with zipfile.ZipFile(plugin_path, 'r') as zip_ref:
            with zip_ref.open('manifest.json') as manifest_file:
                manifest = json.load(manifest_file)
                return ".".join(map(str, manifest['header']['version']))

    def compare_versions(self, version1, version2):
        v1 = list(map(int, version1.split(".")))
        v2 = list(map(int, version2.split(".")))
        return (v1 > v2) - (v1 < v2)

    def load_plugins(self):
        if not os.path.exists(self.plugin_path):
            os.makedirs(self.plugin_path)
            return
        for i in reversed(range(self.plugins_layout.count())):
            widget = self.plugins_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for file_name in os.listdir(self.plugin_path):
            if file_name.endswith(".zip"):
                file_path = os.path.join(self.plugin_path, file_name)
                self.process_plugin(file_path)

    def process_plugin(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                if 'manifest.json' not in zip_ref.namelist():
                    self.show_toast("错误", f"插件包 {file_path} 中缺少 manifest.json 文件", "error")
                    return
                with zip_ref.open('manifest.json') as manifest_file:
                    manifest = json.load(manifest_file)
                    name = manifest['header']['name']
                    description = manifest['header']['description']
                    icon_path = None
                    for file in zip_ref.namelist():
                        if file.endswith('icon.png'):
                            icon_path = zip_ref.extract(file, path=os.path.dirname(file_path))
                            break
                    if icon_path:
                        item = PluginItem(name, description, icon_path, manifest['header'].get('subpack', '').lower() == 'true', parent=self.plugins_widget, main_window=self)
                        self.plugins_layout.addWidget(item)
                    else:
                        self.show_toast("错误", f"插件包 {file_path} 中缺少图标文件 icon.png", "error")
        except Exception as e:
            self.show_toast("错误", f"处理插件 {file_path} 时发生错误: {e}", "error")

    def delete_plugin(self):
        checked_items = []
        for i in range(self.plugins_layout.count()):
            item = self.plugins_layout.itemAt(i).widget()
            if isinstance(item, PluginItem) and item.checkbox.isChecked():
                checked_items.append(item)
        if not checked_items:
            self.show_toast("提示", "没有勾选的插件项目！", "warning")
            return
        if len(checked_items) > 1:
            # 由于需要用户确认，这里暂时保留 QMessageBox，因为 Toast 无法处理交互式确认
            reply = QMessageBox.question(self, "提示", f"您选中了 {len(checked_items)} 个插件，确定要删除吗？", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        for item in checked_items:
            plugin_name = item.name_label.text()
            for file_name in os.listdir(self.plugin_path):
                if file_name.endswith(".zip"):
                    file_path = os.path.join(self.plugin_path, file_name)
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            if 'manifest.json' in zip_ref.namelist():
                                with zip_ref.open('manifest.json') as manifest_file:
                                    manifest = json.load(manifest_file)
                                    if manifest['header']['name'] == plugin_name:
                                        self.files_to_delete.append(file_path)
                                        break
                    except Exception as e:
                        print(f"处理插件文件时发生错误: {file_path}，错误: {e}")
            self.plugins_layout.removeWidget(item)
            item.deleteLater()

    def closeEvent(self, event):
        for file_path in self.files_to_delete:
            try:
                os.remove(file_path)
                print(f"成功删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件时发生错误: {file_path}，错误: {e}")
        event.accept()

    def confirm_kill_en(self):
        if self.radio_full_kill.isChecked():
            kill_type = "full_kill"
        else:
            kill_type = "simplified_kill"
        self.perform_kill(kill_type)

    def perform_kill(self, kill_type):
        appdata_path = os.path.expandvars("%appdata%")
        packcache_path = os.path.join(appdata_path, "MinecraftPE_Netease", "packcache")
        if not os.path.exists(packcache_path):
            self.show_toast("错误", "未找到MinecraftPE_Netease的packcache文件夹!", "warning")
            return
        if kill_type == "full_kill":
            files_to_delete = [
                "player.animation_controllers.json", "player.entity.json", "player.render_controllers.json",
                "player_firstperson.animation.json", "player.animation.json", "bow.player.json",
                "golden_sword.player.json", "netherite_sword.player.json", "stone_sword.player.json",
                "diamond_sword.player.json", "wooden_sword.player.json", "diamond_axe.json",
                "3d_items.json", "weapon_anxinglian_axe.animation.json", "weapon_battle_axe.animation.json",
                "weapon_lood_sword.animation.json", "weapon_double_end_sword.animation.json",
                "weapon_crystal_sword.animation.json", "weapon_deadwood_battle_axe.animation.json",
                "weapon_bone_sword.animation.json", "weapon_energy_sword.animation.json",
                "weapon_gouzhuangti_axe.animation.json", "weapon_holy_axe.animation.json",
                "weapon_lengguangshengjian_sword.json", "weapon_night_sword.animation.json",
                "weapon_mace_axe.animation.json", "weapon_lengguangzhanfu_axe.json",
                "weapon_lengguangzhandao_sword.json", "weapon_pink_heart.animation_axe.animation.json",
                "weapon_non_attack_sword.animation.json", "weapon_spear_sword.animation.json",
                "weapon_shengjian_sword.json", "weapon_xuanlingchi_sword.json",
                "weapon_xiedi_sword.animation.json", "weapon_wars_hammer_axe.geo.animation.json",
                "weapon_storm_sword.animation.json", "weapon_storm_hammer_axe.animation.json",
                "weapon_spikes_mace_axe.animation.json", "sword.json", "caidai.particle.json",
                "ec_hit.particle.json", "ghost.particle.json", "sweep.particle.json", "sound_definitions.json"
            ]
            for root, dirs, files in os.walk(packcache_path):
                for file in files:
                    if file in files_to_delete:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                        except PermissionError:
                            QMessageBox.warning(self, "错误", f"无法删除文件 {file_path},权限不足。")
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"删除文件 {file_path} 时发生错误:{e}")
            self.show_toast("提示", "布吉岛-全杀EN 完成", "tip")
        elif kill_type == "simplified_kill":
            self.delete_player_entity_json(packcache_path)
            self.show_toast("提示", "EaseCation-简杀EN 完成", "tip")

    def delete_player_entity_json(self, base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file == "player.entity.json":
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"已删除文件:{file_path}")
                    except PermissionError:
                        QMessageBox.warning(self, "错误", f"无法删除文件 {file_path},权限不足。")
                    except Exception as e:
                        QMessageBox.warning(self, "错误", f"删除文件 {file_path} 时发生错误:{e}")

    def change_plugin_path(self):
        new_path = QFileDialog.getExistingDirectory(self, "选择新的插件路径")
        if new_path:
            self.plugin_path = new_path
            self.plugin_path_input.setText(self.plugin_path)
            self.load_plugins()

    def toggle_apply_button(self):
        pass

def show_beta_verification():
    dialog = BetaVerificationDialog()
    if dialog.exec() == QDialog.Accepted:
        return True
    else:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if show_beta_verification():
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
