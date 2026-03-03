import streamlit as st
import pandas as pd
from database import listar_negocios, listar_clientes, criar_negocio, atualizar_negocio, deletar_negocio

st.set_page_config(page_title="Negócios · Promed CRM", page_icon="💼", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1f36; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .kanban-card {
        background:#f8fafc; border-left: 4px solid #667eea;
        border-radius:8px; padding:12px; margin-bottom:8px;
        box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }
    .kanban-card h4 { margin:0 0 4px; font-size:.95rem; }
    .kanban-card p  { margin:0; font-size:.8rem; color:#64748b; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📋 Menu")
    st.page_link("app.py",               label="🏠  Dashboard")
    st.page_link("pages/1_Clientes.py",   label="👥  Clientes")
    st.page_link("pages/2_Negocios.py",   label="💼  Negócios")
    st.page_link("pages/3_Atividades.py", label="📅  Atividades")
    st.markdown("---")
    st.markdown(
        "<div style='position:fixed;bottom:16px;font-size:.75rem;color:#64748b;'>© 2026 Promed · v1.0</div>",
        unsafe_allow_html=True,
    )

st.title("💼 Negócios")

ESTAGIOS = ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechado Ganho", "Fechado Perdido"]
CORES    = ["#667eea", "#764ba2", "#11998e", "#2193b0", "#38ef7d", "#cb2d3e"]

tab_kanban, tab_lista, tab_novo, tab_editar = st.tabs(["🗂️ Kanban", "📋 Lista", "➕ Novo Negócio", "✏️ Editar / Excluir"])

# ── Kanban ─────────────────────────────────────────────────────────────────────
with tab_kanban:
    negocios = listar_negocios()
    cols_kanban = st.columns(len(ESTAGIOS))

    for idx, estagio in enumerate(ESTAGIOS):
        filtrados = [n for n in negocios if n["estagio"] == estagio]
        total_val = sum(n["valor"] for n in filtrados)
        with cols_kanban[idx]:
            st.markdown(
                f"<div style='background:{CORES[idx]};color:white;padding:8px 12px;"
                f"border-radius:8px;text-align:center;margin-bottom:8px;'>"
                f"<b>{estagio}</b><br><small>{len(filtrados)} neg · R$ {total_val:,.0f}</small></div>",
                unsafe_allow_html=True,
            )
            for n in filtrados:
                st.markdown(
                    f"<div class='kanban-card'>"
                    f"<h4>💼 {n['titulo']}</h4>"
                    f"<p>👤 {n['cliente_nome'] or '—'}</p>"
                    f"<p>💰 R$ {n['valor']:,.2f}</p>"
                    f"<p>🎯 {n['probabilidade']}%</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

# ── Lista ──────────────────────────────────────────────────────────────────────
with tab_lista:
    negocios = listar_negocios()
    if negocios:
        df = pd.DataFrame(negocios)
        if "criado_em" in df.columns:
            df["criado_em"] = pd.to_datetime(df["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
        df_show = df[["id","titulo","cliente_nome","valor","estagio","probabilidade","data_fechamento"]].copy()
        df_show.columns = ["ID","Título","Cliente","Valor (R$)","Estágio","Prob. (%)","Fechamento"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum negócio cadastrado ainda.")

# ── Novo Negócio ───────────────────────────────────────────────────────────────
with tab_novo:
    clientes = listar_clientes()
    mapa_clientes = {f"[{c['id']}] {c['nome']}": c["id"] for c in clientes}

    with st.form("form_novo_negocio", clear_on_submit=True):
        st.subheader("Cadastrar novo negócio")
        n1, n2 = st.columns(2)
        titulo = n1.text_input("Título *", placeholder="Ex.: Contrato Plano Saúde")
        cliente_label = n2.selectbox("Cliente", ["— Nenhum —"] + list(mapa_clientes.keys()))
        n3, n4, n5 = st.columns(3)
        valor         = n3.number_input("Valor (R$)", min_value=0.0, step=100.0)
        estagio       = n4.selectbox("Estágio", ESTAGIOS)
        probabilidade = n5.slider("Probabilidade (%)", 0, 100, 50)
        data_fechamento = st.date_input("Previsão de fechamento")
        notas           = st.text_area("Notas", placeholder="Observações...")
        submitted = st.form_submit_button("💾 Salvar Negócio", use_container_width=True)

        if submitted:
            if not titulo.strip():
                st.error("O campo **Título** é obrigatório.")
            else:
                cliente_id = mapa_clientes.get(cliente_label)
                criar_negocio(dict(
                    titulo=titulo.strip(), cliente_id=cliente_id, valor=valor,
                    estagio=estagio, probabilidade=probabilidade,
                    data_fechamento=str(data_fechamento), notas=notas,
                ))
                st.success(f"✅ Negócio **{titulo}** cadastrado com sucesso!")
                st.rerun()

# ── Editar / Excluir ──────────────────────────────────────────────────────────
with tab_editar:
    negocios = listar_negocios()
    clientes = listar_clientes()
    mapa_clientes = {f"[{c['id']}] {c['nome']}": c["id"] for c in clientes}

    if not negocios:
        st.info("Nenhum negócio para editar.")
    else:
        opcoes = {f"[{n['id']}] {n['titulo']} — {n['estagio']}": n for n in negocios}
        sel    = st.selectbox("Selecione o negócio", list(opcoes.keys()))
        neg    = opcoes[sel]

        with st.form("form_editar_negocio"):
            st.subheader("Editar negócio")
            e1, e2 = st.columns(2)
            titulo = e1.text_input("Título *", value=neg["titulo"])

            labels_clientes = ["— Nenhum —"] + list(mapa_clientes.keys())
            idx_cli = next(
                (i+1 for i, (k, v) in enumerate(mapa_clientes.items()) if v == neg["cliente_id"]), 0
            )
            cliente_label = e2.selectbox("Cliente", labels_clientes, index=idx_cli)

            e3, e4, e5 = st.columns(3)
            valor         = e3.number_input("Valor (R$)", min_value=0.0, step=100.0, value=float(neg["valor"]))
            idx_est       = ESTAGIOS.index(neg["estagio"]) if neg["estagio"] in ESTAGIOS else 0
            estagio       = e4.selectbox("Estágio", ESTAGIOS, index=idx_est)
            probabilidade = e5.slider("Probabilidade (%)", 0, 100, neg["probabilidade"])
            notas         = st.text_area("Notas", value=neg["notas"] or "")

            col_save, col_del = st.columns(2)
            salvar  = col_save.form_submit_button("💾 Salvar", use_container_width=True)
            excluir = col_del.form_submit_button("🗑️ Excluir", use_container_width=True, type="secondary")

        if salvar:
            cliente_id = mapa_clientes.get(cliente_label)
            atualizar_negocio(neg["id"], dict(
                titulo=titulo.strip(), cliente_id=cliente_id, valor=valor,
                estagio=estagio, probabilidade=probabilidade,
                data_fechamento=neg["data_fechamento"], notas=notas,
            ))
            st.success("✅ Negócio atualizado!")
            st.rerun()

        if excluir:
            deletar_negocio(neg["id"])
            st.warning(f"🗑️ Negócio **{neg['titulo']}** excluído.")
            st.rerun()
