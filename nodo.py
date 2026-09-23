from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import sys
from datetime import datetime


# ============================================================
# CONFIGURACIÓN DEL NODO
# ============================================================

if len(sys.argv) < 3:
    print("Uso:")
    print("python nodo.py <id_nodo> <puerto>")
    print("Ejemplo:")
    print("python nodo.py 1 8001")
    sys.exit(1)


NODE_ID = int(sys.argv[1])
PORT = int(sys.argv[2])

TOTAL_NODES = 3


# ============================================================
# INFORMACIÓN DE LOS NODOS
# ============================================================

NODES = {
    1: "http://127.0.0.1:8001",
    2: "http://127.0.0.1:8002",
    3: "http://127.0.0.1:8003"
}


# ============================================================
# RELOJ VECTORIAL
# ============================================================

vector_clock = [0] * TOTAL_NODES


# ============================================================
# REGISTRO DE EVENTOS
# ============================================================

events = []


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title=f"Nodo {NODE_ID} - Sistema Distribuido",
    description="Simulación de relojes vectoriales",
    version="1.0"
)


# ============================================================
# MODELO PARA RECIBIR MENSAJES
# ============================================================

class Message(BaseModel):
    sender: int
    clock: list[int]
    message: str


# ============================================================
# FUNCIÓN PARA GUARDAR EVENTOS
# ============================================================

def register_event(event_type, description, before, after):
    event = {
        "timestamp": datetime.now().isoformat(),
        "node": NODE_ID,
        "type": event_type,
        "description": description,
        "before": before,
        "after": after
    }

    events.append(event)

    print("\n" + "=" * 70)
    print(f"EVENTO EN NODO {NODE_ID}")
    print("=" * 70)
    print(f"Tipo:        {event_type}")
    print(f"Descripción: {description}")
    print(f"Antes:       {before}")
    print(f"Después:     {after}")
    print("=" * 70)


# ============================================================
# FUNCIÓN PARA INCREMENTAR EL RELOJ
# ============================================================

def increment_clock():
    vector_clock[NODE_ID - 1] += 1


# ============================================================
# ENDPOINT: ESTADO DEL NODO
# ============================================================

@app.get("/")
def root():
    return {
        "node": NODE_ID,
        "message": "Nodo funcionando correctamente",
        "clock": vector_clock
    }


# ============================================================
# ENDPOINT: CONSULTAR ESTADO
# ============================================================

@app.get("/estado")
def get_state():
    return {
        "node": NODE_ID,
        "clock": vector_clock,
        "events": events
    }


# ============================================================
# ENDPOINT: EVENTO LOCAL
# ============================================================

@app.post("/evento")
def local_event():

    before = vector_clock.copy()

    increment_clock()

    after = vector_clock.copy()

    register_event(
        "LOCAL",
        "Evento local generado en el nodo",
        before,
        after
    )

    return {
        "node": NODE_ID,
        "event": "local",
        "before": before,
        "after": after
    }


# ============================================================
# ENDPOINT: RECIBIR MENSAJE
# ============================================================

@app.post("/recibir")
def receive_message(message: Message):

    before = vector_clock.copy()

    received_clock = message.clock.copy()

    # Máximo componente a componente
    for i in range(TOTAL_NODES):
        vector_clock[i] = max(
            vector_clock[i],
            received_clock[i]
        )

    # Incrementar posición correspondiente al nodo receptor
    increment_clock()

    after = vector_clock.copy()

    description = (
        f"Mensaje recibido desde Nodo {message.sender}. "
        f"Contenido: {message.message}. "
        f"Reloj recibido: {received_clock}"
    )

    register_event(
        "RECEPCIÓN",
        description,
        before,
        after
    )

    return {
        "node": NODE_ID,
        "event": "receive",
        "sender": message.sender,
        "received_clock": received_clock,
        "before": before,
        "after": after
    }


# ============================================================
# ENDPOINT: ENVIAR MENSAJE
# ============================================================

@app.post("/enviar/{destination}")
def send_message(destination: int, message: str = "Mensaje distribuido"):

    if destination not in NODES:
        raise HTTPException(
            status_code=400,
            detail="Nodo destino inválido"
        )

    if destination == NODE_ID:
        raise HTTPException(
            status_code=400,
            detail="Un nodo no puede enviarse mensajes a sí mismo"
        )

    before = vector_clock.copy()

    # El envío también es un evento
    increment_clock()

    after = vector_clock.copy()

    register_event(
        "ENVÍO",
        f"Envío de mensaje al Nodo {destination}: {message}",
        before,
        after
    )

    payload = {
        "sender": NODE_ID,
        "clock": after,
        "message": message
    }

    try:

        response = requests.post(
            f"{NODES[destination]}/recibir",
            json=payload,
            timeout=5
        )

        return {
            "node": NODE_ID,
            "event": "send",
            "destination": destination,
            "before": before,
            "after": after,
            "receiver_response": response.json()
        }

    except requests.exceptions.RequestException as e:

        return {
            "node": NODE_ID,
            "event": "send",
            "destination": destination,
            "before": before,
            "after": after,
            "error": str(e)
        }


# ============================================================
# ENDPOINT: CONSULTAR REGISTRO
# ============================================================

@app.get("/eventos")
def get_events():

    return {
        "node": NODE_ID,
        "events": events
    }


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT
    )