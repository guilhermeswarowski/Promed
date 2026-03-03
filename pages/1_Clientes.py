import streamlit as st
import pandas as pd
from database import listar_clientes, criar_cliente, atualizar_cliente, deletar_cliente

st.set_page_config(page_title="Clientes · Promed CRM", page_icon="👥", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a1f36; }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📋 Menu")
    st.page_link("app.py",              label="🏠  Dashboard")
    st.page_link("pages/1_Clientes.py",   label="👥  Clientes")
    st.page_link("pages/2_Negocios.py",   label="💼  Negócios")
    st.page_link("pages/3_Atividades.py", label="📅  Atividades")
    st.markdown("---")
    st.markdown(
        "<div style='position:fixed;bottom:16px;font-size:.75rem;color:#64748b;'>© 2026 Promed · v1.0</div>",
        unsafe_allow_html=True,
    )

st.title("👥 Clientes")

# ─── Abas ─────────────────────────────────────────────────────────────────────
tab_lista, tab_novo, tab_editar = st.tabs(["📋 Lista", "➕ Novo Cliente", "✏️ Editar / Excluir"])

STATUS_OPT  = ["Ativo", "Inativo", "Lead", "Prospect"]
ORIGEM_OPT  = ["Indicação", "Site", "Redes Sociais", "Email Marketing", "Evento", "Outro"]

# ── Lista ──────────────────────────────────────────────────────────────────────
with tab_lista:
    clientes = listar_clientes()

    col_search, col_status = st.columns([3, 1])
    with col_search:
        busca = st.text_input("🔍 Buscar por nome, email ou empresa", "")
    with col_status:
        filtro_status = st.selectbox("Filtrar por status", ["Todos"] + STATUS_OPT)

    if clientes:
        df = pd.DataFrame(clientes)
        if busca:
            mask = (
                df["nome"].str.contains(busca, case=False, na=False) |
                df["email"].str.contains(busca, case=False, na=False) |
                df["empresa"].str.contains(busca, case=False, na=False)
            )
            df = df[mask]
        if filtro_status != "Todos":
            df = df[df["status"] == filtro_status]

        df["criado_em"] = pd.to_datetime(df["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
        df_show = df[["id","nome","email","telefone","empresa","status","origem","criado_em"]].copy()
        df_show.columns = ["ID","Nome","Email","Telefone","Empresa","Status","Origem","Criado em"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        st.caption(f"{len(df_show)} cliente(s) encontrado(s)")
    else:
        st.info("Nenhum cliente cadastrado. Use a aba **Novo Cliente** para adicionar.")

# ── Novo Cliente ───────────────────────────────────────────────────────────────
with tab_novo:
    with st.form("form_novo_cliente", clear_on_submit=True):
        st.subheader("Cadastrar novo cliente")
        c1, c2 = st.columns(2)
        nome     = c1.text_input("Nome *", placeholder="Ex.: João Silva")
        email    = c2.text_input("Email",  placeholder="joao@email.com")
        c3, c4   = st.columns(2)
        telefone = c3.text_input("Telefone", placeholder="(11) 99999-9999")
        empresa  = c4.text_input("Empresa",  placeholder="Nome da empresa")
        c5, c6   = st.columns(2)
        status   = c5.selectbox("Status", STATUS_OPT)
        origem   = c6.selectbox("Origem", ORIGEM_OPT)
        notas    = st.text_area("Notas", placeholder="Observações sobre o cliente...")
        submitted = st.form_submit_button("💾 Salvar Cliente", use_container_width=True)

        if submitted:
            if not nome.strip():
                st.error("O campo **Nome** é obrigatório.")
            else:
                criar_cliente(dict(
                    nome=nome.strip(), email=email, telefone=telefone,
                    empresa=empresa, status=status, origem=origem, notas=notas
                ))
                st.success(f"✅ Cliente **{nome}** cadastrado com sucesso!")
                st.rerun()

# ── Editar / Excluir ──────────────────────────────────────────────────────────
with tab_editar:
    clientes = listar_clientes()
    if not clientes:
        st.info("Nenhum cliente para editar.")
    else:
        opcoes = {f"[{c['id']}] {c['nome']} — {c['empresa'] or '—'}": c for c in clientes}
        sel_label = st.selectbox("Selecione o cliente", list(opcoes.keys()))
        c = opcoes[sel_label]

        with st.form("form_editar_cliente"):
            st.subheader("Editar dados do cliente")
            e1, e2 = st.columns(2)
            nome     = e1.text_input("Nome *",    value=c["nome"])
            email    = e2.text_input("Email",     value=c["email"] or "")
            e3, e4   = st.columns(2)
            telefone = e3.text_input("Telefone",  value=c["telefone"] or "")
            empresa  = e4.text_input("Empresa",   value=c["empresa"] or "")
            e5, e6   = st.columns(2)
            idx_status = STATUS_OPT.index(c["status"]) if c["status"] in STATUS_OPT else 0
            idx_orig   = ORIGEM_OPT.index(c["origem"]) if c["origem"] in ORIGEM_OPT else 0
            status   = e5.selectbox("Status", STATUS_OPT, index=idx_status)
            origem   = e6.selectbox("Origem", ORIGEM_OPT, index=idx_orig)
            notas    = st.text_area("Notas", value=c["notas"] or "")

            col_save, col_del = st.columns(2)
            salvar  = col_save.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            excluir = col_del.form_submit_button("🗑️ Excluir Cliente",   use_container_width=True, type="secondary")

        if salvar:
            if not nome.strip():
                st.error("O campo **Nome** é obrigatório.")
            else:
                atualizar_cliente(c["id"], dict(
                    nome=nome.strip(), email=email, telefone=telefone,
                    empresa=empresa, status=status, origem=origem, notas=notas
                ))
                st.success("✅ Cliente atualizado com sucesso!")
                st.rerun()

        if excluir:
            deletar_cliente(c["id"])
            st.warning(f"🗑️ Cliente **{c['nome']}** excluído.")
            st.rerun()
