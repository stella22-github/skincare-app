import json
import re
import io
from PIL import Image
from pillow_heif import register_heif_opener
from google import genai
from google.genai import types

# 註冊 HEIF/HEIC 檔案讀取器，讓 Image.open() 能直接支援 iPhone 的 HEIC 照片
register_heif_opener()

def process_image(uploaded_file):
    """
    處理使用者上傳的圖片（支援 JPG, PNG, JPEG, HEIC）
    """
    image = Image.open(uploaded_file)
    # 若圖片為 RGBA 或其他模式，轉為 RGB 確保相容性
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image

def analyze_ingredients(image, api_key: str, model_name: str = "gemini-3.5-flash"):
    """
    使用 Google GenAI 深度分析保養品成分標籤
    """
    client = genai.Client(api_key=api_key)
    
    # 將 PIL Image 轉為 JPEG byte 資料傳給 Gemini API
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    prompt = """
    你是一位極度細心的資深皮膚科醫師與保養品配方師。
    請詳細讀取照片中的全成分標籤 (INCI List)，並以繁體中文輸出符合以下 JSON 格式的完整分析結果：

    {
        "product_type_tags": ["美白亮膚", "抗老修護", "屏障強化", "防曬隔離", "保濕鎖水", "控油抗痘"],
        "top_10_ingredients": [
            "Aqua (水)",
            "Butylene Glycol (丁二醇)",
            "Glycerin (甘油)",
            "Panthenol (泛醇)",
            "1,2-Hexanediol (1,2-己二醇)",
            "Niacinamide (菸鹼醯胺)",
            "Cetyl Ethylhexanoate (鯨蠟基乙基己酸酯)",
            "Hydrogenated Polydecene (氫化聚癸烯)",
            "Acrylates/C10-30 Alkyl Acrylate Crosspolymer (丙烯酸酯/C10-30烷基丙烯酸交聯聚合物)",
            "Tromethamine (胺丁三醇)"
        ],
        "ingredients_grouped": [
            {
                "category": "保濕與溶劑",
                "ingredients": "AQUA [TOP 10], BUTYLENE GLYCOL [TOP 10], GLYCERIN [TOP 10], 1,2-HEXANEDIOL [TOP 10], HYDROGENATED POLYDECENE [TOP 10]",
                "good": "提供基礎水分、潤澤並協助有效成分滲透。",
                "bad_note": "多數為常見基底，巨量使用無太大負擔，但敏感肌需留意質感。"
            },
            {
                "category": "修護與美白亮膚活性",
                "ingredients": "PANTHENOL [TOP 10], NIACINAMIDE [TOP 10]",
                "good": "泛醇（B5）具卓越的舒緩、修護屏障功效；菸鹼醯胺（B3）有助於均勻膚色、控油及強化肌膚屏障。",
                "bad_note": "少數人對菸鹼醯胺可能有耐受期（輕微泛紅、刺癢），初次使用者建議局部測試。"
            },
            {
                "category": "膚感調節與乳化劑",
                "ingredients": "CETYL ETHYLHEXANOATE [TOP 10], ACRYLATES/C10-30 ALKYL ACRYLATE CROSSPOLYMER [TOP 10], TROMETHAMINE [TOP 10], ORYZA SATIVA (RICE) LEES EXTRACT, CALCIUM ALGINATE, PROPANEDIOL, HYDROLYZED SOY FLOUR",
                "good": "賦予精華液順滑觸感與適當黏稠度，增加保濕與膚感體驗。",
                "bad_note": "含有多種植物與米渣/大豆水解物萃取，對特定植物蛋白過敏者需留意。"
            },
            {
                "category": "植萃抗老與其他添加物",
                "ingredients": "LEONTOPODIUM ALPINUM EXTRACT, LEONTOPODIUM ALPINUM FLOWER/LEAF EXTRACT, AGAR, ADENOSINE, TRISODIUM ETHYLENEDIAMINE DISUCCINATE, SYNTHETIC FLUORPHLOGOPITE, CAPRYLYL GLYCOL, CITRIC ACID, POTASSIUM SORBATE, SODIUM BENZOATE, BUDDLEJA DAVIDII EXTRACT, THYMUS VULGARIS EXTRACT, TOCOPHEROL, CI 77491",
                "good": "添加腺苷（常見抗老成分）及多種高山雪絨花、蝴蝶草等植萃抗老舒緩成分，協同抗氧化。",
                "bad_note": "成分繁雜且包含多種防腐劑、色素（CI 77491），敏感肌膚需多加注意可能引起的過敏反應。"
            }
        ],
        "summary_pros": "配方包含保濕、舒緩及抗老修護成分，質地溫和，適合日常保養使用。",
        "summary_cons": "成分品項較多，敏感性肌膚初次使用建議先做局部敏感測試。"
    }

    重點注意事項：
    1. 務必「完整涵蓋標籤上的每一個成分」，絕不能遺漏或只列出一部分。
    2. 將所有成分依照功能歸類到相應的 `category` 中（如：保濕與溶劑、修護美白、膚感調節乳化、植萃抗老防腐劑等）。
    3. 在 `ingredients_grouped` 的 `ingredients` 欄位中，凡屬於成分表前 10 大的成分，名稱後面必須標註 `[TOP 10]`。
    4. 請只輸出 JSON 格式，不要包含 ```json 標記。
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    res_text = response.text.strip()
    if res_text.startswith("```"):
        res_text = re.sub(r"^```[a-zA-Z]*\n?", "", res_text)
        res_text = re.sub(r"\n?```$", "", res_text)
        
    return json.loads(res_text)

def fetch_image_via_gemini(product_name: str, api_key: str) -> str:
    """
    使用 Gemini 搭配 Google Search 尋找圖片
    """
    if not product_name or not product_name.strip():
        return None

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        請使用搜尋工具尋找保養品 '{product_name}' 的商品官方圖片或公開展示圖片連結 (Direct Image URL，副檔名通常為 .jpg, .png, .webp)。
        請直接回傳該圖片的 URL 網址即可，不要輸出任何其他文字。如果找不到，請回傳 "NOT_FOUND"。
        """

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}]
            )
        )
        url = response.text.strip()
        if url.startswith("http") and ("NOT_FOUND" not in url):
            match = re.search(r'https?://[^\s<"\']+', url)
            if match:
                return match.group(0)
    except Exception as e:
        print(f"[GeminiSearch] 搜尋圖片失敗: {e}")

    return None