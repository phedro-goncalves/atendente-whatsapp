from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

ZAPI_TOKEN = '538C273AC0E03C3DFD9D1B67'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

# Carrega o arquivo JSON com palavras-chave e respostas
with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

# Função para buscar resposta com base na mensagem
def buscar_resposta(mensagem_cliente):
    texto = str(mensagem_cliente).strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in texto:
            return item['resposta']
    return "Desculpe, não encontrei uma resposta para isso."

# Função para enviar mensagem via Z-API
def enviar_resposta(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN
    }

    print("📤 Enviando resposta para:", numero)
    print("📨 Mensagem:", mensagem)

    response = requests.post(ZAPI_URL, json=payload, headers=headers)

    print("✅ Status:", response.status_code)
    print("📬 Resposta da ZAPI:", response.text)

# Webhook que recebe as mensagens
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    print("📥 Dados recebidos:", dados)

    numero = dados.get('phone')
    mensagem_recebida = dados.get('body', '')

    if not numero or not mensagem_recebida:
        print("⚠️ Número ou mensagem vazia")
        return jsonify({"erro": "Número ou mensagem ausente"}), 400

    resposta = buscar_resposta(mensagem_recebida)
    print("🤖 Resposta encontrada:", resposta)

    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

# Executa localmente (útil para testes locais)
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
