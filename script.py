import streamlit as st
import google.generativeai as genai
import re

api_key = st.secrets['API_KEY']
genai.configure(api_key=api_key) 

model = genai.GenerativeModel("gemini-2.0-flash")

def sugerir_filme_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestão de filme: {str(e)}"

def gerar_prompt_filmes(faixa_etaria, duracao, nota_preferencia, genero, ano_lancamento, atores_atrizes, num_filmes):
    generos_str = ", ".join(genero)

    prompt = (
        f"Sugira {num_filmes} filmes fictícios, mas que pareçam reais, com as seguintes características, apresentando as informações de forma concisa e objetiva:\n"
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
        f"Nota de Crítica: [Nota de 1 a 5, com uma fonte fictícia, ex: '4.2/5 (Críticos IMDb)']\n"
        f"---\n"
    )
    return prompt

def exibir_filmes_sugeridos(filmes_sugeridos_raw):
    st.subheader("Suas Sugestões de Filmes:")
    
    filmes_list = filmes_sugeridos_raw.strip().split('---\n')
    
    for i, filme_text in enumerate(filmes_list):
        if filme_text.strip():
            st.markdown(f"### 🎬 Filme {i+1}")
            
            lines = filme_text.strip().split('\n')
            for line in lines:
                if line.strip():
                    clean_line = re.sub(r'\*+', '', line).strip() 
                    
                    if clean_line.startswith("Título:"):
                        clean_title = clean_line.replace('Título:', '').strip()
                        st.markdown(f"**{clean_title}**")
                    elif clean_line.startswith("Sinopse:"):
                        clean_synopsis = clean_line.replace('Sinopse:', '').strip()
                        st.markdown(f"*{clean_synopsis}*")
                    else:
                        st.write(clean_line)
            st.markdown("---")

def gerar_e_exibir_filmes():
    if not st.session_state.genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
        return

    prompt = gerar_prompt_filmes(
        st.session_state.faixa_etaria,
        st.session_state.duracao,
        st.session_state.nota_preferencia,
        st.session_state.genero,
        st.session_state.ano_lancamento,
        st.session_state.atores_atrizes,
        st.session_state.num_filmes
    )

    with st.spinner("Procurando os filmes perfeitos para você..."):
        filmes_sugeridos_raw = sugerir_filme_gemini(prompt)
        st.session_state['filmes_sugeridos_raw'] = filmes_sugeridos_raw
        exibir_filmes_sugeridos(filmes_sugeridos_raw)


st.set_page_config(page_title="Seu Filme.IA", layout="centered")

st.title("Seu Filme.IA")
st.markdown("Deixe a inteligência artificial te ajudar a encontrar **filmes incríveis** com base nas suas preferências!")

st.header("Suas Preferências Principais")
st.markdown("Selecione os critérios básicos para o filme ideal.")

st.session_state.faixa_etaria = st.selectbox(
    "Para qual faixa etária é o filme?",
    ("Livre", "10+", "12+", "14+", "16+", "18+"),
    key="faixa_etaria_input"
)

st.session_state.duracao = st.select_slider(
    "Qual a duração aproximada que você prefere?",
    options=["Curta (até 90 min)", "Média (90-120 min)", "Longa (acima de 120 min)"],
    key="duracao_input"
)

st.session_state.nota_preferencia = st.slider(
    "Qual a nota mínima que o filme deve ter (de 1 a 5)?",
    min_value=1.0,
    max_value=5.0,
    value=3.5,
    step=0.5,
    key="nota_preferencia_input"
)

st.session_state.genero = st.multiselect(
    "Quais gêneros você gostaria?",
    ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
    default=["Drama", "Ficção Científica"],
    key="genero_input"
)

st.header("Preferências Adicionais (Opcional)")
st.markdown("Quer refinar ainda mais? Adicione detalhes de ano e atores.")

st.session_state.ano_lancamento = st.text_input("A partir de qual ano de lançamento?", placeholder="Ex: 2000", key="ano_lancamento_input")

st.session_state.atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria?", placeholder="Ex: Tom Hanks, Meryl Streep", key="atores_atrizes_input")

st.session_state.num_filmes = st.number_input(
    "Quantos filmes você gostaria de sugestão? (De 1 a 20)",
    min_value=1,
    max_value=20,
    value=5,
    step=1,
    help="Escolha o número de filmes que a IA deve sugerir.",
    key="num_filmes_input"
)

if st.button("Sugerir Filmes", type="primary"):
    gerar_e_exibir_filmes()

if 'filmes_sugeridos_raw' in st.session_state:
    if st.button("Gerar Novamente Outros Filmes"):
        if 'filmes_sugeridos_raw' in st.session_state:
            del st.session_state['filmes_sugeridos_raw']
        gerar_e_exibir_filmes()
    
    if 'filmes_sugeridos_raw' in st.session_state and st.session_state['filmes_sugeridos_raw']:
        exibir_filmes_sugeridos(st.session_state['filmes_sugeridos_raw'])