import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js
from modules.searcher import run_sequential_search

# Configuração de Layout
st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Gerenciador de DNS Imperium TV")
st.markdown("---")

# Sidebar - Configurações Gerais
with st.sidebar:
    st.header("🔑 Acesso ADM")
    usuario_input = st.text_input("Usuário (User)", placeholder="Ex: 86768761454")
    senha_input = st.text_input("Senha (Pass)", type="password")
    st.divider()
    st.subheader("⚙️ Performance")
    threads_opt = st.slider("Velocidade (Threads)", 10, 100, 40)
    timeout_opt = st.slider("Timeout (seg)", 1, 15, 7)

# Estrutura de Abas Protegida
tab1, tab2, tab3 = st.tabs(["🚀 Verificação", "📄 Exportar dns.js", "🔍 Localizar Conteúdo"])

# --- ABA 1: VERIFICAÇÃO ---
with tab1:
    col_file, col_text = st.columns(2)
    with col_file:
        file = st.file_uploader("Upload .txt", type="txt")
    with col_text:
        manual_input = st.text_area("Entrada Manual", height=68)

    if st.button("▶️ Iniciar Teste"):
        dns_totais = []
        if file:
            dns_totais.extend([d.strip() for d in file.read().decode("utf-8").splitlines() if d.strip()])
        if manual_input:
            dns_totais.extend([d.strip() for d in manual_input.splitlines() if d.strip()])
        
        dns_list = list(dict.fromkeys(dns_totais))

        if not usuario_input or not senha_input:
            st.error("⚠️ Preencha usuário e senha!")
        elif not dns_list:
            st.warning("⚠️ Insira ao menos um DNS.")
        else:
            with st.spinner(f"Processando {len(dns_list)} servidores..."):
                sucessos = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, timeout_opt)
                
                # Cálculo de falhas
                set_sucessos = {s['dns'] for s in sucessos}
                falhas = [d for d in dns_list if (d if d.startswith('http') else 'http://'+d).rstrip('/') not in set_sucessos]
                
                # Salva no estado da sessão para não perder os dados
                st.session_state['res_finais'] = sucessos
                st.session_state['falhas'] = falhas

                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.success(f"✅ Ativos: {len(sucessos)}")
                    if sucessos:
                        df_suc = pd.DataFrame(sucessos)
                        st.dataframe(df_suc[['dns', 'expira']], use_container_width=True)
                
                with col_res2:
                    st.error(f"❌ Sem Sucesso: {len(falhas)}")
                    if falhas:
                        st.text_area("DNS Offline ou Inválidos:", value="\n".join(falhas), height=300)

# --- ABA 2: EXPORTAR JS ---
with tab2:
    if 'res_finais' in st.session_state and st.session_state['res_finais']:
        st.subheader("Configuração dns.js")
        js_output = build_dns_js(st.session_state['res_finais'])
        st.code(js_output, language="javascript")
        st.download_button("💾 Baixar dns.js", js_output, "dns.js")
    else:
        st.info("💡 Execute o teste na Aba 1 para gerar o arquivo.")

# --- ABA 3: BUSCA DE CONTEÚDO ---
with tab3:
    st.subheader("🔍 Localizador de Filmes/Séries")
    
    col_mode, col_query = st.columns([1, 3])
    with col_mode:
        modo = st.radio("Tipo:", ["Filmes", "Séries"])
    with col_query:
        query = st.text_input(f"Nome do {modo[:-1]}:", placeholder="Digite para buscar...")

    # Só busca nos DNS que passaram no teste da Aba 1
    dns_ativos = [item['dns'] for item in st.session_state.get('res_finais', [])]

    if st.button(f"🔎 Pesquisar {modo}"):
        if not query or len(query) < 3:
            st.warning("⚠️ Digite um termo com pelo menos 3 letras.")
        elif not dns_ativos:
            st.error("⚠️ Primeiro valide seus DNS na Aba 1.")
        else:
            barra = st.progress(0)
            txt_status = st.empty()
            
            resultados_busca = run_sequential_search(
                dns_ativos, usuario_input, senha_input, query, modo, barra, txt_status
            )
            
            txt_status.empty()
            barra.empty()
            
            if resultados_busca:
                st.success(f"✅ Encontrado em {len(resultados_busca)} servidores!")
                for r in resultados_busca:
                    with st.expander(f"📍 {r['dns']} ({r['total']} resultados)"):
                        for item in r['encontrados']:
                            st.write(item)
            else:
                st.error(f"❌ Nenhum resultado para '{query}' nos servidores ativos.")
