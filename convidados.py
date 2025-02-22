import streamlit as st
import gspread
from google.oauth2 import service_account

# Configurações do Google Sheets
def conectar_google_sheets():
    # Use o arquivo JSON baixado
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
    
    json_file = "credentials.json"
    credentials = service_account.Credentials.from_service_account_file(json_file)
    scoped_credentials = credentials.with_scopes(scopes)
    client = gspread.authorize(scoped_credentials)
    return client

def carregar_dados(planilha):
    worksheet = planilha.get_worksheet(0)  # Pega a primeira aba
    return worksheet.get_all_records()

def salvar_dados(planilha, dados):
    worksheet = planilha.get_worksheet(0)  # Pega a primeira aba
    worksheet.append_row(dados)

# Título da aplicação
st.title("🎉 Lista de Convidados")

# Conecta ao Google Sheets

client = conectar_google_sheets()
print('a')
planilha = client.open("presenca")  # Substitua pelo nome da sua planilha


# Formulário para adicionar convidados
with st.form("form_convidado"):
    nome = st.text_input("Nome completo*:")
    celular = st.text_input("Celular*:")
    comparecera = st.radio("Vai comparecer?*", ["Sim", "Não"])
    acompanhante = st.text_input("Nome do acompanhante (se houver):")

    submitted = st.form_submit_button("Adicionar à lista")

    if submitted:
        if not nome or not celular:
            st.error("Preencha os campos obrigatórios (*)")
        else:
            dados = [nome, celular, comparecera, acompanhante if acompanhante else "Não"]
            try:
                salvar_dados(planilha, dados)
                st.success("Convidado adicionado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")

# Exibe a lista de convidados
st.subheader("📋 Lista de Convidados")
try:
    dados = carregar_dados(planilha)
    if dados:
        st.table(dados)
    else:
        st.info("Nenhum convidado cadastrado ainda.")
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")