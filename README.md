# CRAWL - Ứng dụng thu thập dữ liệu sản phẩm

Ứng dụng desktop được xây dựng bằng PyQt6 để thu thập dữ liệu sản phẩm từ các website thương mại điện tử.

## Tính năng chính

- 🖥️ **Giao diện đồ họa thân thiện** với PyQt6
- 📊 **Đọc file Excel** chứa danh sách sản phẩm
- 🔑 **Tích hợp Gemini API** để xử lý dữ liệu
- 📁 **Chọn thư mục đầu ra** linh hoạt
- 📈 **Thanh tiến trình** hiển thị % hoàn thành
- ⚙️ **Cài đặt tùy chỉnh** cho quá trình thu thập dữ liệu
- 💾 **Lưu cài đặt** tự động giữa các phiên làm việc

## Yêu cầu hệ thống

- Python 3.8+
- PyQt6
- Các thư viện Python khác (xem requirements.txt)

## Cài đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd CRAWL
```

2. **Tạo môi trường ảo:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate  # Windows
```

3. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

## Sử dụng

### Khởi chạy ứng dụng

```bash
python main.py
```

### Hướng dẫn sử dụng

1. **Chọn file Excel:**
   - Nhấn nút "Duyệt..." để chọn file Excel chứa danh sách sản phẩm
   - File Excel phải có cấu trúc phù hợp (xem mẫu trong thư mục `io/templates/`)

2. **Nhập Gemini API Key:**
   - Nhập API Key của bạn vào trường "API Key"
   - API Key sẽ được lưu an toàn và tự động điền trong lần sử dụng tiếp theo

3. **Chọn thư mục đầu ra:**
   - Nhấn nút "Duyệt..." để chọn nơi lưu kết quả
   - Mặc định sẽ là `~/Desktop/CRAWL_Output`

4. **Cấu hình thu thập dữ liệu:**
   - **Độ trễ giữa các yêu cầu:** Thời gian chờ giữa các request (1-10 giây)
   - **Số lần thử lại:** Số lần thử lại khi gặp lỗi (1-5 lần)
   - **Chế độ headless:** Chạy trình duyệt ẩn (khuyến nghị)

5. **Bắt đầu thu thập dữ liệu:**
   - Nhấn nút "Bắt đầu thu thập dữ liệu"
   - Theo dõi tiến trình qua thanh progress bar
   - Xem nhật ký hoạt động ở phần dưới

### Cấu trúc file Excel đầu vào

File Excel phải có các cột sau:
- `url`: URL của sản phẩm
- `name`: Tên sản phẩm (tùy chọn)
- `category`: Danh mục sản phẩm (tùy chọn)

### Kết quả đầu ra

Ứng dụng sẽ tạo các file sau trong thư mục đầu ra:
- `crawl_results.csv`: Dữ liệu đã thu thập
- `crawl_log.txt`: Nhật ký chi tiết quá trình thu thập

## Cấu trúc dự án

```
CRAWL/
├── config/                 # Cấu hình ứng dụng
├── controller/            # Logic điều khiển
├── io/                   # Input/Output
├── services/             # Các service chính
├── views/                # Giao diện người dùng
├── utils/                # Tiện ích
└── main.py               # Điểm khởi đầu
```

## Tùy chỉnh

### Cấu hình website

Chỉnh sửa file `config/crawl-config.json` để thêm website mới:

```json
{
  "name": "WebsiteName",
  "domain": "example.com",
  "product_selector": "div.product-info",
  "image_selector": "img.product-image",
  "requires_js": false,
  "scroll_to_load": false
}
```

### Cài đặt mặc định

Chỉnh sửa file `config/app-config.json` để thay đổi cài đặt mặc định.

## Xử lý lỗi thường gặp

1. **Lỗi "PyQt6 not found":**
   - Cài đặt PyQt6: `pip install PyQt6`

2. **Lỗi "API Key không hợp lệ":**
   - Kiểm tra lại API Key trong Google AI Studio
   - Đảm bảo API Key có quyền truy cập Gemini

3. **Lỗi "Không thể đọc file Excel":**
   - Kiểm tra định dạng file (.xlsx hoặc .xls)
   - Đảm bảo file không bị khóa bởi ứng dụng khác

## Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/new-feature`
3. Commit thay đổi: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## Giấy phép

Dự án này được phát hành dưới giấy phép MIT.

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra phần "Xử lý lỗi thường gặp"
2. Tạo issue trên GitHub
3. Liên hệ qua email: [your-email@example.com]

---

**Lưu ý:** Đảm bảo tuân thủ các quy định về thu thập dữ liệu và điều khoản sử dụng của website đích.
# create by AI
