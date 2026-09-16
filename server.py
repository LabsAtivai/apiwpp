import hashlib
import hmac
import os

from flask import Flask, jsonify, request

from db.session import create_tables
from db import crud

create_tables()

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
APP_SECRET = os.environ.get("APP_SECRET", "")


@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    modo = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if modo == "subscribe" and token and VERIFY_TOKEN and hmac.compare_digest(token, VERIFY_TOKEN):
        return challenge, 200
    return "forbidden", 403


def assinatura_valida(raw_body: bytes) -> bool:
    if not APP_SECRET:
        return True  # sem APP_SECRET configurado, pula validação (não recomendado em produção)
    assinatura = request.headers.get("X-Hub-Signature-256", "")
    if not assinatura.startswith("sha256="):
        return False
    esperado = "sha256=" + hmac.new(APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(assinatura, esperado)


@app.route("/webhook", methods=["POST"])
def receber_evento():
    raw = request.get_data()
    if not assinatura_valida(raw):
        return jsonify({"error": "assinatura inválida"}), 401

    body = request.get_json(silent=True) or {}
    if body.get("object") != "whatsapp_business_account":
        return "", 200

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            valor = change.get("value", {})
            metadata = valor.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")
            display_phone_number = metadata.get("display_phone_number")

            for msg in valor.get("messages", []):
                tipo = msg.get("type")
                corpo = msg.get("text", {}).get("body") if tipo == "text" else None
                crud.salvar_mensagem(
                    message_id=msg.get("id"),
                    phone_number_id=phone_number_id,
                    display_phone_number=display_phone_number,
                    de=msg.get("from"),
                    tipo=tipo,
                    corpo=corpo,
                    payload=msg,
                )

            for status in valor.get("statuses", []):
                crud.salvar_status(
                    message_id=status.get("id"),
                    status=status.get("status"),
                    phone_number_id=phone_number_id,
                    destinatario=status.get("recipient_id"),
                    payload=status,
                )

    return jsonify({"received": True}), 200


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    app.run(host="0.0.0.0", port=port)
