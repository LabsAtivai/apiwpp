from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean

Base = declarative_base()


class MensagemWhatsapp(Base):
    """Mensagens recebidas via webhook da Cloud API (campo 'messages')."""
    __tablename__ = "mensagens_whatsapp"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), unique=True, nullable=False)  # messages[].id (idempotência)
    phone_number_id = Column(String(50), nullable=False)  # metadata.phone_number_id (número institucional)
    display_phone_number = Column(String(30), nullable=True)  # metadata.display_phone_number
    de = Column(String(30), nullable=False)  # messages[].from (número do contato)
    tipo = Column(String(30), nullable=False)  # text, image, audio, document, button, interactive...
    corpo = Column(Text, nullable=True)  # texto da mensagem, quando tipo=text
    payload = Column(Text, nullable=False)  # JSON bruto do evento inteiro, pra nunca perder dado
    recebido_em = Column(DateTime, nullable=False)


class StatusMensagemWhatsapp(Base):
    """Status de entrega/leitura (campo 'statuses'): sent, delivered, read, failed."""
    __tablename__ = "status_mensagens_whatsapp"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), nullable=False)  # statuses[].id, referencia mensagem enviada
    status = Column(String(20), nullable=False)
    phone_number_id = Column(String(50), nullable=False)
    destinatario = Column(String(30), nullable=True)  # statuses[].recipient_id
    payload = Column(Text, nullable=False)
    recebido_em = Column(DateTime, nullable=False)
