import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import init_db, metricas_dashboard

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Promed CRM",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1f36; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 12px; color: white;
        text-align: center; margin-bottom: 10px;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; }
    .metric-card p  { margin: 4px 0 0; opacity: .85; font-size: .9rem; }
    .metric-green { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
    .metric-blue  { background: linear-gradient(135deg, #2193b0, #6dd5ed) !important; }
    .metric-orange{ background: linear-gradient(135deg, #f7971e, #ffd200) !important; }
    .metric-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a) !important; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 0 4px;'>"
        "<span style='font-size:1.6rem;font-weight:700;color:#667eea;'>🏥 Promed</span>"
        "<br><span style='font-size:.75rem;color:#94a3b8;letter-spacing:2px;'>CRM</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 📋 Menu")
    st.page_link("app.py",             label="🏠  Dashboard",  )
    st.page_link("pages/1_Clientes.py",  label="👥  Clientes",   )
    st.page_link("pages/2_Negocios.py",  label="💼  Negócios",   )
    st.page_link("pages/3_Atividades.py",label="📅  Atividades", )
    st.markdown("---")
    st.markdown(
        "<div style='position:fixed;bottom:16px;font-size:.75rem;color:#64748b;'>© 2026 Promed · v1.0</div>",
        unsafe_allow_html=True,
    )

# ─── Dashboard ────────────────────────────────────────────────────────────────
st.title("🏠 Dashboard")
st.caption("Visão geral do seu CRM")

m = metricas_dashboard()

col1, col2, col3, col4, col5 = st.columns(5)

def card(col, icon, valor, label, css_class="metric-card"):
    col.markdown(
        f'<div class="{css_class}"><h2>{icon} {valor}</h2><p>{label}</p></div>',
        unsafe_allow_html=True,
    )

card(col1, "👥", m["total_clientes"],       "Clientes Ativos")
card(col2, "💼", m["total_negocios"],        "Negócios", "metric-card metric-blue")
card(col3, "💰", f"R$ {m['valor_pipeline']:,.0f}", "Pipeline Total", "metric-card metric-green")
card(col4, "🏆", f"R$ {m['receita_fechada']:,.0f}", "Receita Fechada", "metric-card metric-orange")
card(col5, "📅", m["atividades_pendentes"],  "Atividades Pendentes", "metric-card metric-red")

st.markdown("---")

# ─── Gráficos ─────────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Negócios por Estágio")
    if m["negocios_por_estagio"]:
        df_estagio = pd.DataFrame(m["negocios_por_estagio"])
        fig_funil = go.Figure(go.Funnel(
            y=df_estagio["estagio"],
            x=df_estagio["total"],
            textinfo="value+percent initial",
            marker=dict(color=["#667eea","#764ba2","#11998e","#2193b0","#f7971e","#cb2d3e"]),
        ))
        fig_funil.update_layout(margin=dict(t=20,b=20), height=320)
        st.plotly_chart(fig_funil, use_container_width=True)
    else:
        st.info("Nenhum negócio cadastrado ainda.")

with col_b:
    st.subheader("💰 Valor por Estágio (R$)")
    if m["negocios_por_estagio"]:
        df_valor = pd.DataFrame(m["negocios_por_estagio"])
        fig_bar = px.bar(
            df_valor, x="estagio", y="valor",
            color="estagio",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"estagio": "Estágio", "valor": "Valor (R$)"},
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=20,b=20), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Nenhum negócio cadastrado ainda.")

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("📈 Novos Clientes por Mês")
    if m["clientes_por_mes"]:
        df_mes = pd.DataFrame(m["clientes_por_mes"])
        fig_line = px.line(
            df_mes[::-1], x="mes", y="total", markers=True,
            labels={"mes": "Mês", "total": "Novos Clientes"},
            color_discrete_sequence=["#667eea"],
        )
        fig_line.update_layout(margin=dict(t=20,b=20), height=280)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

with col_d:
    st.subheader("🍩 Distribuição de Estágios")
    if m["negocios_por_estagio"]:
        df_pie = pd.DataFrame(m["negocios_por_estagio"])
        fig_pie = px.pie(
            df_pie, names="estagio", values="total",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.45,
        )
        fig_pie.update_layout(margin=dict(t=20,b=20), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Nenhum negócio cadastrado ainda.")
