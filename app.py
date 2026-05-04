import streamlit as st
import pandas as pd
from modules.checker import iniciar_varredura
from modules.formatter import build_dns_js

st.set_page_config(page_title="Imperium M3U Master", layout="wide")

st.title("🌐 Gerenciador de DNS Imperium TV")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔑 Acesso ADM")
    usuario_input = st.text_input("Usuário (User)")
    senha_input = st.text_input("Senha (Pass)", type="password")
    st.divider()
    threads_opt = st.slider("Velocidade (Threads)", 10, 100, 40)
    timeout_opt = st.slider("Timeout (seg)", 1, 15, 7)

tab1, tab2 = st.tabs(["🚀 Verificação", "📄 Exportar dns.js"])

with tab1:
    col_file, col_text = st.columns(2)
    with col_file:
        file = st.file_uploader("Upload .txt", type="txt")
    with col_text:
        manual_input = st.text_area("Entrada Manual", height=68)

    if st.button("▶️ Iniciar Teste"):
        # Unificação da lista
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
                # Realiza o teste
                sucessos = iniciar_varredura(dns_list, usuario_input, senha_input, threads_opt, timeout_opt)
                
                # Identifica as falhas comparando a lista inicial com os sucessos
                set_sucessos = {s['dns'] for s in sucessos}
                falhas = [d for d in dns_list if (d if d.startswith('http') else 'http://'+d).rstrip('/') not in set_sucessos]
                
                # Salva no estado da sessão
                st.session_state['res_finais'] = sucessos
                st.session_state['falhas'] = falhas

                # Exibição de Resultados
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.success(f"✅ Ativos: {len(sucessos)}")
                    if sucessos:
                        df_suc = pd.DataFrame(sucessos)
                        st.dataframe(df_suc[['dns', 'expira']], use_container_width=True)
                
                with col_res2:
                    st.error(f"❌ Sem Sucesso: {len(falhas)}")
                    if falhas:
                        # Exibe os DNS que falharam em uma caixa de texto para fácil cópia/remoção
                        st.text_area("DNS Offline ou Inválidos:", value="\n".join(falhas), height=300)

with tab2:
    if 'res_finais' in st.session_state and st.session_state['res_finais']:
        js_output = build_dns_js(st.session_state['res_finais'])
        st.code(js_output, language="javascript")
        st.download_button("💾 Baixar dns.js", js_output, "dns.js")
    else:
        st.info("💡 Execute o teste para gerar o arquivo.")
