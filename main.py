"""

诚挚感谢各位一起修改代码！

"""


import sys
import cv2
import numpy as np
import os
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QListWidget, QRadioButton,
                             QButtonGroup, QScrollArea, QSlider, QSpinBox, QDialog,
                             QGridLayout, QCheckBox, QComboBox)


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
        self.current_image_path = None  # 当前加载的原图路径
        self.processed_image = None  # 存储当前处理后的图像（numpy 数组）

    def initUI(self):
        self.setWindowTitle('多功能图片处理集成工具')
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()

        # 左侧面板
        left_layout = QVBoxLayout()
        self.load_btn = QPushButton('请选择图片导入')
        self.load_btn.clicked.connect(self.load_image)
        self.load_folder_btn = QPushButton('请选择文件夹路径导入')
        self.load_folder_btn.clicked.connect(self.load_folder)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.display_selected_image)

        left_layout.addWidget(self.load_btn)
        left_layout.addWidget(self.load_folder_btn)
        left_layout.addWidget(self.file_list)

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

        # 镜像翻转选项
        self.horizontal_flip_check = QCheckBox('水平翻转')
        self.vertical_flip_check = QCheckBox('垂直翻转')
        self.origin_flip_check = QCheckBox('原点翻转')
        self.flip_btn = QPushButton('应用镜像翻转')
        self.flip_btn.clicked.connect(self.apply_flip)
        # 添加控件到右侧面板
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
        right_layout.addWidget(self.add_noise_btn)
        right_layout.addWidget(self.noise_slider)
        right_layout.addWidget(self.add_brightness_btn)
        right_layout.addWidget(self.brightness_slider)
        right_layout.addWidget(self.inverse_brightness_check)
        right_layout.addWidget(self.random_brightness_check)
        right_layout.addWidget(self.horizontal_flip_check)
        right_layout.addWidget(self.vertical_flip_check)
        right_layout.addWidget(self.origin_flip_check)
        right_layout.addWidget(self.flip_btn)
        right_layout.addWidget(self.stats_btn)

        self.reset_btn = QPushButton('恢复原图')
        self.reset_btn.clicked.connect(self.reset_image)
        right_layout.addWidget(self.reset_btn)

        self.export_btn = QPushButton('导出')
        self.export_btn.clicked.connect(self.export_image)
        right_layout.addWidget(self.export_btn)

        # 连接信号
        self.blur_combobox.currentIndexChanged.connect(self.apply_blur)
        self.blur_radius_slider.valueChanged.connect(self.apply_blur)
        self.sharpen_intensity.valueChanged.connect(self.apply_sharpen)
        self.sharpen_kernel.valueChanged.connect(self.apply_sharpen)

        # 设置主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(mid_layout, 2)
        main_layout.addLayout(right_layout, 1)

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
        # 加载图片并获取原始大小
        pixmap = QPixmap(file_path)

        # 获取QLabel的当前尺寸
        label_width = label.width()
        label_height = label.height()

        # 将图片按比例缩放，保持宽高比
        scaled_pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 设置缩放后的图片到标签
        label.setPixmap(scaled_pixmap)
        label.setFixedSize(scaled_pixmap.size())  # 设置QLabel大小与图像大小一致

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

        height, width = self.processed_image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.processed_image = cv2.warpAffine(self.processed_image, rotation_matrix, (width, height))
        self.save_and_display(self.processed_image)

    def apply_denoise(self):
        if self.processed_image is None:
            return

        self.processed_image = cv2.fastNlMeansDenoisingColored(self.processed_image)
        self.save_and_display(self.processed_image)

    def apply_hist_eq(self):
        if self.processed_image is None:
            return

        img_yuv = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        self.processed_image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        self.save_and_display(self.processed_image)

    def apply_sharpen(self):
        if self.processed_image is None:
            return

        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        self.processed_image = cv2.filter2D(self.processed_image, -1, kernel)
        self.save_and_display(self.processed_image)

    def apply_noise(self):
        if self.processed_image is None:
            return

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

        flipped_image = self.processed_image.copy()  # 复制当前处理的图像

        if self.horizontal_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, 1)

        if self.vertical_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, 0)

        if self.origin_flip_check.isChecked():
            flipped_image = cv2.flip(flipped_image, -1)

        self.processed_image = flipped_image  # 更新当前处理图像
        self.save_and_display(self.processed_image)

    def save_and_display(self, processed_image):
        self.processed_image = processed_image  # 更新当前处理图像
        processed_image_path = 'processed_image.png'
        cv2.imwrite(processed_image_path, self.processed_image)
        self.display_image(processed_image_path, self.processed_label)

    def export_image(self):
        if hasattr(self, 'current_image_path'):
            file_path, _ = QFileDialog.getSaveFileName(self, '保存处理后图像', '',
                                                       'Images (*.png *.jpg *.jpeg *.bmp)')
            if file_path:
                image = cv2.imread('processed_image.png')

                # 确保数据是 8-bit，并去除 Alpha 通道
                if image.dtype != np.uint8:
                    image = cv2.convertScaleAbs(image)
                if image.shape[-1] == 4:  # 移除 Alpha 通道
                    image = image[:, :, :3]

                cv2.imwrite(file_path, image)

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

        intensity = self.sharpen_intensity.value()
        ksize = self.sharpen_kernel.value() // 2 * 2 + 1  # 确保为奇数

        # 创建自定义锐化核
        kernel = np.ones((ksize, ksize), np.float32) * (-1)
        center = ksize // 2
        kernel[center, center] = ksize ** 2 * intensity - 1

        sharpened = cv2.filter2D(self.processed_image, -1, kernel)
        self.processed_image = np.clip(sharpened, 0, 255).astype(np.uint8)
        self.save_and_display(self.processed_image)

    def reset_image(self):
        if self.current_image_path:
            self.processed_image = cv2.imread(self.current_image_path)  # 重新加载原图
            self.save_and_display(self.processed_image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessingApp()
    ex.show()
    sys.exit(app.exec_())
