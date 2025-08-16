import os, json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog,
                             QProgressBar, QTextEdit, QGroupBox, QMessageBox,
                             QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from utils.excel_file import ExcelManager
from services.genai_service.llm_worker import LLMWorker
from services.crawl_service.crawl_worker import CrawlWorker
from services.parser_service.csv_parser import JSONToCSVConverter


class CrawlThread(QThread):
    """Separate thread for crawling operations to prevent UI freezing"""
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished_crawling = pyqtSignal(bool, str)

    def __init__(self, excel_path, api_key, output_folder, delay, retry, headless):
        super().__init__()
        self.excel_path = excel_path
        self.api_key = api_key
        self.output_folder = output_folder
        self.delay = delay
        self.retry = retry
        self.headless = headless
        self.should_stop = False

    def run(self):
        try:
            # Initialize workers
            crawl_worker = CrawlWorker()
            llm_worker = LLMWorker(self.api_key)
            convert_worker = JSONToCSVConverter(self.output_folder)

            # Read links from Excel
            excel_manager = ExcelManager(self.excel_path)
            list_of_links = excel_manager.get_list_of_links()
            num_of_links = len(list_of_links)

            if num_of_links == 0:
                self.finished_crawling.emit(False, "Không tìm thấy link nào trong file Excel!")
                return

            successful_crawls = 0

            for link in list_of_links:
                if self.should_stop:
                    self.log_message.emit("Quá trình thu thập đã bị dừng bởi người dùng")
                    break

                # Update progress
                progress = int((link['index']+1 / num_of_links) * 100)
                self.progress_updated.emit(progress)

                if not link['url'].startswith("http"):
                    self.log_message.emit(f"Link thứ {link['index']+1} không hợp lệ: {link['url']}")
                    continue

                try:
                    self.log_message.emit(f"Đang thu thập dữ liệu từ link {link['index']+1}/{num_of_links}")
                    crawl_output = crawl_worker.crawl_product(link['url'])

                    if not crawl_output:
                        self.log_message.emit(f"Không thể thu thập dữ liệu từ {link['url']}")
                        continue

                    self.log_message.emit(f"Đã thu thập dữ liệu từ {link['url']}")
                    llm_output = llm_worker.generate_json_from_product(crawl_output)

                    if not llm_output:
                        self.log_message.emit(f"Lỗi khi chuyển đổi dữ liệu từ {link['url']}")
                        continue

                    self.log_message.emit(f"Đã chuyển đổi dữ liệu từ {link['url']} sang JSON")
                    convert_worker.append_to_csv(llm_output)
                    successful_crawls += 1

                    excel_manager.update_link(link['index'], True)

                    # Add delay between requests
                    self.msleep(self.delay * 1000)

                except Exception as e:
                    excel_manager.update_link(link['index'], False, str(e))
                    self.log_message.emit(f"Lỗi khi xử lý {link['url']}: {str(e)}")
                    continue

            self.progress_updated.emit(100)

            if self.should_stop:
                self.finished_crawling.emit(False,
                                            f"Quá trình bị dừng. Đã thu thập {successful_crawls}/{num_of_links} sản phẩm.")
            else:
                self.finished_crawling.emit(True,
                                            f"Hoàn tất! Đã thu thập {successful_crawls}/{num_of_links} sản phẩm thành công.")

        except Exception as e:
            self.finished_crawling.emit(False, f"Lỗi nghiêm trọng: {str(e)}")

    def stop(self):
        self.should_stop = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.settings = QSettings('CRAWL', 'CrawlApp')
        self.load_settings()

        # Thread for crawling
        self.crawl_thread = None

    def init_ui(self):
        self.setWindowTitle("CRAWL - Ứng dụng thu thập dữ liệu sản phẩm")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 1ex;
                color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ecf0f1;
            }
            QLineEdit, QSpinBox {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 5px;
                color: #ecf0f1;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #e74c3c;
            }
            QCheckBox {
                color: #ecf0f1;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("CRAWL - Thu thập dữ liệu sản phẩm")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #3498db; margin: 15px; padding: 10px;")
        layout.addWidget(title_label)

        # File Selection Group
        file_group = QGroupBox("📁 Chọn file Excel")
        file_layout = QVBoxLayout(file_group)

        # Excel file selection
        excel_layout = QHBoxLayout()
        self.excel_path_edit = QLineEdit()
        self.excel_path_edit.setPlaceholderText("Chọn file Excel chứa danh sách sản phẩm...")
        self.excel_path_edit.setReadOnly(True)

        self.browse_excel_btn = QPushButton("Duyệt...")
        self.browse_excel_btn.clicked.connect(self.browse_excel_file)
        self.style_button(self.browse_excel_btn, "#3498db")

        excel_layout.addWidget(QLabel("File Excel:"))
        excel_layout.addWidget(self.excel_path_edit)
        excel_layout.addWidget(self.browse_excel_btn)
        file_layout.addLayout(excel_layout)

        layout.addWidget(file_group)

        # API Configuration Group
        api_group = QGroupBox("🔑 Cấu hình Gemini API")
        api_layout = QVBoxLayout(api_group)

        # API Key input
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Nhập Gemini API Key của bạn...")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Show/Hide API Key button
        self.toggle_api_btn = QPushButton("Hiện")
        self.toggle_api_btn.clicked.connect(self.toggle_api_visibility)
        self.style_button(self.toggle_api_btn, "#95a5a6")
        self.toggle_api_btn.setMaximumWidth(60)

        api_key_layout.addWidget(QLabel("API Key:"))
        api_key_layout.addWidget(self.api_key_edit)
        api_key_layout.addWidget(self.toggle_api_btn)
        api_layout.addLayout(api_key_layout)

        layout.addWidget(api_group)

        # Output Configuration Group
        output_group = QGroupBox("📂 Cấu hình đầu ra")
        output_layout = QVBoxLayout(output_group)

        # Output folder selection
        output_folder_layout = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setPlaceholderText("Chọn thư mục lưu kết quả...")
        self.output_folder_edit.setReadOnly(True)

        self.browse_output_btn = QPushButton("Duyệt...")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        self.style_button(self.browse_output_btn, "#3498db")

        output_folder_layout.addWidget(QLabel("Thư mục đầu ra:"))
        output_folder_layout.addWidget(self.output_folder_edit)
        output_folder_layout.addWidget(self.browse_output_btn)
        output_layout.addLayout(output_folder_layout)

        layout.addWidget(output_group)

        # Crawl Configuration Group
        crawl_group = QGroupBox("⚙️ Cấu hình thu thập dữ liệu")
        crawl_layout = QVBoxLayout(crawl_group)

        # Crawl settings
        settings_layout = QHBoxLayout()

        # Delay between requests
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 30)
        self.delay_spin.setValue(2)
        self.delay_spin.setSuffix(" giây")
        self.delay_spin.setToolTip("Thời gian chờ giữa các yêu cầu để tránh bị chặn")

        # Retry attempts
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(3)
        self.retry_spin.setSuffix(" lần")
        self.retry_spin.setToolTip("Số lần thử lại khi gặp lỗi")

        # Headless mode
        self.headless_checkbox = QCheckBox("Chế độ ẩn trình duyệt")
        self.headless_checkbox.setChecked(True)
        self.headless_checkbox.setToolTip("Chạy trình duyệt ở chế độ ẩn để tăng tốc độ")

        settings_layout.addWidget(QLabel("Độ trễ:"))
        settings_layout.addWidget(self.delay_spin)
        settings_layout.addWidget(QLabel("Thử lại:"))
        settings_layout.addWidget(self.retry_spin)
        settings_layout.addWidget(self.headless_checkbox)
        settings_layout.addStretch()

        crawl_layout.addLayout(settings_layout)
        layout.addWidget(crawl_group)

        # Control Buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("🚀 Bắt đầu thu thập dữ liệu")
        self.start_btn.clicked.connect(self.start_crawling)
        self.style_button(self.start_btn, "#27ae60")

        self.stop_btn = QPushButton("⏹️ Dừng")
        self.stop_btn.clicked.connect(self.stop_crawling)
        self.stop_btn.setEnabled(False)
        self.style_button(self.stop_btn, "#e74c3c")

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Progress Section
        progress_group = QGroupBox("📊 Tiến trình")
        progress_layout = QVBoxLayout(progress_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                                stop: 0 #3498db, stop: 1 #2ecc71);
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_group)

        # Log Section
        log_group = QGroupBox("📝 Nhật ký hoạt động")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(180)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group)

        # Set default output folder
        default_output = os.path.join(os.path.expanduser("~"), "Desktop", "CRAWL_Output")
        self.output_folder_edit.setText(default_output)

        # Initial log message
        self.log_message("Ứng dụng đã sẵn sàng! Vui lòng cấu hình và bắt đầu thu thập dữ liệu.")

    def style_button(self, button, color):
        """Apply consistent styling to buttons"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-height: 25px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
            QPushButton:disabled {{
                background-color: #7f8c8d;
                color: #bdc3c7;
            }}
        """)

    def darken_color(self, color, factor=0.2):
        """Darken a hex color by a factor"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def toggle_api_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_api_btn.setText("Ẩn")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_api_btn.setText("Hiện")

    def browse_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.excel_path_edit.setText(file_path)
            self.log_message(f"✅ Đã chọn file Excel: {os.path.basename(file_path)}")

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục đầu ra"
        )
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.log_message(f"✅ Đã chọn thư mục đầu ra: {folder_path}")

    def validate_inputs(self):
        """Validate all required inputs"""
        if not self.excel_path_edit.text():
            QMessageBox.warning(self, "⚠️ Lỗi", "Vui lòng chọn file Excel!")
            return False

        if not os.path.exists(self.excel_path_edit.text()):
            QMessageBox.warning(self, "⚠️ Lỗi", "File Excel không tồn tại!")
            return False

        if not self.api_key_edit.text():
            QMessageBox.warning(self, "⚠️ Lỗi", "Vui lòng nhập Gemini API Key!")
            return False

        if len(self.api_key_edit.text()) < 20:  # Basic API key length check
            QMessageBox.warning(self, "⚠️ Lỗi", "API Key có vẻ không hợp lệ!")
            return False

        if not self.output_folder_edit.text():
            QMessageBox.warning(self, "⚠️ Lỗi", "Vui lòng chọn thư mục đầu ra!")
            return False

        # Create output directory if it doesn't exist
        try:
            os.makedirs(self.output_folder_edit.text(), exist_ok=True)
        except Exception as e:
            QMessageBox.warning(self, "⚠️ Lỗi", f"Không thể tạo thư mục đầu ra: {str(e)}")
            return False

        return True

    def start_crawling(self):
        if not self.validate_inputs():
            return

        # Save current settings before starting
        self.save_settings()

        # Update UI state
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_message("🚀 Bắt đầu quá trình thu thập dữ liệu...")

        # Create and start crawling thread
        self.crawl_thread = CrawlThread(
            self.excel_path_edit.text(),
            self.api_key_edit.text(),
            self.output_folder_edit.text(),
            self.delay_spin.value(),
            self.retry_spin.value(),
            self.headless_checkbox.isChecked()
        )

        # Connect signals
        self.crawl_thread.progress_updated.connect(self.update_progress)
        self.crawl_thread.log_message.connect(self.log_message)
        self.crawl_thread.finished_crawling.connect(self.crawling_finished)

        # Start the thread
        self.crawl_thread.start()

    def stop_crawling(self):
        if self.crawl_thread and self.crawl_thread.isRunning():
            self.log_message("⏹️ Đang dừng quá trình thu thập...")
            self.crawl_thread.stop()
            self.crawl_thread.wait(5000)  # Wait up to 5 seconds for thread to finish

            if self.crawl_thread.isRunning():
                self.crawl_thread.terminate()  # Force terminate if still running
                self.log_message("⚠️ Đã buộc dừng quá trình thu thập")

            self.crawling_finished(False, "Quá trình thu thập đã được dừng")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def crawling_finished(self, success, message):
        # Update UI state
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Show completion message
        if success:
            QMessageBox.information(self, "✅ Thành công", message)
        else:
            QMessageBox.warning(self, "⚠️ Thông báo", message)

        self.log_message(f"{'✅' if success else '⚠️'} {message}")

        # Clean up thread
        if self.crawl_thread:
            self.crawl_thread.deleteLater()
            self.crawl_thread = None

    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def load_settings(self):
        # Load saved settings
        self.api_key_edit.setText(self.settings.value('api_key', ''))
        saved_output = self.settings.value('output_folder', '')
        if saved_output:
            self.output_folder_edit.setText(saved_output)

        # Load crawl settings
        self.delay_spin.setValue(int(self.settings.value('delay', 2)))
        self.retry_spin.setValue(int(self.settings.value('retry', 3)))
        self.headless_checkbox.setChecked(
            self.settings.value('headless', True, type=bool)
        )

    def save_settings(self):
        # Save current settings
        self.settings.setValue('api_key', self.api_key_edit.text())
        self.settings.setValue('excel_path', self.excel_path_edit.text())
        self.settings.setValue('output_folder', self.output_folder_edit.text())
        self.settings.setValue('delay', self.delay_spin.value())
        self.settings.setValue('retry', self.retry_spin.value())
        self.settings.setValue('headless', self.headless_checkbox.isChecked())

    def closeEvent(self, event):
        # Stop crawling if running
        if self.crawl_thread and self.crawl_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Xác nhận thoát",
                "Quá trình thu thập đang chạy. Bạn có muốn dừng và thoát?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.crawl_thread.stop()
                self.crawl_thread.wait(3000)
                if self.crawl_thread.isRunning():
                    self.crawl_thread.terminate()
            else:
                event.ignore()
                return

        self.save_settings()
        event.accept()