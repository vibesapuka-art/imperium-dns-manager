import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js

st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Validador de Listas Imperium TV")

# Sidebar - Onde você coloca suas credenciais de teste
with st.sidebar:
    st.header("🔑 Credenciais de Teste")
    usuario_input = st.text_input("Digite o Usuário")
    senha_input = st.text_input("Digite a Senha", type="password")
    st.divider()
    threads_opt = st.slider("Velocidade (Threads)", 10, 100, 40)

tab1, tab2 = st.tabs(["📥 Testar DNS", "📄 Gerar dns.js"])

with tab1:
    st.subheader("Suba sua lista de DNS (.txt)")
    file = st.file_uploader("Arraste o arquivo aqui", type="txt")
    
    if st.button("🚀 Iniciar Teste"):
        if file and usuario_input and senha_input:
            conteudo = file.read().decode("utf-8")
            dns_list = [d.strip() for d in conteudo.splitlines() if d.strip()]
            
            with st.spinner("Validando servidores..."):
                resultados = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, 7)
                st.session_state['res_finais'] = resultados
                
                if resultados:
                    st.success(f"Encontrados {len(resultados)} servidores ativos!")
                    df = pd.DataFrame(resultados)
                    # Mostra a tabela com o DNS e o link M3U que ele gerou
                    st.dataframe(df[['dns', 'status', 'expira']], use_container_width=True)
                else:
                    st.error("Nenhum DNS funcionou com esses dados.")
        else:
            st.warning("Preencha o usuário, senha e suba o arquivo TXT.")

with tab2:
    if 'res_finais' in st.session_state:
        js_output = build_dns_js(st.session_state['res_finais'])
        st.code(js_output, language="javascript")
        st.download_button("Baixar dns.js", js_output, "dns.js")
