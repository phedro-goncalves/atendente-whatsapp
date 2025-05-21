from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

ZAPI_TOKEN = '538C273AC0E03C3DFD9D1B67'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

def buscar_resposta(mensagem_cliente):
    texto = str(mensagem_cliente).strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in texto:
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

    print("📤 Enviando resposta para:", numero, flush=True)
    print("📨 Mensagem:", mensagem, flush=True)

    try:
        response = requests.post(ZAPI_URL, json=payload, headers=headers)
        print("✅ Status:", response.status_code, flush=True)
        print("📬 Resposta da ZAPI:", response.text, flush=True)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", str(e), flush=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    print("📥 Dados recebidos:", dados, flush=True)

    numero = dados.get('phone')
    mensagem_recebida = dados.get('texto', {}).get('mensagem', '')

    print("🔎 Número:", numero, flush=True)
    print("🔎 Tipo da mensagem:", type(mensagem_recebida), flush=True)
    print("🔎 Conteúdo da mensagem:", repr(mensagem_recebida), flush=True)

    if not numero or not mensagem_recebida:
        print("⚠️ Número ou mensagem ausente", flush=True)
        return jsonify({"erro": "Número ou mensagem ausente"}), 400

    resposta = buscar_resposta(mensagem_recebida)
    print("🤖 Resposta encontrada:", resposta, flush=True)

    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
