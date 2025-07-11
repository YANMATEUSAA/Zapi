import requests
import json
from flask import Flask, request

# Configuração
# Substitua pelas suas credenciais reais da plataforma Meta
ACCESS_TOKEN = ""
PHONE_NUMBER_ID = ""

# Tokens e URLs
VERIFY_TOKEN = "" # Seu token secreto do webhook
OLLAMA_API_URL = "http://localhost:/api/chat"
WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

app = Flask(__name__)

# Função para se comunicar com a IA (Ollama)
def get_ai_response(user_message):
    """Envia a mensagem do usuário para o Ollama e retorna a resposta da IA."""
    print(f"[*] Enviando para a IA: {user_message}")
    payload = {"model": "llama3.1", "messages": [{"role": "user", "content": user_message}], "stream": False}
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=90)
        response.raise_for_status()
        ai_message = response.json()['message']['content']
        print(f"[*] Resposta da IA recebida: {ai_message}")
        return ai_message
    except requests.exceptions.RequestException as e:
        print(f"[!] Erro ao conectar com o Ollama: {e}")
        return "Desculpe, estou com problemas para me conectar à minha inteligência."

# Função para ENVIAR mensagens para o WhatsApp
def send_whatsapp_message(recipient_id, message_text):
    """Envia uma mensagem de texto para um destinatário no WhatsApp."""
    print(f"[*] Enviando resposta para {recipient_id}: {message_text}")
    
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message_text}
    }
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        print(f"[*] Mensagem enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"[!] Erro ao enviar mensagem para o WhatsApp: {e.response.text}")

# Endpoint do Webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        return "OK", 200

    if request.method == 'POST':
        data = request.get_json()
        print(f"\n[*] Notificação completa recebida: {json.dumps(data, indent=2)}")
        
        try:
            sender_id = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            user_message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            print(f"[*] Mensagem de {sender_id}: '{user_message}'")
            
            ai_response = get_ai_response(user_message)
            
            send_whatsapp_message(sender_id, ai_response)

        except (KeyError, IndexError):
            print("[*] Notificação recebida não é uma mensagem de usuário. Ignorando.")
            pass
            
        return "OK", 200

# Inicia o servidor 
if __name__ == "__main__":
    app.run(port=5000, debug=True)
