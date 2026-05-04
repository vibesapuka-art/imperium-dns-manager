import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js
from modules.searcher import run_sequential_search

# Configuração da página para aproveitar o espaço do navegador
st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Painel de Controle Imperium TV")
st.markdown("---")

# Sidebar - Credenciais e Performance
with st.sidebar:
    st.header("🔑 Acesso ADM")
    usuario_input = st.text_input("Usuário (User)", placeholder="Ex: 86768761454")
    senha_input = st.text_input("Senha (Pass)", type="password")
    st.divider()
    st.subheader("⚙️ Configurações")
    threads_opt = st.slider("Velocidade Verificação (Threads)", 10, 100, 40)
    timeout_opt = st.slider("Timeout (seg)", 1, 15, 7)

# Definição das Abas
tab1, tab2, tab3 = st.tabs(["🚀 Verificação", "📄 Exportar dns.js", "🔍 Localizar Conteúdo"])

# --- ABA 1: VERIFICAÇÃO DE DNS ---
with tab1:
    col_file, col_text = st.columns(2)
    with col_file:
        st.subheader("📁 Upload de Arquivo")
        file = st.file_uploader("Upload arquivo .txt", type="txt")
    with col_text:
        st.subheader("⌨️ Entrada Manual")
        manual_input = st.text_area("Cole os DNS (um por linha)", height=68)

    if st.button("▶️ Iniciar Teste de Login"):
        dns_totais = []
        if file:
            dns_totais.extend([d.strip() for d in file.read().decode("utf-8").splitlines() if d.strip()])
        if manual_input:
            dns_totais.extend([d.strip() for d in manual_input.splitlines() if d.strip()])
        
        dns_list = list(dict.fromkeys(dns_totais))

        if not usuario_input or not senha_input:
            st.error("⚠️ Preencha o Usuário e a Senha na barra lateral!")
        elif not dns_list:
            st.warning("⚠️ Insira ao menos um DNS para testar.")
        else:
            with st.spinner(f"Validando {len(dns_list)} servidores..."):
                sucessos = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, timeout_opt)
                
                # Separa os sucessos das falhas
                set_sucessos = {s['dns'] for s in sucessos}
                falhas = [d for d in dns_list if (d if d.startswith('http') else 'http://'+d).rstrip('/') not in set_sucessos]
                
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

# --- ABA 2: EXPORTAR DNS.JS ---
with tab2:
    if 'res_finais' in st.session_state and st.session_state['res_finais']:
        st.subheader("Configuração dns.js")
        js_output = build_dns_js(st.session_state['res_finais'])
        st.code(js_output, language="javascript")
        st.download_button("💾 Baixar dns.js", js_output, "dns.js")
    else:
        st.info("💡 Realize a Verificação na Aba 1 para gerar o arquivo.")

# --- ABA 3: LOCALIZAR CONTEÚDO (SEQUENCIAL) ---
with tab3:
    st.subheader("🔍 Localizador de Filmes/Séries")
    st.info("A busca é feita um por um nos servidores ativos para garantir estabilidade e precisão.")
    
    busca_query = st.text_input("Digite o nome do filme ou série", placeholder="Ex: Deadpool")
    
    dns_online = []
    if 'res_finais' in st.session_state:
        dns_online = [item['dns'] for item in st.session_state['res_finais']]

    if st.button("🔎 Iniciar Busca Precisa"):
        if not busca_query or len(busca_query) < 3:
            st.warning("⚠️ Digite um termo com pelo menos 3 letras.")
        elif not dns_online:
            st.error("⚠️ Valide seus DNS na Aba 1 primeiro para saber quais estão online.")
        else:
            progresso_busca = st.progress(0)
            texto_status = st.empty()
            
            # Realiza a busca um por um
            achados = run_sequential_search(
                dns_online, 
                usuario_input, 
                senha_input, 
                busca_query, 
                progresso_busca, 
                texto_status
            )
            
            texto_status.empty()
            progresso_busca.empty()
            
            if achados:
                st.success(f"✅ Encontrado em {len(achados)} servidores!")
                for item in achados:
                    with st.expander(f"📍 {item['dns']} ({item['total']} resultados)"):
                        for t in item['encontrados']:
                            st.write(f"🎬 {t}")
                        if item['total'] > 10:
                            st.caption(f"... e mais {item['total'] - 10} resultados.")
            else:
                st.error("❌ Título não encontrado nos servidores ativos.")
