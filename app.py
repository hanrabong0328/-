import streamlit as st
import openai
import pandas as pd
import re

st.set_page_config(page_title="AI 보안 분석기", layout="wide")
st.title("🛡️ AI 기반 일반 파일 보안 분석기")

# 1. API 키 설정 확인 (환경변수 또는 streamlit secrets)
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API 키가 설정되어 있지 않습니다. streamlit secrets에 OPENAI_API_KEY를 등록하세요.")
    st.stop()
openai.api_key = api_key

# 2. 파일 업로드
uploaded_file = st.file_uploader("🔽 .py, .txt, .env, .log 파일만 업로드 가능", type=["py", "txt", "env", "log"])

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
    st.code(file_content[:1000], language="text")  # 미리보기

    # 3. AI 보안 분석
    st.header("2. AI 보안 분석 결과")
    with st.spinner("🔍 AI가 보안 분석 중입니다..."):
        prompt = f"""
        너는 보안 전문가야. 아래 파일 내용을 분석해서 보안 취약점을 찾아줘.

        요구사항:
        1. 표 형식으로 최대 5개의 취약점을 출력해.
        2. 각 항목은 ["취약점명", "심각도 (1~5)", "설명"] 형태로 정리해.
        3. 실제 취약한 코드 줄이 있다면 간략히 인용해줘.

        파일 내용:
        {file_content[:3000]}  # 토큰 제한 때문에 일부만 사용
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # 또는 "gpt-3.5-turbo"
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        except Exception as e:
            st.error(f"OpenAI API 요청 중 오류 발생: {e}")
            st.stop()

        analysis = response.choices[0].message.content
        st.markdown("**📋 분석 요약:**")
        st.markdown(analysis)

        # 4. 표 파싱 시도
        table_pattern = r"\|(.+?)\|\n\|[- :]+\|\n((\|.*\|\n?)+)"
        match = re.search(table_pattern, analysis, re.DOTALL)

        if match:
            header_line = match.group(1)
            rows_text = match.group(2).strip()
            columns = [c.strip() for c in header_line.split("|")]
            rows = [row.strip("| ").split("|") for row in rows_text.split("\n")]

            # 데이터프레임 생성
            df = pd.DataFrame(rows, columns=columns)

            # 심각도 컬럼 처리 (컬럼명이 다를 수 있으니 유연하게 처리)
            severity_cols = [col for col in df.columns if "심각도" in col or "Severity" in col]
            if severity_cols:
                severity_col = severity_cols[0]
                df[severity_col] = pd.to_numeric(df[severity_col], errors="coerce").fillna(0)

                avg_risk = df[severity_col].mean()
            else:
                avg_risk = 0

            st.success("✅ 취약점 목록 분석 완료")
            st.dataframe(df, use_container_width=True)

            # 위험도 평가
            if avg_risk >= 4:
                st.error("⚠️ 보안 위험도가 매우 높습니다. 즉각 조치가 필요합니다.")
            elif avg_risk >= 2.5:
                st.warning("⚠️ 중간 수준 위험이 감지되었습니다. 점검이 필요합니다.")
            else:
                st.success("✅ 보안 위험이 낮은 수준으로 판단됩니다.")

        else:
            st.warning("❗ AI 응답에서 표 형식을 찾을 수 없어 분석 표를 표시하지 못했습니다.")

