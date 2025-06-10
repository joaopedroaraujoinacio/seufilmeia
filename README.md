# Seu Filme.IA

## Participantes
- Etienne Pedro Pautet
- Fabiano Quirino
- João Pedro Araújo Inácio
- Renan Chacon

## Descrição
Aplicação Streamlit que utiliza IA (Google Gemini) para sugerir filmes personalizados baseados nas preferências do usuário, com pré-requisitos como por exemplo, a faixa etária, nota, duração e os possíveis gêneros. A aplicação também conta com a função de identificar filmes, caso a necessidade seja descobrir de qual filme se trata, com as informações fornecidas pelo usuário.

## Pré-requisitos
- Python 3.7+
- Conta Google Cloud com acesso à API Gemini
- Chave API do Google Generative AI

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/joaopedroaraujoinacio/seufilmeia
cd seufilmeia
```

2. Instale as dependências:
```bash
pip install streamlit
pip install google-generativeai
```

## Como Executar

1. No terminal, navegue até o diretório do projeto
2. Execute o comando:
```bash
streamlit run app.py
```

3. Acesse o aplicativo no navegador através do link fornecido (`https://seufilmeia-kew2t9szth2zyufxzl2mnk.streamlit.app/`)

## Funcionalidades
- Seleção de faixa etária
- Escolha de duração preferida
- Definição de nota mínima
- Seleção múltipla de gêneros
- Seleção da quantidade de sugestões
- Geração de sugestões personalizadas via IA
- Identificação de filme baseado nas informações fornecidas pelo usuário

## Estrutura do Projeto
```
seufilmeia/
├── streamlit_env
├── README.md
├── requirements.txt
└── script.py
```
