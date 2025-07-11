from flask import Flask, request

# Cria a aplicação Flask
app = Flask(__name__)

# Token para verificação (pode ser qualquer string secreta)
VERIFY_TOKEN = "token-secreto-aqui" 

# Endpoint que receberá os webhooks
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # --- Parte de Verificação (usada apenas na configuração inicial) ---
    if request.method == 'GET':
        # A Meta envia esses parâmetros para verificar seu endpoint
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        return "Hello world", 200

    # --- Parte de Recebimento de Mensagens ---
    if request.method == 'POST':
        # Obtém o corpo da notificação
        data = request.get_json()
        print("=======================================")
        print("MENSAGEM RECEBIDA:")
        print(data) # Imprime a mensagem completa no terminal
        print("=======================================")

        # Aqui, no futuro, vamos enviar a mensagem para o Llama3

        return "Message received", 200

# Inicia o servidor
if __name__ == "__main__":
    app.run(port=5000, debug=True)