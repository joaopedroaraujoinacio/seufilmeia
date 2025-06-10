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

qtd_filmes = st.slider(
    "Quantos filmes você deseja receber?",
    min_value=1,
    max_value=10,
    value=5
)

st.header("Preferências Adicionais (Opcional)")
ano_lancamento = st.text_input("A partir de qual ano de lançamento?", placeholder="Ex: 2000")
atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria?", placeholder="Ex: Tom Hanks, Meryl Streep")

# Inicializando estados
if "filmes_anteriores" not in st.session_state:
    st.session_state.filmes_anteriores = []
if "prompt_base" not in st.session_state:
    st.session_state.prompt_base = ""
if "sugeriu" not in st.session_state:
    st.session_state.sugeriu = False

def montar_prompt(base=False):
    generos_str = ", ".join(genero)
    prompt = (
        f"Com base nas preferências abaixo, sugira {qtd_filmes} filmes que **existem de verdade** e que podem ser verificados em fontes como IMDb ou Rotten Tomatoes.\n"
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

    if not base and st.session_state.filmes_anteriores:
        lista_titulos = ', '.join(st.session_state.filmes_anteriores)
        prompt += f"\nEvite repetir qualquer filme das sugestões anteriores: {lista_titulos}.\n"

    return prompt

col1, col2 = st.columns([1, 1])
with col1:
    sugerir = st.button("Sugerir Filmes")
with col2:
    gerar_novos = st.button("Gerar Novos Filmes") if st.session_state.sugeriu else None

# Área comum para exibição dos filmes — fora das colunas
if sugerir:
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero.")
    else:
        prompt = montar_prompt(base=True)
        with st.spinner("Procurando os filmes perfeitos para você..."):
            resposta = sugerir_filme_gemini(prompt)
            st.session_state.sugeriu = True
            st.session_state.prompt_base = prompt
            filmes_raw = resposta.strip().split('---\n')
            st.session_state.filmes_anteriores = []

            st.markdown("---")
            st.subheader("🎥 Suas Sugestões de Filmes")
            for i, filme in enumerate(filmes_raw[:qtd_filmes]):
                if filme.strip():
                    st.markdown(f"### 🎬 Filme {i+1}")
                    for line in filme.strip().split('\n'):
                        if "Título:" in line:
                            titulo = line.replace("Título:", "").strip()
                            st.session_state.filmes_anteriores.append(titulo)
                            st.markdown(f"**{titulo}**")
                        elif "Sinopse:" in line:
                            st.markdown(f"*{line.replace('Sinopse:', '').strip()}*")
                        else:
                            st.write(line.strip())
                    st.markdown("---")

elif gerar_novos:
    prompt = montar_prompt(base=False)
    with st.spinner("Gerando nova lista..."):
        resposta = sugerir_filme_gemini(prompt)
        filmes_raw = resposta.strip().split('---\n')
        novos_titulos = []

        st.markdown("---")
        st.subheader("🎬 Novas Sugestões de Filmes")
        for i, filme in enumerate(filmes_raw[:qtd_filmes]):
            if filme.strip():
                st.markdown(f"### 🎬 Filme {i+1}")
                for line in filme.strip().split('\n'):
                    if "Título:" in line:
                        titulo = line.replace("Título:", "").strip()
                        novos_titulos.append(titulo)
                        st.markdown(f"**{titulo}**")
                    elif "Sinopse:" in line:
                        st.markdown(f"*{line.replace('Sinopse:', '').strip()}*")
                    else:
                        st.write(line.strip())
                st.markdown("---")
        st.session_state.filmes_anteriores.extend(novos_titulos)

