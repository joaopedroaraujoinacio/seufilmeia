import streamlit as st
import google.generativeai as genai

# Configurar API
api_key = st.secrets['API_KEY']
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Função para obter sugestões do Gemini
def sugerir_filme_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestão de filme: {str(e)}"

# Configuração da página
st.set_page_config(page_title="Seu Filme.IA", layout="centered")
st.title("Seu Filme.IA")
st.markdown("Deixe a inteligência artificial te ajudar a encontrar **filmes incríveis de verdade**, com base nas suas preferências!")

# Preferências do usuário
st.header("Suas Preferências Principais")
faixa_etaria = st.selectbox("Para qual faixa etária é o filme?", ("Livre", "10+", "12+", "14+", "16+", "18+"))

duracao = st.select_slider(
    "Qual a duração aproximada que você prefere?",
    options=["Curta (até 90 min)", "Média (90-120 min)", "Longa (acima de 120 min)"]
)

nota_preferencia = st.slider("Qual a nota mínima que o filme deve ter (de 1 a 5)?", 1.0, 5.0, 3.5, 0.5)

genero = st.multiselect(
    "Quais gêneros você gostaria?",
    ["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Documentário", "Fantasia", "Suspense", "Musical"],
    default=["Drama", "Ficção Científica"]
)

# Preferências adicionais
st.header("Preferências Adicionais (Opcional)")
ano_lancamento = st.text_input("A partir de qual ano de lançamento?", placeholder="Ex: 2000")
atores_atrizes = st.text_input("Atores ou Atrizes que você gostaria?", placeholder="Ex: Tom Hanks, Meryl Streep")

# Novo campo: Quantidade de filmes
quantidade_filmes = st.slider(
    "Quantos filmes você gostaria de receber?", 
    min_value=1, 
    max_value=20, 
    value=5
)

# Botões para sugerir filmes
sugerir = st.button("Sugerir Filmes 🎥")
sugerir_novamente = st.button("Sugerir Outros Filmes 🔁")

# Armazenar prompt para reaproveitamento
if 'prompt_salvo' not in st.session_state:
    st.session_state.prompt_salvo = ""
if 'qtd_filmes' not in st.session_state:
    st.session_state.qtd_filmes = 5

# Geração de prompt
def montar_prompt():
    generos_str = ", ".join(genero)
    prompt = (
        f"Liste {quantidade_filmes} filmes reais com as seguintes características:\n"
        f"- Faixa Etária: {faixa_etaria}\n"
        f"- Duração: {duracao}\n"
        f"- Nota mínima: {nota_preferencia} de 5\n"
        f"- Gêneros: {generos_str}\n"
    )
    if ano_lancamento:
        prompt += f"- A partir do ano: {ano_lancamento}\n"
    if atores_atrizes:
        prompt += f"- Com os atores/atrizes: {atores_atrizes}\n"

    prompt += (
        "\nPara cada filme, apresente as seguintes informações:\n"
        "Título: [Nome do Filme]\n"
        "Sinopse: [Breve resumo de até 2 linhas]\n"
        "Duração: [Tempo aproximado]\n"
        "Faixa Etária: [Classificação indicativa]\n"
        "Gêneros: [Gêneros principais]\n"
        "Nota de Crítica: [Ex: 4.5/5 IMDb ou Rotten Tomatoes]\n"
        "---\n"
        "Apenas filmes reais e conhecidos, com dados reais e fontes confiáveis."
    )
    return prompt

# Função para exibir os filmes
def exibir_filmes(texto_filmes):
    filmes_list = texto_filmes.strip().split('---\n')
    st.subheader("Sugestões de Filmes:")
    for i, filme_text in enumerate(filmes_list):
        if filme_text.strip():
            st.markdown(f"### 🎬 Filme {i+1}")
            lines = filme_text.strip().split('\n')
            for line in lines:
                if line.strip():
                    if "Título:" in line:
                        st.markdown(f"**{line.replace('Título:', '').strip()}**")
                    elif "Sinopse:" in line:
                        st.markdown(f"*{line.replace('Sinopse:', '').strip()}*")
                    else:
                        st.write(line.strip())
            st.markdown("---")

# Lógica principal dos botões
if sugerir or sugerir_novamente:
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero.")
    else:
        # Atualiza quantidade no estado da sessão
        st.session_state.qtd_filmes = quantidade_filmes
        st.session_state.prompt_salvo = montar_prompt()

        with st.spinner("Procurando os melhores filmes para você..."):
            resposta = sugerir_filme_gemini(st.session_state.prompt_salvo)
            exibir_filmes(resposta)
