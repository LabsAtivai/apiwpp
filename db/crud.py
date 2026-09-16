import json
from datetime import datetime

from db.session import SessionLocal
from db.models import MensagemWhatsapp, StatusMensagemWhatsapp


def salvar_mensagem(message_id, phone_number_id, display_phone_number, de, tipo, corpo, payload):
    session = SessionLocal()
    try:
        existente = session.query(MensagemWhatsapp).filter_by(message_id=message_id).first()
        if existente:
            return existente.id, False  # já processado (Meta reenvia em retry)

        registro = MensagemWhatsapp(
            message_id=message_id,
            phone_number_id=phone_number_id,
            display_phone_number=display_phone_number,
            de=de,
            tipo=tipo,
            corpo=corpo,
            payload=json.dumps(payload, ensure_ascii=False),
            recebido_em=datetime.now(),
        )
        session.add(registro)
        session.commit()
        return registro.id, True
    finally:
        session.close()


def salvar_status(message_id, status, phone_number_id, destinatario, payload):
    session = SessionLocal()
    try:
        registro = StatusMensagemWhatsapp(
            message_id=message_id,
            status=status,
            phone_number_id=phone_number_id,
            destinatario=destinatario,
            payload=json.dumps(payload, ensure_ascii=False),
            recebido_em=datetime.now(),
        )
        session.add(registro)
        session.commit()
        return registro.id
    finally:
        session.close()
