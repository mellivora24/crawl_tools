import re
import json

try:
    import os
    from dotenv import load_dotenv
    import google.generativeai as genai
    from services.genai_service.prompt import generate_prompt
except ImportError as e:
    raise ImportError(f"Thiếu thư viện cần thiết: {e} => Sử dụng: pip install -r requirements.txt")


class LLMWorker:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        load_dotenv()
        if not API_KEY:
            raise ValueError("GOOGLE_API_KEY không được tìm thấy trong file .env")

        genai.configure(api_key=self.API_KEY)

        # Cấu hình generation config để có kết quả ổn định hơn
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        self.model = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config=generation_config
        )

    def extract_json_from_response(self, text: str) -> str:
        """
        Trích xuất JSON từ response của AI model
        """
        if not text:
            return ""

        # Loại bỏ markdown code blocks
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)

        # Tìm JSON object bắt đầu bằng {
        start_idx = text.find('{')
        if start_idx == -1:
            return text.strip()

        # Tìm JSON object kết thúc bằng } (đếm brackets)
        brace_count = 0
        end_idx = len(text)

        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break

        json_str = text[start_idx:end_idx].strip()
        return json_str

    def fix_common_json_errors(self, json_str: str) -> str:
        """
        Sửa một số lỗi JSON phổ biến với logic cải thiện
        """
        try:
            # Loại bỏ trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

            # Fix unquoted property names (property: value -> "property": value)
            # Tìm tất cả các property names không có quotes
            json_str = re.sub(r'(?<=[{\s,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', json_str)

            # Convert single quotes to double quotes cho property names và values
            # Nhưng cẩn thận với escaped quotes
            json_str = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', json_str)

            # Fix escaped newlines và các escape sequences khác
            json_str = re.sub(r'\\n', r'\\\\n', json_str)  # Fix literal \n
            json_str = re.sub(r'(?<!\\)\n', r'\\n', json_str)  # Escape actual newlines
            json_str = re.sub(r'(?<!\\)\t', r'\\t', json_str)  # Escape tabs
            json_str = re.sub(r'(?<!\\)\r', r'\\r', json_str)  # Escape carriage returns

            # Fix unescaped quotes trong string values
            # Tìm strings và escape quotes bên trong
            def fix_quotes_in_strings(match):
                content = match.group(1)
                # Escape unescaped quotes inside the string
                content = re.sub(r'(?<!\\)"', r'\\"', content)
                return f'"{content}"'

            json_str = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', fix_quotes_in_strings, json_str)

            return json_str
        except Exception as e:
            print(f"Lỗi khi fix JSON: {e}")
            return json_str

    def validate_and_fix_json(self, json_str: str, max_attempts: int = 3) -> dict:
        """
        Validate và fix JSON với nhiều attempts
        """
        for attempt in range(max_attempts):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}: JSON decode error: {e}")

                if attempt == max_attempts - 1:
                    # Last attempt, save debug info
                    debug_file = f"debug_json_error_attempt_{attempt + 1}.txt"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(f"ATTEMPT {attempt + 1} JSON:\n")
                        f.write(json_str)
                        f.write(f"\n\nJSON DECODE ERROR:\n{e}")
                    raise e

                # Try more aggressive fixes
                json_str = self.apply_aggressive_json_fixes(json_str, e)

        raise ValueError("Could not fix JSON after maximum attempts")

    def apply_aggressive_json_fixes(self, json_str: str, error: json.JSONDecodeError) -> str:
        """
        Apply more aggressive JSON fixes based on specific error
        """
        error_msg = str(error).lower()

        if "expecting property name" in error_msg:
            # More aggressive property name fixing
            json_str = re.sub(r'([{\s,])\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', json_str)

        elif "expecting ',' delimiter" in error_msg:
            # Fix missing commas
            json_str = re.sub(r'}\s*{', r'},{', json_str)
            json_str = re.sub(r']\s*[{\[]', r'],{', json_str)

        elif "unterminated string" in error_msg:
            # Try to fix unterminated strings
            lines = json_str.split('\n')
            for i, line in enumerate(lines):
                # Count quotes in line
                quote_count = line.count('"') - line.count('\\"')
                if quote_count % 2 != 0:  # Odd number of quotes
                    lines[i] = line + '"'
            json_str = '\n'.join(lines)

        elif "expecting value" in error_msg:
            # Fix common value issues
            json_str = re.sub(r':\s*,', r': null,', json_str)
            json_str = re.sub(r':\s*}', r': null}', json_str)

        # Apply standard fixes again
        return self.fix_common_json_errors(json_str)

    def process_product_raw_data(self, message: str) -> str:
        """
        Gọi API Gemini với error handling tốt hơn
        :param message: string
        :return: dict
        """
        if not message or not message.strip():
            raise ValueError("Dữ liệu đầu vào rỗng hoặc không hợp lệ")

        try:
            prompt = generate_prompt(message)
            response = self.model.generate_content(prompt)

            if not response or not hasattr(response, 'text') or not response.text:
                raise ValueError("API Gemini trả về response rỗng hoặc không hợp lệ")

            result = response.text.strip()

            # Loai bỏ (```json) va (```) nếu có
            result = re.sub(r'```json\s*', '', result, flags=re.IGNORECASE)
            result = re.sub(r'```\s*$', '', result, flags=re.MULTILINE)


            return result

        except Exception as e:
            print(f"Lỗi khi gọi API Gemini: {e}")
            raise RuntimeError(f"Lỗi khi xử lý dữ liệu sản phẩm: {str(e)}")

    def generate_json_from_product(self, product_data: str) -> dict:
        """
        Xử lý dữ liệu sản phẩm thô và trả về JSON chuẩn của Shopify
        :param product_data: string
        :return: dict
        """
        try:
            result = self.process_product_raw_data(product_data)
            return result
        except Exception as e:
            raise RuntimeError(f"Lỗi khi xử lý dữ liệu sản phẩm: {str(e)}")
