import telebot
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
PERSONALITY = os.getenv("PERSONALITY")

if not TOKEN or not GEMINI_KEY:
    raise ValueError("¡Cuidado! Faltan tokens en el archivo .env")

bot = telebot.TeleBot(TOKEN)
modelo = genai.Client(api_key=GEMINI_KEY)

BOT_USERNAME = bot.get_me().username

@bot.message_handler(commands=['start', 'help'])
def enviar_bienvenida(message):
    bot.reply_to(message, "¡Hola! Soy tu bot de servidor. Estoy vivo y listo para recibir órdenes.")

@bot.message_handler(func=lambda message: message.text.lower() == 'ping')
def responder_ping(message):
    bot.reply_to(message, "¡Pong! 🏓 El servidor Agathos sigue vivo.")

@bot.message_handler(func=lambda message: True)
def charlar_con_ia(message):
    es_grupo = message.chat.type in ['group', 'supergroup']
    texto_limpio = message.text

    # LÓGICA DE GRUPOS: Filtramos para no ser pesados
    if es_grupo:
        mencionado = f"@{BOT_USERNAME}" in message.text
        respondiendo = message.reply_to_message and message.reply_to_message.from_user.username == BOT_USERNAME
        
        if not (mencionado or respondiendo):
            return  # Si no es con nosotros, ignoramos el mensaje y salimos
        
        # Quitamos la mención del texto para no confundir a la IA
        texto_limpio = message.text.replace(f"@{BOT_USERNAME}", "").strip()
        if not texto_limpio:
            return

    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        configuracion = types.GenerateContentConfig(
            system_instruction=PERSONALITY,
        )
        
        respuesta = modelo.models.generate_content(
            model='gemini-2.5-flash',
            contents=texto_limpio, # Le pasamos el texto ya limpio
            config=configuracion
        )
        
        bot.reply_to(message, respuesta.text)
        
    except Exception as e:
        bot.reply_to(message, f"Uf, me ha dado un error en la nube: {e}")

print("Iniciando el botardo... Presiona Ctrl+C para detenerlo.")

bot.infinity_polling()