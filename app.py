from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

ZAPI_TOKEN = '9D3046B6FE2D8358711BED7B'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

def buscar_resposta(mensagem_cliente):
    mensagem = mensagem_cliente.strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in mensagem:
            return item['resposta']
    return "Desculpe, não encontrei uma resposta para isso."

def enviar_resposta(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN
    }
    requests.post(ZAPI_URL, json=payload, headers=headers)

@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    numero = dados.get('phone')
    mensagem_recebida = dados.get('body', '')

    resposta = buscar_resposta(mensagem_recebida)
    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
