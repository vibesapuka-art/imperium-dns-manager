import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js
from modules.searcher import run_sequential_search

st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Painel de Controle Imperium TV")

# Sidebar
with st.sidebar:
    st.header("🔑 Acesso ADM")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    st.divider()
    threads_opt = st.slider("Velocidade Verificação", 10, 100, 40)
    timeout_opt = st.slider("Timeout (seg)", 1, 15, 7)

tab1, tab2, tab3 = st.tabs(["🚀 Verificação", "📄 Exportar dns.js", "🔍 Localizar Conteúdo"])

# ... (Tab 1 e Tab 2 permanecem com seu código anterior) ...

with tab3:
    st.subheader("🔍 Localizador de Conteúdo Inteligente")
    
    # Novo Filtro: Escolha o que buscar
    modo_busca = st.radio("O que deseja procurar?", ["Filmes", "Séries"], horizontal=True)
    busca_query = st.text_input(f"Digite o nome do {modo_busca[:-1]}", placeholder="Ex: Deadpool ou Game of Thrones")
    
    dns_online = [item['dns'] for item in st.session_state.get('res_finais', [])]

    if st.button(f"🔎 Pesquisar {modo_busca}"):
        if not busca_query or len(busca_query) < 3:
            st.warning("⚠️ Digite um termo com pelo menos 3 letras.")
        elif not dns_online:
            st.error("⚠️ Valide seus DNS na Aba 1 primeiro.")
        else:
            progresso_busca = st.progress(0)
            texto_status = st.empty()
            
            achados = run_sequential_search(
                dns_online, usuario_input, senha_input, busca_query, modo_busca, progresso_busca, texto_status
            )
            
            texto_status.empty()
            progresso_busca.empty()
            
            if achados:
                st.success(f"✅ Localizado em {len(achados)} servidores!")
                for item in achados:
                    with st.expander(f"📍 {item['dns']} ({item['total']} resultados)"):
                        for t in item['encontrados']:
                            st.write(t)
            else:
                st.error(f"❌ Nenhuma {modo_busca.lower()} encontrada com esse nome.")
