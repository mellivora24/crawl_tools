standard_prompt = """
Xử lý dữ liệu sản phẩm thô và chuyển đổi thành định dạng JSON chuẩn Shopify và dịch mô tả sản phẩm sang tiếng Việt.

YÊU CẦU QUAN TRỌNG NHẤT:
- Trả về CHÍNH XÁC một JSON object hợp lệ
- KHÔNG thêm text giải thích, markdown hoặc bất kỳ ký tự nào khác
- KHÔNG sử dụng ```json hoặc code blocks
- TẤT CẢ keys và string values PHẢI được bao bọc bởi double quotes "..."
- KHÔNG có trailing commas
- Escape đúng ký tự đặc biệt: \n, \t, \", \\

PROCESSING RULES:
1. Làm sạch dữ liệu, loại bỏ thông tin không cần thiết
2. Nếu thiếu thông tin, điền chuỗi rỗng ""
3. Image Src: chỉ lấy 1 trong các URL hình ảnh
4. Body (HTML): giữ nguyên HTML tags, escape quotes thành \"
5. Variant Inventory Qty: mặc định "20"
6. Vendor: lấy từ thương hiệu/brand
7. Mô tả sản phẩm: viết lại bằng HTML tags <p>, <ul>, <li>
8. Product Category: bao gồm các danh mục sản phẩm sau, hãy chọn phù hợp:
    - MCU & Processor
    - FPGA & CPLD
    - IoT & Connectivity
    - Motion & Actuators
    - Sensors, Power & Energy
    - Prototyping & Accessories
    - Test & Measurement

REQUIRED JSON STRUCTURE (EXACT ORDER):
{
    "Handle": "",
    "Title": "",
    "Body (HTML)": "",
    "Vendor": "",
    "Product Category": "",
    "Type": "",
    "Tags": "",
    "Published": "TRUE",
    "Option1 Name": "",
    "Option1 Value": "",
    "Option2 Name": "",
    "Option2 Value": "",
    "Option3 Name": "",
    "Option3 Value": "",
    "Variant SKU": "",
    "Variant Grams": "",
    "Variant Inventory Tracker": "shopify",
    "Variant Inventory Qty": "20",
    "Variant Inventory Policy": "deny",
    "Variant Fulfillment Service": "manual",
    "Variant Price": "",
    "Variant Compare At Price": "",
    "Variant Requires Shipping": "TRUE",
    "Variant Taxable": "TRUE",
    "Variant Barcode": "",
    "Image Src": "",
    "Image Position": "1",
    "Image Alt Text": "",
    "Gift Card": "FALSE",
    "SEO Title": "",
    "SEO Description": "",
    "Google Shopping / Google Product Category": "",
    "Google Shopping / Gender": "",
    "Google Shopping / Age Group": "",
    "Google Shopping / MPN": "",
    "Google Shopping / Condition": "new",
    "Google Shopping / Custom Product": "FALSE",
    "Google Shopping / Custom Label 0": "",
    "Google Shopping / Custom Label 1": "",
    "Google Shopping / Custom Label 2": "",
    "Google Shopping / Custom Label 3": "",
    "Google Shopping / Custom Label 4": "",
    "Variant Image": "",
    "Variant Weight Unit": "g",
    "Variant Tax Code": "",
    "Cost per item": "",
    "Status": "active"
}

VALIDATION CHECKLIST:
✓ JSON bắt đầu bằng { và kết thúc bằng }
✓ Tất cả 48 keys có mặt và đúng thứ tự
✓ Tất cả keys và string values có double quotes
✓ Không có trailing comma trước }
✓ Escape sequences đúng trong string values
✓ Không có text nào ngoài JSON object

PRODUCT DATA:
"""


def generate_prompt(product_data: str) -> str:
    """
    Generate an improved prompt for processing product data into Shopify JSON format.

    Args:
        product_data (str): The raw product data to be processed.

    Returns:
        str: The formatted prompt string.
    """
    if not product_data or not product_data.strip():
        raise ValueError("Product data cannot be empty")

    # Clean and validate product data
    cleaned_data = product_data.strip()

    return (
            standard_prompt +
            cleaned_data +
            "\n\nIMPORTANT: Return ONLY the JSON object above. No explanations, no markdown, no additional text."
    )


# Alternative more structured prompt for better results
def generate_structured_prompt(product_data: str) -> str:
    """
    Generate a more structured prompt with examples for better AI understanding.
    """
    structured_prompt = """
You are a product data processor. Convert raw product data to valid Shopify JSON format.

CRITICAL REQUIREMENTS:
1. Output MUST be a single valid JSON object
2. NO markdown formatting, NO explanations, NO additional text
3. All keys and string values MUST use double quotes "..."
4. NO trailing commas
5. Properly escape special characters: \" \\ \n \t

EXAMPLE OUTPUT FORMAT:
{"Handle": "example-product", "Title": "Example Product", "Body (HTML)": "<p>Description here</p>"}

FIELD MAPPING RULES:
- Handle: Create URL-friendly slug from title
- Title: Clean product name
- Body (HTML): Rich HTML description in Vietnamese with <p>, <ul>, <li> tags
- Vendor: Extract brand/manufacturer name
- Product Category: Determine appropriate category
- Tags: Comma-separated relevant keywords
- Image Src: All image URLs separated by ", "
- Variant Inventory Qty: Default "20"
- Published: Default "TRUE"
- Status: Default "active"

JSON MUST CONTAIN EXACTLY THESE 48 KEYS IN ORDER:
Handle, Title, Body (HTML), Vendor, Product Category, Type, Tags, Published, Option1 Name, Option1 Value, Option2 Name, Option2 Value, Option3 Name, Option3 Value, Variant SKU, Variant Grams, Variant Inventory Tracker, Variant Inventory Qty, Variant Inventory Policy, Variant Fulfillment Service, Variant Price, Variant Compare At Price, Variant Requires Shipping, Variant Taxable, Variant Barcode, Image Src, Image Position, Image Alt Text, Gift Card, SEO Title, SEO Description, Google Shopping / Google Product Category, Google Shopping / Gender, Google Shopping / Age Group, Google Shopping / MPN, Google Shopping / Condition, Google Shopping / Custom Product, Google Shopping / Custom Label 0, Google Shopping / Custom Label 1, Google Shopping / Custom Label 2, Google Shopping / Custom Label 3, Google Shopping / Custom Label 4, Variant Image, Variant Weight Unit, Variant Tax Code, Cost per item, Status

PROCESS THIS PRODUCT DATA:
""" + product_data + """

OUTPUT ONLY THE JSON OBJECT:"""

    return structured_prompt


# Enhanced prompt with JSON schema validation
def generate_schema_validated_prompt(product_data: str) -> str:
    """
    Generate prompt with explicit JSON schema for validation.
    """
    return f"""
Convert the following product data to valid Shopify JSON format.

STRICT JSON REQUIREMENTS:
- Must be parseable by JSON.parse()
- All property names in double quotes
- All string values in double quotes
- No trailing commas
- Proper escaping of special characters

REQUIRED SCHEMA - ALL 48 PROPERTIES MUST BE PRESENT:
{{
  "Handle": "string (URL-friendly slug)",
  "Title": "string (product name)",
  "Body (HTML)": "string (HTML description in Vietnamese)",
  "Vendor": "string (brand/manufacturer)",
  "Product Category": "string",
  "Type": "string",
  "Tags": "string (comma-separated)",
  "Published": "TRUE",
  "Option1 Name": "string or empty",
  "Option1 Value": "string or empty", 
  "Option2 Name": "string or empty",
  "Option2 Value": "string or empty",
  "Option3 Name": "string or empty", 
  "Option3 Value": "string or empty",
  "Variant SKU": "string or empty",
  "Variant Grams": "string or empty",
  "Variant Inventory Tracker": "shopify",
  "Variant Inventory Qty": "20",
  "Variant Inventory Policy": "deny", 
  "Variant Fulfillment Service": "manual",
  "Variant Price": "string or empty",
  "Variant Compare At Price": "string or empty",
  "Variant Requires Shipping": "TRUE",
  "Variant Taxable": "TRUE", 
  "Variant Barcode": "string or empty",
  "Image Src": "string (URLs separated by comma-space)",
  "Image Position": "1",
  "Image Alt Text": "string or empty",
  "Gift Card": "FALSE",
  "SEO Title": "string or empty",
  "SEO Description": "string or empty", 
  "Google Shopping / Google Product Category": "string or empty",
  "Google Shopping / Gender": "string or empty",
  "Google Shopping / Age Group": "string or empty",
  "Google Shopping / MPN": "string or empty",
  "Google Shopping / Condition": "new",
  "Google Shopping / Custom Product": "FALSE",
  "Google Shopping / Custom Label 0": "string or empty",
  "Google Shopping / Custom Label 1": "string or empty", 
  "Google Shopping / Custom Label 2": "string or empty",
  "Google Shopping / Custom Label 3": "string or empty",
  "Google Shopping / Custom Label 4": "string or empty",
  "Variant Image": "string or empty",
  "Variant Weight Unit": "g",
  "Variant Tax Code": "string or empty",
  "Cost per item": "string or empty",
  "Status": "active"
}}

INPUT DATA:
{product_data}

RETURN ONLY VALID JSON - NO EXPLANATIONS OR MARKDOWN:
"""