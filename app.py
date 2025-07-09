import streamlit as st
import google.generativeai as genai
import os

# 환경변수 또는 secrets에서 API 키 로드
GOOGLE_API_KEY = st.secrets.get("AIzaSyCcZ2IQtrtDk8C_j1HwqXdxGmS8gwwq3gE", os.getenv("AIzaSyCcZ2IQtrtDk8C_j1HwqXdxGmS8gwwq3gE"))

if not GOOGLE_API_KEY:
    st.error("❌ Google Gemini API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=AIzaSyCcZ2IQtrtDk8C_j1HwqXdxGmS8gwwq3gE)

# 모델 초기화
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("🛡️ Gemini 기반 보안 취약점 자동 분석기")

st.markdown("업로드된 구성 파일, 코드, 로그 파일에서 **잠재적인 보안 취약점**을 자동 분석합니다.")

uploaded_file = st.file_uploader("🔐 분석할 파일을 업로드하세요 (예: .py, .txt)", type=['py', 'txt', 'log', 'conf'])

if uploaded_file is not None:
    file_content = uploaded_file.read().decode('utf-8', errors='ignore')

    st.subheader("📄 업로드된 파일 내용")
    st.code(file_content[:2000], language="plaintext")  # 2000자까지만 표시

    with st.spinner("Gemini AI가 보안 분석 중입니다..."):
        prompt = f"""
        다음은 사용자가 업로드한 구성 파일 또는 코드입니다.
        이 코드에서 **보안 취약점**이나 **개선이 필요한 점**을 전문가처럼 상세히 분석하고 요약해 주세요.
        가능하면 각 항목에 대해 보안 등급(낮음/중간/높음)도 포함해 주세요.

        파일 내용:
        {file_content}
        """

        try:
            response = model.generate_content(prompt)
            result = response.text
            st.success("✅ 분석 완료!")
            st.subheader("🔍 보안 취약점 분석 결과")
            st.markdown(result)
        except Exception as e:
            st.error(f"❌ Gemini 응답 중 오류 발생: {e}")
else:
    st.info("👆 먼저 분석할 파일을 업로드하세요.")

