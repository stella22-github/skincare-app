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

def render_creator_story():
    """渲染創作者的心路歷程與初衷"""
    with st.sidebar.expander("💌 寫給姊妹們的真心話"):
        st.markdown("""
        <div style="font-size: 14px; line-height: 1.6; color: #d0d0d0;">
        每次去寶雅、康是美、屈臣氏，架上總是擺滿琳瑯滿目的護膚品。<br><br>
        但我一直很在意的是——<b>裡面的成分是不是真的有效？</b>而不只是被漂亮的廣告吸引。<br><br>
        當然，實際使用後的膚感與效果最重要，但看懂成分能幫我們少走很多冤枉路。所以我做了這個小工具來幫大家把關，希望對妳們有幫助！✨
        </div>
        """, unsafe_allow_html=True)    
