from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

# Função para enviar lembrete
def enviar_lembrete(mensagem):
    client.messages.create(
        from_=TWILIO_NUMBER,
        body=f"🔔 Lembrete: {mensagem}",
        to=MY_NUMBER
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body").lower()
    resp = MessagingResponse()

    if "lembre" in msg:
        try:
            partes = msg.split("lembre de")[1].strip()
            if "às" in partes:
                texto, hora = partes.split("às")
                texto = texto.strip()
                hora = hora.strip().replace("horas", "").replace("h", "").strip()
                hora_int = int(hora.split(":")[0])
                minuto_int = int(hora.split(":")[1]) if ":" in hora else 0

                agendamento = datetime.now().replace(hour=hora_int, minute=minuto_int, second=0, microsecond=0)
                if agendamento < datetime.now():
                    agendamento = agendamento.replace(day=agendamento.day + 1)

                scheduler.add_job(enviar_lembrete, 'date', run_date=agendamento, args=[texto])
                resp.message(f"Lembrete agendado para {hora_int:02d}:{minuto_int:02d} ✅")

            else:
                resp.message("Por favor, diga o horário. Exemplo: 'me lembre de comprar pão às 19h'")
        except Exception as e:
            resp.message(f"Erro ao processar lembrete: {e}")
    else:
        resp.message("Envie algo como: 'Me lembre de beber água às 15h'")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
