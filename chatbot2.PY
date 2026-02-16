import json                                                                                # Import library for manipulating JSON data files.
import re                                                                                  # Imports a Regular Expression library for searching text patterns.
import os                                                                                  # Import library for manipulating file and directory paths.
from difflib import SequenceMatcher                                                        # Import tool to compare similarity between texts
from groq import Groq                                                                      # Import Groq API client to use AI (Llama)
import requests                                                                            # Imports library for making HTTP requests (used in ViaCEP)

client = Groq(api_key="put_your_key_here")                                                 # Initialize the Groq client with your API key to enable communication with the AI.

diretorio_atual = os.path.dirname(os.path.abspath(__file__))                               # Get the path to the folder where this script file is saved.

caminho_bd = os.path.join(diretorio_atual, "bd.json")                                      # Creates the full path to the database file 'bd.json'.
try:
   
    with open(caminho_bd, "r", encoding="utf-8") as f:                                     # Try opening the database file for reading with support for special characters.
        bd = json.load(f)                                                                  # Loads the JSON data into the variable 'bd'.
except (FileNotFoundError, json.JSONDecodeError) as e:                                     # If the file does not exist or is corrupted, it displays an error and creates an empty database.
    
    print(f"❌ Erro ao carregar banco de dados: {e}")
    bd = {"produtos": [], "pagamento": "Erro.", "suporte": "Erro."}

ultimo_produto = None                                                                      # Global variable to remember which was the last product mentioned in the conversation.

NUMEROS = {"um": 1, "dois": 2, "três": 3, "quatro": 4, "cinco": 5, "dez": 10}              # Dictionary for converting numbers written out in words into integer values.


def extrair_cep(msg):                                                                      # Function that uses Regex to find ZIP code patterns (8 digits with or without hyphens)
    match = re.search(r'\b\d{5}-?\d{3}\b', msg)                                            # Looking for the pattern 00000-000
    return match.group() if match else None                                                # Returns the found ZIP code or nothing.

def extrair_quantidade(msg):                                                               # Function to identify the quantity of items the user wants.
    numeros = re.findall(r'\d+', msg)                                                      # Try to find digit numbers (ex: "2")
    if numeros: return int(numeros[0])                                                     # If found, it returns the first number found.
    for palavra, valor in NUMEROS.items():                                                 # If not, check if you spelled it out in full (ex: "two").
        if palavra in msg.lower(): return valor
    return 1                                                                               # Default value if no quantity is detected.


def formatar_produto(produto, quantidade=1):                                               # Function that assembles the product's visual string with price, colors, and description.
    total = produto['preco'] * quantidade                                                  # It calculates the total value based on the quantity.
    msg = f"\n{produto['emoji']} {produto['nome']} - R${produto['preco']:.2f}"
    if quantidade > 1:                                                                     # If there is more than one item, add the total calculation to the message.
        msg += f" (Total para {quantidade} unidades - R${total:.2f})"
    msg += f"\nCores - {', '.join(produto.get('cores', []))}"                              # List available colors
    msg += f"\nDescrição - {produto['descricao']}\n"                                       # Add the product description.
    msg += "-"*40                                                                          # Aesthetic separator line
    return msg


def buscar_produto_msg(msg):                                                               # Function that checks if the user has mentioned any product from the database.
    global ultimo_produto                                                                  # Accesses the global context memory variable.
    msg_normalizada = msg.lower()                                                          # Write the message in lowercase to make it easier to search.
    qtd = extrair_quantidade(msg_normalizada)                                              # Detects the requested quantity.
    for p in bd.get("produtos", []):                                                       # Iterates through the list of products in the JSON.
                                                                                           # Checks if the product name or category is in the user's sentence.
        if p['nome'].lower() in msg_normalizada or any(c in msg_normalizada for c in p.get('categorias', [])):
            ultimo_produto = p                                                             # Saved as the last viewed product to maintain context.
            return formatar_produto(p, qtd)                                                # Returns the formatted product.
                                                                                           # If the user only mentioned a number without specifying the name, it's assumed they're referring to the last product viewed.
    if ultimo_produto and (re.search(r'\d+', msg_normalizada) or any(n in msg_normalizada for n in NUMEROS)):
        return formatar_produto(ultimo_produto, qtd)
    return None                                                                            # Returns nothing if no product is identified.


def calcular_frete_viacep(cep_digitado):                                                   # Function that queries the external API ViaCEP to retrieve an address and calculate shipping costs.
    cep_limpo = re.sub(r'\D', '', cep_digitado)                                            # Remove hyphens and letters, leaving only numbers.
    if len(cep_limpo) != 8: return "❌ Formato de CEP inválido."                           # Validates ZIP code size.
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"                                    # Public API URL
    try:
        response = requests.get(url, timeout=5)                                            # Makes the API request with a 5-second time limit.
        dados = response.json()                                                            # Converts the response to a Python dictionary.
        if "erro" in dados: return "❌ CEP não encontrado."                                # Check if the ZIP code exists.
        cidade, uf = dados['localidade'], dados['uf']                                      # Extract city and state
        
       
        if uf == "SP": prazo, valor = "2 a 4 dias úteis", "R$ 12,00"                       # Fictitious business logic for pricing and deadlines based on state (UF)
        elif uf in ["RJ", "MG", "PR", "SC", "RS"]: prazo, valor = "5 a 9 dias úteis", "R$ 25,50"
        else: prazo, valor = "10 a 15 dias úteis", "R$ 35,00"

        return f"🚚 Para {cidade}-{uf}:\n- Frete: {valor}\n- Prazo: {prazo}"
    except: return "⚠️ Erro ao consultar frete."                                           # Connection error handling

                                                                                            
def detectar_intencao_geral(msg):                                                          # Function that detects whether the user wants information about Payment or Support (JSON keys)
    msg_l = msg.lower()
    for chave in bd:                                                                       # Scans the main keys in the database (excluding products).
        if chave in msg_l and chave != "produtos":
            return bd[chave]                                                               # Returns the fixed text defined in the JSON for that query.
    return None


def resposta_groq(msg):                                                                    # Function that activates Artificial Intelligence (Groq/Llama) for general conversations
    global last_product
    try:
        
        p_contexto = ultimo_produto['nome'] if ultimo_produto else "nenhum"                # Define which product is being targeted so the AI ​​knows what they're talking about.
       
        sistema = f"Você é o chatbot da Lumina Style. REGRAS: SEM negrito (**), use '-' para separar. Contexto: {p_contexto}."  # Personality configuration and strict rules for AI
        
        completion = client.chat.completions.create(                                       # Creates the chat request for the Groq API.
            model="llama-3.1-8b-instant",                                                  # Define the AI ​​model used.
            messages=[
                {"role": "system", "content": sistema},                                    # Send the behavior instructions.
                {"role": "system", "content": "Dados: " + json.dumps(bd, ensure_ascii=False)}, # Feed the AI ​​with your database.
                {"role": "user", "content": msg}                                           # Send the user's question.
            ],
            timeout=10, max_tokens=250                                                     # Define time limits and response size.              
        )
        return completion.choices[0].message.content                                       # Returns the text generated by the AI.
    except Exception as e:
        return "Conexão instável. Pode repetir? 🌐"                                        # Error if the Groq API fails.


def processar_mensagem_total(msg_usuario):                                                 # Main function that decides which tool to use to respond (Orchestrator)

    res = detectar_intencao_geral(msg_usuario)                                             # 1º: Try to answer common general questions (Payment/Support)
    if res: return res
    
    
    cep = extrair_cep(msg_usuario)                                                         # 2º: If there is a postal code, focus on calculating shipping costs.
    if cep: return calcular_frete_viacep(cep)
    
    
    res = buscar_produto_msg(msg_usuario)                                                  # 3º: If you mention a product, look for the item's technical information.
    if res: return res
    
    
    return resposta_groq(msg_usuario)                                                      # 4º: If nothing above works, AI takes over the conversation.

print("🛍️ Chatbot Lumina Style iniciado!")                                                # Log message in the terminal


while True:                                                                               # Infinite loop to keep the bot running in the terminal.
    try:
        msg_usuario = input("\nVocê: ").strip()                                           # Receives text from the user and clears up spaces.
        if not msg_usuario: continue                                                      # If empty, return to the beginning of the loop.
        if msg_usuario.lower() in ["sair", "tchau"]:                                      # Output command
            print("Bot: Até breve! 💙")
            break

        
        resposta = processar_mensagem_total(msg_usuario)                                 # It processes the message and generates the final response.
        
        
        print(f"Bot: {resposta.replace('*', '')}")                                       # Displays the answer removing asterisks (extra formatting cleanup).

    except KeyboardInterrupt:                                                            # Exit the program if you press Ctrl+C.
        break
    except Exception as e:                                                               # It captures and displays any unexpected errors.
        print(f"🚨 Erro: {e}")




# ------------------------ put this in a "bd.json" file ------------------------


{
  "produtos": [
    {
      "nome": "Camiseta Oversized Urban Vibes",
      "preco": 79.90,
      "emoji": "👕",
      "cores": ["Preto", "Branco", "Azul", "Vermelho"],
      "categorias": ["camiseta", "camisa", "blusa", "camisetas"],
      "descricao": "Camiseta de algodão premium com corte moderno e caimento confortável."
    },
    {
      "nome": "Mochila Anti-furto Urban",
      "preco": 149.90,
      "emoji": "🎒",
      "cores": ["Preto", "Azul", "Vermelho"],
      "categorias": ["mochila", "mochilas"],
      "descricao": "Segurança e estilo para o seu dia a dia, com compartimento oculto."
    },
    {
      "nome": "Vestido Midi Floral",
      "preco": 119.90,
      "emoji": "👗",
      "cores": ["Rosa", "Azul", "Branco"],
      "categorias": ["vestido", "vestidos"],
      "descricao": "Leveza e elegância para dias ensolarados."
    },
    {
      "nome": "Boné Classic Street",
      "preco": 59.90,
      "emoji": "🧢",
      "cores": ["Preto", "Branco", "Azul"],
      "categorias": ["boné", "bone", "bonés"],
      "descricao": "Acessório indispensável para compor seu look streetwear."
    },
    {
      "nome": "Calça Cargo Urban",
      "preco": 139.90,
      "emoji": "👖",
      "cores": ["Preto", "Branco", "Azul", "Vermelho"],
      "categorias": ["calça", "calças", "calca"],
      "descricao": "Calça resistente com múltiplos bolsos e ajuste moderno."
    },
    {
      "nome": "Jaqueta Corta-Vento Street",
      "preco": 189.90,
      "emoji": "🧥",
      "cores": ["Preto", "Azul", "Vermelho"],
      "categorias": ["jaqueta", "jaquetas", "casaco"],
      "descricao": "Proteção contra o vento com tecido leve e impermeável."
    },
    {
      "nome": "Tênis Urban Comfort",
      "preco": 199.90,
      "emoji": "👟",
      "cores": ["Preto", "Branco", "Azul", "Vermelho"],
      "categorias": ["tênis", "tenis", "sapato"],
      "descricao": "Conforto extremo para longas caminhadas no asfalto."
    },
    {
      "nome": "Colar Prata Urban",
      "preco": 49.90,
      "emoji": "📿",
      "categorias": ["colar", "colares", "acessórios"],
      "descricao": "Colar de prata 925 com pingente geométrico minimalista."
    },
    {
      "nome": "Pulseira de Couro",
      "preco": 34.90,
      "emoji": "⌚",
      "categorias": ["pulseira", "pulseiras", "acessórios"],
      "descricao": "Pulseira em couro legítimo com fecho magnético reforçado."
    },
    {
      "nome": "Brincos de Argola",
      "preco": 29.90,
      "emoji": "👂",
      "categorias": ["brinco", "brincos", "acessórios"],
      "descricao": "Argolas leves em aço cirúrgico, ideais para uso diário."
    },
    {
      "nome": "Anel Signo",
      "preco": 39.90,
      "emoji": "💍",
      "categorias": ["anel", "anéis", "acessórios"],
      "descricao": "Anel ajustável com gravação personalizada a laser."
    }
  ],
  "promoções": "🎉 Promoções do dia:\n- Camisetas: 20% OFF\n- Mochilas: Frete grátis\n- Vestidos: Leve 2 e pague 1",
  "tabela de medidas": "📏 Tabela de medidas:\nP: 165–175 cm / 55–65 kg\nM: 170–180 cm / 65–75 kg\nG: 175–185 cm / 75–85 kg\nGG: 180–195 cm / 85–100 kg",
  "pagamento": "💸 Aceitamos PIX, cartão, boleto e Mercado Pago.",
  "pix": "🔥 Pagando via PIX você ganha 10% de desconto!",
  "cartão": "💳 Aceitamos Visa, MasterCard, Elo e mais.",
  "troca": "🔁 Trocas e devoluções em até 7 dias após o recebimento.",
  "rastrear": "📦 Assim que o pedido for enviado, o código aparecerá aqui no chat.",
  "frete": "🚚 Enviamos para todo o Brasil! Me diga o CEP para calcular.",
  "suporte": "📞 Suporte 08h–18h\nEmail: suporte@luminastyle.com\nWhatsApp: (11) 99999-9999",
  "horário": "⏰ A loja funciona 24h online.",
  "menu": "Aqui está o menu principal:\n1. Ver produtos\n2. Tabela de medidas\n3. Formas de pagamento\n4. Informações de frete\n5. Troca e devolução"
}

# -------------------------------------------------------------------------------------------------------------------------------------------------------------

# To run this project, create a folder on your computer and save the Python code as main.py and the data as bd.json, ensuring they are both in the same location. 
# Then, open the terminal in that folder, install the necessary dependencies with the command pip install groq requests, and be sure to replace the text "put_your_key_here" in the code with your actual Groq API key. 
# Finally, run the bot with the command python main.py and interact through the terminal, testing product searches (ex: "backpack details"), shipping cost calculations (by entering a valid ZIP code), or general conversations, 
# remembering that the system prioritizes the information in your JSON before consulting the artificial intelligence.