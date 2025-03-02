import sys
import os
import zipfile
import json
import shutil
import winreg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QGroupBox, QRadioButton, QStackedWidget, QMessageBox, QDialog, QListWidget, QTextEdit, QScrollArea, QCheckBox
)
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt, QSize


class PluginItem(QWidget):
    def __init__(self, name, description, icon_path, has_subpack, parent=None, main_window=None):
        super().__init__(parent)
        self.has_subpack = has_subpack
        self.main_window = main_window  # 保存主窗口的引用
        self.initUI(name, description, icon_path)

    def initUI(self, name, description, icon_path):
        layout = QHBoxLayout(self)  # 使用水平布局
        layout.setContentsMargins(10, 0, 0, 0)  # 设定布局的边距
        layout.setSpacing(4)  # 设定布局中控件间的间距
        self.setFixedSize(500, 70)  # 调整固定大小以适应内容

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 30px; }")  # 复选框大小
        self.checkbox.stateChanged.connect(self.onCheckboxClicked)  # 绑定状态改变事件
        layout.addWidget(self.checkbox)  # 复选框在顶部

        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio)  # 调整图标大小
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(50, 50)  # 固定图标大小
        layout.addWidget(self.icon_label)  # 图标在复选框右侧

        self.mix_text_box = QWidget()  # 创建一个Widget作为混合文本框
        mix_text_layout = QVBoxLayout(self.mix_text_box)  # 使用垂直布局

        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        mix_text_layout.addWidget(self.name_label)  # 名称在混合文本框中
        mix_text_layout.setContentsMargins(0, 0, 0, 15)  # 设置名称和描述之间的边距

        self.description_label = QLabel(description)
        self.description_label.setFont(QFont("Microsoft YaHei", 10))
        mix_text_layout.addWidget(self.description_label)  # 描述在名称下方

        layout.addWidget(self.mix_text_box)  # 将混合文本框添加到水平布局中

        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)  # 删除控件的边距

        # 设置布局的拉伸因子，确保文本框大小固定
        layout.setStretchFactor(self.mix_text_box, 1)

        self.setStyleSheet("border: 1px solid transparent;")  # 默认无边框

    def onCheckboxClicked(self, state):
        if self.main_window:  # 检查是否传入了主窗口
            self.main_window.toggle_apply_button()
        if state == Qt.Checked:
            self.setStyleSheet("border: 2px solid white;")  # 选中时添加白色边框
        else:
            self.setStyleSheet("border: 1px solid transparent;")  # 未选中时无边框

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.checkbox.setChecked(not self.checkbox.isChecked())
            self.onCheckboxClicked(self.checkbox.checkState())


class UserAgreementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户协议&更新日志")
        self.setGeometry(200, 200, 800, 500)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Microsoft YaHei", 10))
        self.text_edit.setText("""
        <h2>用户协议 | User Agreement</h2>
        <p>协议版本 | Protocol version: V1.0.2</p>
        <p>协议更新时间 | Protocol date: 2025/2/21</p>
        <p>欢迎您使用LerioClient!在使用LerioClient之前,请您仔细阅读并理解本用户使用协议(以下简称“本协议”)。</p>
        <p>您一旦使用客户端,即表示您已经充分阅读、理解并同意遵守本协议的所有条款和条件。</p>
        <p>除非你已阅读并接受本协议所有条款,否则你将无权下载、获取、使用LerioClient的任何内容。</p>
        <p>以下内容是您与LerioClient的使用协议:</p>
        <h3>| 使用许可</h3>
        <p>1.1 当前版本LerioClient采用署名标示(BY)- 非商业性使用(NC)- 禁止演绎(ND)国际许可协议 CC 4.0 协议进行许可(以下简称 "BY-NC-ND CC 协议")</p>
        <h3>| 免责声明</h3>
        <p>2.1 在遵守 BY-NC-ND CC 协议的基础下,LerioClient及其原作者不承担用户使用LerioClient引起的任何直接或间接的损失责任。</p>
        <h3>| 适用范围</h3>
        <p>3.1 此协议适用于任何版本的LerioClient (包含官方发行的LerioClient扩展,不属于官方发行的LerioClient扩展插件的使用协议因当由扩展插件作者决定)</p>
        <p>3.2 除特殊声明外,当前版本LerioClient均遵守 BY-NC-ND CC 协议,协议内容可在该网址查看:<a href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh">https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh</a></p>
        <h3>| 主要规定</h3>
        <p>4.1 如果您未满十八周岁,请在以监护人陪同下阅读本协议</p>
        <p>4.2 该协议条款的所有解释权归作者所有</p>
        <p>4.3 用户禁止修改、引用、衍生本协议且以任何形式发布至互联网</p>
        <p>4.4 不得谎称自己是LerioClient的原作者</p>
        <p>4.5 不得隐去、删除LerioClient中的任意版权信息</p>
        <p>4.6 未经作者同意的情况下,禁止作为任何商业用途,不得将其进行转让、出售或者用于其他商业用途</p>
        <p>4.7 未经作者同意的情况下,禁止使用LeiroClient内的源代码或媒体文件进行修改、引用、洐生代码</p>
        <p>4.8 您所制作的LerioClient自定义包的所有权归您所有,LerioClient及其原作者不承担使用、分发自定义包引起的任何责任损失</p>
        <p>4.9 您在使用LerioClient产品时应遵守国家法律法规、社会公共利益和公共道德,并承担因违反本协议而产生的一切后果</p>
        <h3>| 转载规定</h3>
        <p>5.1 未经作者同意的情况下,禁止转载至互联网</p>
        <p>5.2 搬运需要标注原作者的署名</p>
        <h3>| 分享规定</h3>
        <p>6.1 除非本协议或原作者明确禁止,用户有权将LeiroClient分享至社交群组或他人</p>
        <p>6.2 用户将LeiroClient在平台 (非社交媒体群组) 以相同的形式公开发布,将其视为转载,需要按照上方转载规定获得作者本人的许可</p>
        <p>6.3 用户在分享LeiroClient时,应当遵守本协议的规定</p>
        <h3>| 协议变更</h3>
        <p>7.1 LerioClient的原作者有权对本协议进行修改,您应定期查阅并了解最新的协议内容。如果您不同意相关变更,应停止使用LeiroClient</p>
        <p>7.2 以最新版本的协议为主</p>
        <h3>| 其他</h3>
        <p>8.1 本协议将在LeiroClient原作者所属居住地区签订,当发生任何分岐或争议时,双方应当友好协商解决；若无法通过友好协商解决,任意一方均可以提交争议至本协议签订地有管辖权的人民法院处理</p>
        <h2>更新日志 | Update Log</h2>
        <h3>客户端版本 | Client version: V2.0.5.24</h3>
        <p>修改Addons插件页面</p>
        <p>侧边栏新增设置与关于选项</p>
        <p>为侧边栏按钮新增图标</p>
        <p>修复部分已知BUG</p>
        <p>TIP: Addons的部分功能的开发暂未完成,请等待后续更新</p>
        <hr>
        """)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        self.accept_button = QPushButton("同意")
        self.accept_button.clicked.connect(self.accept)
        self.accept_button.setFixedHeight(50)  # 增加按钮高度
        self.accept_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(135, 153, 255); /* 按钮背景颜色 */
                font-size: 16px; /* 字体大小 */
                padding: 10px; /* 内边距 */
            }
            QPushButton:hover {
                background-color: rgb(65, 183, 55); /* 鼠标悬停时的背景颜色 */
            }
        """)

        self.reject_button = QPushButton("不同意")
        self.reject_button.clicked.connect(self.reject)
        self.reject_button.setFixedHeight(50)  # 增加按钮高度
        self.reject_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(50, 50, 50); /* 按钮背景颜色 */
                font-size: 16px; /* 字体大小 */
                padding: 10px; /* 内边距 */
            }
            QPushButton:hover {
                background-color: rgb(250, 230, 230); /* 鼠标悬停时的背景颜色 */
            }
        """)

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.reject_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class PluginDialog(QDialog):
    def __init__(self, selected_plugins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件选择")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("您已选择以下插件:")
        layout.addWidget(self.label)

        self.plugin_list = QListWidget()
        for plugin in selected_plugins:
            self.plugin_list.addItem(plugin)
        layout.addWidget(self.plugin_list)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lerio Client Release 2.0.5.24")
        self.setGeometry(100, 100, 800, 400)
        self.setFixedSize(800, 400)

        # 初始化主窗口的中心部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 初始化主布局，并将其存储为实例变量
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 确保主布局没有边距

        # 初始化侧边栏
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(5, 0, 0, 200)  # 设置侧边栏边距
        sidebar.setSpacing(0)

        # 创建一个 QWidget 容器用于侧边栏
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setStyleSheet("""
            background-color: rgb(20, 20, 20);  /* 设置背景颜色 */
            border-right: 10px solid rgb(20, 20, 20);  /* 右侧延伸10像素 */
        """)
        sidebar_widget.setFixedWidth(130)  # 设置侧边栏宽度（根据按钮大小调整）

        # 获取根目录路径并存储为类属性
        self.base_path = os.path.dirname(os.path.abspath(__file__))

        # 初始化侧边栏按钮
        self.install_button = QPushButton("安装")
        self.install_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "setup.png")))
        self.install_button.setIconSize(QSize(28, 28))
        self.install_button.setFixedSize(120, 40)
        self.install_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")

        self.plugin_button = QPushButton("插件")
        self.plugin_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "addons.png")))
        self.plugin_button.setIconSize(QSize(28, 28))
        self.plugin_button.setFixedSize(120, 40)
        self.plugin_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")

        self.tools_button = QPushButton("工具")
        self.tools_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "tools.png")))
        self.tools_button.setIconSize(QSize(28, 28))
        self.tools_button.setFixedSize(120, 40)
        self.tools_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")

        self.settings_button = QPushButton("设置")
        self.settings_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "settings.png")))
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(120, 40)
        self.settings_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")

        self.about_button = QPushButton("关于")
        self.about_button.setIcon(QIcon(os.path.join(self.base_path, "assets", "icon", "about.png")))
        self.about_button.setIconSize(QSize(24, 24))
        self.about_button.setFixedSize(120, 40)
        self.about_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")

        sidebar.addWidget(self.install_button)
        sidebar.addWidget(self.plugin_button)
        sidebar.addWidget(self.tools_button)
        sidebar.addWidget(self.settings_button)
        sidebar.addWidget(self.about_button)

        # 将侧边栏容器添加到主布局
        self.main_layout.addWidget(sidebar_widget)

        # 初始化主内容区域
        self.main_content = QStackedWidget()
        self.main_layout.addWidget(self.main_content)

        # 初始化各个 Tab 的内容
        self.init_tabs()

        # 设置按钮点击事件
        self.install_button.clicked.connect(lambda: self.switch_tab(self.install_tab))
        self.plugin_button.clicked.connect(lambda: self.switch_tab(self.plugins_tab))
        self.tools_button.clicked.connect(lambda: self.switch_tab(self.tools_tab))
        self.settings_button.clicked.connect(lambda: self.switch_tab(self.settings_tab))  # 绑定到设置页面
        self.about_button.clicked.connect(lambda: self.switch_tab(self.about_tab))

    def init_tabs(self):
        # 初始化安装 Tab
        self.install_tab = QWidget()
        install_layout = QVBoxLayout(self.install_tab)
        install_label = QLabel("✨ Lerio Client\n by ZNi")
        install_label.setFont(QFont("Microsoft YaHei", 20))
        install_layout.addWidget(install_label)

        options = QGroupBox("安装目录选项")
        options_layout = QVBoxLayout()
        self.option1 = QRadioButton("163")
        self.option1.setChecked(True)
        self.option2 = QRadioButton("4399")
        self.option3 = QRadioButton("自定义")
        self.custom_button = QPushButton("选择路径")
        self.custom_button.clicked.connect(self.select_custom_path)
        self.custom_button.setFixedWidth(100)

        self.option1_value = self.read_reg_value(r'Software\Netease\MCLauncher')
        self.option2_value = self.read_reg_value(r'Software\Netease\PC4399_MCLauncher')

        if self.option1_value is None:
            self.option1_value = "未找到路径"
            self.option1.setEnabled(False)
        if self.option2_value is None:
            self.option2_value = "未找到路径"
            self.option2.setEnabled(False)

        self.option1_label = QLabel(f"路径: {self.option1_value}")
        self.option2_label = QLabel(f"路径: {self.option2_value}")
        self.custom_label = QLabel("未选择路径")

        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.option3)
        custom_layout.addWidget(self.custom_button)
        custom_layout.addStretch()

        options_layout.addWidget(self.option1)
        options_layout.addWidget(self.option1_label)
        options_layout.addWidget(self.option2)
        options_layout.addWidget(self.option2_label)
        options_layout.addLayout(custom_layout)
        options_layout.addWidget(self.custom_label)
        options.setLayout(options_layout)
        install_layout.addWidget(options)

        install_button = QPushButton("安装")
        install_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
        install_button.clicked.connect(self.start_installation)
        install_layout.addWidget(install_button)

        # 初始化插件 Tab
        self.plugins_tab = QWidget()
        plugins_layout = QVBoxLayout(self.plugins_tab)
        self.plugins_label = QLabel("Addons")
        self.plugins_label.setFont(QFont("Microsoft YaHei", 24))

        # 定义图标路径
        delete_icon_path = os.path.join(self.base_path, "assets", "icon", "delete.png")
        settings_icon_path = os.path.join(self.base_path, "assets", "icon", "plugin_setting.png")  # 更新图标路径
        import_icon_path = os.path.join(self.base_path, "assets", "icon", "import.png")

        # 创建按钮并设置图标
        self.import_button = QPushButton()
        self.import_button.setIcon(QIcon(import_icon_path))
        self.import_button.setIconSize(QSize(24, 24))  # 设置图标大小
        self.import_button.setStyleSheet("background-color: transparent; border: none; padding: 0px;")  # 设置透明背景
        self.import_button.clicked.connect(self.import_plugin)  # 绑定导入按钮点击事件
        self.import_button.setToolTip("导入")  # 添加提示

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(delete_icon_path))
        self.delete_button.setIconSize(QSize(32, 32))  # 设置图标大小
        self.delete_button.setStyleSheet("background-color: transparent; border: none; padding: 0px;")  # 设置透明背景
        self.delete_button.clicked.connect(self.delete_plugin)  # 绑定删除按钮的点击事件
        self.delete_button.setEnabled(False)  # 初始状态禁用
        self.delete_button.setToolTip("删除")  # 添加提示

        self.plugin_setting_button = QPushButton()  # 修改键名为 plugin_setting_button
        self.plugin_setting_button.setIcon(QIcon(settings_icon_path))  # 更新图标路径
        self.plugin_setting_button.setIconSize(QSize(24, 24))  # 设置图标大小
        self.plugin_setting_button.setStyleSheet("background-color: transparent; border: none; padding: 0px;")  # 设置透明背景
        self.plugin_setting_button.setToolTip("插件设置")  # 添加提示

        # 创建水平布局并右对齐按钮
        control_layout = QHBoxLayout()
        control_layout.addStretch()  # 添加伸展因子以右对齐
        control_layout.addWidget(self.plugin_setting_button)  # 更新引用新键名
        control_layout.addWidget(self.delete_button)
        control_layout.addWidget(self.import_button)

        # 将按钮布局与标题布局合并
        plugins_title_layout = QHBoxLayout()
        plugins_title_layout.addWidget(self.plugins_label)
        plugins_title_layout.addLayout(control_layout)  # 将按钮布局添加到标题布局中
        plugins_layout.addLayout(plugins_title_layout)

        # 创建滚动区域
        self.plugins_scroll_area = QScrollArea()
        self.plugins_scroll_area.setWidgetResizable(True)  # 确保滚动区域可以调整大小
        self.plugins_widget = QWidget()  # 插件列表的容器
        self.plugins_layout = QVBoxLayout(self.plugins_widget)  # 插件列表的布局
        self.plugins_layout.addStretch()  # 添加伸展因子以填充空白
        self.plugins_scroll_area.setWidget(self.plugins_widget)  # 将插件列表容器设置为滚动区域的部件
        plugins_layout.addWidget(self.plugins_scroll_area)  # 将滚动区域添加到插件 Tab 的布局中

        self.next_button = QPushButton("下一步")
        self.next_button.setStyleSheet("background-color: rgb(135, 153, 255); font-size: 16px; padding: 10px;")
        self.next_button.setEnabled(True)
        plugins_layout.addWidget(self.next_button)

        # 初始化工具 Tab
        self.tools_tab = QWidget()
        tools_layout = QVBoxLayout(self.tools_tab)
        tools_label = QLabel("✨ 杀EN \n 杀EN前请确认已下载服务器资源包")
        tools_label.setFont(QFont("Microsoft YaHei", 20))
        tools_layout.addWidget(tools_label)

        options = QGroupBox("杀EN选项")
        options_layout = QVBoxLayout()
        self.radio_full_kill = QRadioButton("全杀-布吉岛")
        self.radio_simplified_kill = QRadioButton("简杀-EaseCation")
        self.radio_full_kill.setChecked(True)

        font = QFont("Microsoft YaHei", 18)
        self.radio_full_kill.setFont(font)
        self.radio_simplified_kill.setFont(font)

        options_layout.addWidget(self.radio_full_kill)
        options_layout.addWidget(self.radio_simplified_kill)
        options.setLayout(options_layout)
        tools_layout.addWidget(options)

        self.kill_en_button = QPushButton("确定")
        self.kill_en_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
        self.kill_en_button.clicked.connect(self.confirm_kill_en)
        tools_layout.addWidget(self.kill_en_button)

        # 初始化设置 Tab
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)
        settings_label = QLabel("✨ 设置")
        settings_label.setFont(QFont("Microsoft YaHei", 20))
        settings_layout.addWidget(settings_label)
        settings_layout.addWidget(QLabel("设置功能尚待开发"))

        # 初始化关于 Tab
        self.about_tab = QWidget()
        about_layout = QVBoxLayout(self.about_tab)

        # 添加图标
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)  # 图标居中
        self.icon_label.setScaledContents(False)  # 图标随窗口大小调整
        self.icon_label.setPixmap(QPixmap(os.path.join(self.base_path, "assets", "icon", "lerio.png")))  # 加载图标
        about_layout.addWidget(self.icon_label)

        # 添加标题
        about_label = QLabel("About Lerio Client")
        about_label.setFont(QFont("Microsoft YaHei", 20))
        about_label.setAlignment(Qt.AlignCenter)  # 标题居中
        about_layout.addWidget(about_label)

        # 添加内容
        about_content = QLabel("Lerio Client Beta\nVersion 2.0.5.24\nDeveloper ZNi")
        about_content.setFont(QFont("Microsoft YaHei", 16))
        about_content.setAlignment(Qt.AlignCenter)  # 内容居中
        about_layout.addWidget(about_content)

        # 将所有 Tab 添加到 main_content 中
        self.main_content.addWidget(self.install_tab)
        self.main_content.addWidget(self.plugins_tab)
        self.main_content.addWidget(self.tools_tab)
        self.main_content.addWidget(self.settings_tab)
        self.main_content.addWidget(self.about_tab)

        # 默认显示安装 Tab
        self.main_content.setCurrentWidget(self.install_tab)

        self.update_button_style()

        # 在初始化时加载插件
        self.load_plugins()

    def switch_tab(self, tab):
        self.main_content.setCurrentWidget(tab)
        self.update_button_style()

    def update_button_style(self):
        current_tab = self.main_content.currentWidget()
        if current_tab == self.install_tab:
             self.install_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
             self.plugin_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.tools_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.settings_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.about_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
        elif current_tab == self.plugins_tab:
             self.install_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.plugin_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
             self.tools_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.settings_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.about_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
        elif current_tab == self.tools_tab:
             self.install_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.plugin_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.tools_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
             self.settings_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.about_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
        elif current_tab == self.settings_tab:
             self.install_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.plugin_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.tools_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.settings_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")
             self.about_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
        elif current_tab == self.about_tab:
             self.install_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.plugin_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.tools_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.settings_button.setStyleSheet("background-color:rgb(110, 114, 114); font-size: 16px; padding: 10px;")
             self.about_button.setStyleSheet("background-color:rgb(135, 153, 255); font-size: 16px; padding: 10px;")

    def start_installation(self):
        selected_option = None
        if self.option1.isChecked():
             selected_option = self.option1_value
        elif self.option2.isChecked():
             selected_option = self.option2_value
        elif self.option3.isChecked():
             selected_option = self.cstmPath

        if not selected_option:
             QMessageBox.warning(self, "提示", "请选择一个安装选项!")
             return

        source_dir = os.path.join(self.base_path, "assets", "data")
        if not os.path.exists(source_dir):
             QMessageBox.warning(self, "提示", "当前目录下没有找到 data 文件夹!")
             return

        try:
             if self.option3.isChecked():
                 target_dir = selected_option
             else:
                 target_dir = os.path.join(selected_option, "x64_mc")
                 if not os.path.exists(target_dir):
                     target_dir = os.path.join(selected_option, "windowsmc")

             shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
             print(f"安装完成,文件已复制到 {target_dir}")
        except Exception as e:
             QMessageBox.warning(self, "错误", f"安装过程中出现错误:{e}")
             return

        QMessageBox.information(self, "提示", "安装完成!")

    def import_plugin(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择插件", "", "ZIP 文件 (*.zip)")
        if file_path:
             self.save_plugin(file_path)
             self.load_plugins()  # 重新加载插件

    def save_plugin(self, file_path):
        appdata_path = os.path.expandvars("%appdata%")
        lerio_client_path = os.path.join(appdata_path, "LerioClient")
        if not os.path.exists(lerio_client_path):
             os.makedirs(lerio_client_path)

        try:
             with zipfile.ZipFile(file_path, 'r') as zip_ref:
                 if 'manifest.json' not in zip_ref.namelist():
                     QMessageBox.warning(self, "错误", "插件包中缺少 manifest.json 文件")
                     return

                 with zip_ref.open('manifest.json') as manifest_file:
                     manifest = json.load(manifest_file)
                     uuid = manifest['header']['uuid']
                     version = ".".join(map(str, manifest['header']['version']))  # 将版本号数组转换为字符串

                 existing_plugin_path = self.find_plugin_by_uuid(uuid)

                 if existing_plugin_path:
                     existing_version = self.get_plugin_version(existing_plugin_path)
                     if self.compare_versions(version, existing_version) <= 0:
                         QMessageBox.warning(self, "提示", "已存在相同或更高版本的插件包")
                         return
                     else:
                         os.remove(existing_plugin_path)  # 删除旧插件

                 plugin_name = os.path.basename(file_path)
                 target_path = os.path.join(lerio_client_path, plugin_name)
                 shutil.copy(file_path, target_path)
                 QMessageBox.information(self, "提示", "插件已成功更新为最新版本")
        except Exception as e:
             QMessageBox.warning(self, "错误", f"处理插件时发生错误: {e}")

    def find_plugin_by_uuid(self, uuid):
        appdata_path = os.path.expandvars("%appdata%")
        lerio_client_path = os.path.join(appdata_path, "LerioClient")

        if not os.path.exists(lerio_client_path):
             return None

        for file_name in os.listdir(lerio_client_path):
             if file_name.endswith(".zip"):
                 file_path = os.path.join(lerio_client_path, file_name)
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
        appdata_path = os.path.expandvars("%appdata%")
        lerio_client_path = os.path.join(appdata_path, "LerioClient")

        if not os.path.exists(lerio_client_path):
             os.makedirs(lerio_client_path)
             return

        for i in reversed(range(self.plugins_layout.count())):
             widget = self.plugins_layout.itemAt(i).widget()
             if widget:
                 widget.deleteLater()

        for file_name in os.listdir(lerio_client_path):
             if file_name.endswith(".zip"):
                 file_path = os.path.join(lerio_client_path, file_name)
                 self.process_plugin(file_path)

    def process_plugin(self, file_path):
         try:
             with zipfile.ZipFile(file_path, 'r') as zip_ref:
                 if 'manifest.json' not in zip_ref.namelist():
                     QMessageBox.warning(self, "错误", f"插件包 {file_path} 中缺少 manifest.json 文件")
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
                         item.checkbox.stateChanged.connect(self.toggle_apply_button)
                     else:
                         QMessageBox.warning(self, "错误", f"插件包 {file_path} 中缺少图标文件 icon.png")
         except Exception as e:
             QMessageBox.warning(self, "错误", f"处理插件 {file_path} 时发生错误: {e}")

    def toggle_apply_button(self):
         has_checked = any(
             isinstance(item, PluginItem) and item.checkbox.isChecked()
             for item in self.plugins_layout.children()
         )
         self.delete_button.setEnabled(has_checked)  # 更新删除按钮的状态

    def delete_plugin(self):
         checked_items = [item for item in self.plugins_layout.children() if isinstance(item, PluginItem) and item.checkbox.isChecked()]
         if not checked_items:
             QMessageBox.warning(self, "提示", "没有选中的插件项目！")
             return

         for item in checked_items:
             self.plugins_layout.removeWidget(item)
             item.deleteLater()
         self.toggle_apply_button()

    def read_reg_value(self, path):
         try:
             with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as key:
                 value, _ = winreg.QueryValueEx(key, 'MinecraftBENeteasePath')
                 return value
         except FileNotFoundError:
             return None

    def select_custom_path(self):
         self.cstmPath = QFileDialog.getExistingDirectory(self, "选择路径")
         if self.cstmPath:
             self.custom_label.setText(f"路径: {self.cstmPath}")
         else:
             self.custom_label.setText("未选择路径")

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
             QMessageBox.warning(self, "错误", "未找到MinecraftPE_Netease的packcache文件夹!")
             return

         if kill_type == "full_kill":
             files_to_delete = [
                 "player.animation_controllers.json",
                 "player.entity.json",
                 "player.render_controllers.json",
                 "player_firstperson.animation.json",
                 "player.animation.json",
                 "bow.player.json",
                 "golden_sword.player.json",
                 "netherite_sword.player.json",
                 "stone_sword.player.json",
                 "diamond_sword.player.json",
                 "wooden_sword.player.json",
                 "diamond_axe.json",
                 "3d_items.json",
                 "weapon_anxinglian_axe.animation.json",
                 "weapon_battle_axe.animation.json",
                 "weapon_lood_sword.animation.json",
                 "weapon_double_end_sword.animation.json",
                 "weapon_crystal_sword.animation.json",
                 "weapon_deadwood_battle_axe.animation.json",
                 "weapon_bone_sword.animation.json",
                 "weapon_energy_sword.animation.json",
                 "weapon_gouzhuangti_axe.animation.json",
                 "weapon_holy_axe.animation.json",
                 "weapon_lengguangshengjian_sword.json",
                 "weapon_night_sword.animation.json",
                 "weapon_mace_axe.animation.json",
                 "weapon_lengguangzhanfu_axe.json",
                 "weapon_lengguangzhandao_sword.json",
                 "weapon_pink_heart.animation_axe.animation.json",
                 "weapon_non_attack_sword.animation.json",
                 "weapon_spear_sword.animation.json",
                 "weapon_shengjian_sword.json",
                 "weapon_xuanlingchi_sword.json",
                 "weapon_xiedi_sword.animation.json",
                 "weapon_wars_hammer_axe.geo.animation.json",
                 "weapon_storm_sword.animation.json",
                 "weapon_storm_hammer_axe.animation.json",
                 "weapon_spikes_mace_axe.animation.json",
                 "sword.json",
                 "caidai.particle.json",
                 "ec_hit.particle.json",
                 "ghost.particle.json",
                 "sweep.particle.json",
                 "sound_definitions.json"
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
             QMessageBox.information(self, "提示", "全杀操作完成!")
         elif kill_type == "simplified_kill":
             self.delete_player_entity_json(packcache_path)
             QMessageBox.information(self, "提示", "简杀操作完成!")

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


def show_user_agreement():
    dialog = UserAgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return True
    else:
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if show_user_agreement():
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)