import os, sys

def resource_path(relative_path: str) -> str:
    """
    Trả về đường dẫn tuyệt đối đến resource, hỗ trợ cả khi chạy trực tiếp
    và khi đóng gói bằng PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        # Lấy thư mục gốc project dựa trên vị trí file này
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # utils/
        base_path = os.path.abspath(os.path.join(base_path, ".."))  # ra gốc project CRAWL/

    return os.path.join(base_path, relative_path)
