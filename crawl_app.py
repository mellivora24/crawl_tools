#!/usr/bin/env python3
"""
Script khởi chạy đơn giản cho ứng dụng CRAWL
"""

import sys
import os
from pathlib import Path

def main():
    """Khởi chạy ứng dụng CRAWL"""
    
    # Thêm thư mục gốc vào Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Kiểm tra PyQt6
        import PyQt6
        print("✓ PyQt6 đã được cài đặt")
    except ImportError:
        print("❌ PyQt6 chưa được cài đặt!")
        print("Vui lòng chạy: pip install PyQt6")
        return 1
    
    try:
        # Kiểm tra các thư viện cần thiết
        import pandas as pd
        import openpyxl
        print("✓ Các thư viện cần thiết đã được cài đặt")
    except ImportError as e:
        print(f"❌ Thiếu thư viện: {e}")
        print("Vui lòng chạy: pip install -r requirements.txt")
        return 1
    
    try:
        # Khởi chạy ứng dụng
        from views.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        print("🚀 Khởi chạy ứng dụng CRAWL...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("CRAWL")
        app.setApplicationVersion("1.0.0")
        
        main_window = MainWindow()
        main_window.show()
        
        print("✓ Ứng dụng đã khởi chạy thành công!")
        print("💡 Sử dụng giao diện để:")
        print("   - Chọn file Excel chứa danh sách sản phẩm")
        print("   - Nhập Gemini API Key")
        print("   - Chọn thư mục đầu ra")
        print("   - Bắt đầu thu thập dữ liệu")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Lỗi khởi chạy ứng dụng: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 