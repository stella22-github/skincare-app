import json
import streamlit as st
from analyzer import process_image, analyze_ingredients, fetch_image_via_gemini
from database import init_db, save_product, get_all_products, delete_product
from conflict_checker import check_skincare_conflicts
from gemini_help import render_gemini_help_sidebar, render_main_page_api_warning

# 預設高品質保養品示意圖 (備援機制)
DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=800&auto=format&fit=crop"

# 初始化資料庫
init_db()

st.set_page_config(page_title="護膚營養標籤分析器", layout="centered")

# --- CSS 樣式定義 ---
st.markdown("""
<style>
    .nutrition-label {
        border: 3px solid #111;
        padding: 20px;
        background-color: #ffffff;
        color: #111;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin-bottom: 25px;
    }
    .nutrition-header {
        text-align: center;
        border-bottom: 8px solid #111;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .nutrition-title {
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
    }
    .nutrition-subtitle {
        font-size: 14px;
        color: #555;
        margin-top: 4px;
    }
    .smart-tag {
        display: inline-block;
        background-color: #111;
        color: #fff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .top10-box {
        background: #18181c;
        border: 2px solid #ffd700;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .top10-title {
        color: #ffd700;
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .top10-item {
        display: inline-block;
        background: #2a2a32;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 13px;
        margin: 3px;
        border: 1px solid #444;
    }
    .top10-rank {
        color: #ffd700;
        font-weight: 800;
        margin-right: 4px;
    }
    .ing-card {
        background: #1e1e24;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        color: #e0e0e0;
    }
    .ing-cat {
        font-size: 16px;
        font-weight: 700;
        color: #64b5f6;
        border-bottom: 1px solid #444;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }
    .ing-names {
        font-size: 14px;
        color: #ffffff;
        font-weight: 500;
        margin-bottom: 10px;
        word-wrap: break-word;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    .ing-good {
        font-size: 13px;
        color: #81c784;
        background: rgba(46, 125, 50, 0.15);
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 6px;
        word-wrap: break-word;
    }
    .ing-bad {
        font-size: 13px;
        color: #ffb74d;
        background: rgba(239, 108, 0, 0.15);
        padding: 8px;
        border-radius: 4px;
        word-wrap: break-word;
    }
    .top-badge {
        background: #ffd700;
        color: #000;
        font-size: 11px;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 10px;
        margin-left: 6px;
        vertical-align: middle;
    }
    .pros-box {
        background-color: #eef9f1;
        border-left: 5px solid #2e7d32;
        padding: 15px 18px;
        border-radius: 6px;
        margin-bottom: 15px;
        color: #1b5e20;
    }
    .cons-box {
        background-color: #fff4e5;
        border-left: 5px solid #ef6c00;
        padding: 15px 18px;
        border-radius: 6px;
        margin-bottom: 20px;
        color: #e65100;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧴 護膚營養標籤與個人保養品櫃")

# 側邊欄使用 gemini_help 提供的 API Key 輸入與免費申請教學
api_key = render_gemini_help_sidebar()

model_choice = st.sidebar.selectbox(
    "選擇模型",
    ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"],
    index=0
)

# 使用 Streamlit Tab 切換分頁
tab1, tab2 = st.tabs(["🔍 拍照分析成分", "🗄️ 我的保養品櫃 (歷史紀錄)"])


# 通用的成分結果渲染函式
def render_analysis_result(data, product_name=None, image_url=None):
    if product_name:
        st.subheader(f"📌 產品名稱：{product_name}")
    
    # 若有圖片 URL，則展示商品外觀照
    if image_url:
        st.image(image_url, caption="商品外觀包裝", width=250)

    tags_html = "".join([f'<span class="smart-tag">{tag}</span>' for tag in data.get("product_type_tags", [])])
    
    st.markdown(f"""
    <div class="nutrition-label">
        <div class="nutrition-header">
            <div class="nutrition-title">SKINCARE NUTRITION FACTS</div>
            <div class="nutrition-subtitle">前 10 大成分與分類優缺點分析</div>
        </div>
        <div style="margin-bottom: 15px;">
            {tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    top10_list = data.get("top_10_ingredients", [])
    if top10_list:
        items_html = "".join([
            f'<div class="top10-item"><span class="top10-rank">#{i+1}</span>{ing}</div>'
            for i, ing in enumerate(top10_list)
        ])
        st.markdown(f"""
        <div class="top10-box">
            <div class="top10-title">👑 前 10 大高濃度基底成分 (按配方比例高低排序)</div>
            <div>{items_html}</div>
        </div>
        """, unsafe_allow_html=True)

    raw_table = data.get("ingredients_grouped", [])
    if raw_table:
        for item in raw_table:
            if isinstance(item, dict):
                cat = item.get("category", "")
                ings = item.get("ingredients", "")
                ings_formatted = ings.replace("[TOP 10]", '<span class="top-badge">TOP 10 高濃度</span>')
                good = item.get("good", "")
                bad = item.get("bad_note", "")
                
                st.markdown(f"""
                <div class="ing-card">
                    <div class="ing-cat">📂 {cat}</div>
                    <div class="ing-names"><strong>主要成分：</strong><br>{ings_formatted}</div>
                    <div class="ing-good"><strong>💡 作用與優點：</strong><br>{good}</div>
                    <div class="ing-bad"><strong>⚠️ 潛在顧慮：</strong><br>{bad}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pros-box">
        <strong>💡 核心優勢 (Pros)：</strong><br>{data.get('summary_pros', '')}
    </div>
    <div class="cons-box">
        <strong>⚠️ 避坑提示 (Cons)：</strong><br>{data.get('summary_cons', '')}
    </div>
    """, unsafe_allow_html=True)


# ==================== TAB 1: 拍照分析成分 ====================
with tab1:
    uploaded_file = st.file_uploader(
        "拍下或上傳瓶身背後全英文成分表 (INCI List)",
        type=["jpg", "png", "jpeg", "heic"],
    )

    if uploaded_file and api_key:
        try:
            image = process_image(uploaded_file)
            st.image(image, caption="已上傳的照片（背面成分表）", width="stretch")
        except Exception as img_err:
            st.error(f"⚠️ 圖片讀取失敗：{img_err}")
            st.stop()

        if st.button("🚀 開始分析成分", type="primary"):
            with st.spinner("AI 配方師連線分析中..."):
                try:
                    res_json = analyze_ingredients(image, api_key, model_name=model_choice)
                    st.session_state["current_analysis"] = res_json
                except Exception as e:
                    st.error(f"分析失敗，詳細錯誤訊息如下：\n\n{e}")

    elif not api_key:
        st.warning("👈 請先在左側邊欄輸入你的 Gemini API Key！")

    # 呈現分析結果與儲存區域
    if "current_analysis" in st.session_state:
        st.divider()
        data = st.session_state["current_analysis"]
        
        render_analysis_result(data)

        # ---------------- 智慧成分衝突檢測 ----------------
        all_cabinet = get_all_products()
        conflicts = check_skincare_conflicts(data, all_cabinet, current_prod_name="這款新產品")
        
        if conflicts:
            st.markdown("### 🛑 智慧護膚疊擦與成分衝突提醒")
            for c in conflicts:
                if c["level"] == "error":
                    st.error(f"### {c['title']}\n{c['msg']}")
                elif c["level"] == "warning":
                    st.warning(f"### {c['title']}\n{c['msg']}")
                else:
                    st.info(f"### {c['title']}\n{c['msg']}")

        # ---------------- 存檔專區 ----------------
        st.success("🎉 分析完成！輸入產品完整名稱後，系統將自動搜尋商品正面包裝圖並存檔。")
        with st.form("save_form"):
            prod_name = st.text_input("產品名稱 (例如：Cetaphil Healthy Renew Face Serum)", value="")
            prod_cat = st.selectbox("主要功效分類", ["美白亮膚", "抗老緊緻", "修護屏障", "保濕鎖水", "防曬隔離","控油抗痘", "其他"], index=0)
            
            submit_save = st.form_submit_button("💾 存入我的保養品櫃 (自動抓取外觀圖)")
            if submit_save:
                if prod_name.strip():
                    clean_name = prod_name.strip()
                    img_url = None

                    with st.spinner("正在搜尋商品正面包裝照..."):
                        # 1. 優先透過 Gemini Google Search 檢索產品真實圖片
                        if api_key:
                            try:
                                img_url = fetch_image_via_gemini(clean_name, api_key)
                            except Exception as e:
                                print(f"[GeminiSearch Error] {e}")

                        # 2. 若 Gemini 沒找到，回退使用 image_fetcher 網路搜尋
                       # if not img_url:
                        #    try:
                         #       img_url = fetch_product_image_url(clean_name)
                          #  except Exception as e:
                           #     print(f"[ImageFetcher Error] {e}")

                        # 3. 兩者皆無結果時，使用高品質預設示意圖
                        if not img_url:
                            img_url = DEFAULT_IMAGE_URL
                        
                    save_product(
                        name=clean_name, 
                        category=prod_cat, 
                        tags=data.get("product_type_tags", []), 
                        analysis_data=data,
                        image_url=img_url
                    )
                    st.toast("✅ 成功存入保養品櫃！已自動抓取並綁定商品正面圖片。")
                    st.rerun()
                else:
                    st.error("請輸入產品名稱再存檔！")


# ==================== TAB 2: 我的保養品櫃 (歷史紀錄) ====================
with tab2:
    st.header("🗄️ 我的護膚品記憶庫")
    
    products = get_all_products()
    if not products:
        st.info("尚無存檔產品。在「拍照分析成分」頁面分析後即可一鍵存入！")
    else:
        # 搜尋與篩選列
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 搜尋產品名稱", "")
        with col_filter:
            category_filter = st.selectbox("🏷️ 功效篩選", ["全部", "美白亮膚", "抗老緊緻", "修護屏障", "保濕鎖水", "防曬隔離","控油抗痘", "其他"])

        filtered_products = []
        for p in products:
            p_id, p_name, p_cat, p_tags, p_data_str, p_img_url, p_time = p
            
            matches_search = search_query.lower() in p_name.lower() if search_query else True
            matches_cat = (category_filter == "全部") or (p_cat == category_filter)
            
            if matches_search and matches_cat:
                filtered_products.append(p)

        st.caption(f"共找到 {len(filtered_products)} 款保養品")
        st.divider()

        # 展示產品卡片
        for p in filtered_products:
            p_id, p_name, p_cat, p_tags, p_data_str, p_img_url, p_time = p
            try:
                p_data = json.loads(p_data_str) if isinstance(p_data_str, str) else p_data_str
            except Exception:
                p_data = {}
            
            with st.expander(f"🧴 【{p_cat}】{p_name}  （存檔時間：{p_time}）"):
                # 帶入從網路擷取到的圖片 URL 並渲染
                render_analysis_result(p_data, product_name=p_name, image_url=p_img_url)
                
                # 自動比對與保養品櫃內其他產品的搭配建議
                p_conflicts = check_skincare_conflicts(p_data, products, current_prod_name=p_name)
                if p_conflicts:
                    st.markdown("#### 🛑 與櫃子內其他產品的搭配建議：")
                    for c in p_conflicts:
                        if c["level"] == "error":
                            st.error(f"**{c['title']}**\n\n{c['msg']}")
                        elif c["level"] == "warning":
                            st.warning(f"**{c['title']}**\n\n{c['msg']}")
                        else:
                            st.info(f"**{c['title']}**\n\n{c['msg']}")

                if st.button(f"🗑️ 刪除此紀錄", key=f"del_{p_id}"):
                    delete_product(p_id)
                    st.rerun()

                    # 替代原本側邊欄的輸入與教學
                    api_key = render_gemini_help_sidebar()

                    # 在主畫面判斷，如果沒有 api_key 就顯示警告
                    if not api_key:
                        render_main_page_api_warning()
                    else:
                        # 妳原本的相片上傳與成分分析主程式邏輯...
                        pass
