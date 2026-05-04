import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js
from modules.searcher import run_global_search

# Configuração da página para aproveitar o monitor do PC
st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Gerenciador de DNS Imperium TV")
st.markdown("---")

# Sidebar - Configurações de Acesso e Performance
with st.sidebar:
    st.header("🔑 Acesso ADM")
    usuario_input = st.text_input("Usuário (User)", placeholder="Ex: 86768761454")
    senha_input = st.text_input("Senha (Pass)", type="password")
    st.divider()
    st.subheader("⚙️ Performance")
    threads_opt = st.slider("Velocidade (Threads)", 10, 100, 40)
    timeout_opt = st.slider("Timeout (seg)", 1, 15, 7)

# Definição das Abas: Validação, Exportação e a nova de Busca
tab1, tab2, tab3 = st.tabs(["🚀 Verificação", "📄 Exportar dns.js", "🔍 Localizar Conteúdo"])

# --- ABA 1: VERIFICAÇÃO DE DNS ---
with tab1:
    col_file, col_text = st.columns(2)
    with col_file:
        st.subheader("📁 Upload de Arquivo")
        file = st.file_uploader("Upload .txt", type="txt")
    with col_text:
        st.subheader("⌨️ Entrada Manual")
        manual_input = st.text_area("Cole os DNS aqui", height=68)

    if st.button("▶️ Iniciar Teste"):
        # Unificação e limpeza da lista de entrada
        dns_totais = []
        if file:
            dns_totais.extend([d.strip() for d in file.read().decode("utf-8").splitlines() if d.strip()])
        if manual_input:
            dns_totais.extend([d.strip() for d in manual_input.splitlines() if d.strip()])
        
        dns_list = list(dict.fromkeys(dns_totais))

        if not usuario_input or not senha_input:
            st.error("⚠️ Preencha usuário e senha na barra lateral!")
        elif not dns_list:
            st.warning("⚠️ Insira ao menos um DNS para testar.")
        else:
            with st.spinner(f"Processando {len(dns_list)} servidores..."):
                # Realiza o teste de login/status
                sucessos = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, timeout_opt)
                
                # Lógica para identificar falhas (DNS inicial vs DNS que retornaram sucesso)
                set_sucessos = {s['dns'] for s in sucessos}
                falhas = [d for d in dns_list if (d if d.startswith('http') else 'http://'+d).rstrip('/') not in set_sucessos]
                
                # Salva os resultados no estado da sessão para usar nas outras abas
                st.session_state['res_finais'] = sucessos
                st.session_state['falhas'] = falhas

                # Exibição dos resultados em duas colunas (Sucesso vs Falha)
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

# --- ABA 2: EXPORTAÇÃO PARA JAVASCRIPT ---
with tab2:
    if 'res_finais' in st.session_state and st.session_state['res_finais']:
        st.subheader("Configuração dns.js")
        js_output = build_dns_js(st.session_state['res_finais'])
        st.code(js_output, language="javascript")
        st.download_button("💾 Baixar dns.js", js_output, "dns.js")
    else:
        st.info("💡 Execute o teste na Aba 1 para gerar o arquivo.")

# --- ABA 3: LOCALIZAR CONTEÚDO (VOD) ---
with tab3:
    st.subheader("🔍 Buscar Filmes/Séries")
    st.info("Pesquise títulos nos catálogos dos servidores que passaram no teste de verificação.")
    
    busca_query = st.text_input("Digite o nome do conteúdo", placeholder="Ex: Deadpool, Avengers...")
    
    # Recupera apenas os DNS que estão online para a busca
    dns_online_para_busca = []
    if 'res_finais' in st.session_state:
        dns_online_para_busca = [item['dns'] for item in st.session_state['res_finais']]

    if st.button("🔎 Pesquisar nos Ativos"):
        if not busca_query:
            st.warning("⚠️ Digite um termo para busca.")
        elif not dns_online_para_busca:
            st.error("⚠️ Nenhum DNS ativo encontrado. Valide a lista na Aba 1 primeiro.")
        else:
            with st.spinner(f"Vasculhando {len(dns_online_para_busca)} servidores..."):
                achados = run_global_search(dns_online_para_busca, usuario_input, senha_input, busca_query, threads_opt)
                
                if achados:
                    st.success(f"Encontrado em {len(achados)} servidores!")
                    for item in achados:
                        with st.expander(f"📍 {item['dns']} ({item['total']} resultados)"):
                            for titulo in item['encontrados']:
                                st.write(f"- {titulo}")
                            if item['total'] > 10:
                                st.caption(f"... e mais {item['total'] - 10} resultados.")
                else:
                    st.error("❌ O título não foi encontrado em nenhum dos servidores ativos.")
