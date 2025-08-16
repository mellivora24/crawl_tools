import pandas as pd
from datetime import datetime
from typing import List
import os

class ExcelManager:
    def __init__(self, excel_file_path: str):
        """
        Khởi tạo class với đường dẫn file Excel

        Args:
            excel_file_path (str): Đường dẫn tới file Excel
        """
        self.excel_file_path = excel_file_path
        self.df = None
        self.links = []
        self._load_excel_file()
        self._load_links()

    def _load_excel_file(self):
        """Đọc file Excel và load dữ liệu"""
        try:
            if not os.path.exists(self.excel_file_path):
                raise FileNotFoundError(f"File không tồn tại: {self.excel_file_path}")

            # Đọc file Excel
            self.df = pd.read_excel(self.excel_file_path)

            # Kiểm tra các cột cần thiết
            required_columns = ['STT', 'Product URL', 'Is Crawled', 'Crawled Time', 'Note']
            missing_columns = [col for col in required_columns if col not in self.df.columns]

            if missing_columns:
                raise ValueError(f"Thiếu các cột: {missing_columns}")
        except Exception as e:
            raise RuntimeError(f"Lỗi khi đọc file Excel: {str(e)}")

    def _load_links(self):
        """Load tất cả links từ DataFrame vào mảng theo thứ tự STT"""
        try:
            sorted_df = self.df.sort_values('STT').reset_index()

            self.links = []
            for _, row in sorted_df.iterrows():
                if pd.notna(row['Product URL']):  # bỏ nan
                    self.links.append({
                        'index': row['index'],  # index trong DataFrame
                        'stt': row['STT'],
                        'url': row['Product URL'],
                        'is_crawled': row['Is Crawled'],
                        'crawled_time': row['Crawled Time'],
                        'note': row['Note']
                    })

        except Exception as e:
            print(f"Lỗi khi load links: {str(e)}")
            raise

    def get_list_of_links(self) -> List[dict]:
        """
        Trả về danh sách tất cả links theo thứ tự

        Returns:
            List[dict]: Danh sách các dict chứa thông tin link
        """
        return self.links.copy()  # Trả về copy để tránh modification bên ngoài

    def update_link(self, index: int, is_crawled: bool, note: str = ""):
        """
        Cập nhật trạng thái crawl cho một link theo STT và lưu ngay vào file Excel gốc
        """
        try:
            link_to_update = next((link for link in self.links if link['index'] == index), None)
            if link_to_update is None:
                raise ValueError(f"Không tìm thấy link với INDEX = {index}")

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update trong mảng links
            link_to_update['is_crawled'] = is_crawled
            link_to_update['crawled_time'] = current_time
            link_to_update['note'] = note

            # Update trong DataFrame
            df_index = link_to_update['index']
            self.df.at[df_index, 'Is Crawled'] = is_crawled
            self.df.at[df_index, 'Crawled Time'] = current_time
            self.df.at[df_index, 'Note'] = note

            # Lưu lại vào file Excel gốc
            self.save_to_excel()

            print(f"Đã cập nhật link STT {index}: Crawled={is_crawled}, Time={current_time}")

        except Exception as e:
            print(f"Lỗi khi cập nhật link STT {index}: {str(e)}")
            raise

    def save_to_excel(self):
        """Lưu DataFrame đã cập nhật ngược lại file Excel"""
        try:
            self.df.to_excel(self.excel_file_path, index=False)
            print(f"Đã lưu dữ liệu vào file: {self.excel_file_path}")
        except Exception as e:
            print(f"Lỗi khi lưu file Excel: {str(e)}")
            raise
