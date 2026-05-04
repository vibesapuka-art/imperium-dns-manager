import streamlit as st
from modules.checker import run_mass_test
from modules.formatter import build_dns_js

st.set_page_config(page_title="Imperium DNS", layout="wide")

# Sidebar - Credenciais
with st.sidebar:
    st.title("Configurações")
    user = st.text_input("Usuário ADM")
    pw = st.text_input("Senha ADM", type="password")
    threads = st.slider("Threads", 10, 100, 30)

st.title("🌐 Gerenciador de Infraestrutura DNS")

tab1, tab2 = st.tabs(["📥 Testador", "💾 Exportar dns.js"])

with tab1:
    txt_input = st.text_area("Lista de DNS (Bruta)", height=300)
    if st.button("Executar Verificação"):
        lista_bruta = [l for l in txt_input.splitlines() if l.strip()]
        if lista_bruta and user and pw:
            with st.spinner("Testando servidores..."):
                # Chama o módulo externo
                onlines = run_mass_test(lista_bruta, user, pw, threads, 5)
                st.session_state['onlines'] = onlines
                st.success(f"{len(onlines)} servidores ativos!")
        else:
            st.error("Preencha as credenciais e a lista.")

with tab2:
    if 'onlines' in st.session_state:
        js_code = build_dns_js(st.session_state['onlines'])
        st.code(js_code, language="javascript")
        st.download_button("Baixar dns.js", js_code, "dns.js")
    else:
        st.info("Aguardando resultados do teste...")
