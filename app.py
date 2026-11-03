import streamlit as st
import pandas as pd
from datetime import datetime
import libsql_client
import plotly.express as px

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E TEMA HERMÉTICO
# ==========================================
st.set_page_config(page_title="Auditoria da Alma", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    /* Estética Hermética / Alquímica */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #d4af37 !important; /* Dourado */
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        background-color: #d4af37;
        color: #0a0a0a;
        font-weight: bold;
        border: 1px solid #b8860b;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #b8860b;
        color: #ffffff;
        box-shadow: 0px 0px 10px #d4af37;
    }
    .stSelectbox label, .stSlider label, .stTextInput label, .stRadio label {
        color: #b8860b !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LIGAÇÃO AO BANCO DE DADOS TURSO
# ==========================================
def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

@st.cache_resource
def get_db_client():
    url = get_secret("TURSO_DATABASE_URL", "file:banco_local.db").strip().strip("'\"")
    token = get_secret("TURSO_AUTH_TOKEN", "").strip().strip("'\"")
    
    # libsql-client utiliza o esquema 'file:' para bancos SQLite locais
    if url.startswith("sqlite:///"):
        url = url.replace("sqlite:///", "file:")
    elif url.startswith("sqlite://"):
        url = url.replace("sqlite://", "file:")
    
    # Converte libsql:// para https:// para evitar bloqueios de WebSocket (WSServerHandshakeError)
    # na nuvem do Streamlit. O Turso suporta requisições HTTP seguras nativamente.
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")

    if url.startswith("file:"):
        client = libsql_client.create_client_sync(url)
    else:
        client = libsql_client.create_client_sync(url=url, auth_token=token)
    
    client.execute("""
        CREATE TABLE IF NOT EXISTS auditoria_mental (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            contexto TEXT,
            fadiga INTEGER,
            tema TEXT,
            categoria TEXT,
            somatizacao TEXT,
            resposta TEXT,
            duracao REAL
        )
    """)
    return client

try:
    db = get_db_client()
except Exception as e:
    st.error("⚠️ **Falha de Conexão com o Banco de Dados (Turso)**")
    st.warning(
        f"**Detalhe do Erro:** `{e}`\n\n"
        "**Como verificar no Streamlit Cloud:**\n"
        "1. No canto inferior direito, clique em **Manage app** > **⋮** > **Settings** > **Secrets**.\n"
        "2. Confira se as variáveis estão no formato:\n"
        "```toml\n"
        "TURSO_DATABASE_URL = \"https://seu-banco-seu-usuario.turso.io\"\n"
        "TURSO_AUTH_TOKEN = \"seu_token_aqui\"\n"
        "```\n"
        "*(Dica: use `https://` em vez de `libsql://` para maior estabilidade)*."
    )
    st.stop()

# ==========================================
# INTERFACE DO UTILIZADOR
# ==========================================
st.title("⚖️ Tribunal de Cheshbon HaNefesh")
st.markdown("*Solve et Coagula: O mapeamento alquímico da mente.*")

tab_registro, tab_dashboard = st.tabs(["👁️ O Observador (Registar)", "📊 A Balança (Análise)"])

with tab_registro:
    with st.form("form_auditoria"):
        st.subheader("1. O Cenário")
        contexto = st.selectbox("Onde a mente foi interceptada?", [
            "Casa da Sogra",
            "Casa de Parentes",
            "Clínicas / Consultórios",
            "Estudos (Direito / Contábeis)",
            "Igreja Assembleia de Deus (Culto)",
            "Lazer",
            "Mercado / Compras",
            "Outros Locais",
            "Parque / Ar Livre",
            "Plantão PMPR (Cartório TCO)",
            "Pós-Plantão (Exaustão / Trânsito)",
            "Tempo com a Família (Esposa/Filha)",
            "TV & Celular (Telas / Redes)",
            "Web Coding / Projetos IA"
        ])
        
        fadiga = st.slider("Carga Miasmática / Fadiga Físico-Mental (1-5)", 1, 5, 3)

        st.subheader("2. A Petição do Promotor (O Ruído)")
        tema = st.selectbox("Tema do Pensamento Intrusivo", [
            "Vontade de julgar (Lashon Hará) / Crítica",
            "Carga Tóxica / Raiva de Ocorrência Policial",
            "Debugging Mental (Revisando TCO/Código sem fim)",
            "Nostalgia / Fuga para o passado seguro",
            "Sequestro Dopaminérgico / Luxúria (Conteúdo Adulto)",
            "Frustração com a Hierarquia Militar / Ego Ferido",
            "Ruído Catastrófico e Aleatório"
        ])
        
        categoria = st.selectbox("Classificação Cabalística/Hermética", [
            "Yesh (Ego defendendo status ou razão)", 
            "Mão Fechada (Fuga / Ilusão de Controle)", 
            "A Sedutora (Dopamina / Vício)",
            "Mazik (Ruído puro de exaustão)"
        ])
        
        somatizacao = st.text_input("Somatização Física (Registo do Corpo)", placeholder="Ex: Mandíbula travada, peito pesado.")
        
        st.subheader("3. O Veredito (A Vontade)")
        resposta = st.radio("Ação Tomada no Tribunal Mental", [
            "Bitul (Corte Hermético / Não-Engajamento imediato)", 
            "Alquimia da Centelha (Transformou raiva em foco técnico no TCO)",
            "Interação (Debateu com o pensamento, gerou atrito)", 
            "Concessão (Cedeu: Julgou, fofocou ou buscou dopamina)"
        ])
        
        duracao = st.number_input("Duração do Inquérito (Minutos sequestrados)", min_value=0.0, step=0.5)
        
        submit = st.form_submit_button("Arquivar Inquérito no Turso")
        
        if submit:
            timestamp = datetime.now().isoformat()
            somat_final = somatizacao if somatizacao else "Nenhuma"
            
            db.execute(
                """INSERT INTO auditoria_mental 
                (timestamp, contexto, fadiga, tema, categoria, somatizacao, resposta, duracao) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (timestamp, contexto, fadiga, tema, categoria, somat_final, resposta, duracao)
            )
            st.success("O pensamento foi dissecado e arquivado. Ordem restaurada.")

with tab_dashboard:
    resultado = db.execute("SELECT * FROM auditoria_mental")
    
    if not resultado.rows:
        st.info("Nenhum registo encontrado nos arquivos cósmicos.")
    else:
        colunas = ["id", "timestamp", "contexto", "fadiga", "tema", "categoria", "somatizacao", "resposta", "duracao"]
        df = pd.DataFrame(resultado.rows, columns=colunas)
        
        st.subheader("Resumo Alquímico")
        total = len(df)
        sucessos_corte = len(df[df["resposta"].str.contains("Bitul")])
        sucessos_alquimia = len(df[df["resposta"].str.contains("Alquimia")])
        concessoes = len(df[df["resposta"].str.contains("Concessão")])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Intrusões Totais", total)
        c2.metric("Vitórias (Corte/Alquimia)", sucessos_corte + sucessos_alquimia)
        c3.metric("Concessões (Toxidade)", concessoes)
        
        st.divider()
        
        st.markdown("### 📈 Gatilhos por Nível de Exaustão (Fadiga vs Frequência)")
        fadiga_counts = df['fadiga'].value_counts().sort_index()
        st.bar_chart(fadiga_counts, color="#d4af37")

        st.markdown("### ⚖️ O Veredito do Tribunal (Suas Respostas Volitivas)")
        resposta_counts = df['resposta'].value_counts()
        st.bar_chart(resposta_counts, color="#b8860b")

        st.divider()

        st.markdown("### ⚔️ Relação: Pensamento Intrusivo vs. Ação Tomada")
        st.caption("Mapeamento do combate: veja onde você aplicou domínio (Bitul/Alquimia) ou onde houve atrito/concessão para cada ruído mental.")
        
        # Agrupamento para gráfico empilhado
        cruzamento = df.groupby(['tema', 'resposta']).size().reset_index(name='contagem')
        
        # Paleta com significado alquímico:
        # Bitul: Dourado (#d4af37)
        # Alquimia: Ciano / Esmeralda (#00b4d8)
        # Interação: Âmbar (#f4a261)
        # Concessão: Vermelho Carmesim (#e63946)
        color_discrete_map = {}
        for r in df['resposta'].unique():
            if "Bitul" in r:
                color_discrete_map[r] = "#d4af37"
            elif "Alquimia" in r:
                color_discrete_map[r] = "#00b4d8"
            elif "Interação" in r:
                color_discrete_map[r] = "#f4a261"
            elif "Concessão" in r:
                color_discrete_map[r] = "#e63946"
            else:
                color_discrete_map[r] = "#888888"

        fig = px.bar(
            cruzamento,
            y="tema",
            x="contagem",
            color="resposta",
            orientation="h",
            barmode="stack",
            color_discrete_map=color_discrete_map,
            labels={"tema": "Tema do Ruído", "contagem": "Ocorrências", "resposta": "Ação Tomada"}
        )

        fig.update_layout(
            plot_bgcolor="#0a0a0a",
            paper_bgcolor="#0a0a0a",
            font=dict(color="#e0e0e0", family="Courier New"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(title="Quantidade de Batalhas", gridcolor="#222222"),
            yaxis=dict(title="", gridcolor="#222222", autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Matriz tabular de ocorrências
        st.markdown("#### 📋 Matriz Numérica de Batalhas")
        matriz = pd.crosstab(df['tema'], df['resposta'], margins=True, margins_name="Total")
        st.dataframe(matriz, use_container_width=True)

        with st.expander("📖 Manual Tático: Guia de Combate por Tipo de Pensamento"):
            st.markdown("""
            | Pensamento Intrusivo | Categoria | Ação Soberana Recomendada | Postura Prática |
            | :--- | :--- | :--- | :--- |
            | **Vontade de julgar (Lashon Hará)** | *Yesh* (Ego) | **Bitul** (Corte) | Silêncio intencional: *"Não sou o juiz do universo."* |
            | **Carga Tóxica / Raiva de Ocorrência** | *Mazik* (Veneno) | **Alquimia da Centelha** | Transmutar a adrenalina em precisão cirúrgica na redação do TCO. |
            | **Debugging Mental sem fim** | *Mão Fechada* (Controle) | **Bitul** (Entrega) | Encerrar o ciclo: *"Dever cumprido com excelência técnica."* |
            | **Nostalgia / Fuga para o passado** | *Mão Fechada* (Medo) | **Bitul** (Presença) | Ancorar no agora: *"O passado não existe; foco na missão de hoje."* |
            | **Sequestro Dopaminérgico / Luxúria** | *A Sedutora* (Alívio) | **Bitul** (Não-Engajamento) | Corte radical: afastar o celular, mudar de ambiente físico. |
            | **Frustração com Hierarquia / Ego** | *Yesh* (Ferida) | **Alquimia da Centelha** | Converter contrariedade em combustível para estudos (Direito/Contábeis). |
            | **Ruído Catastrófico e Aleatório** | *Mazik* (Exaustão) | **Bitul** (Desdém) | Reconhecer o biológico: *"Apenas sono e fadiga falando."* Ignorar. |
            """)

