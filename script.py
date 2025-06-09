import streamlit as st
import google.generativeai as genai

api_key = st.secrets['API_KEY']
genai.configure(api_key = api_key) 

model = genai.GenerativeModel("gemini-2.0-flash")

def sugerir_filme_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestão de filme: {str(e)}"

st.set_page_config(page_title="Seu Filme.IA", layout="centered")

st.title("Seu Filme.IA")
st.markdown("Deixe a inteligência artificial te ajudar a encontrar **filmes incríveis** com base nas suas preferências!")

col1, col2 = st.columns(2)

with col1:
    faixa_etaria = st.selectbox(
        "Para qual faixa etária é o filme?",
        ("Livre", "10+", "12+", "14+", "16+", "18+")
    )

    duracao = st.select_slider(
        "Qual a duração aproximada que você prefere?",
        options=["Curta (até 90 min)", "Média (90-120 min)", "Longa (acima de 120 min)"]
    )

    nota_preferencia = st.slider(
        "Qual a nota mínima que o filme deve ter (de 1 a 5)?",
        min_value=1.0,
        max_value=5.0,
        value=3.5,
        step=0.5
    )

with col2:
    ano_lancamento = st.text_input("A partir de qual ano de lançamento? (Opcional)", placeholder="Ex: 2000")
    
    atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria? (Opcional)", placeholder="Ex: Tom Hanks, Meryl Streep")

genero = st.multiselect(
    "Quais gêneros você gostaria?",
    ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
    default=["Drama", "Ficção Científica"] 
)

if st.button("Sugerir Filmes"):
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
    else:
        generos_str = ", ".join(genero)

        prompt = (
            f"Sugira 5 filmes fictícios, mas que pareçam reais, com as seguintes características, apresentando apenas as informações solicitadas em cada item:\n"
            f"- Faixa Etária: {faixa_etaria}\n"
            f"- Duração: {duracao}\n"
            f"- Nota Mínima Esperada: {nota_preferencia} de 5\n"
            f"- Gêneros: {generos_str}\n"
        )
        
        if ano_lancamento:
            prompt += f"- Ano de Lançamento a partir de: {ano_lancamento}\n"
        if atores_atrizes:
            prompt += f"- Atores/Atrizes sugeridos: {atores_atrizes}\n"
        
        prompt += (
            f"\nPara cada filme, apresente as seguintes informações de forma concisa e objetiva:\n"
            f"**Título:** [Título do Filme]\n"
            f"**Sinopse:** [Breve Sinopse - máximo de duas linhas]\n"
            f"**Duração:** [Duração aproximada]\n"
            f"**Faixa Etária:** [Faixa Etária]\n"
            f"**Gêneros:** [Gêneros]\n"
            f"**Nota de Crítica:** [Nota de 1 a 5, com uma fonte fictícia, ex: '4.2/5 (Críticos IMDb)']\n"
            f"---\n"
        )

        with st.spinner("Procurando os filmes perfeitos para você..."):
            filmes_sugeridos = sugerir_filme_gemini(prompt)
            st.subheader("Suas Sugestões de Filmes:")
            st.write(filmes_sugeridos)