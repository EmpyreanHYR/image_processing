"""

诚挚感谢各位一起修改代码！
感受一下推送

"""
import sys
import cv2
import numpy as np
import os
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QListWidget, QRadioButton,
                             QButtonGroup, QScrollArea, QSlider, QSpinBox, QDialog,
                             QGridLayout, QCheckBox, QComboBox)

# 定义护眼模式颜色
eye_comfort_bg = "#FFF4E6"
eye_comfort_fg = "#6B4C3B"

# 定义浅色和深色模式颜色
light_bg = "#F0F0F0"
dark_bg = "#2E2E2E"
light_fg = "#333333"
dark_fg = "#FFFFFF"

# 定义样式表
DAY_STYLE = """
    QWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QListWidget {
        background-color: #ffffff;
        color: #000000;
    }
"""

NIGHT_STYLE = """
    QWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }
    QListWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }
    QScrollArea {
        background-color: #2e2e2e;
    }
"""

EYE_COMFORT_STYLE = f"""
    QWidget {{
        background-color: {eye_comfort_bg};
        color: #000000;
    }}
    QListWidget {{
        background-color: {eye_comfort_bg};
        color: #000000;
    }}
    QScrollArea {{
        background-color: {eye_comfort_bg};
    }}
"""

LIGHT_STYLE = f"""
    QWidget {{
        background-color: {light_bg};
        color: {light_fg};
    }}
    QListWidget {{
        background-color: {light_bg};
        color: {light_fg};
    }}
    QScrollArea {{
        background-color: {light_bg};
    }}
"""

DARK_STYLE = f"""
    QWidget {{
        background-color: {dark_bg};
        color: {dark_fg};
    }}
    QListWidget {{
        background-color: {dark_bg};
        color: {dark_fg};
    }}
    QScrollArea {{
        background-color: {dark_bg};
    }}
"""

BLUE_STYLE = """
    QWidget {
        background-color: #003366;
        color: #FFFFFF;
    }
    QListWidget {
        background-color: #003366;
        color: #FFFFFF;
    }
    QScrollArea {
        background-color: #003366;
    }
"""

GRAY_STYLE = """
    QWidget {
        background-color: #999999;
        color: #000000;
    }
    QListWidget {
        background-color: #999999;
        color: #000000;
    }
    QScrollArea {
        background-color: #999999;
    }
"""

WARM_YELLOW_STYLE = """
    QWidget {
        background-color: #FFF9C4;
        color: #000000;
    }
    QListWidget {
        background-color: #FFF9C4;
        color: #000000;
    }
    QScrollArea {
        background-color: #FFF9C4;
    }
"""

Green_STYLE = """
    QWidget {
        background-color: #C7EDCC;
        color: #000000;
    }
    QListWidget {
        background-color: #C7EDCC;
        color: #000000;
    }
    QScrollArea {
        background-color: #C7EDCC;
    }
"""
xrh_STYLE = """
    QWidget {
        background-color: #FAF9DE;
        color: #000000;
    }
    QListWidget {
        background-color: #FAF9DE;
        color: #000000;
    }
    QScrollArea {
        background-color: #FAF9DE;
    }
"""

qyh_STYLE = """
    QWidget {
        background-color: #FFF2E2;
        color: #000000;
    }
    QListWidget {
        background-color: #FFF2E2;
        color: #000000;
    }
    QScrollArea {
        background-color: #FFF2E2;
    }
"""
htl_STYLE = """
    QWidget {
        background-color: #DCE2F1;
        color: #000000;
    }
    QListWidget {
        background-color: #DCE2F1;
        color: #000000;
    }
    QScrollArea {
        background-color: #DCE2F1;
    }
"""

gjz_STYLE = """
    QWidget {
        background-color: #E9EBFE;
        color: #000000;
    }
    QListWidget {
        background-color: #E9EBFE;
        color: #000000;
    }
    QScrollArea {
        background-color: #E9EBFE;
    }
"""
qcl_STYLE = """
    QWidget {
        background-color: #E3EDCD;
        color: #000000;
    }
    QListWidget {
        background-color: #E3EDCD;
        color: #000000;
    }
    QScrollArea {
        background-color: #E3EDCD;
    }
"""
class RotationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('旋转角度设置')
        self.setModal(True)
        layout = QGridLayout()

        # 旋转角度设置
        self.angle_spin = QSpinBox()
        self.angle_spin.setRange(0, 360)
        self.angle_spin.setValue(90)
        layout.addWidget(QLabel('旋转角度:'), 0, 0)
        layout.addWidget(self.angle_spin, 0, 1)

        # 确定按钮
        self.ok_button = QPushButton('确定')
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, 1, 0, 1, 2)

        self.setLayout(layout)


class ImageProcessingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_mode = "day"
        self.current_image_path = None
        self.processed_image = None
        self.history = []
        self.redo_stack = []

    def initUI(self):
        self.setWindowTitle('多功能图片处理集成工具V1.0')
        self.setGeometry(100, 100, 1200, 800)

        # 新增模式切换按钮
        self.mode_btn = QPushButton('切换到夜间模式')
        self.mode_btn.clicked.connect(self.toggle_mode)

        self.eye_comfort_btn = QPushButton('切换到护眼模式')
        self.eye_comfort_btn.clicked.connect(self.toggle_eye_comfort_mode)

        self.light_mode_btn = QPushButton('切换到浅色模式')
        self.light_mode_btn.clicked.connect(self.toggle_light_mode)

        self.dark_mode_btn = QPushButton('切换到深色模式')
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)

        self.blue_mode_btn = QPushButton('切换到深蓝色模式')
        self.blue_mode_btn.clicked.connect(self.toggle_blue_mode)

        self.gray_mode_btn = QPushButton('切换到灰色模式')
        self.gray_mode_btn.clicked.connect(self.toggle_gray_mode)

        self.warm_yellow_mode_btn = QPushButton('切换到暖黄色模式')
        self.warm_yellow_mode_btn.clicked.connect(self.toggle_warm_yellow_mode)

        self.Green_mode_btn = QPushButton('切换到绿豆沙模式')
        self.Green_mode_btn.clicked.connect(self.toggle_Green_mode)

        self.xrh_mode_btn = QPushButton('切换到杏仁黄模式')
        self.xrh_mode_btn.clicked.connect(self.toggle_xrh_mode)

        self.qyh_mode_btn = QPushButton('切换到秋叶褐模式')
        self.qyh_mode_btn.clicked.connect(self.toggle_qyh_mode)

        self.htl_mode_btn = QPushButton('切换到海天蓝模式')
        self.htl_mode_btn.clicked.connect(self.toggle_htl_mode)

        self.gjz_mode_btn = QPushButton('切换到葛巾紫模式')
        self.gjz_mode_btn.clicked.connect(self.toggle_gjz_mode)

        self.qcl_mode_btn = QPushButton('切换到青草绿模式')
        self.qcl_mode_btn.clicked.connect(self.toggle_qcl_mode)

        main_layout = QHBoxLayout()

        # 左侧面板
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.mode_btn)
        left_layout.addWidget(self.eye_comfort_btn)
        left_layout.addWidget(self.light_mode_btn)
        left_layout.addWidget(self.dark_mode_btn)
        left_layout.addWidget(self.blue_mode_btn)
        left_layout.addWidget(self.gray_mode_btn)
        left_layout.addWidget(self.warm_yellow_mode_btn)
        left_layout.addWidget(self.Green_mode_btn)
        left_layout.addWidget(self.xrh_mode_btn)
        left_layout.addWidget(self.qyh_mode_btn)
        left_layout.addWidget(self.htl_mode_btn)
        left_layout.addWidget(self.gjz_mode_btn)
        left_layout.addWidget(self.qcl_mode_btn)
        self.load_btn = QPushButton('请选择图片导入')
        self.load_btn.clicked.connect(self.load_image)
        self.load_folder_btn = QPushButton('请选择文件夹路径导入')
        self.load_folder_btn.clicked.connect(self.load_folder)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.display_selected_image)

        left_layout.addWidget(self.load_btn)
        left_layout.addWidget(self.load_folder_btn)
        left_layout.addWidget(self.file_list)

        # 添加帮助和关于按钮
        self.help_btn = QPushButton('帮助')
        self.help_btn.clicked.connect(self.show_help)
        left_layout.addWidget(self.help_btn)

        self.about_btn = QPushButton('关于')
        self.about_btn.clicked.connect(self.show_about)
        left_layout.addWidget(self.about_btn)

        # 设置初始样式
        self.setStyleSheet(DAY_STYLE)

        # 中间面板
        mid_layout = QVBoxLayout()
        self.original_label = QLabel('原始图像')
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(500, 400)

        self.processed_label = QLabel('处理后图像')
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(500, 400)

        # 创建滚动区域
        original_scroll = QScrollArea()
        original_scroll.setWidget(self.original_label)
        original_scroll.setWidgetResizable(True)
        original_scroll.setMinimumSize(520, 420)

        processed_scroll = QScrollArea()
        processed_scroll.setWidget(self.processed_label)
        processed_scroll.setWidgetResizable(True)
        processed_scroll.setMinimumSize(520, 420)

        mid_layout.addWidget(original_scroll)
        mid_layout.addWidget(processed_scroll)

        # 右侧面板
        right_layout = QVBoxLayout()
        self.single_radio = QRadioButton('单个图像')
        self.batch_radio = QRadioButton('已导入的所有图片')
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.single_radio)
        self.radio_group.addButton(self.batch_radio)
        self.single_radio.setChecked(True)

        right_layout.addWidget(self.single_radio)
        right_layout.addWidget(self.batch_radio)

        # 处理按钮
        self.rotate_btn = QPushButton('旋转')
        self.rotate_btn.clicked.connect(self.show_rotation_dialog)
        self.denoise_btn = QPushButton('去噪')
        self.denoise_btn.clicked.connect(self.apply_denoise)
        self.hist_eq_btn = QPushButton('直方图均衡化')
        self.hist_eq_btn.clicked.connect(self.apply_hist_eq)
        self.sharpen_btn = QPushButton('锐化')
        self.sharpen_btn.clicked.connect(self.apply_sharpen)

        # 噪点强度控制
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(0, 160)
        self.noise_slider.setValue(0)
        self.noise_slider.setTickInterval(10)

        self.add_noise_btn = QPushButton('应用高斯噪点')
        self.add_noise_btn.clicked.connect(self.apply_noise)

        # 亮度控制
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)

        self.add_brightness_btn = QPushButton('调整亮度')
        self.add_brightness_btn.clicked.connect(self.apply_brightness)

        # 双向生成亮度
        self.inverse_brightness_check = QCheckBox('生成亮度降低图像')

        # 随机亮度生成
        self.random_brightness_check = QCheckBox('随机亮度生成')

        self.stats_btn = QPushButton('显示统计信息')
        self.stats_btn.clicked.connect(self.show_statistics)

        # 在右侧面板添加以下新控件
        self.blur_combobox = QComboBox()
        self.blur_combobox.addItem("无模糊")
        self.blur_combobox.addItem("高斯模糊")
        self.blur_combobox.addItem("中值模糊")
        self.blur_combobox.addItem("均值模糊")

        self.blur_radius_slider = QSlider(Qt.Horizontal)
        self.blur_radius_slider.setRange(1, 20)
        self.blur_radius_slider.setValue(5)
        self.blur_radius_slider.setTickInterval(2)

        self.sharpen_intensity = QSlider(Qt.Horizontal)
        self.sharpen_intensity.setRange(1, 10)
        self.sharpen_intensity.setValue(3)

        self.sharpen_kernel = QSlider(Qt.Horizontal)
        self.sharpen_kernel.setRange(3, 15)
        self.sharpen_kernel.setValue(3)
        self.sharpen_kernel.setSingleStep(2)

        # 在右侧面板添加边缘检测控件
        self.edge_detection_combobox = QComboBox()
        self.edge_detection_combobox.addItem("无边缘检测")
        self.edge_detection_combobox.addItem("Canny边缘检测")
        self.edge_detection_combobox.addItem("Sobel边缘检测")

        # 添加滤镜控件
        self.filter_combobox = QComboBox()
        self.filter_combobox.addItem("无滤镜")
        self.filter_combobox.addItem("黑白色调")
        self.filter_combobox.addItem("复古色调")
        self.filter_combobox.addItem("冷色调")
        self.filter_combobox.currentIndexChanged.connect(self.apply_filter)

        # 镜像翻转选项
        self.horizontal_flip_check = QCheckBox('水平翻转')
        self.vertical_flip_check = QCheckBox('垂直翻转')
        self.origin_flip_check = QCheckBox('原点翻转')
        self.flip_btn = QPushButton('应用镜像翻转')
        self.flip_btn.clicked.connect(self.apply_flip)
        # 添加控件到右侧面板
        right_content = QWidget()
        right_content.setLayout(right_layout)
        right_layout.addWidget(self.rotate_btn)
        right_layout.addWidget(self.denoise_btn)
        right_layout.addWidget(self.hist_eq_btn)
        right_layout.addWidget(self.sharpen_btn)
        right_layout.addWidget(QLabel('模糊类型:'))
        right_layout.addWidget(self.blur_combobox)
        right_layout.addWidget(QLabel('模糊半径:'))
        right_layout.addWidget(self.blur_radius_slider)
        right_layout.addWidget(QLabel('锐化强度:'))
        right_layout.addWidget(self.sharpen_intensity)
        right_layout.addWidget(QLabel('锐化核大小:'))
        right_layout.addWidget(self.sharpen_kernel)
        right_layout.addWidget(QLabel('边缘检测:'))
        right_layout.addWidget(self.edge_detection_combobox)
        right_layout.addWidget(self.add_noise_btn)
        right_layout.addWidget(self.noise_slider)
        right_layout.addWidget(self.add_brightness_btn)
        right_layout.addWidget(self.brightness_slider)
        right_layout.addWidget(self.inverse_brightness_check)
        right_layout.addWidget(self.random_brightness_check)
        right_layout.addWidget(QLabel('滤镜:'))
        right_layout.addWidget(self.filter_combobox)
        right_layout.addWidget(self.horizontal_flip_check)
        right_layout.addWidget(self.vertical_flip_check)
        right_layout.addWidget(self.origin_flip_check)
        right_layout.addWidget(self.flip_btn)
        right_layout.addWidget(self.stats_btn)
        right_layout.addWidget(QLabel('颜色替换:'))
        self.color_replace_combobox = QComboBox()
        self.color_replace_combobox.addItem("无颜色替换")
        self.color_replace_combobox.addItem("红色替换白色")
        self.color_replace_combobox.addItem("蓝色替换白色")
        self.color_replace_combobox.addItem("绿色替换白色")
        self.color_replace_combobox.addItem("黄色替换白色")
        self.color_replace_combobox.addItem("橙色替换白色")
        self.color_replace_combobox.addItem("紫色替换白色")
        self.color_replace_combobox.addItem("黑色替换白色")
        self.color_replace_combobox.addItem("灰色替换白色")
        self.color_replace_combobox.addItem("粉色替换白色")
        self.color_replace_combobox.addItem("棕色替换白色")
        self.color_replace_combobox.addItem("金色替换白色")
        self.color_replace_combobox.addItem("银色替换白色")
        self.color_replace_combobox.addItem("青色替换白色")
        self.color_replace_combobox.addItem("深蓝色替换白色")
        self.color_replace_combobox.addItem("浅蓝色替换白色")
        self.color_replace_combobox.addItem("藏青色替换白色")
        self.color_replace_combobox.addItem("桃色替换白色")
        self.color_replace_combobox.addItem("天蓝色替换白色")
        self.color_replace_combobox.addItem("橄榄色替换白色")
        self.color_replace_combobox.addItem("浅绿色替换白色")

        right_layout.addWidget(self.color_replace_combobox)

        self.color_replace_btn = QPushButton('应用颜色替换')
        self.color_replace_btn.clicked.connect(self.apply_color_replace)
        right_layout.addWidget(self.color_replace_btn)

        self.reset_btn = QPushButton('恢复原图')
        self.reset_btn.clicked.connect(self.reset_image)
        right_layout.addWidget(self.reset_btn)

        self.export_btn = QPushButton('导出')
        self.export_btn.clicked.connect(self.export_image)
        right_layout.addWidget(self.export_btn)

        # 添加撤销和反撤销按钮
        self.undo_btn = QPushButton('撤销')
        self.undo_btn.clicked.connect(self.undo)
        right_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton('反撤销')
        self.redo_btn.clicked.connect(self.redo)
        right_layout.addWidget(self.redo_btn)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(right_content)

        self.blur_combobox.currentIndexChanged.connect(self.apply_blur)
        self.blur_radius_slider.valueChanged.connect(self.apply_blur)
        self.sharpen_intensity.valueChanged.connect(self.apply_sharpen)
        self.sharpen_kernel.valueChanged.connect(self.apply_sharpen)
        self.edge_detection_combobox.currentIndexChanged.connect(self.apply_edge_detection)

        # 设置主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(mid_layout, 2)
        main_layout.addWidget(scroll_area, 1)

        self.setLayout(main_layout)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '',
                                                   'Images (*.png *.jpg *.jpeg *.bmp)')
        if file_path:
            self.current_image_path = file_path
            self.processed_image = cv2.imread(file_path)  # 记录原图
            self.display_image(file_path, self.original_label)

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder_path:
            self.file_list.clear()
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self.file_list.addItem(os.path.join(folder_path, file_name))

    def display_image(self, file_path, label):
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        label.resize(pixmap.size())

    def display_selected_image(self, item):
        self.current_image_path = item.text()
        self.display_image(self.current_image_path, self.original_label)

    def show_rotation_dialog(self):
        dialog = RotationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            angle = dialog.angle_spin.value()
            self.rotate_image(angle)

    def rotate_image(self, angle):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        height, width = self.processed_image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.processed_image = cv2.warpAffine(self.processed_image, rotation_matrix, (width, height))
        self.save_and_display(self.processed_image)

    def apply_denoise(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        self.processed_image = cv2.fastNlMeansDenoisingColored(self.processed_image)
        self.save_and_display(self.processed_image)

    def apply_hist_eq(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        img_yuv = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        self.processed_image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        self.save_and_display(self.processed_image)

    def apply_sharpen(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        self.processed_image = cv2.filter2D(self.processed_image, -1, kernel)
        self.save_and_display(self.processed_image)

    def apply_noise(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        noise_strength = self.noise_slider.value() / 1000
        self.processed_image = self.add_gaussian_noise(self.processed_image, noise_strength)
        self.save_and_display(self.processed_image)

    def add_gaussian_noise(self, image, strength):
        row, col, _ = image.shape
        gauss = np.random.normal(0, strength, (row, col, 3))
        noisy = np.clip(image + gauss * 255, 0, 255)
        return noisy.astype(np.uint8)

    def apply_brightness(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        brightness_value = self.brightness_slider.value()

        if self.random_brightness_check.isChecked():
            brightness_value += np.random.randint(-10, 10)  # 随机波动

        if self.inverse_brightness_check.isChecked():
            brightness_value = -brightness_value  # 反向调整亮度

        self.processed_image = self.adjust_brightness(self.processed_image, brightness_value)
        self.save_and_display(self.processed_image)

    def adjust_brightness(self, image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + value, 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def apply_flip(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        flipped_image = self.processed_image.copy()  # 复制当前处理的图像

        if self.horizontal_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, 1)

        if self.vertical_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, 0)

        if self.origin_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, -1)

        self.processed_image = flipped_image  # 更新当前处理图像
        self.save_and_display(self.processed_image)

    def toggle_mode(self):
        """切换白天/夜间模式"""
        if self.current_mode == "day":
            self.setStyleSheet(NIGHT_STYLE)
            self.current_mode = "night"
            self.mode_btn.setText('切换到白天模式')
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.mode_btn.setText('切换到夜间模式')

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_eye_comfort_mode(self):
        """切换护眼模式"""
        if self.current_mode != "eye_comfort":
            # 切换为护眼模式
            self.setStyleSheet(EYE_COMFORT_STYLE)
            self.current_mode = "eye_comfort"
            self.eye_comfort_btn.setText("切换到正常模式")
        else:
            # 切换为正常模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.eye_comfort_btn.setText("切换到护眼模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_light_mode(self):
        """切换浅色模式"""
        if self.current_mode != "light":
            # 切换为浅色模式
            self.setStyleSheet(LIGHT_STYLE)
            self.current_mode = "light"
            self.light_mode_btn.setText("切换到其他模式")
        else:
            # 切换为默认模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.light_mode_btn.setText("切换到浅色模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_dark_mode(self):
        """切换深色模式"""
        if self.current_mode != "dark":
            # 切换为深色模式
            self.setStyleSheet(DARK_STYLE)
            self.current_mode = "dark"
            self.dark_mode_btn.setText("切换到其他模式")
        else:
            # 切换为默认模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.dark_mode_btn.setText("切换到深色模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_blue_mode(self):
        """切换深蓝色模式"""
        if self.current_mode != "blue":
            # 切换为深蓝色模式
            self.setStyleSheet(BLUE_STYLE)
            self.current_mode = "blue"
            self.blue_mode_btn.setText("切换到其他模式")
        else:
            # 切换为默认模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.blue_mode_btn.setText("切换到深蓝色模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_gray_mode(self):
        """切换灰色模式"""
        if self.current_mode != "gray":
            # 切换为灰色模式
            self.setStyleSheet(GRAY_STYLE)
            self.current_mode = "gray"
            self.gray_mode_btn.setText("切换到其他模式")
        else:
            # 切换为默认模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.gray_mode_btn.setText("切换到灰色模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_warm_yellow_mode(self):
        """切换暖黄色模式"""
        if self.current_mode != "warm_yellow":
            # 切换为暖黄色模式
            self.setStyleSheet(WARM_YELLOW_STYLE)
            self.current_mode = "warm_yellow"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            # 切换为默认模式
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到暖黄色模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_Green_mode(self):
        if self.current_mode != "Green":
            self.setStyleSheet(Green_STYLE)
            self.current_mode = "Green"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到绿豆沙模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_xrh_mode(self):
        if self.current_mode != "xrh":
            self.setStyleSheet(xrh_STYLE)
            self.current_mode = "xrh"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到杏仁黄模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_qyh_mode(self):
        if self.current_mode != "qyh":
            self.setStyleSheet(qyh_STYLE)
            self.current_mode = "qyh"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到秋叶褐模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_htl_mode(self):
        if self.current_mode != "htl":
            self.setStyleSheet(htl_STYLE)
            self.current_mode = "htl"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到海天蓝模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_gjz_mode(self):
        if self.current_mode != "gjz":
            self.setStyleSheet(gjz_STYLE)
            self.current_mode = "gjz"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到葛巾紫模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def toggle_qcl_mode(self):
        if self.current_mode != "qcl":
            self.setStyleSheet(qcl_STYLE)
            self.current_mode = "qcl"
            self.warm_yellow_mode_btn.setText("切换到其他模式")
        else:
            self.setStyleSheet(DAY_STYLE)
            self.current_mode = "day"
            self.warm_yellow_mode_btn.setText("切换到青草绿模式")

        # 更新所有子部件的样式
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(self.styleSheet())

        # 更新图像显示区域的背景色
        self.update_label_background()

    def save_and_display(self, processed_image):
        self.processed_image = processed_image
        # 转换OpenCV BGR图像为Qt可显示的RGB格式
        height, width, channel = self.processed_image.shape
        bytes_per_line = 3 * width
        q_img = QImage(self.processed_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)

        # 根据当前模式设置标签背景
        if self.current_mode == "night":
            bg_color = "#2e2e2e"
        elif self.current_mode == "eye_comfort":
            bg_color = eye_comfort_bg
        elif self.current_mode == "light":
            bg_color = light_bg
        elif self.current_mode == "dark":
            bg_color = dark_bg
        elif self.current_mode == "blue":
            bg_color = "#003366"
        elif self.current_mode == "gray":
            bg_color = "#999999"
        elif self.current_mode == "warm_yellow":
            bg_color = "#FFF9C4"
        elif self.current_mode == "Green":
            bg_color = "#C7EDCC"
        elif self.current_mode == "xrh":
            bg_color = "#FAF9DE"
        elif self.current_mode == "qyh":
            bg_color = "#FFF2E2"
        elif self.current_mode == "htl":
            bg_color = "#DCE2F1"
        elif self.current_mode == "gjz":
            bg_color = "#E9EBFE"
        elif self.current_mode == "qcl":
            bg_color = "#E3EDCD"
        else:
            bg_color = "#ffffff"

        self.processed_label.setStyleSheet(f"background-color: {bg_color};")

        self.processed_label.setPixmap(pixmap)
        self.processed_label.resize(pixmap.size())

    def export_image(self):
        if self.processed_image is not None:
            # 扩展支持的文件格式
            file_types = (
                "PNG文件 (*.png);;"
                "JPEG文件 (*.jpg *.jpeg);;"
                "BMP文件 (*.bmp);;"
                "GIF文件 (*.gif);;"
                "TIFF文件 (*.tif *.tiff);;"
                "所有文件 (*)"
            )

            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                '保存图像',
                '',
                file_types
            )

            if file_path:
                try:
                    # 转换OpenCV图像到PIL格式
                    img_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(img_rgb)

                    # 根据选择的文件类型确定保存格式
                    if selected_filter.startswith("JPEG"):
                        if not file_path.lower().endswith(('.jpg', '.jpeg')):
                            file_path += '.jpg'
                        pil_image.save(file_path, "JPEG", quality=95)
                    elif selected_filter.startswith("PNG"):
                        if not file_path.lower().endswith('.png'):
                            file_path += '.png'
                        pil_image.save(file_path, "PNG")
                    elif selected_filter.startswith("BMP"):
                        if not file_path.lower().endswith('.bmp'):
                            file_path += '.bmp'
                        pil_image.save(file_path, "BMP")
                    elif selected_filter.startswith("GIF"):
                        if not file_path.lower().endswith('.gif'):
                            file_path += '.gif'
                        pil_image.convert("P").save(file_path, "GIF")  # GIF需要调色板模式
                    elif selected_filter.startswith("TIFF"):
                        if not file_path.lower().endswith(('.tif', '.tiff')):
                            file_path += '.tif'
                        pil_image.save(file_path, "TIFF")
                    else:  # 默认保存为PNG
                        if '.' not in os.path.basename(file_path):
                            file_path += '.png'
                        pil_image.save(file_path)

                    print(f"图像已成功保存为 {file_path}")
                except Exception as e:
                    print(f"保存失败: {str(e)}")

    def get_image_statistics(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            return None
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        min_val = np.min(grayscale)
        max_val = np.max(grayscale)
        mean_val = np.mean(grayscale)
        std_val = np.std(grayscale)
        return min_val, max_val, mean_val, std_val

    def show_statistics(self):
        if not hasattr(self, 'current_image_path'):
            return
        stats = self.get_image_statistics(self.current_image_path)
        if stats is None:
            return
        min_pixel, max_pixel, mean_pixel, std_pixel = stats

        # 创建统计信息对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('图像统计信息')
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"最小像素值: {min_pixel}"))
        layout.addWidget(QLabel(f"最大像素值: {max_pixel}"))
        layout.addWidget(QLabel(f"平均像素值: {mean_pixel:.2f}"))
        layout.addWidget(QLabel(f"标准差: {std_pixel:.2f}"))

        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def apply_blur(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        blur_type = self.blur_combobox.currentText()
        ksize = self.blur_radius_slider.value() * 2 + 1  # 确保为奇数

        if blur_type == "高斯模糊":
            blurred = cv2.GaussianBlur(self.processed_image, (ksize, ksize), 0)
        elif blur_type == "中值模糊":
            blurred = cv2.medianBlur(self.processed_image, ksize)
        elif blur_type == "均值模糊":
            blurred = cv2.blur(self.processed_image, (ksize, ksize))
        else:
            return

        self.processed_image = blurred
        self.save_and_display(blurred)

    def apply_sharpen(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        intensity = self.sharpen_intensity.value()
        ksize = self.sharpen_kernel.value() // 2 * 2 + 1  # 确保为奇数

        # 创建自定义锐化核
        kernel = np.ones((ksize, ksize), np.float32) * (-1)
        center = ksize // 2
        kernel[center, center] = ksize ** 2 * intensity - 1

        sharpened = cv2.filter2D(self.processed_image, -1, kernel)
        self.processed_image = np.clip(sharpened, 0, 255).astype(np.uint8)
        self.save_and_display(self.processed_image)

    def apply_edge_detection(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        edge_type = self.edge_detection_combobox.currentText()
        if edge_type == "无边缘检测":
            self.save_and_display(self.processed_image)
            return

        # 转换为灰度图像
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)

        if edge_type == "Canny边缘检测":
            # 自动计算阈值
            median = np.median(gray)
            lower = int(max(0, 0.7 * median))
            upper = int(min(255, 1.3 * median))
            edges = cv2.Canny(gray, lower, upper)
        elif edge_type == "Sobel边缘检测":
            # Sobel算子
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges = cv2.magnitude(sobel_x, sobel_y)
            edges = np.uint8(edges)

        # 转换为彩色图像显示
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.processed_image = edges_color
        self.save_and_display(edges_color)

    def reset_image(self):
        if self.current_image_path:
            # 保存当前状态到撤销栈
            self.history.append(self.processed_image.copy())
            self.redo_stack.clear()

            self.processed_image = cv2.imread(self.current_image_path)  # 重新加载原图
            self.save_and_display(self.processed_image)

    def apply_filter(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        filter_type = self.filter_combobox.currentText()
        filtered_image = self.processed_image.copy()

        if filter_type == "黑白色调":
            # 应用黑白滤镜
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)
        elif filter_type == "复古色调":
            # 应用复古滤镜
            kernel = np.array([[0.393, 0.769, 0.189],
                               [0.349, 0.686, 0.168],
                               [0.272, 0.534, 0.131]])
            filtered_image = cv2.transform(filtered_image, kernel)
            filtered_image = np.clip(filtered_image, 0, 255)
        elif filter_type == "冷色调":
            # 应用冷色调滤镜（增强蓝色通道）
            blue_tint = np.array([1.2, 1.0, 1.0])  # 增强蓝色通道
            filtered_image = filtered_image * blue_tint
            filtered_image = np.clip(filtered_image, 0, 255)

        self.processed_image = filtered_image.astype(np.uint8)
        self.save_and_display(filtered_image)

    def undo(self):
        if self.history:
            # 弹出栈中的最后一个状态并应用
            self.redo_stack.append(self.processed_image.copy())  # 保存当前图像到反撤销栈
            self.processed_image = self.history.pop()  # 恢复到上一个状态
            self.save_and_display(self.processed_image)

    def redo(self):
        if self.redo_stack:
            # 弹出反撤销栈中的最后一个状态并应用
            self.history.append(self.processed_image.copy())  # 保存当前图像到撤销栈
            self.processed_image = self.redo_stack.pop() # 恢复到反撤销的状态
            self.save_and_display(self.processed_image)

    # 新增颜色替换方法
    def apply_color_replace(self):
        if self.processed_image is None:
            return

        # 保存当前状态到撤销栈
        self.history.append(self.processed_image.copy())
        self.redo_stack.clear()

        # 获取颜色替换类型
        color_type = self.color_replace_combobox.currentText()
        if color_type == "无颜色替换":
            return

        # 将OpenCV图像转换为PIL格式
        img = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)

        # 定义颜色映射
        color_map = {
            "红色替换白色": (255, 0, 0),
            "蓝色替换白色": (0, 0, 255),
            "绿色替换白色": (0, 255, 0),
            "黄色替换白色": (255, 255, 0),
            "橙色替换白色": (255, 165, 0),
            "紫色替换白色": (128, 0, 128),
            "黑色替换白色": (0, 0, 0),
            "灰色替换白色": (128, 128, 128),
            "粉色替换白色": (255, 192, 203),
            "棕色替换白色": (139, 69, 19),
            "金色替换白色": (255, 215, 0),
            "银色替换白色": (192, 192, 192),
            "青色替换白色": (0, 255, 255),
            "深蓝色替换白色": (0, 0, 139),
            "浅蓝色替换白色": (173, 216, 230),
            "藏青色替换白色": (0, 0, 128),
            "桃色替换白色": (255, 218, 185),
            "天蓝色替换白色": (135, 206, 235),
            "橄榄色替换白色": (128, 128, 0),
            "浅绿色替换白色": (144, 238, 144)
        }

        # 执行颜色替换
        target_color = color_map.get(color_type, (255, 0, 0))
        pil_img = self.change_white_to_color(pil_img, target_color)

        # 转换回OpenCV格式
        self.processed_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        self.save_and_display(self.processed_image)

    def change_white_to_color(self, pil_img, target_color):
        """将白色替换为目标颜色"""
        img = pil_img.convert("RGB")
        pixels = img.load()

        for i in range(img.width):
            for j in range(img.height):
                r, g, b = pixels[i, j]
                # 检测接近白色的像素（RGB值均大于200）
                if r > 200 and g > 200 and b > 200:
                    pixels[i, j] = target_color
        return img

    def update_label_background(self):
        if self.current_mode == "night":
            bg_color = "#2e2e2e"
        elif self.current_mode == "eye_comfort":
            bg_color = eye_comfort_bg
        elif self.current_mode == "light":
            bg_color = light_bg
        elif self.current_mode == "dark":
            bg_color = dark_bg
        elif self.current_mode == "blue":
            bg_color = "#003366"
        elif self.current_mode == "gray":
            bg_color = "#999999"
        elif self.current_mode == "warm_yellow":
            bg_color = "#FFF9C4"
        elif self.current_mode == "Green":
            bg_color = "#C7EDCC"
        elif self.current_mode == "xrh":
            bg_color = "#FAF9DE"
        elif self.current_mode == "qyh":
            bg_color = "#FFF2E2"
        elif self.current_mode == "htl":
            bg_color = "#DCE2F1"
        elif self.current_mode == "gjz":
            bg_color = "#E9EBFE"
        elif self.current_mode == "qcl":
            bg_color = "#E3EDCD"
        else:
            bg_color = "#ffffff"

        self.original_label.setStyleSheet(f"background-color: {bg_color};")
        self.processed_label.setStyleSheet(f"background-color: {bg_color};")

    def show_help(self):
        # 创建帮助对话框
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle('帮助内容')
        help_layout = QVBoxLayout()

        # 添加帮助内容
        help_content = """
        图像导入:
          点击“请选择图片导入”按钮，选择单张图片进行导入。
          点击“请选择文件夹路径导入”按钮，选择一个文件夹，批量导入该文件夹下的所有支持格式的图片。

        图像显示:
          左侧为原始图像显示区域，显示导入的原始图像。
          右侧为处理后图像显示区域，显示对原始图像进行各种处理后的结果。

        图像处理功能:
          旋转：点击“旋转”按钮，在弹出的对话框中设置旋转角度，点击“确定”对图像进行旋转操作。
          去噪：点击“去噪”按钮，对图像进行降噪处理，减少图像中的噪声。
          直方图均衡化：点击“直方图均衡化”按钮，对图像进行直方图均衡化处理，增强图像的对比度。
          锐化：点击“锐化”按钮，对图像进行锐化处理，使图像边缘更加清晰。
          模糊：在“模糊类型”下拉菜单中选择模糊类型，拖动“模糊半径”滑块设置模糊程度，对图像进行模糊处理。
          边缘检测：在“边缘检测”下拉菜单中选择边缘检测类型，对图像进行边缘检测。
          添加高斯噪点：拖动滑块调整噪点强度，点击“应用高斯噪点”按钮，为图像添加高斯噪声。
          调整亮度：拖动滑块调整亮度值，勾选“生成亮度降低图像”可反向调整亮度，勾选“随机亮度生成”可添加随机亮度波动，点击“调整亮度”按钮应用亮度调整。
          滤镜：在“滤镜”下拉菜单中选择滤镜类型，对图像应用不同色调的滤镜效果。
          镜像翻转：勾选“水平翻转”、“垂直翻转”或“原点翻转”，点击“应用镜像翻转”按钮，对图像进行相应的翻转操作。
          颜色替换：在“颜色替换”下拉菜单中选择颜色替换类型，点击“应用颜色替换”按钮，将图像中的白色替换为目标颜色。
          恢复原图：点击“恢复原图”按钮，将处理后的图像恢复为原始图像。
          导出：点击“导出”按钮，选择保存路径和文件格式，将处理后的图像保存到本地。
          撤销与反撤销：点击“撤销”按钮，撤销上一步操作；点击“反撤销”按钮，恢复上一步撤销的操作。

        主题切换:
          点击相应的主题切换按钮，可在不同主题模式之间切换，包括白天模式、夜间模式、护眼模式、浅色模式、深色模式、深蓝色模式、灰色模式、暖黄色模式、绿豆沙模式、杏仁黄模式、秋叶褐模式、海天蓝模式、葛巾紫模式、青草绿模式等。
        """
        help_label = QLabel(help_content)
        help_label.setWordWrap(True)  # 自动换行
        help_layout.addWidget(help_label)

        # 添加关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(help_dialog.accept)
        help_layout.addWidget(close_btn)

        help_dialog.setLayout(help_layout)
        help_dialog.exec_()

    def show_about(self):
        # 创建关于对话框
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle('关于本工具')
        about_layout = QVBoxLayout()
        about_content = """
        简介:
          本工具是一款集多种图像处理功能于一体的集成工具，旨在为用户提供便捷、高效的图片处理体验。用户可以通过本工具轻松实现图像的导入、显示、处理以及结果保存等操作。

        功能特点:
          丰富的图像处理功能：支持旋转、去噪、直方图均衡化、锐化、模糊、边缘检测、添加噪点、调整亮度等多种图像处理操作。
          多样的主题模式：提供多种主题模式切换，满足不同用户的视觉需求，包括白天模式、夜间模式、护眼模式等。
          便捷的图像导入与导出：支持从本地导入单张图片或批量导入文件夹中的图片，处理后的图像可保存为多种常见格式。
          直观的用户界面：采用简洁明了的界面设计，操作方便，易于上手。

        技术信息:
          开发框架：基于PyQt5开发，利用其丰富的UI组件构建用户界面。
          图像处理库：采用OpenCV进行图像处理操作，确保处理效率和效果。
          适用平台：可在支持Python的多个操作系统上运行，包括Windows、Linux、MacOS等。
        """
        about_label = QLabel(about_content)
        about_label.setWordWrap(True)  # 自动换行
        about_layout.addWidget(about_label)

        # 添加关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(about_dialog.accept)
        about_layout.addWidget(close_btn)

        about_dialog.setLayout(about_layout)
        about_dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessingApp()
    ex.show()
    sys.exit(app.exec_())