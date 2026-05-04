# 🌐 Imperium DNS Manager

Sistema de gerenciamento e validação de infraestrutura DNS para a rede Imperium TV.

## 🚀 Funcionalidades
- **Validação em Massa:** Testa centenas de DNS simultaneamente via multithreading.
- **Autenticação ADM:** Valida o status real do servidor usando credenciais de administrador.
- **Exportação Inteligente:** Gera automaticamente o arquivo `dns.js` formatado para o projeto.
- **Relatório de Latência:** Exibe o tempo de resposta de cada servidor.

## 🛠️ Como Instalar
1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Execute o app: `streamlit run app.py`.

## 📂 Estrutura
O projeto é modularizado para facilitar a manutenção da lógica de teste e formatação separadamente da interface.
