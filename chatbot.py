import json                                                                                     # Imports the library to read and manipulate .json data files
import re                                                                                       # Imports the regular expression module to search for patterns like ZIP codes and numbers
import os                                                                                       # Imports functions to interact with the operating system, such as folder paths
import requests                                                                                 # Imports the library to make HTTP requests (used to consult the ZIP code)
from groq import Groq                                                                           # Imports the Groq client to connect the bot to the artificial intelligence
from langdetect import detect, DetectorFactory                                                  # Imports tools to automatically identify the text language

DetectorFactory.seed = 0                                                                        # Ensures consistent results in language detection by setting a fixed seed

# 1. API Key Configuration
api_key = "put_your_key_here"                                                                   # Placeholder for you to insert your Groq Cloud access key
client = Groq(api_key=api_key)                                                                  # Initializes the Groq client using the key provided above

# 2. Database Configuration
diretorio_atual = os.path.dirname(os.path.abspath(__file__))                                    # Finds out in which folder this script file is saved
caminho_bd = os.path.join(diretorio_atual, "bd.json")                                           # Creates the full path to find the bd.json file in the same folder

def carregar_bd(lang="pt"):                                                                     # Defines the function that opens the database file
    try:                                                                                        # Tries to execute the code block below
        with open(caminho_bd, "r", encoding="utf-8") as f:                                      # Opens the bd.json file for reading with support for accents
            banco_total = json.load(f)                                                          # Converts the JSON file content into a Python dictionary
            return banco_total.get(lang, banco_total["pt"])                                     # Returns data in the requested language or Portuguese by default
    except Exception as e:                                                                      # In case an error occurs (like file not found)
        print(f"❌ Error loading database: {e}")                                                # Displays the error in the console
        return {"produtos": [], "pagamento": "Error.", "suporte": "Error."}                     # Returns an empty structure to prevent the bot from stopping

ultimo_produto = None                                                                           # Global variable to "remember" the last product mentioned in the conversation
NUMEROS = {                                                                                     # Dictionary to convert written numbers into digits
    "um": 1, "dois": 2, "três": 3, "quatro": 4, "cinco": 5, "dez": 10,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "ten": 10
}

# --- HELPER FUNCTIONS ---

def detectar_idioma(texto):                                                                    # Function that discovers if the user is speaking Portuguese or English
    """Detects if the text is in pt or en. Default: pt"""
    try:                                                                                       # Tries to detect the language
        lang = detect(texto)                                                                   # Uses the langdetect library on the user's text
        return "en" if lang == "en" else "pt"                                                  # If English is detected, returns 'en', otherwise returns 'pt'
    except:                                                                                    # If detection fails (text too short, for example)
        return "pt"                                                                            # Sets Portuguese as the default language

def extrair_cep(msg):                                                                          # Function that searches for a ZIP code format within the user's message
    match = re.search(r'\b\d{5}-?\d{3}\b', msg)                                                # Searches for the pattern: 5 numbers, an optional dash, and 3 more numbers
    return match.group() if match else None                                                    # Returns the ZIP code found or 'None' if nothing is found

def extrair_quantidade(msg):                                                                   # Function that tries to understand how many units the user wants to buy
    numeros = re.findall(r'\d+', msg)                                                          # Searches for any numeric digit in the message
    if numeros:                                                                                # If numbers are found (e.g.: "I want 2")
        return int(numeros[0])                                                                 # Returns the first number found as an integer
    for palavra, valor in NUMEROS.items():                                                     # If no digits, checks if there are numbers written in full
        if palavra in msg.lower():                                                             # If the word (e.g.: "two") is in the message
            return valor                                                                       # Returns the corresponding numeric value
    return 1                                                                                   # If no quantity reference is found, assumes it is just 1

def formatar_produto(produto, quantidade=1, lang="pt"):                                        # Function that creates the pretty text with product info
    total = produto['preco'] * quantidade                                                      # Calculates the total value by multiplying price by quantity
    moeda = "R$" if lang == "pt" else "$"                                                      # Defines the currency symbol according to the detected language

    msg = f"\n{produto['emoji']} {produto['nome']} - {moeda}{produto['preco']:.2f}"            # Creates the name and unit price line
    if quantidade > 1:                                                                         # If the user asked for more than one item
        label_total = "Total para" if lang == "pt" else "Total for"                            # Defines the total label text
        label_unid = "unidades" if lang == "pt" else "units"                                   # Defines the units label text
        msg += f" ({label_total} {quantidade} {label_unid} - {moeda}{total:.2f})"              # Adds the total calculation to the message

    cor_label = "Cores" if lang == "pt" else "Colors"                                          # Translates the "Colors" label
    desc_label = "Descrição" if lang == "pt" else "Description"                                # Translates the "Description" label

    msg += f"\n{cor_label} - {', '.join(produto.get('cores', []))}"                            # Adds the list of available colors
    msg += f"\n{desc_label} - {produto['descricao']}\n"                                        # Adds the product description
    msg += "-"*40                                                                              # Adds a divider line to organize the text
    return msg                                                                                 # Returns the formatted message ready for sending

def buscar_produto_msg(msg, bd_idioma, lang="pt"):                                             # Function that scans the database for the right product
    global ultimo_produto                                                                      # Allows the function to change the global variable that holds context
    msg_l = msg.lower()                                                                        # Transforms user message to lowercase to facilitate the search
    qtd = extrair_quantidade(msg_l)                                                            # Checks if the user mentioned quantity in the sentence

    for p in bd_idioma.get("produtos", []):                                                    # Iterates through each product list in the database
                                                                                               # Checks if product name or any category was mentioned in the message
        if p['nome'].lower() in msg_l or any(c in msg_l for c in p.get('categorias', [])):
            ultimo_produto = p                                                                 # Saves this product as the last one mentioned (for future questions)
            return formatar_produto(p, qtd, lang)                                              # Formats and returns product details

                                                                                               # If user only types a number, bot assumes they mean the last product seen
    if ultimo_produto and (re.search(r'\d+', msg_l) or any(n in msg_l for n in NUMEROS)):
        return formatar_produto(ultimo_produto, qtd, lang)                                     # Formats the last product with the new quantity
    return None                                                                                # If nothing related to products is found, returns 'None'

def calcular_frete_viacep(cep_digitado, lang):                                                 # Function that consults shipping using the ViaCEP API
    cep_limpo = re.sub(r'\D', '', cep_digitado)                                                # Removes dashes or dots, leaving only the 8 ZIP code numbers
    if len(cep_limpo) != 8:                                                                    # Checks if ZIP code has the correct length
        return "❌ CEP inválido." if lang == "pt" else "❌ Invalid ZIP code."                 # Returns error for short/long ZIP code
    try:                                                                                       # Tries to make the request to the internet
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5).json()      # Consults the ViaCEP website
        if "erro" in r:                                                                        # If the site responds that the ZIP code does not exist
            return "❌ CEP não encontrado." if lang == "pt" else "❌ ZIP code not found."

        uf, cidade = r['uf'], r['localidade']                                                  # Extracts State and City from result
        if uf == "SP":                                                                         # Business rule: shipping to São Paulo
            p, v = ("2 a 4 dias úteis", "R$ 12,00") if lang == "pt" else ("2-4 business days", "$ 12.00")
        elif uf in ["RJ", "MG", "PR", "SC", "RS"]:                                             # Shipping to South and Southeast (except SP)
            p, v = ("5 a 9 dias úteis", "R$ 25,50") if lang == "pt" else ("5-9 business days", "$ 25.50")
        else:                                                                                  # Shipping to the rest of Brazil
            p, v = ("10 a 15 dias úteis", "R$ 35,00") if lang == "pt" else ("10-15 business days", "$ 35.00")

        header = f"🚚 Para {cidade}-{uf}:" if lang == "pt" else f"🚚 To {cidade}-{uf}:"       # Creates the shipping header
        return f"{header}\n- {'Frete' if lang=='pt' else 'Shipping'}: {v}\n- {'Prazo' if lang=='pt' else 'Estimate'}: {p}"
    except:                                                                                    # In case of connection error or ViaCEP site failure
        return "⚠️ Erro ao consultar frete." if lang == "pt" else "⚠️ Error checking shipping."

# --- AI LOGIC ---

def resposta_groq(msg, lang, bd_idioma):                                                       # Function that triggers Llama 3 to talk freely
    try:
        p_ctx = ultimo_produto['nome'] if ultimo_produto else "none"                           # Passes to the AI which product is being discussed
        instrucao_idioma = "Responda em PORTUGUÊS." if lang == "pt" else "Respond in ENGLISH." # Forces the response language

        sistema = (                                                                            # Defines assistant personality and rules
            f"You are the Lumina Style assistant. {instrucao_idioma} "
            "Do not use bold (**). Use '-' for lists. "
            f"Context: {p_ctx}."
        )

        completion = client.chat.completions.create(                                          # Sends the conversation to the Groq server
            model="llama-3.1-8b-instant",                                                     # Chooses the fast and efficient AI model
            messages=[                                                                        # Assembles conversation history for AI processing
                {"role": "system", "content": sistema},                                       # Behavior rules
                {"role": "system", "content": "Store Data: " + json.dumps(bd_idioma, ensure_ascii=False)},  # Sends the database
                {"role": "user", "content": msg}                                              # The current user question
            ],
            temperature=0.1                                                                   # Defines "creativity": 0.1 makes the response more precise and less random
        )
        return completion.choices[0].message.content                                          # Returns only the AI's response text
    except:                                                                                   # If connection with Groq fails
        return "Connection Error 🌐"

# --- ORCHESTRATOR ---

def processar_mensagem_total(msg_usuario):                                                    # The "brain" that decides which function to call first
                                                                                              # Detects language automatically before everything to load correct database
    lang = detectar_idioma(msg_usuario)
    bd_idioma = carregar_bd(lang)
    msg_l = msg_usuario.lower()

    # 1. Checks if it's a question about general information (Menu, Payment, Support)
    for chave in bd_idioma:
        if chave != "produtos" and chave in msg_l:                                           # If the user typed a keyword (e.g.: "payment")
            return bd_idioma[chave]                                                          # Returns the direct response from the database

    # 2. Checks if the message contains a ZIP code to calculate shipping
    cep = extrair_cep(msg_usuario)
    if cep:
        return calcular_frete_viacep(cep, lang)

    # 3. Checks if the user is asking for a specific product
    res_prod = buscar_produto_msg(msg_usuario, bd_idioma, lang)
    if res_prod:
        return res_prod

    # 4. If it's nothing specific, let the AI decide how to respond
    return resposta_groq(msg_usuario, lang, bd_idioma)

# --- EXECUTION ---

print("🛍️ Chatbot Lumina Style (Auto-Detection Active)")                                   # Displays initial message in the terminal
print("Say 'Sair' to exit.")                                                               # Explains how to close the program

while True:                                                                                # Starts an infinite loop to keep the chat running
    try:
        msg_usuario = input("\nYou: ").strip()                                             # Captures user input and removes useless spaces

        if not msg_usuario:                                                                # If user presses Enter without typing anything
            continue                                                                       # Returns to the start of the loop

        if msg_usuario.lower() in ["sair", "exit", "quit"]:                                # Checks if user wants to close
            print("Até logo! / See you soon! 💙")
            break                                                                          # Breaks the loop and closes the program

        resposta = processar_mensagem_total(msg_usuario)                                   # Processes message and generates response
        
        print(f"Bot: {resposta.replace('*', '')}")                                         # Cleans bold characters AI might use and displays bot response
    except KeyboardInterrupt:                                                              # If user presses Ctrl+C
        break                                                                              # Closes the program
    except Exception as e:                                                                 # If any other unexpected error occurs
        print(f"🚨 Unexpected error: {e}")                                                 # Displays error for diagnostics
