try:
    import os, time, json, random
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse
    from playwright.sync_api import sync_playwright
    from utils.resource_path import resource_path as path_to
except ImportError as e:
    raise ImportError(f"Thiếu thư viện cần thiết: {e} => Sử dụng: pip install -r requirements.txt")

CRAWL_CONFIG_PATH = path_to("CRAWL/config/crawl-config.json")
CRAWL_INPUT_FILE = path_to("io/input/product_links_template.xlsx")

# Nếu chưa có file cấu hình cào dữ liệu thì báo lỗi
if not os.path.exists(CRAWL_CONFIG_PATH):
    raise FileNotFoundError(f"Không tìm thấy file cấu hình cào dữ liệu: {CRAWL_CONFIG_PATH}")

class CrawlWorker:
    def __init__(self):
        self.config_list = self.load_crawl_config()

    def load_crawl_config(self):
        """Đọc JSON cấu hình crawl."""
        try:
            with open(CRAWL_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "websites" not in config or not isinstance(config["websites"], list):
                raise ValueError("Cấu hình JSON phải có key 'websites' dạng list.")
            return config["websites"]
        except json.JSONDecodeError as e:
            raise ValueError(f"Lỗi JSON: {e}")

    def get_site_config_by_domain(self, domain: str):
        """Tìm config website khớp với domain."""
        for site in self.config_list:
            if site["domain"] in domain:
                return site
        return None

    def product_selector_elements(self, site_config):
        """Trả về selector mô tả sản phẩm."""
        if site_config:
            return site_config.get("product_selector")
        return None

    def crawl_product(self, url: str) -> str | None:
        url_domain = urlparse(url).netloc
        site_config = self.get_site_config_by_domain(url_domain)

        if not site_config:
            print(f"[x] Không tìm thấy config cho domain: {url_domain}")
            return None

        product_selector = site_config.get("product_selector")
        if not product_selector:
            print("[x] Không có product_selector trong config")
            return None

        with sync_playwright() as p:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
            ]
            ua = random.choice(user_agents)

            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=ua,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )

            page = context.new_page()
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """)

            print(f"[>] Đang tải {url}")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            # Cuộn trang để load nội dung
            for _ in range(5):
                page.mouse.wheel(0, random.randint(800, 1500))
                time.sleep(random.uniform(0.8, 1.5))

            try:
                page.wait_for_selector(product_selector, timeout=15000)
            except:
                print("[x] Không tìm thấy selector, sẽ lấy toàn bộ HTML để kiểm tra.")

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        desc_tag = soup.select_one(product_selector)

        if not desc_tag:
            print("[x] Không tìm thấy phần tử mô tả!")
            return None

        result_lines = []
        for elem in desc_tag.descendants:
            if elem.name == "img" and elem.get("src"):
                result_lines.append(elem["src"])
            elif elem.name is None:
                text = elem.strip()
                if text:
                    result_lines.append(text)

        crawl_result = "\n".join(result_lines)
        print(f"[v] Đã cào dữ liệu từ {url_domain} thành công!")

        return crawl_result
