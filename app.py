import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

# Carrega as credenciais da secret
def carregar_credenciais():
    credenciais = os.getenv("GOOGLE_CREDENTIALS")
    if not credenciais:
        st.error("Credenciais do Google não encontradas. Verifique as secrets.")
        st.stop()
    return json.loads(credenciais)

# Configurações do Google Sheets
def conectar_google_sheets():
    # Escopo da API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Use as credenciais carregadas da secret
    creds = ServiceAccountCredentials.from_json_keyfile_dict(carregar_credenciais(), scope)
    client = gspread.authorize(creds)
    return client

def carregar_dados(planilha):
    worksheet = planilha.get_worksheet(0)  # Pega a primeira aba
    return worksheet.get_all_records()

def salvar_dados(planilha, dados):
    worksheet = planilha.get_worksheet(0)  # Pega a primeira aba
    worksheet.append_row(dados)
    
def criar_cabecalho(planilha):
    worksheet = planilha.get_worksheet(0)  # Pega a primeira aba
    cabecalho = ["Nome", "Celular", "Comparecerá", "Acompanhante"]
    # Verifica se o cabeçalho já existe
    if not worksheet.row_values(1):
        worksheet.append_row(cabecalho)
    
    
# Configurações da página
st.set_page_config(page_title="Convite Churrasquinho MarcolaDay", layout="wide")

# Senha de acesso (altere para uma senha segura)
SENHA_CORRETA = os.getenv("SENHA_APP")

# Função para verificar a senha
def verificar_senha(senha):
    return senha == SENHA_CORRETA

# Título da aplicação
st.title("🎉 Convite Churrasquinho")

# Informações do Evento
st.subheader("📅 Informações do Evento")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        **Data:** 8 de março de 2025  
        **Horário:** 13:00 até o horário que eu quiser  
        **Local:** Casa de Tony
    """)

with col2:
    st.markdown("""
        **Endereço:**  
        Rua Iranduba, 225  
        Bairro Cordovil 
        Rio de Janeiro - RJ 
    """)

# Mapa do Google Maps
st.subheader("📍 Localização do Evento")
st.markdown("""
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3677.497166976015!2d-43.301600199999996!3d-22.821088700000004!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x997b11f29b54bd%3A0x6b9dd20180e1af51!2sR.%20Iranduba%2C%20225%20-%20Cordovil%2C%20Rio%20de%20Janeiro%20-%20RJ%2C%2021250-380!5e0!3m2!1spt-BR!2sbr!4v1740498602796!5m2!1spt-BR!2sbr" 
    width="800" 
    height="600" 
    style="border:0;" 
    allowfullscreen="" 
    loading="lazy" 
    referrerpolicy="no-referrer-when-downgrade">
    </iframe>
""", unsafe_allow_html=True)

# Lista de Convidados
st.divider()
st.subheader("📋 Lista de Convidados")

# Inicializa os DataFrames na session_state
if 'df_confirmados' not in st.session_state:
    st.session_state.df_confirmados = pd.DataFrame(columns=["Nome", "Celular", "Acompanhante"])

if 'df_nao_comparecerao' not in st.session_state:
    st.session_state.df_nao_comparecerao = pd.DataFrame(columns=["Nome", "Celular"])
    
    
# Conecta ao Google Sheets
try:
    client = conectar_google_sheets()
    planilha = client.open("presenca")  # Substitua pelo ID da sua planilha
    criar_cabecalho(planilha)  # Cria o cabeçalho se não existir
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# Formulário de entrada
with st.form("convite_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome completo*:")
        celular = st.text_input("Celular*:")
        
    with col2:
        comparecera = st.radio("Vai comparecer?*", ["Sim", "Não"])
        acompanhante = st.text_input("Nome do acompanhante (se houver):")
    
    submitted = st.form_submit_button("Adicionar à lista")
    
    if submitted:
        if not nome or not celular:
            st.error("Preencha os campos obrigatórios (*)")
        else:
            if comparecera == "Sim":
                dados = [nome.title(), celular, comparecera, acompanhante.title() if acompanhante else "Não"]
            else:
                dados = [nome.title(), celular, comparecera, "Não"]
            try:
                salvar_dados(planilha, dados)
                st.success("Convidado adicionado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")

# Botão de Login
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    if st.button("🔒 Acessar Listas"):
        st.session_state.mostrar_login = True

    if 'mostrar_login' in st.session_state and st.session_state.mostrar_login:
        senha = st.text_input("Digite a senha para acessar:", type="password")
        if senha:
            if verificar_senha(senha):
                st.session_state.autenticado = True
                st.session_state.mostrar_login = False
                st.success("Acesso permitido!")
            else:
                st.error("Senha incorreta. Tente novamente.")

# Exibe as tabelas e exportação apenas se autenticado
if st.session_state.autenticado:
    # Carrega os dados da planilha
    try:
        dados = carregar_dados(planilha)
        if dados:
            df = pd.DataFrame(dados)
            df_confirmados = df[df["Comparecerá"] == "Sim"]
            df_nao_comparecerao = df[df["Comparecerá"] == "Não"]

            # Exibe as tabelas
            if not df_confirmados.empty:
                st.divider()
                st.subheader("✅ Lista de Confirmados")
                st.dataframe(df_confirmados, use_container_width=True)

            if not df_nao_comparecerao.empty:
                st.divider()
                st.subheader("❌ Lista de Não Comparecerão")
                st.dataframe(df_nao_comparecerao, use_container_width=True)
        else:
            st.info("Nenhum convidado cadastrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")