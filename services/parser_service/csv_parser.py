import json
import csv
import os
from typing import Dict

class JSONToCSVConverter:
    def __init__(self, csv_file: str, default_filename: str = "output.csv"):
        # Nếu truyền vào là thư mục thì tự động gắn thêm tên file mặc định
        if os.path.isdir(csv_file):
            self.csv_file = os.path.join(csv_file, default_filename)
        else:
            self.csv_file = csv_file
        self.headers = None  # sẽ lấy từ JSON đầu tiên truyền vào

    def json_to_csv_row(self, data: Dict) -> list:
        """
        Chuyển đổi JSON dict thành một list (theo đúng thứ tự headers)
        """
        return [data.get(h, "") for h in self.headers]

    def append_to_csv(self, data):
        """
        Ghi dòng CSV mới xuống cuối file, nếu Handle chưa tồn tại.
        Nếu file chưa tồn tại thì tạo file mới với header lấy từ JSON truyền vào.
        """
        # Nếu data là string thì parse thành dict
        if isinstance(data, str):
            data = json.loads(data)

        if self.headers is None:
            self.headers = list(data.keys())

        row = self.json_to_csv_row(data)
        write_header = False
        existing_handles = set()

        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for line in reader:
                    if 'Handle' in line:
                        existing_handles.add(line['Handle'])
                if reader.fieldnames is None:
                    write_header = True
        except FileNotFoundError:
            write_header = True

        # Kiểm tra trùng Handle
        if data.get('Handle') in existing_handles:
            print(f"Handle {data.get('Handle')} đã tồn tại, bỏ qua.")
            return

        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(self.headers)
            writer.writerow(row)
