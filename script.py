import streamlit as st
import google.generativeai as genai
import re

api_key = st.secrets['API_KEY']
genai.configure(api_key = api_key) 

# Mudando para o modelo 'gemini-1.5-pro' para melhor precisão e aderência a instruções complexas,
# especialmente quando se trata de buscar informações reais.
model = genai.GenerativeModel("gemini-1.5-pro")

def sugerir_filme_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar sugestão de filme: {str(e)}"

st.set_page_config(page_title="Seu Filme.IA", layout="centered")

st.title("Seu Filme.IA")
st.markdown("Deixe a inteligência artificial te ajudar para encontrar **filmes incríveis** com base nas suas preferências!")

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

# Adiciona a opção para o usuário escolher a quantidade de filmes
num_filmes_sugerir = st.slider(
    "Quantos filmes você gostaria de sugerir?",
    min_value=1,
    max_value=20,
    value=5, # Valor padrão de 5 filmes
    step=1
)

# Inicializa o estado da sessão para armazenar as sugestões
if 'filmes_sugeridos_str' not in st.session_state:
    st.session_state.filmes_sugeridos_str = None

# Função para gerar e exibir filmes, agora focada em filmes reais
def gerar_e_exibir_filmes():
    if not genero:
        st.warning("Por favor, selecione pelo menos um gênero para a sugestão.")
        st.session_state.filmes_sugeridos_str = None
        return
    
    generos_str = ", ".join(genero)

    # Prompt reajustado para pedir filmes REAIS e informações VERDADEIRAS
    prompt = (
        f"Gere {num_filmes_sugerir} filmes REAIS que se encaixem nas seguintes características:\n"
        f"- Faixa Etária: {faixa_etaria}\n"
        f"- Duração: {duracao}\n"
        f"- Nota Mínima Esperada: {nota_preferencia} de 5\n"
        f"- Gêneros: {generos_str}\n"
    )
    
    if ano_lancamento:
        prompt += f"- Ano de Lançamento a partir de: {ano_lancamento}\n"
    if atores_atrizes:
        prompt += f"- Atores/Atrizes que o filme teria: {atores_atrizes}\n"
    
    prompt += (
        f"\nInstruções de Formato (MUITO IMPORTANTE):"
        f"\n1. NÃO inclua nenhum texto introdutório, explicativo ou conclusivo, apenas as sugestões de filmes."
        f"\n2. Cada filme deve começar com a linha '###FILME_NOVO###' para fácil separação."
        f"\n3. Para cada filme, siga rigorosamente o formato, fornecendo informações REAIS:"
        f"\nTítulo: [Título do Filme]"
        f"\nSinopse: [Breve Sinopse - máximo de duas linhas]"
        f"\nDuração: [Duração aproximada, ex: 100 min]"
        f"\nFaixa Etária: [Faixa Etária oficial e real]"
        f"\nGêneros: [Gêneros reais]"
        f"\nNota de Crítica: [Nota de 1 a 5, com uma fonte real e conhecida, ex: '4.2/5 (IMDb)' ou '85% (Rotten Tomatoes)']"
        f"\nAno de Lançamento: [Ano real de lançamento]"
        f"\n" # Adiciona uma linha em branco para melhor leitura
    )

    with st.spinner(f"Procurando {num_filmes_sugerir} filmes perfeitos para você..."):
        filmes_sugeridos_raw = sugerir_filme_gemini(prompt)
        st.session_state.filmes_sugeridos_str = filmes_sugeridos_raw
        
        st.subheader("Suas Sugestões de Filmes:")
        
        # Usa expressões regulares para dividir os filmes de forma mais robusta
        filmes_list = re.split(r'###FILME_NOVO###', filmes_sugeridos_raw)
        filmes_list = [f.strip() for f in filmes_list if f.strip()]

        if not filmes_list:
            st.warning("Não foi possível gerar sugestões de filmes com os critérios informados. Tente ajustar as preferências ou gere novamente.")
            st.write(f"Resposta bruta do modelo (para depuração): {filmes_sugeridos_raw}") 
            return

        for i, filme_text in enumerate(filmes_list):
            st.markdown(f"### 🎬 Filme {i+1}")
            
            # Divide as linhas do texto do filme e processa
            lines = filme_text.strip().split('\n')
            
            titulo = ""
            sinopse = ""
            duracao_filme = ""
            faixa_etaria_filme = ""
            generos_filme = ""
            nota_critica = ""
            ano_lancamento_filme = ""

            for line in lines:
                if "Título:" in line:
                    titulo = line.replace('Título:', '').strip()
                elif "Sinopse:" in line:
                    sinopse = line.replace('Sinopse:', '').strip()
                elif "Duração:" in line:
                    duracao_filme = line.replace('Duração:', '').strip()
                elif "Faixa Etária:" in line:
                    faixa_etaria_filme = line.replace('Faixa Etária:', '').strip()
                elif "Gêneros:" in line:
                    generos_filme = line.replace('Gêneros:', '').strip()
                elif "Nota de Crítica:" in line:
                    nota_critica = line.replace('Nota de Crítica:', '').strip()
                elif "Ano de Lançamento:" in line:
                    ano_lancamento_filme = line.replace('Ano de Lançamento:', '').strip()

            if titulo: st.markdown(f"**{titulo}**")
            if sinopse: st.markdown(f"*{sinopse}*")
            if duracao_filme: st.write(f"Duração: {duracao_filme}")
            if faixa_etaria_filme: st.write(f"Faixa Etária: {faixa_etaria_filme}")
            if generos_filme: st.write(f"Gêneros: {generos_filme}")
            if nota_critica: st.write(f"Nota de Crítica: {nota_critica}")
            if ano_lancamento_filme: st.write(f"Ano de Lançamento: {ano_lancamento_filme}")

            st.markdown("---") # Separador visual entre os filmes

# Botão principal para sugerir filmes
if st.button("Sugerir Filmes", key="sugerir_primeira_vez"):
    gerar_e_exibir_filmes()

# Botão "Sugerir Outros Filmes" só aparece se já houver sugestões
if st.session_state.filmes_sugeridos_str:
    if st.button("Sugerir Outros Filmes", key="sugerir_novamente"):
        # Limpa as sugestões anteriores e força um novo ciclo de geração
        st.session_state.filmes_sugeridos_str = None 
        st.experimental_rerun()
    
    # Exibe as sugestões armazenadas na sessão (para manter na tela)
    else: 
        filmes_sugeridos_raw = st.session_state.filmes_sugeridos_str
        
        st.subheader("Suas Sugestões de Filmes:")
        
        filmes_list = re.split(r'###FILME_NOVO###', filmes_sugeridos_raw)
        filmes_list = [f.strip() for f in filmes_list if f.strip()]

        if not filmes_list: 
            st.warning("Não foi possível carregar as sugestões anteriores. Tente gerar novamente.")
        else:
            for i, filme_text in enumerate(filmes_list):
                st.markdown(f"### 🎬 Filme {i+1}")
                lines = filme_text.strip().split('\n')
                
                titulo = ""
                sinopse = ""
                duracao_filme = ""
                faixa_etaria_filme = ""
                generos_filme = ""
                nota_critica = ""
                ano_lancamento_filme = ""

                for line in lines:
                    if "Título:" in line:
                        titulo = line.replace('Título:', '').strip()
                    elif "Sinopse:" in line:
                        sinopse = line.replace('Sinopse:', '').strip()
                    elif "Duração:" in line:
                        duracao_filme = line.replace('Duração:', '').strip()
                    elif "Faixa Etária:" in line:
                        faixa_etaria_filme = line.replace('Faixa Etária:', '').strip()
                    elif "Gêneros:" in line:
                        generos_filme = line.replace('Gêneros:', '').strip()
                    elif "Nota de Crítica:" in line:
                        nota_critica = line.replace('Nota de Crítica:', '').strip()
                    elif "Ano de Lançamento:" in line:
                        ano_lancamento_filme = line.replace('Ano de Lançamento:', '').strip()

                if titulo: st.markdown(f"**{titulo}**")
                if sinopse: st.markdown(f"*{sinopse}*")
                if duracao_filme: st.write(f"Duração: {duracao_filme}")
                if faixa_etaria_filme: st.write(f"Faixa Etária: {faixa_etaria_filme}")
                if generos_filme: st.write(f"Gêneros: {generos_filme}")
                if nota_critica: st.write(f"Nota de Crítica: {nota_critica}")
                if ano_lancamento_filme: st.write(f"Ano de Lançamento: {ano_lancamento_filme}")
                st.markdown("---")

st.info("Sua Filme.IA é alimentada por Google Gemini!")