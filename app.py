import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js
from modules.searcher import run_global_search

st.set_page_config(page_title="Imperium DNS Manager", layout="wide")

st.title("🌐 Painel de Controle Imperium TV")

# Sidebar - Credenciais Master
with st.sidebar:
    st.header("🔑 Credenciais Master")
    user_adm = st.text_input("Usuário")
    pass_adm = st.text_input("Senha", type="password")
    st.divider()
    threads = st.slider("Threads (Velocidade)", 10, 100, 30)

# Abas
tab1, tab2, tab3 = st.tabs(["🚀 Validar DNS", "📄 Gerar dns.js", "🔍 Localizar Conteúdo"])

# ... (Código da Tab1 e Tab2 permanecem iguais aos anteriores) ...

with tab3:
    st.subheader("Buscar Filmes/Séries nos Servidores")
    st.info("Esta função varre o catálogo de todos os DNS ativos para encontrar um título específico.")
    
    busca_query = st.text_input("O que você está procurando?", placeholder="Ex: Deadpool, Avengers...")
    
    # Usamos a lista de sucessos do teste anterior para não buscar em DNS offline
    dns_para_busca = []
    if 'res_finais' in st.session_state:
        dns_para_busca = [item['dns'] for item in st.session_state['res_finais']]

    if st.button("🔎 Pesquisar em Todos os Servidores"):
        if not busca_query:
            st.warning("Digite um nome para buscar.")
        elif not dns_para_busca:
            st.error("Primeiro valide seus DNS na Tab 1 para saber quais estão online.")
        else:
            with st.spinner(f"Vasculhando catálogos em {len(dns_para_busca)} servidores..."):
                achados = run_global_search(dns_para_busca, user_adm, pass_adm, busca_query, threads)
                
                if achados:
                    st.success(f"Conteúdo encontrado em {len(achados)} servidores!")
                    for item in achados:
                        with st.expander(f"📍 {item['dns']} ({item['total']} resultados)"):
                            for titulo in item['encontrados']:
                                st.write(f"- {titulo}")
                            if item['total'] > 10:
                                st.caption(f"... e mais {item['total'] - 10} resultados.")
                else:
                    st.error("Nenhum servidor da sua lista possui esse título no momento.")
