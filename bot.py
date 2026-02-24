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

@bot.message_handler(commands=['start', 'help'])
def enviar_bienvenida(message):
    bot.reply_to(message, "¡Hola! Soy tu bot de servidor. Estoy vivo y listo para recibir órdenes.")

@bot.message_handler(func=lambda message: message.text.lower() == 'ping')
def responder_ping(message):
    bot.reply_to(message, "¡Pong! 🏓 El servidor Agathos sigue vivo.")

@bot.message_handler(func=lambda message: True)
def charlar_con_ia(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        configuracion = types.GenerateContentConfig(
            system_instruction=PERSONALITY,
        )
        
        respuesta = modelo.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
            config=configuracion
        )
        
        bot.reply_to(message, respuesta.text)
        
    except Exception as e:
        bot.reply_to(message, f"Uf, me ha dado un error en la nube: {e}")

print("Iniciando el botardo... Presiona Ctrl+C para detenerlo.")
bot.infinity_polling()