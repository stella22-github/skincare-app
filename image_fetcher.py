import time
from ddgs import DDGS

def fetch_product_image_url(product_name: str) -> str:
    """
    根據產品名稱，自動透過 DuckDuckGo 搜尋正面外觀圖片連結 (URL)
    """
    if not product_name or not product_name.strip():
        return None

    clean_name = product_name.strip()
    
    # 簡化搜尋詞，優先試品牌+主檔名，提升命中率
    queries = [
        f"{clean_name} skincare",
        clean_name
    ]

    for q in queries:
        try:
            with DDGS() as ddgs:
                # 指定 region="wt-wt" (全球) 且關閉嚴格過濾，大幅提升抓取成功率
                results = list(ddgs.images(q, region="wt-wt", safesearch="off", max_results=5))
                if results and len(results) > 0:
                    for item in results:
                        img_url = item.get("image")
                        if img_url and img_url.startswith("http"):
                            print(f"[ImageFetcher] 成功抓取圖片: {img_url}")
                            return img_url
        except Exception as e:
            print(f"[ImageFetcher] 關鍵字 '{q}' 搜尋失敗: {e}")
            time.sleep(1)

    return None