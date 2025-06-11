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
st.markdown("Esse aplicativo, junto da inteligência artificial, irá te ajudar a encontrar o filme ideal, baseado nas suas preferências!")

st.header("Suas Preferências Principais")
st.markdown("Por favor, selecione os critérios básicos para o filme ideal.")

faixa_etaria = st.selectbox(
    "Para qual faixa etária é o filme?",
    ("Livre", "10+", "12+", "14+", "16+", "18+")
)

duracao = st.select_slider(
    "Qual seria a duração aproximada que você prefere?",
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
    "De quais gêneros você gostaria?",
    ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
    default=["Drama", "Ficção Científica"]
)

qtd_filmes = st.slider(
    "Quantos filmes você deseja receber sugestões?",
    min_value=1,
    max_value=10,
    value=5
)

st.header("Preferências Adicionais Opcionais")
ano_lancamento = st.text_input("A partir de qual ano de lançamento?", placeholder="Ex: 2001")
atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria?", placeholder="Ex: Fernanda Torres, Wagner Moura")

if "filmes_anteriores" not in st.session_state:
    st.session_state.filmes_anteriores = []
if "prompt_base" not in st.session_state:
    st.session_state.prompt_base = ""
if "sugeriu" not in st.session_state:
    st.session_state.sugeriu = False
if "filmes_gerados" not in st.session_state:
    st.session_state.filmes_gerados = []

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
    gerar_novos = st.button("Gerar Novos Filmes")

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
            st.session_state.filmes_gerados = filmes_raw

if gerar_novos and st.session_state.sugeriu:
    prompt = montar_prompt(base=False)
    with st.spinner("Gerando nova lista..."):
        resposta = sugerir_filme_gemini(prompt)
        filmes_raw = resposta.strip().split('---\n')
        novos_titulos = []
        for filme in filmes_raw[:qtd_filmes]:
            if filme.strip():
                for line in filme.strip().split('\n'):
                    if "Título:" in line:
                        titulo = line.replace("Título:", "").strip()
                        novos_titulos.append(titulo)
        st.session_state.filmes_anteriores.extend(novos_titulos)
        st.session_state.filmes_gerados = filmes_raw

if st.session_state.sugeriu and st.session_state.filmes_gerados:
    st.markdown("---")
    st.subheader("Suas Sugestões de Filmes")
    for i, filme in enumerate(st.session_state.filmes_gerados[:qtd_filmes]):
        if filme.strip():
            st.markdown(f"### Filme {i+1}")
            for line in filme.strip().split('\n'):
                if "Título:" in line:
                    titulo = line.replace("Título:", "").strip()
                    if titulo not in st.session_state.filmes_anteriores:
                        st.session_state.filmes_anteriores.append(titulo)
                    st.markdown(f"**{titulo}**")
                elif "Sinopse:" in line:
                    st.markdown(f"*{line.replace('Sinopse:', '').strip()}*")
                else:
                    st.write(line.strip())
            st.markdown("---")

st.markdown("## Identificar Filme")
st.markdown("Lembra de partes de um filme mas não sabe o nome? Me conte o que você lembra e eu tentarei descobrir!")

descricao_filme = st.text_area("Descreva tudo o que você lembra sobre o filme (cenas, atores, enredo, época...)", height=150)

if st.button("Identificar Filme", key="identificar"):
    if descricao_filme.strip():
        prompt_identificar = (
            f"Você é um assistente de cinema. Com base na descrição abaixo, diga qual pode ser o filme.\n"
            f"Descreva o nome mais provável do filme, uma breve sinopse e o motivo da sua escolha.\n"
            f"Se não souber ao certo, dê a resposta mais plausível com base nos dados disponíveis.\n\n"
            f"Descrição: {descricao_filme.strip()}"
        )
        with st.spinner("Analisando sua descrição..."):
            resposta_identificar = sugerir_filme_gemini(prompt_identificar)
            st.markdown("### Resultado:")
            st.write(resposta_identificar)
    else:
        st.warning("Por favor, escreva uma descrição para identificar o filme.")

