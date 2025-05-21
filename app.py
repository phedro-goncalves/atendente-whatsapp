from flask import Flask, request, jsonify
import json
import requests
import os

app = Flask(__name__)

# 🔧 Configuração da Z-API
ZAPI_TOKEN = '9D3046B6FE2D8358711BED7B'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

# 📚 Base de conhecimento
with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

# 🔍 Busca a resposta correta
def buscar_resposta(mensagem_cliente):
    mensagem = mensagem_cliente.strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in mensagem:
            return item['resposta']
    return "Desculpe, não encontrei uma resposta para isso."

# 📤 Envia a resposta via Z-API
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
    print(f"✅ Enviando para {numero} | Status: {response.status_code}")
    print(f"📦 Payload: {payload}")
    print(f"📨 Resposta Z-API: {response.text}")

# 🔁 Webhook que recebe mensagens da Z-API
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    print("🟡 JSON recebido:", dados)

    mensagem_recebida = ''
    numero = ''

    try:
        # Captura segura dos dados
        if isinstance(dados, dict):
            corpo = dados.get("body", dados)
            mensagem_recebida = corpo.get("message", "") or corpo.get("text", "")
            numero = corpo.get("phone", "") or corpo.get("from", "")
    except Exception as e:
        print("❌ Erro ao interpretar JSON:", e)
        return jsonify({"status": "erro", "mensagem": "Erro ao processar dados"}), 400

    if not mensagem_recebida or not numero:
        print("⚠️ Dados ausentes:", mensagem_recebida, numero)
        return jsonify({"status": "erro", "mensagem": "Mensagem ou número ausente"}), 400

    resposta = buscar_resposta(mensagem_recebida)
    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

# 🚀 Inicialização correta para ambientes como Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
