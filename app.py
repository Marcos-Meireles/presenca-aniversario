import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Configurações da página
st.set_page_config(page_title="Convite de Aniversário", layout="wide")

# Senha de acesso (altere para uma senha segura)
SENHA_CORRETA = os.getenv("SENHA_APP")


# Função para verificar a senha
def verificar_senha(senha):
    return senha == SENHA_CORRETA

# Título da aplicação
st.title("🎉 Convite de Aniversário")

# Informações do Evento
st.subheader("📅 Informações do Evento")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        **Data:** 15 de março de 2025  
        **Horário:** 13:00 até o horário que eu quiser  
        **Local:** Casa de Marlon
    """)

with col2:
    st.markdown("""
        **Endereço:**  
        Rua Umbu, 311  
        Bairro Campo Grande/Inhoaíba  
        Rio de Janeiro - RJ 
    """)

# Mapa do Google Maps
st.subheader("📍 Localização do Evento")
st.markdown("""
    <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3675.25428941122!2d-43.57775122380676!3d-22.90398973777275!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9be3f5e0283799%3A0x5a1b572bf933d5c!2sR.%20Umb%C3%BA%2C%20311%20-%20Inhoa%C3%ADba%2C%20Rio%20de%20Janeiro%20-%20RJ%2C%2023070-120!5e0!3m2!1spt-BR!2sbr!4v1740230173696!5m2!1spt-BR!2sbr"
    width="100%"
    height="450"
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
                new_row = {
                    "Nome": nome.title(),
                    "Celular": celular,
                    "Acompanhante": acompanhante.title() if acompanhante else "Não"
                }
                st.session_state.df_confirmados = pd.concat(
                    [st.session_state.df_confirmados, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success("Convidado adicionado à lista de confirmados!")
            else:
                new_row = {
                    "Nome": nome.title(),
                    "Celular": celular
                }
                st.session_state.df_nao_comparecerao = pd.concat(
                    [st.session_state.df_nao_comparecerao, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success("Convidado adicionado à lista de não comparecerão.")

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
    # Exibe as tabelas
    if not st.session_state.df_confirmados.empty:
        st.divider()
        st.subheader("✅ Lista de Confirmados")
        st.dataframe(st.session_state.df_confirmados, use_container_width=True)

    if not st.session_state.df_nao_comparecerao.empty:
        st.divider()
        st.subheader("❌ Lista de Não Comparecerão")
        st.dataframe(st.session_state.df_nao_comparecerao, use_container_width=True)

    # Botão para exportar Excel
    if not st.session_state.df_confirmados.empty or not st.session_state.df_nao_comparecerao.empty:
        st.divider()
        
        def to_excel(df_confirmados, df_nao_comparecerao):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_confirmados.to_excel(writer, sheet_name="Confirmados", index=False)
                df_nao_comparecerao.to_excel(writer, sheet_name="Não Comparecerão", index=False)
            return output.getvalue()
        
        excel_data = to_excel(st.session_state.df_confirmados, st.session_state.df_nao_comparecerao)
        
        st.download_button(
            label="📥 Exportar para Excel",
            data=excel_data,
            file_name="lista_convidados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )