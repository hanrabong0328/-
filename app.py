import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="코드 보안 분석기 (Gemini)", layout="wide")
st.title("🔐 AI 기반 코드 보안 분석기 (Gemini 2.5 Flash)")

st.markdown("✅ 사용자의 **Gemini API 키**를 입력하고, 분석할 코드를 업로드하면 AI가 보안 취약점을 진단해줍니다.")

# ✅ 1. 사용자로부터 API 키 받기
user_api_key = st.text_input("🔑 Gemini API 키를 입력하세요", type="password")

if not user_api_key:
    st.info("먼저 Gemini API 키를 입력해주세요.")
    st.stop()

# ✅ 2. API 키 설정
try:
    genai.configure(api_key=user_api_key)
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
except Exception as e:
    st.error("❌ API 키 인증에 실패했습니다. 유효한 키인지 확인해주세요.")
    st.stop()

# ✅ 3. 파일 업로드
uploaded_file = st.file_uploader("📁 분석할 파일 업로드 (.py, .js, .json, .yaml, .yml, .env, .cfg, .ini, .sh, .log, .txt 등)", type=["py", "txt", "conf", "json", "yaml", "log"])

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")

    st.subheader("📄 업로드된 코드 미리보기")
    st.code(code, language='python')

    st.subheader("🔍 Gemini 기반 보안 분석 결과")

    with st.spinner("Gemini가 코드를 분석 중입니다..."):
        prompt = f"""
        아래 코드는 설정파일 또는 보안 구성 코드입니다.
        다음 항목을 기준으로 취약점을 찾아주세요:

        1. 하드코딩된 비밀번호/토큰/시크릿 키
        2. 인증 없는 요청
        3. 민감한 로그 출력
        4. 위험한 시스템 명령 (rm -rf, chmod, etc.)
        5. SSL 인증 검증 생략

        출력 형식:
        - 취약점 설명
        - 예시 코드
        - 개선 방법

        분석 대상 코드:
        {code}
        """
        try:
            response = model.generate_content(prompt)
            st.success("✅ 분석 완료!")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ Gemini 분석 중 오류 발생: {e}")
