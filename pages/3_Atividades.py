import streamlit as st
import pandas as pd
from database import (
    listar_atividades, criar_atividade,
    atualizar_status_atividade, deletar_atividade,
    listar_clientes, listar_negocios,
)

st.set_page_config(page_title="Atividades · Promed CRM", page_icon="📅", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1f36; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
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

st.title("📅 Atividades")

TIPOS   = ["Ligação", "Email", "Reunião", "Visita", "Tarefa", "Follow-up"]
STATUS  = ["Pendente", "Em andamento", "Concluída", "Cancelada"]
ICONES  = {"Ligação": "📞", "Email": "📧", "Reunião": "🤝", "Visita": "🚗", "Tarefa": "✅", "Follow-up": "🔄"}
STATUS_ICONE = {"Pendente": "🟡", "Em andamento": "🔵", "Concluída": "🟢", "Cancelada": "🔴"}

tab_lista, tab_nova, tab_gerenciar = st.tabs(["📋 Lista", "➕ Nova Atividade", "⚙️ Gerenciar"])

# ── Lista ──────────────────────────────────────────────────────────────────────
with tab_lista:
    atividades = listar_atividades()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_tipo   = st.multiselect("Filtrar por tipo",   TIPOS,  default=[])
    with col_f2:
        filtro_status = st.multiselect("Filtrar por status", STATUS, default=[])

    if atividades:
        df = pd.DataFrame(atividades)
        if filtro_tipo:
            df = df[df["tipo"].isin(filtro_tipo)]
        if filtro_status:
            df = df[df["status"].isin(filtro_status)]

        for _, row in df.iterrows():
            icone_tipo   = ICONES.get(row["tipo"], "📌")
            icone_status = STATUS_ICONE.get(row["status"], "⚪")
            with st.expander(
                f"{icone_tipo} {row['tipo']} · {row['descricao'] or '—'} "
                f"| {icone_status} {row['status']} | 📅 {row['data_atividade'] or '—'}"
            ):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**👤 Cliente:** {row['cliente_nome'] or '—'}")
                c2.markdown(f"**💼 Negócio:** {row['negocio_titulo'] or '—'}")
                c3.markdown(f"**👨‍💼 Responsável:** {row['responsavel'] or '—'}")
    else:
        st.info("Nenhuma atividade cadastrada. Use **Nova Atividade** para adicionar.")

# ── Nova Atividade ─────────────────────────────────────────────────────────────
with tab_nova:
    clientes = listar_clientes()
    negocios = listar_negocios()
    mapa_clientes = {f"[{c['id']}] {c['nome']}": c["id"] for c in clientes}
    mapa_negocios = {f"[{n['id']}] {n['titulo']}": n["id"] for n in negocios}

    with st.form("form_nova_atividade", clear_on_submit=True):
        st.subheader("Registrar nova atividade")
        a1, a2 = st.columns(2)
        tipo        = a1.selectbox("Tipo *", TIPOS)
        status_atv  = a2.selectbox("Status", STATUS)
        descricao   = st.text_input("Descrição *", placeholder="Ex.: Ligar para apresentar proposta")
        a3, a4      = st.columns(2)
        cli_label   = a3.selectbox("Cliente", ["— Nenhum —"] + list(mapa_clientes.keys()))
        neg_label   = a4.selectbox("Negócio", ["— Nenhum —"] + list(mapa_negocios.keys()))
        a5, a6      = st.columns(2)
        responsavel = a5.text_input("Responsável", placeholder="Nome do responsável")
        data_atv    = a6.date_input("Data da atividade")
        submitted   = st.form_submit_button("💾 Salvar Atividade", use_container_width=True)

        if submitted:
            if not descricao.strip():
                st.error("O campo **Descrição** é obrigatório.")
            else:
                criar_atividade(dict(
                    tipo=tipo,
                    descricao=descricao.strip(),
                    cliente_id=mapa_clientes.get(cli_label),
                    negocio_id=mapa_negocios.get(neg_label),
                    responsavel=responsavel,
                    data_atividade=str(data_atv),
                    status=status_atv,
                ))
                st.success("✅ Atividade registrada com sucesso!")
                st.rerun()

# ── Gerenciar ─────────────────────────────────────────────────────────────────
with tab_gerenciar:
    atividades = listar_atividades()
    if not atividades:
        st.info("Nenhuma atividade para gerenciar.")
    else:
        opcoes = {
            f"[{a['id']}] {ICONES.get(a['tipo'],'📌')} {a['descricao'] or a['tipo']} · {a['status']}": a
            for a in atividades
        }
        sel  = st.selectbox("Selecione a atividade", list(opcoes.keys()))
        atv  = opcoes[sel]

        col_s, col_d = st.columns(2)
        novo_status = col_s.selectbox(
            "Alterar status",
            STATUS,
            index=STATUS.index(atv["status"]) if atv["status"] in STATUS else 0,
        )
        if col_s.button("💾 Atualizar Status", use_container_width=True):
            atualizar_status_atividade(atv["id"], novo_status)
            st.success(f"✅ Status atualizado para **{novo_status}**!")
            st.rerun()

        if col_d.button("🗑️ Excluir Atividade", use_container_width=True, type="secondary"):
            deletar_atividade(atv["id"])
            st.warning("🗑️ Atividade excluída.")
            st.rerun()
