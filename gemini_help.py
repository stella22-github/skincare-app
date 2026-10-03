# ==========================================
# 檔案名稱: gemini_help.py
# 說明: 專門提供 Gemini API Key 免費申請教學與引導
# ==========================================

import streamlit as st

def render_gemini_help_sidebar():
    """在側邊欄渲染 Gemini API Key 輸入與免費申請教學"""
    st.sidebar.header("🔑 設定 API Key")
    
    # 讓使用者輸入金鑰
    api_key = st.sidebar.text_input("請輸入 Gemini API Key", type="password")
    
    # 用摺疊選單收納教學，不佔用太多畫面空間
    with st.sidebar.expander("💡 沒有 Gemini API Key 怎麼免費申請？"):
        st.markdown("""
        不用擔心！Gemini API 提供非常充足的免費額度，只需 30 秒即可免費取得：
        
        1. 前往 **[Google AI Studio 官方網站](https://aistudio.google.com/)**。
        2. 使用您的 **Google 帳號** 登入。
        3. 點擊畫面左上角的 **「Get API key」** 按鈕。
        4. 點擊 **「Create API key」**（可選擇建立新專案）。
        5. 將產生的金鑰**複製**並貼到左側輸入框中即可開始使用！
        """)
        
    return api_key

def render_main_page_api_warning():
    """當使用者未輸入 API Key 時，在主畫面顯示的引導提示"""
    st.warning("👈 請先在左側邊欄輸入您的 Gemini API Key 才能開始分析保養品成分與管理保養品櫃！")
