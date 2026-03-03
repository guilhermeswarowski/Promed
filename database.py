import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def _get_credentials():
    """Lê credenciais do Streamlit Cloud (secrets.toml) ou do .env local."""
    try:
        import streamlit as st
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return url, key
    except Exception:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise EnvironmentError(
                "Credenciais do Supabase não encontradas.\n"
                "Crie um arquivo .env com SUPABASE_URL e SUPABASE_KEY."
            )
        return url, key


def get_client() -> Client:
    url, key = _get_credentials()
    return create_client(url, key)


def init_db():
    """Testa a conexão com o Supabase ao iniciar o app."""
    get_client().table("clientes").select("id").limit(1).execute()


# ─── CLIENTES ───────────────────────────────────────────────────────────────

def listar_clientes():
    return get_client().table("clientes").select("*").order("criado_em", desc=True).execute().data


def buscar_cliente(cliente_id: int):
    res = get_client().table("clientes").select("*").eq("id", cliente_id).maybe_single().execute()
    return res.data


def criar_cliente(dados: dict):
    get_client().table("clientes").insert(dados).execute()


def atualizar_cliente(cliente_id: int, dados: dict):
    get_client().table("clientes").update(dados).eq("id", cliente_id).execute()


def deletar_cliente(cliente_id: int):
    get_client().table("clientes").delete().eq("id", cliente_id).execute()


# ─── NEGÓCIOS ────────────────────────────────────────────────────────────────

def listar_negocios():
    res = get_client().table("negocios").select("*, clientes(nome)").order("criado_em", desc=True).execute()
    negocios = []
    for n in res.data:
        n["cliente_nome"] = (n.pop("clientes") or {}).get("nome")
        negocios.append(n)
    return negocios


def criar_negocio(dados: dict):
    get_client().table("negocios").insert(dados).execute()


def atualizar_negocio(negocio_id: int, dados: dict):
    get_client().table("negocios").update(dados).eq("id", negocio_id).execute()


def deletar_negocio(negocio_id: int):
    get_client().table("negocios").delete().eq("id", negocio_id).execute()


# ─── ATIVIDADES ──────────────────────────────────────────────────────────────

def listar_atividades():
    res = (
        get_client().table("atividades")
        .select("*, clientes(nome), negocios(titulo)")
        .order("data_atividade", desc=True)
        .execute()
    )
    atividades = []
    for a in res.data:
        a["cliente_nome"]   = (a.pop("clientes") or {}).get("nome")
        a["negocio_titulo"] = (a.pop("negocios") or {}).get("titulo")
        atividades.append(a)
    return atividades


def criar_atividade(dados: dict):
    get_client().table("atividades").insert(dados).execute()


def atualizar_status_atividade(atividade_id: int, status: str):
    get_client().table("atividades").update({"status": status}).eq("id", atividade_id).execute()


def deletar_atividade(atividade_id: int):
    get_client().table("atividades").delete().eq("id", atividade_id).execute()


# ─── MÉTRICAS ────────────────────────────────────────────────────────────────

def metricas_dashboard():
    client = get_client()

    total_clientes       = len(client.table("clientes").select("id").eq("status", "Ativo").execute().data)
    total_negocios       = len(client.table("negocios").select("id").execute().data)
    atividades_pendentes = len(client.table("atividades").select("id").eq("status", "Pendente").execute().data)

    todos_negocios  = client.table("negocios").select("estagio, valor").execute().data
    valor_pipeline  = sum(n["valor"] or 0 for n in todos_negocios if n["estagio"] != "Fechado Ganho")
    receita_fechada = sum(n["valor"] or 0 for n in todos_negocios if n["estagio"] == "Fechado Ganho")

    # Negócios por estágio
    estagios: dict = {}
    for n in todos_negocios:
        e = n["estagio"]
        if e not in estagios:
            estagios[e] = {"estagio": e, "total": 0, "valor": 0.0}
        estagios[e]["total"] += 1
        estagios[e]["valor"] += n["valor"] or 0

    # Clientes por mês (últimos 6)
    todos_clientes = client.table("clientes").select("criado_em").execute().data
    meses: dict = {}
    for c in todos_clientes:
        mes = (c["criado_em"] or "")[:7]
        meses[mes] = meses.get(mes, 0) + 1
    clientes_por_mes = [
        {"mes": k, "total": v}
        for k, v in sorted(meses.items(), reverse=True)
    ][:6]

    return {
        "total_clientes":       total_clientes,
        "total_negocios":       total_negocios,
        "valor_pipeline":       valor_pipeline,
        "receita_fechada":      receita_fechada,
        "atividades_pendentes": atividades_pendentes,
        "negocios_por_estagio": list(estagios.values()),
        "clientes_por_mes":     clientes_por_mes,
    }
