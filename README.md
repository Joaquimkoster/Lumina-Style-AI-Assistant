🛍️ Lumina Style Chatbot

Um assistente virtual bilíngue (PT/EN) inteligente para e-commerce, capaz de consultar produtos, calcular frete em tempo real via API e responder dúvidas gerais usando Inteligência Artificial.
🚀 Funcionalidades

    Detecção Automática de Idioma: Identifica se o usuário fala Português ou Inglês.

    Busca Semântica de Produtos: Reconhece itens por nome ou categoria.

    Cálculo de Frete Real: Integração com a API ViaCEP para consultar endereços brasileiros.

    Inteligência Artificial: Utiliza o modelo llama-3.1-8b da Groq para diálogos naturais.

    Memória de Contexto: Lembra do último produto mencionado para facilitar a compra.

🛠️ Pré-requisitos

Antes de começar, você precisará de:

    Python 3.8+ instalado.

    Uma API Key da Groq (obtenha gratuitamente em groq.com).

    As bibliotecas listadas no passo a passo abaixo.

📥 Instalação e Configuração
1. Clonar o repositório

git clone https://github.com/seu-usuario/lumina-style-bot.git
cd lumina-style-bot

2. Instalar dependências

Execute o comando abaixo para instalar as bibliotecas necessárias:
Bash

pip install groq langdetect requests

3. Configurar a Base de Dados

Certifique-se de que o arquivo bd.json (com o conteúdo JSON que você forneceu) esteja na mesma pasta do script Python.
4. Configurar a API Key

Abra o arquivo Python e localize a linha 24:
Python

api_key = "COLOQUE_SUA_CHAVE_AQUI"

Substitua pelo seu token da Groq.
🎮 Como Usar

Para iniciar o bot, execute:

python seu_arquivo.py

Exemplos de interação:

    “Quero ver as camisetas” -> O bot listará os detalhes e preços.

    “What is the shipping for 01310-930?” -> O bot consultará a localização e dará o valor.

    “Como funciona o pagamento?” -> O bot trará as informações do banco de dados.

    “I want two of these” -> Se você acabou de ver um produto, ele calculará o total para 2 unidades.

💡 Dicas para o Desenvolvedor

    Personalização: Você pode alterar a "personalidade" do bot editando a variável sistema dentro da função resposta_groq.

    Novas Categorias: Para adicionar produtos, basta seguir o padrão no bd.json. Lembre-se de adicionar sinônimos na lista de categorias     para que a busca direta funcione melhor.

    Segurança: Nunca suba sua API Key para o GitHub. Use variáveis de ambiente (os.getenv) se for tornar o repositório público.

    Melhoria no Frete: Atualmente, as regras de preço de frete são estáticas por estado. Você pode expandir a função calcular_frete_viacep para calcular o peso dos itens.

📝 Licença

Este projeto é para fins educacionais. Sinta-se à vontade para usar e adaptar!
