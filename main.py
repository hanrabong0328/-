import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 앱 타이틀
st.title("정보 보안 분석 및 시각화 프로그램")

# 1. 사용자 정보 입력
st.header("1. 보호할 정보 입력 및 상태 설정")

info_name = st.text_input("보호할 정보명 (예: 고객 개인정보, 서버 DB 등)", max_chars=50)
importance = st.slider("정보 중요도 (1: 낮음 ~ 5: 매우 높음)", 1, 5, 3)
exposure = st.slider("정보 노출도 (1: 공개됨 ~ 5: 완전 비공개)", 1, 5, 3)
security_ready = st.slider("보안 대응 준비도 (1: 미흡 ~ 5: 완전 준비)", 1, 5, 3)

# 2. 취약점 직접 입력
st.header("2. 취약점 및 위협 요소 입력")
vulnerabilities = st.text_area("발견한 취약점 또는 위협 요소를 자세히 입력해주세요", height=100)

# 보안도 계산 (간단 가중치 예시)
# 보안도 = (중요도 + 노출도) / 대응준비도 으로 단순 계산 (높을수록 위험도 높음)
if security_ready > 0:
    risk_score = (importance + exposure) / security_ready
else:
    risk_score = 10  # 대응 준비가 없으면 위험도 최대치

# 점수 정규화 (1~5 scale)
risk_score_norm = min(max(risk_score, 1), 5)

# 3. 데이터 프레임 생성
data = {
    "항목": ["정보 중요도", "정보 노출도", "보안 대응 준비도", "위험도 (계산값)"],
    "점수": [importance, exposure, security_ready, round(risk_score_norm, 2)]
}
df = pd.DataFrame(data)

# 4. 시각화 - 막대그래프
st.header("3. 보안 상태 시각화")

fig = go.Figure(data=[
    go.Bar(name='점수', x=df['항목'], y=df['점수'], marker_color=['blue', 'orange', 'green', 'red'])
])
fig.update_layout(yaxis=dict(range=[0,5]), title_text='보안 항목별 점수 (1~5)', template='plotly_white')

st.plotly_chart(fig, use_container_width=True)

# 5. 분석 결과 출력
st.header("4. 분석 결과 및 제안")

st.markdown(f"- **보호할 정보명:** {info_name if info_name else '미입력'}")
st.markdown(f"- **위험도 점수:** {round(risk_score_norm,2)} / 5 (높을수록 위험)")
st.markdown(f"- **취약점 내용:**\n{vulnerabilities if vulnerabilities.strip() != '' else '취약점 미입력'}")

# 위험도에 따른 간단 제안
if risk_score_norm >= 4:
    st.error("⚠️ 위험도가 매우 높습니다! 즉시 보안 대응을 강화하세요.")
elif risk_score_norm >= 3:
    st.warning("⚠️ 주의가 필요합니다. 보안 점검을 권장합니다.")
else:
    st.success("✅ 현재 보안 상태가 양호합니다.")

# 추가 기능 제안 (댓글 등)

st.info("본 프로그램은 간단한 참고용 보안 분석 도구입니다. 실제 보안 진단은 전문기관과 상담하세요.")
