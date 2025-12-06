import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="Elon Musk 輿情監控", layout="wide")
st.title("🐦 Elon Musk 市場言論監控器")
st.markdown("由於 X (Twitter) API 封鎖嚴重，此工具透過**聚合財經新聞**來追蹤馬斯克的最新動態與推文報導。")

# --- 核心函數：抓取新聞 ---
def fetch_musk_news():
    # 使用 Google News RSS 針對特定關鍵字搜索
    # 關鍵字邏輯：Elon Musk AND (Tweet OR X OR Tesla)
    # hl=en-US (抓英文新聞通常比中文快 10-20 分鐘)
    rss_url = "https://news.google.com/rss/search?q=Elon+Musk+(Tweet+OR+X+OR+Tesla)+when:2d&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        pub_date = entry.published
        
        # 簡單的情緒關鍵字標記 (這可以用 AI 升級)
        sentiment = "Neutral"
        if any(w in title.lower() for w in ['soar', 'surge', 'jump', 'bull', 'buy', 'high']):
            sentiment = "🟢 Positive"
        elif any(w in title.lower() for w in ['drop', 'plunge', 'fall', 'bear', 'sell', 'crash', 'sued', 'recall']):
            sentiment = "🔴 Negative"
            
        news_list.append({
            "時間": pub_date,
            "標題": title,
            "連結": link,
            "情緒指標": sentiment
        })
        
    return pd.DataFrame(news_list)

# --- 側邊欄 ---
st.sidebar.header("設定")
if st.sidebar.button("🔄 立即刷新"):
    st.cache_data.clear()

# --- 主畫面 ---
st.subheader("🔥 最新 48 小時馬斯克相關頭條")

try:
    df = fetch_musk_news()
    
    if not df.empty:
        # 轉換時間格式方便閱讀
        df['時間'] = pd.to_datetime(df['時間']).dt.strftime('%m-%d %H:%M')
        
        # 顯示統計
        pos_count = len(df[df['情緒指標'].str.contains("Positive")])
        neg_count = len(df[df['情緒指標'].str.contains("Negative")])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("相關新聞數", len(df))
        c2.metric("🟢 利多關鍵字", pos_count)
        c3.metric("🔴 利空關鍵字", neg_count)
        
        st.divider()
        
        # 顯示新聞列表
        for index, row in df.iterrows():
            # 根據情緒變色
            color = "gray"
            if "Positive" in row['情緒指標']: color = "green"
            if "Negative" in row['情緒指標']: color = "red"
            
            with st.container():
                c_date, c_sentiment, c_title = st.columns([1.5, 1.5, 7])
                c_date.text(row['時間'])
                c_sentiment.markdown(f":{color}[{row['情緒指標']}]")
                c_title.markdown(f"[{row['標題']}]({row['連結']})")
                
    else:
        st.info("目前沒有相關新聞。")
        
except Exception as e:
    st.error(f"抓取失敗: {e}")

# --- 進階策略教學 ---
with st.expander("💡 透過這個工具你可以怎麼做？"):
    st.markdown("""
    **交易策略：情緒反轉 (Sentiment Reversal)**
    
    1. **監控極端情緒：** 當你在這裡看到一整排全是 **🔴 Negative** (例如：裁員、召回、推文失言) 時。
    2. **結合你的 75% 下跌數據：** - 如果壞消息發生在 **股價高檔** + **事件剛結束** (如 Robotaxi 後)，這會加速那 75% 的下跌機率 -> **加空**。
       - 如果壞消息發生在 **股價已大跌 20% 後**，這通常是「利空出盡」的訊號 -> **準備抄底**。
    
    **此工具的價值：**
    幫你把「感覺馬斯克在亂講話」轉化為「量化的新聞數量與情緒指標」。
    """)
