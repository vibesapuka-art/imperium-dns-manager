import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js

st.set_page_config(page_title="Imperium M3U Master", layout="wide")

# Interface Principal
st.title("🌐 Validador de Listas Imperium TV")
st.markdown("---")

# Sidebar - Credenciais e Performance
with st.sidebar:
    st.header("🔑 Acesso Administrativo")
    usuario_input = st.text_input("Usuário (User)", placeholder="Ex: 86768761454")
    senha_input = st.text_input("Senha (Pass)", type="password", placeholder="Ex: 59177356817")
    
    st.divider()
    st.subheader("⚙️ Performance")
    threads_opt = st.slider("Velocidade (Threads)", 10, 100, 40)
    timeout_opt = st.slider("Timeout (segundos)", 1, 15, 7)

# Abas do Sistema
tab1, tab2 = st.tabs(["🚀 Verificação", "📄 Gerar dns.js"])

with tab1:
    col_file, col_text = st.columns(2)
    
    with col_file:
        st.subheader("📁 Upload de Arquivo")
        file = st.file_uploader("Suba sua lista .txt", type="txt")
    
    with col_text:
        st.subheader("⌨️ Entrada Manual")
        manual_input = st.text_area("Cole os DNS aqui (um por linha)", height=150, placeholder="http://exemplo.com")

    if st.button("▶️ Iniciar Teste em Massa"):
        # Unifica as duas entradas
        dns_list = []
        
        # Pega do arquivo se existir
        if file:
            conteudo = file.read().decode("utf-8")
            dns_list.extend([d.strip() for d in conteudo.splitlines() if d.strip()])
            
        # Pega da caixa de texto se existir
        if manual_input:
            dns_list.extend([d.strip() for d in manual_input.splitlines() if d.strip()])
            
        # Remove duplicados mantendo a ordem
        dns_list = list(dict.fromkeys(dns_list))

        if not usuario_input or not senha_input:
            st.error("⚠️ Você precisa preencher o Usuário e a Senha na barra lateral!")
        elif not dns_list:
            st.warning("⚠️ Forneça ao menos um DNS (via arquivo ou digitando).")
        else:
            with st.spinner(f"Validando {len(dns_list)} servidores..."):
                resultados = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, timeout_opt)
                st.session_state['res_finais'] = resultados
                
                if resultados:
                    st.success(f"✅ {len(resultados)} servidores ativos encontrados!")
                    df = pd.DataFrame(resultados)
                    # Exibe o DNS e a data de expiração para controle
                    st.table(df[['dns', 'status', 'expira']])
                else:
                    st.error("❌ Nenhum DNS da lista respondeu com sucesso.")

with tab2:
    if 'res_finais' in st.session_state and st.session_state['res_finais']:
        st.subheader("Visualização do dns.js")
        js_output = build_dns_js(st.session_state['res_finais'])
        
        st.code(js_output, language="javascript")
        
        st.download_button(
            label="💾 Baixar Arquivo dns.js",
            data=js_output,
            file_name="dns.js",
            mime="application/javascript"
        )
    else:
        st.info("💡 Realize um teste primeiro para gerar o arquivo de exportação.")
