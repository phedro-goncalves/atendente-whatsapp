from flask import Flask, request, jsonify
import json
import requests
import os

app = Flask(__name__)

# ⚙️ Configuração da Z-API
ZAPI_TOKEN = '9D3046B6FE2D8358711BED7B'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

# 📄 Carrega as respostas do arquivo JSON
with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

# 🔍 Busca a resposta com base na palavra-chave
def buscar_resposta(mensagem_cliente):
    mensagem = mensagem_cliente.strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in mensagem:
            return item['resposta']
    return "Desculpe, não encontrei uma resposta para isso."

# 📤 Envia a resposta para o cliente via Z-API
def enviar_resposta(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN
    }
    response = requests.post(ZAPI_URL, json=payload, headers=headers)
    print("Resposta enviada:", response.status_code, response.text)

# 🔁 Webhook que escuta as mensagens da Z-API
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    corpo = dados.get('body', {})
    mensagem_recebida = corpo.get('message', '')
    numero = corpo.get('phone', '')

    if not mensagem_recebida or not numero:
        return jsonify({"status": "erro", "mensagem": "Mensagem ou número ausente"}), 400

    resposta = buscar_resposta(mensagem_recebida)
    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

# 🚀 Rodar o app com host e porta correta para a Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
