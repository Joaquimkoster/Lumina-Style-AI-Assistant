🛍️ Lumina Style Chatbot

An intelligent bilingual (PT/EN) virtual assistant for e-commerce, capable of searching for products, calculating real-time shipping via API, and answering general questions using Artificial Intelligence.
🚀 Features

    Auto Language Detection: Automatically identifies if the user is speaking Portuguese or English.

    Semantic Product Search: Recognizes items by name or category keywords.

    Real Shipping Calculation: Integrated with the ViaCEP API to consult Brazilian addresses and estimate costs/delivery times.

    Artificial Intelligence: Powered by the Llama-3.1-8b model via Groq for natural, fluid dialogues.

    Contextual Memory: Remembers the last product mentioned to handle follow-up questions (e.g., "I want two of those").

🛠️ Prerequisites

Before you begin, ensure you have:

    Python 3.8+ installed.

    A Groq API Key (get it for free at groq.com).

    The libraries listed in the installation step below.

📥 Installation & Setup
1. Clone the repository

git clone https://github.com/Joaquimkoster/Lumina-Style-AI-Assistant.git
cd lumina-style-bot

2. Install dependencies

Run the following command to install the required libraries:

pip install groq langdetect requests

3. Configure the Database

Ensure the bd.json file (containing the product and store data) is in the same folder as the Python script.
4. Configure the API Key

Open the Python file and locate line 24:

api_key = "PUT_YOUR_KEY_HERE"

Replace it with your actual Groq token.
🎮 How to Use

To start the bot, run:

python your_file_name.py

Interaction Examples:

    “I want to see the t-shirts” -> The bot will list details and prices.

    “Qual o frete para 01310-930?” -> The bot will fetch the location and provide shipping rates.

    “How does payment work?” -> The bot retrieves information directly from the database.

    “I want two of these” -> If you just viewed a product, it will calculate the total for 2 units.

💡 Developer Tips

    Customization: You can change the bot's "personality" by editing the sistema (system prompt) variable inside the resposta_groq function.

    Adding Products: To add new items, simply follow the pattern in bd.json. Add synonyms to the categorias list to improve the search accuracy.

    Security: Never upload your API Key to GitHub. Use environment variables (os.getenv) if you plan to make the repository public.

    Shipping Logic: Currently, shipping rules are static based on the State (UF). You can expand the calcular_frete_viacep function to calculate costs based on weight or dimensions.

📝 License

This project is for educational purposes. Feel free to use, modify, and adapt it!
