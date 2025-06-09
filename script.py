import streamlit as st
import google.generativeai as genai

api_key = st.secrets['API_KEY']
genai.configure(api_key=api_key) 

model_suggestion = genai.GenerativeModel("gemini-1.5-flash")
model_discovery = genai.GenerativeModel("gemini-1.5-pro")

def gerar_sugestoes_filme_gemini(prompt):
    try:
        response = model_suggestion.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestões de filme: {str(e)}"

def descobrir_filme_gemini(prompt):
    try:
        response = model_discovery.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao descobrir filme: {str(e)}"

st.set_page_config(page_title="Seu Filme.IA", layout="centered")

st.title("Seu Filme.IA")
st.markdown("Deixe a inteligência artificial te ajudar a encontrar um filme legal para assistir ou descobrir um filme que você não lembra o nome!")

st.header("✨ Sugestão de Filmes Fictícios")
st.markdown("Com base nas suas preferências, a IA criará algumas sugestões de filmes originais para você!")

with st.expander("Defina suas preferências para as sugestões"):
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

    genero = st.multiselect(
        "Quais gêneros você gostaria?",
        ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
        default=["Drama", "Ficção Científica"] 
    )

    ano_lancamento = st.slider(
        "Ano de lançamento (opcional, ou deixe 0 para qualquer ano):",
        min_value=0,
        max_value=2030,
        value=0,
        step=1
    )

    atores_sugestao = st.text_input(
        "Atores/Atrizes que o filme teria (opcional, separe por vírgulas):",
        placeholder="Ex: Tom Hanks, Meryl Streep"
    )

    fonte_nota = st.text_input(
        "Sugira uma fonte para a nota de crítica (opcional, ex: Rotten Tomatoes, IMDb):",
        placeholder="Ex: Rotten Tomatoes"
    )

if st.button("Gerar Sugestões de Filmes"):
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
    else:
        generos_str = ", ".join(genero)
        
        prompt_sugestao = (
            f"Sugira 5 filmes fictícios, mas que pareçam reais, com as seguintes características:\n"
            f"- Faixa Etária: {faixa_etaria}\n"
            f"- Duração: {duracao}\n"
            f"- Nota Mínima Esperada: {nota_preferencia} de 5\n"
            f"- Gêneros: {generos_str}\n"
        )
        if ano_lancamento > 0:
            prompt_sugestao += f"- Ano de Lançamento: {ano_lancamento}\n"
        if atores_sugestao:
            prompt_sugestao += f"- Atores/Atrizes: {atores_sugestao}\n"
        if fonte_nota:
            prompt_sugestao += f"- Fonte da Nota de Crítica: {fonte_nota}\n"
            
        prompt_sugestao += (
            f"\nPara cada filme, apresente de forma concisa e objetiva:\n"
            f"1. **Título do Filme**\n"
            f"2. **Sinopse Breve** (1-2 frases)\n"
            f"3. **Duração** (aprox.)\n"
            f"4. **Faixa Etária**\n"
            f"5. **Gêneros**\n"
            f"6. **Nota de Crítica** (fictícia, de 1 a 5, com a fonte se informada)\n"
            f"7. **Ano de Lançamento** (fictício, se informado)\n"
            f"8. **Atores/Atrizes** (fictícios, se informados)\n\n"
            f"Formate cada sugestão de filme de forma clara, separada por linhas."
        )

        with st.spinner("Gerando sugestões de filmes fictícios..."):
            sugestoes_filmes = gerar_sugestoes_filme_gemini(prompt_sugestao)
            st.subheader("🎉 Suas Sugestões de Filmes:")
            st.markdown(sugestoes_filmes)

st.header("🔍 Descobrir Um Filme")
st.markdown("Descreva o filme que você está tentando lembrar ou informe atores/atrizes e a IA tentará te ajudar a descobrir qual é!")

descricao_filme = st.text_area(
    "Descreva o filme (enredo, personagens, cenas marcantes, etc.):",
    placeholder="Ex: Um grupo de cientistas viaja pelo espaço para encontrar um novo lar para a humanidade..."
)

atores_descoberta = st.text_input(
    "Atores ou Atrizes do filme (opcional, separe por vírgulas):",
    placeholder="Ex: Leonardo DiCaprio, Brad Pitt"
)

if st.button("Descobrir Filme"):
    if not descricao_filme and not atores_descoberta:
        st.warning("Por favor, forneça uma descrição do filme ou o nome de atores/atrizes para a descoberta.")
    else:
        prompt_descoberta = "Eu estou tentando lembrar de um filme. Por favor, me ajude a identificá-lo."
        if descricao_filme:
            prompt_descoberta += f"\n- Descrição: {descricao_filme}"
        if atores_descoberta:
            prompt_descoberta += f"\n- Atores/Atrizes: {atores_descoberta}"
        
        prompt_descoberta += "\n\nCom base nessas informações, qual(is) filme(s) você acha que é? Forneça o título, ano de lançamento e uma breve sinopse para cada sugestão."

        with st.spinner("Procurando o filme para você..."):
            filme_descoberto = descobrir_filme_gemini(prompt_descoberta)
            st.subheader("💡 Filmes Sugeridos:")
            st.write(filme_descoberto)

st.markdown("---")
st.info("Sua Filme.IA é alimentada por Google Gemini!")