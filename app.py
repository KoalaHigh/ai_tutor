import streamlit as st
import google.generativeai as genai
from PIL import Image

# 網頁基本設定
st.set_page_config(page_title="簡易老師的AI小助教", page_icon="📐", layout="centered")

st.title("📐 簡易老師的AI小助教 🧪")
st.write("孩子們別擔心，先讓小助教來幫幫你")

# 1. 🔑 從後台 Secrets 安全讀取 API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ 後台讀取金鑰失敗，詳細原因：{e}")
    st.stop()

# 2. 讓學生選擇回答模式
mode = st.radio(
    "💡 請選擇你的學習模式：",
    ("🧠 引導式教學（推薦！給你提示，帶你思考）", "📝 直接給答案（適合最後對答案與看詳解）"),
    index=0
)

# 3. 提供圖片上傳與文字輸入
st.subheader("📸 上傳你的題目")
uploaded_file = st.file_uploader("點擊上傳或拖曳題目照片 (支援 JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
text_question = st.text_area("或者，你也可以在這裡直接輸入文字題目：", placeholder="例如：已知一個等差數列的第 5 項為...")

# 4. 根據模式設定不同的系統指令
base_instruction = (
    "你是一位專業且非常有耐心的台灣國中數學與理化老師（適用於 108 課綱）。"
    "你的目標是協助國中生（7-9年級）解決課業問題。"
    "重要原則：1. 所有的專有名詞、公式、範例都必須嚴格限制在台灣國中課綱範圍內，絕對不能使用高中或大學的微積分、矩陣、高階化學公式等。"
    "2. 語氣要親切、多用鼓勵的字眼，像一個熱心的家長或大哥哥大姊姊。"
)

if "🧠 引導式教學" in mode:
    system_prompt = (
        base_instruction + 
        "【核心任務：引導式教學】"
        "請絕對不要直接給出最終答案、數字或完整的計算過程！"
        "你的回答步驟必須是："
        "1. 稱讚並鼓勵學生願意發問。"
        "2. 分析這個題目考的是國中課綱的哪一個『核心觀念』（例如：密度公式、一元二次方程式、牛頓第一運動定律）。"
        "3. 給予 1 到 2 個關鍵提示（Hint），引導他們去思考下一步該怎麼做。"
        "4. 留下一個反問句，邀請學生回答，激發他們動腦。"
    )
else:
    system_prompt = (
        base_instruction + 
        "【核心任務：直接給答案】"
        "請直接給出最精準的最終答案，並附上清晰、條理分明的步驟。"
        "你的回答步驟必須嚴格包含以下字樣並以此結構呈現："
        "1. 開頭第一句必須是：『來吧，讓我們看看這一題！』"
        "2. 清晰列出【正確答案】。"
        "3. 標題使用【解題觀念】與【讓我們分析一下】，在『讓我們分析一下』區塊內詳細列出計算步驟，每一步都要寫清楚為什麼，符合國中生的理解能力。"
        "4. 結尾必須包含標題：【容易想錯的地方可能是】，並提醒學生這題容易踩到的陷阱（盲點）。"
    )

# 5. 當學生點擊「開始解題」時觸發
if st.button("🚀 開始解題", type="primary"):
    if not uploaded_file and not text_question.strip():
        st.error("❌ 請至少上傳一張照片或輸入文字題目喔！")
    else:
        with st.spinner("小助教正在認真看題中，請稍候..."):
            try:
                # 選擇模型
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_prompt
                )
                
                # 準備內容清單
                contents = []
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    contents.append(image)
                    st.image(image, caption="你上傳的題目照片", width="stretch")
                    
                if text_question.strip():
                    contents.append(text_question)
                
                # 呼叫 API 產生回應
                response = model.generate_content(contents)
                
                # 呈現結果
                st.success("✨ 解題完成！")
                st.markdown("---")
                st.markdown(response.text)
                st.markdown("---")
                
            except Exception as e:
                error_msg = str(e)
                # 🔍 判斷是否為 429 超過免費版頻率限制
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    st.warning(
                        "⏳ **小助教正在喝口水，請等一下下！**\n\n"
                        "因為目前系統使用免費版通道，**每分鐘有查詢次數限制**。若剛才點擊太快或多人同時使用就會觸發這個限制。\n\n"
                        "👉 **學生的解法：** 請等待約 30 到 60 秒，再次點擊「🚀 開始解題」就可以囉！\n\n"
                        "💡 **老師的升級解法：** 如果未來正式給多位學生使用，建議前往 Google AI Studio 後台綁定信用卡，升級成 **Pay-as-you-go（隨收隨付）** 專案。升級後每分鐘限制會大幅放寬至上百次。而且 Gemini 2.5 Flash 費用極低，每個人偶爾查幾題，基本上幾乎不會花到什麼錢（甚至可能仍在免費的免費額度內），非常劃算！"
                    )
                else:
                    # 其他真正的系統錯誤才印出詳細原因
                    st.error(f"❌ 執行解題時發生錯誤，詳細原因：{e}")