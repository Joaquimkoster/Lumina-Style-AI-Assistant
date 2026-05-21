# Lumina Style Bot

Chatbot de atendimento para uma loja ficticia de moda, desenvolvido em Python com Flet e integrado a IA da Groq. O projeto responde perguntas sobre produtos, pagamento, frete, trocas, suporte e tambem usa um catalogo local em JSON para consultar informacoes da loja.

## Funcionalidades

- Interface grafica simples usando Flet
- Chat com respostas em portugues e ingles
- Integracao com a API da Groq
- Consulta de produtos cadastrados em `bd.json`
- Busca por categorias, nomes de produtos e quantidades
- Calculo simples de frete usando CEP com ViaCEP
- Respostas prontas para pagamento, promocao, tabela de medidas, troca, suporte e rastreio
- Configuracao da API Key pela propria interface

## Tecnologias utilizadas

- Python
- Flet
- Groq API
- Requests
- Langdetect
- ViaCEP
- JSON

## Estrutura do projeto

```text
Lumina_Style/
├── main.py             # Arquivo de entrada do projeto
├── src/
│   ├── __init__.py
│   ├── app.py          # Interface grafica do chatbot
│   └── chatbot.py      # Logica de mensagens, produtos, idioma, frete e IA
├── data/
│   └── bd.json         # Base de dados da loja em portugues e ingles
├── .env.example        # Exemplo de configuracao da API Key
├── .gitignore
├── requirements.txt    # Dependencias do projeto
└── readme.md           # Documentacao do projeto
```

## Como executar

### 1. Clone ou baixe o projeto

```bash
git clone <url-do-repositorio>
cd Lumina_Style
```

Se voce ja tem a pasta do projeto, basta abrir o terminal dentro dela.

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

No Windows:

```bash
.venv\Scripts\activate
```

### 3. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 4. Configure a API Key da Groq

Ao abrir o aplicativo, clique em **Configurar API** e informe sua chave da Groq.

Ao salvar uma chave, o app cria um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
```

Se o campo da chave for apagado e salvo vazio, o app remove o arquivo `.env`.

> Importante: nao publique sua API Key em repositorios publicos.

### 5. Rode o projeto

```bash
python main.py
```

Tambem e possivel executar como modulo:

```bash
python -m src.app
```

## Exemplos de perguntas

```text
Quais produtos voces vendem?
Tem camiseta?
Quero 2 mochilas
Qual o frete para 01001-000?
Quais formas de pagamento?
Tem promocao?
Como funciona a troca?
Show me the products
Do you have sneakers?
```

## Base de dados

O arquivo `data/bd.json` guarda os dados da loja em dois idiomas:

- `pt`: respostas e produtos em portugues
- `en`: respostas e produtos em ingles

Cada produto possui campos como:

- `nome`
- `preco`
- `emoji`
- `cores`
- `categorias`
- `descricao`

## Como funciona

O fluxo principal fica em `processar_mensagem_total`, dentro de `src/chatbot.py`.

O chatbot primeiro tenta responder usando regras locais:

- identifica o idioma da mensagem;
- verifica se o usuario pediu informacoes prontas, como pagamento ou frete;
- identifica CEPs;
- busca produtos pelo nome ou categoria;
- calcula quantidade quando o usuario informa numeros.

Se nenhuma regra local resolver a mensagem, o projeto envia a pergunta para a Groq, incluindo os dados da loja como contexto.

## Melhorias futuras

- Adicionar testes automatizados
- Melhorar o visual da interface
- Adicionar historico de conversa
- Separar testes em uma pasta `tests/`
- Validar automaticamente o formato do `bd.json`
- Criar uma versao web publicada

## Autor

Projeto desenvolvido por Joaquim Koster como estudo de chatbot com IA, interface grafica e atendimento automatizado para e-commerce.
