import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 타이틀
st.title("🛡️ 정보 보안 위험도 분석 도구")

# 1. 사용자 입력
st.header("1. 보호 대상 정보 입력")

info_name = st.text_input("보호할 정보명 (예: 고객정보, 내부DB 등)", max_chars=50)
importance = st.slider("정보 중요도 (1~5)", 1, 5, 3)
exposure = st.slider("정보 노출도 (1~5)", 1, 5, 3)
security_ready = st.slider("보안 대응 준비도 (1~5)", 1, 5, 3)

# 2. 취약점 파일 업로드
st.header("2. 취약점 CSV 파일 업로드")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (컬럼: Vulnerability, Severity, Description)", type=["csv"])

avg_severity = 0
vuln_df = None

if uploaded_file is not None:
    try:
        vuln_df = pd.read_csv(uploaded_file)

        expected_cols = {'Vulnerability', 'Severity', 'Description'}
        if not expected_cols.issubset(set(vuln_df.columns)):
            st.error(f"❌ CSV 파일에 다음 컬럼이 모두 필요합니다: {expected_cols}")
        else:
            st.success("✅ 취약점 파일 정상 업로드됨")
            st.dataframe(vuln_df)

            # 평균 심각도 계산
            avg_severity = vuln_df['Severity'].mean()
            st.markdown(f"📊 **평균 취약점 심각도**: `{avg_severity:.2f} / 5`")

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")

# 3. 위험도 계산
if security_ready > 0:
    risk_score = (importance + exposure + avg_severity) / security_ready
else:
    risk_score = 10  # 대응 준비 0일 경우 최대 위험도

risk_score_norm = min(max(risk_score, 1), 5)

# 4. 시각화
st.header("3. 보안 항목별 시각화")

labels = ['정보 중요도', '정보 노출도', '보안 대응 준비도', '평균 취약점 심각도', '위험도 (계산값)']
values = [importance, exposure, security_ready, round(avg_severity, 2), round(risk_score_norm, 2)]
colors = ['blue', 'orange', 'green', 'purple', 'red']

fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors)])
fig.update_layout(yaxis=dict(range=[0, 5]), title_text="보안 항목별 점수 (1~5)", template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# 5. 결과 요약
st.header("4. 분석 결과 요약")

st.markdown(f"- **보호할 정보명:** `{info_name if info_name else '미입력'}`")
st.markdown(f"- **위험도 점수:** `{round(risk_score_norm, 2)} / 5`")

# 취약점 목록 출력
if vuln_df is not None:
    st.markdown("### 📋 업로드된 취약점 목록:")
    for i, row in vuln_df.iterrows():
        st.markdown(f"- `{row['Vulnerability']}` (심각도: {row['Severity']}) - {row['Description']}")

# 위험도 평가 메시지
st.subheader("📢 보안 권고사항")
if risk_score_norm >= 4:
    st.error("⚠️ 위험도가 매우 높습니다. 즉각적인 보안 조치가 필요합니다!")
elif risk_score_norm >= 3:
    st.warning("⚠️ 보안 점검이 필요합니다. 대비 방안을 검토하세요.")
else:
    st.success("✅ 현재 보안 상태는 비교적 양호합니다.")

st.info("※ 본 분석 도구는 참고용입니다. 실제 보안 진단은 보안 전문가와 상의하세요.")
