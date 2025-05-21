from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Configuração da Z-API
ZAPI_TOKEN = '538C273AC0E03C3DFD9D1B67'
ZAPI_INSTANCE = '3E17A25DC8280054AB9B16374B74BED7'
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-messages"

# Carrega a base de conhecimento do arquivo JSON
with open('respostas.json', 'r', encoding='utf-8') as f:
    BASE_CONHECIMENTO = json.load(f)

# Função para buscar a resposta com base na palavra-chave
def buscar_resposta(mensagem_cliente):
    if not isinstance(mensagem_cliente, str):
        print("[Erro] mensagem_cliente não é string:", mensagem_cliente)
        return "Desculpe, não entendi sua pergunta."

    mensagem = mensagem_cliente.strip().lower()
    for item in BASE_CONHECIMENTO:
        if item['palavra'] in mensagem:
            return item['resposta']
    return "Desculpe, não encontrei uma resposta para isso."

# Envia a mensagem via Z-API
def enviar_resposta(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN  # ATENÇÃO: deve ser "Client-Token"
    }

    response = requests.post(ZAPI_URL, json=payload, headers=headers)

    # Logs para análise
    print("➡️ Enviando mensagem para:", numero)
    print("📝 Conteúdo:", mensagem)
    print("📦 Payload:", payload)
    print("✅ Status Code:", response.status_code)
    print("🔁 Resposta da API:", response.text)

# Rota do webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()

    print("📨 Dados recebidos no webhook:", dados)

    numero = dados.get('phone')
    mensagem_recebida = dados.get('body', '')

    resposta = buscar_resposta(mensagem_recebida)
    enviar_resposta(numero, resposta)

    return jsonify({"status": "ok", "resposta": resposta})

# Início do app Flask
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=10000)
