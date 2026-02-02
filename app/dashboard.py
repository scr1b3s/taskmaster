import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Taskmaster Review", layout="wide")

# Conexão com o Banco (Leitura)
# Pegamos o caminho absoluto do DB na raiz do projeto
base_dir = os.getcwd()
db_path = os.path.join(base_dir, "focuspipe.db")
engine = create_engine(f"sqlite:///{db_path}")

def load_data():
    """Carrega os dados brutos do SQLite para DataFrames do Pandas."""
    try:
        # 1. Carrega Entradas de Tempo (com join em Tasks e Domains)
        query_time = """
            SELECT 
                te.start_time, 
                te.duration_seconds, 
                t.title as task_title, 
                d.name as domain_name,
                d.color_hex
            FROM timeentry te
            JOIN task t ON te.task_id = t.google_task_id
            LEFT JOIN domain d ON t.domain_id = d.id
            WHERE te.end_time IS NOT NULL
        """
        df_time = pd.read_sql(query_time, engine)
        
        # 2. Carrega Interrupções
        query_int = """
            SELECT 
                i.occurred_at, 
                i.reason, 
                t.title as task_title
            FROM interruption i
            JOIN task t ON i.task_id = t.google_task_id
        """
        df_int = pd.read_sql(query_int, engine)
        
        return df_time, df_int
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- UI DO DASHBOARD ---
st.title("🧠 Taskmaster: Weekly Review")
st.markdown("Uma visão honesta sobre onde seu tempo está indo.")

df_time, df_int = load_data()

if df_time.empty:
    st.warning("Ainda não há dados de tempo registrados. Vá focar!")
else:
    # Converter segundos para minutos/horas
    df_time["minutes"] = df_time["duration_seconds"] / 60
    df_time["hours"] = df_time["minutes"] / 60
    
    # KPIs do Topo
    total_hours = df_time["hours"].sum()
    total_sessions = len(df_time)
    avg_session = df_time["minutes"].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas Totais Focadas", f"{total_hours:.1f}h")
    col2.metric("Sessões de Foco", total_sessions)
    col3.metric("Média por Sessão", f"{avg_session:.0f} min")
    
    st.divider()

    # LINHA 1: Onde foi o tempo?
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Tempo por Domínio")
        # Agrupa por domínio
        df_domain = df_time.groupby("domain_name")["hours"].sum().reset_index()
        
        fig_domain = px.bar(
            df_domain, 
            x="domain_name", 
            y="hours", 
            color="domain_name",
            text_auto='.1f', # type: ignore
            title="Horas Dedicadas por Área"
        )
        st.plotly_chart(fig_domain, use_container_width=True)
        
    with c2:
        st.subheader("Top Tarefas")
        # Agrupa por Tarefa
        df_task = df_time.groupby("task_title")["minutes"].sum().reset_index().sort_values("minutes", ascending=False).head(5)
        st.dataframe(
            df_task.style.format({"minutes": "{:.0f}"}), 
            hide_index=True, 
            use_container_width=True
        )

    st.divider()

    # LINHA 2: Análise de Interrupções
    st.subheader("🕵️ Análise de Dispersão")
    
    if df_int.empty:
        st.info("Nenhuma interrupção registrada! Você é um monge zen. 🧘")
    else:
        ic1, ic2 = st.columns(2)
        
        with ic1:
            # Gráfico de Pizza dos Motivos
            df_reasons = df_int["reason"].value_counts().reset_index()
            df_reasons.columns = ["Motivo", "Contagem"]
            
            fig_int = px.pie(
                df_reasons, 
                values="Contagem", 
                names="Motivo", 
                hole=0.4,
                title="Principais Causas de Interrupção"
            )
            st.plotly_chart(fig_int, use_container_width=True)
            
        with ic2:
            st.write("### Últimas Interrupções")
            st.dataframe(df_int.sort_values("occurred_at", ascending=False).head(10), hide_index=True)