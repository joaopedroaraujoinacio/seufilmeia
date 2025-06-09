import streamlit as st
import google.generativeai as genai

# Configura a API key do Gemini
# ATENÇÃO: Em uma aplicação real, a chave API não deve ser exposta diretamente no código.
# Use variáveis de ambiente ou secrets do Streamlit para armazená-la de forma segura.

api_key = st.secrets['API_KEY']
genai.configure(api_key = api_key) # Substitua pela sua chave API real

model = genai.GenerativeModel("gemini-2.0-flash")

def sugerir_filme_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestão de filme: {str(e)}"

st.set_page_config(page_title="Filme Certo.IA", layout="centered")

st.title("Filme Certo.IA")
st.markdown("Deixe a inteligência artificial te ajudar a encontrar um filme bacana para assistir, com base nas suas preferências!")

# Faixa Etária
faixa_etaria = st.selectbox(
    "Para qual faixa etária é o filme?",
    ("Livre", "10+", "12+", "14+", "16+", "18+")
)

# Duração
duracao = st.select_slider(
    "Qual a duração aproximada que você prefere?",
    options=["Curta (até 90 min)", "Média (90-120 min)", "Longa (acima de 120 min)"]
)

# Nota (simulação de preferência)
nota_preferencia = st.slider(
    "Qual a nota mínima que o filme deve ter (de 1 a 5)?",
    min_value=1.0,
    max_value=5.0,
    value=3.5,
    step=0.5
)

# Gênero
genero = st.multiselect(
    "Quais gêneros você gostaria?",
    ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
    default=["Drama", "Ficção Científica"] # Exemplo de default
)

# Botão para Sugerir Filme
if st.button("Sugerir Filme"):
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
    else:
        # Construindo a string de gêneros
        generos_str = ", ".join(genero)

        # Construindo o prompt para a IA Gemini
        prompt = (
            f"Sugira um filme fictício, mas que pareça real, com as seguintes características:\n"
            f"- Faixa Etária: {faixa_etaria}\n"
            f"- Duração: {duracao}\n"
            f"- Nota Mínima Esperada: {nota_preferencia} de 5\n"
            f"- Gêneros: {generos_str}\n\n"
            f"Apresente o Título do Filme, uma breve Sinopse, a Duração aproximada, a Faixa Etária, os Gêneros e uma Nota de Crítica (fictícia) de 1 a 5."
        )

        with st.spinner("Procurando o filme perfeito para você..."):
            filme_sugerido = sugerir_filme_gemini(prompt)
            st.subheader("🎉 Sua Sugestão de Filme:")
            st.write(filme_sugerido)