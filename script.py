import streamlit as st
import google.generativeai as genai

# Configuração da API Key (substitua pela sua chave secreta)
api_key = st.secrets['API_KEY']
genai.configure(api_key = api_key) 

# Usando um modelo que é bom para gerar conteúdo criativo
model = genai.GenerativeModel("gemini-1.5-flash")

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

# Nova opção: Quantidade de filmes
num_filmes_sugerir = st.slider(
    "Quantos filmes você gostaria de sugerir?",
    min_value=1,
    max_value=20,
    value=5, # Valor padrão de 5 filmes
    step=1
)

# Inicializa o estado da sessão para armazenar as sugestões
if 'filmes_sugeridos' not in st.session_state:
    st.session_state.filmes_sugeridos = None

# Função para gerar e exibir filmes
def gerar_e_exibir_filmes():
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
        st.session_state.filmes_sugeridos = None # Limpa sugestões se não houver gênero
        return
    
    generos_str = ", ".join(genero)

    prompt = (
        f"Sugira {num_filmes_sugerir} filmes com as seguintes características, apresentando as informações de forma concisa e objetiva:\n"
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

    with st.spinner(f"Procurando {num_filmes_sugerir} filmes perfeitos para você..."):
        filmes_sugeridos_raw = sugerir_filme_gemini(prompt)
        st.session_state.filmes_sugeridos = filmes_sugeridos_raw # Armazena na sessão
        
        # Processa e exibe os filmes
        filmes_list = filmes_sugeridos_raw.strip().split('---\n')
        
        st.subheader("Suas Sugestões de Filmes:")

        for i, filme_text in enumerate(filmes_list):
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

# Botão principal para sugerir filmes
if st.button("Sugerir Filmes", key="sugerir_primeira_vez"):
    gerar_e_exibir_filmes()

# Botão "Sugerir Outros Filmes" só aparece se já houver sugestões
if st.session_state.filmes_sugeridos:
    if st.button("Sugerir Outros Filmes", key="sugerir_novamente"):
        # Limpa as sugestões anteriores para "trocar" na tela
        st.session_state.filmes_sugeridos = None 
        st.experimental_rerun() # Força o Streamlit a redesenhar a página
    
    # Se houver sugestões armazenadas, exibe-as (para manter na tela após o primeiro clique)
    if st.session_state.filmes_sugeridos:
        filmes_sugeridos_raw = st.session_state.filmes_sugeridos
        filmes_list = filmes_sugeridos_raw.strip().split('---\n')
        
        st.subheader("Suas Sugestões de Filmes:")
        for i, filme_text in enumerate(filmes_list):
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

st.info("Sua Filme.IA é alimentada por Google Gemini!")