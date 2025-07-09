import streamlit as st
import openai  # OpenAI API 사용
import pandas as pd
import os

st.set_page_config(page_title="AI 보안 분석기", layout="wide")
st.title("🛡️ AI 기반 일반 파일 보안 분석기")

# OpenAI 키 설정 (환경변수로 처리하거나 직접 입력 가능)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...")  # 실제로는 안전하게 보관하세요

# 1. 파일 업로드
st.header("1. 분석할 파일 업로드")
uploaded_file = st.file_uploader("🔽 .py, .txt, .env, .log 파일만 업로드 가능", type=["py", "txt", "env", "log"])

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
    st.code(file_content[:1000], language="text")  # 미리보기

    # 2. AI 요청 생성
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

        response = openai.ChatCompletion.create(
            model="gpt-4",  # 또는 gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        analysis = response.choices[0].message.content
        st.markdown("**📋 분석 요약:**")
        st.markdown(analysis)

        # 3. 표에서 내용 파싱 시도 (단순한 테이블 포맷 감지 시)
        import re
        table_pattern = r"\|(.+?)\|\n\|(.+?)\|\n((\|.+\|\n?)+)"
        match = re.search(table_pattern, analysis, re.DOTALL)

        if match:
            rows = match.group(3).strip().split("\n")
            records = [r.strip("|").split("|") for r in rows]
            columns = [c.strip() for c in match.group(1).split("|")]
            df = pd.DataFrame(records, columns=columns)

            # 심각도 숫자화
            if "심각도" in df.columns:
                df["심각도"] = pd.to_numeric(df["심각도"], errors="coerce")
                df["심각도"] = df["심각도"].fillna(0)

            st.success("✅ 취약점 목록 분석 완료")
            st.dataframe(df, use_container_width=True)

            avg_risk = df["심각도"].mean()
            if avg_risk >= 4:
                st.error("⚠️ 보안 위험도가 매우 높습니다. 즉각 조치가 필요합니다.")
            elif avg_risk >= 2.5:
                st.warning("⚠️ 중간 수준 위험이 감지되었습니다. 점검이 필요합니다.")
            else:
                st.success("✅ 보안 위험이 낮은 수준으로 판단됩니다.")

        else:
            st.warning("❗ AI 응답에서 테이블 형식을 찾을 수 없어 분석 표를 표시하지 못했습니다.")
