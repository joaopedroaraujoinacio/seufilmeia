import streamlit as st
import google.generativeai as genai

api_key = st.secrets['API_KEY']
genai.configure(api_key=api_key)

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

st.header("Suas Preferências Principais")
st.markdown("Selecione os critérios básicos para o filme ideal.")

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

st.header("Preferências Adicionais (Opcional)")
st.markdown("Quer refinar ainda mais? Adicione detalhes de ano e atores.")

ano_lancamento = st.text_input("A partir de qual ano de lançamento?", placeholder="Ex: 2000")
atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria?", placeholder="Ex: Tom Hanks, Meryl Streep")

# Novo seletor: número de sugestões
num_filmes = st.slider(
    "Quantos filmes deseja receber?",
    min_value=1,
    max_value=10,
    value=5
)

# Controle de estado para manter o prompt entre cliques
if "ultimo_prompt" not in st.session_state:
    st.session_state.ultimo_prompt = ""
if "ultimo_num" not in st.session_state:
    st.session_state.ultimo_num = 5

def gerar_prompt():
    generos_str = ", ".join(genero)
    prompt = (
        f"Com base nas preferências abaixo, sugira {num_filmes} filmes que **existem de verdade** e que podem ser verificados em fontes como IMDb ou Rotten Tomatoes.\n"
        f"Não invente filmes fictícios. Não inclua observações ou comentários adicionais após as sugestões.\n"
        f"Cada sugestão deve conter apenas as informações pedidas. Nada além disso.\n\n"
        f"Critérios:\n"
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
        f"\nPara cada filme, apresente as seguintes informações:\n"
        f"Título: [Título do Filme]\n"
        f"Sinopse: [Breve Sinopse - máximo de duas linhas]\n"
        f"Duração: [Duração aproximada]\n"
        f"Faixa Etária: [Faixa Etária]\n"
        f"Gêneros: [Gêneros]\n"
        f"Nota de Crítica: [Nota de 1 a 5, ex: '4.2/5 (Críticos IMDb)']\n"
        f"---\n"
    )
    return prompt

# Botões lado a lado
col1, col2 = st.columns([1, 1])

with col1:
    gerar = st.button("🎥 Sugerir Filmes")

with col2:
    gerar_novos = st.button("🔄 Gerar Novos Filmes")

# Lógica de sugestão
if gerar or gerar_novos:
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
    else:
        if gerar:
            prompt = gerar_prompt()
            st.session_state.ultimo_prompt = prompt
            st.session_state.ultimo_num = num_filmes
        else:  # botão "Gerar Novos Filmes"
            prompt = st.session_state.ultimo_prompt
            num_filmes = st.session_state.ultimo_num  # manter valor anterior

        with st.spinner("Procurando os filmes perfeitos para você..."):
            filmes_sugeridos_raw = sugerir_filme_gemini(prompt)

        st.subheader("Suas Sugestões de Filmes:")

        filmes_list = filmes_sugeridos_raw.strip().split('---\n')
        for i, filme_text in enumerate(filmes_list[:num_filmes]):
            if filme_text.strip():
                st.markdown(f"### 🎬 Filme {i+1}")
                lines = filme_text.strip().split('\n')
                for line in lines:
                    if line.strip():
                        if "Título:" in line:
                            clean_title = line.replace('Título:', '').replace('**', '').strip()
                            st.markdown(f"**{clean_title}**")
                        elif "Sinopse:" in line:
                            clean_synopsis = line.replace('Sinopse:', '').replace('**', '').strip()
                            st.markdown(f"*{clean_synopsis}*")
                        else:
                            clean_line = line.replace('**', '').strip()
                            st.write(clean_line)
                st.markdown("---")
