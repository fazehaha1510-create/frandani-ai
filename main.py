from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import base64
import httpx
from swap import run_face_swap
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Frandani AI Backend", version="1.0.0")

# Permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Avatares disponibles (más adelante los subirás a tu propio storage)
AVATARES = {
    "profesional": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
    "moda": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
}


@app.get("/")
def root():
    return {"status": "ok", "mensaje": "Frandani AI backend funcionando"}


@app.get("/avatares")
def listar_avatares():
    """Devuelve la lista de avatares disponibles"""
    return {"avatares": list(AVATARES.keys())}


@app.post("/swap")
async def hacer_swap(
    foto_usuario: UploadFile = File(...),
    avatar_id: str = "profesional"
):
    """
    Recibe la foto del usuario y el ID del avatar,
    devuelve la imagen con el face swap aplicado.
    """
    # Validar que sea una imagen
    if not foto_usuario.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Validar que el avatar existe
    if avatar_id not in AVATARES:
        raise HTTPException(status_code=404, detail=f"Avatar '{avatar_id}' no encontrado")

    # Leer la imagen del usuario
    contenido = await foto_usuario.read()

    # Convertir a base64 para enviar a Replicate
    imagen_base64 = base64.b64encode(contenido).decode("utf-8")
    extension = foto_usuario.content_type.split("/")[1]
    source_url = f"data:image/{extension};base64,{imagen_base64}"

    target_url = AVATARES[avatar_id]

    try:
        resultado_url = await run_face_swap(source_url, target_url)
        return JSONResponse({
            "success": True,
            "resultado_url": resultado_url,
            "avatar_usado": avatar_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el swap: {str(e)}")


@app.post("/swap/tiempo-real")
async def swap_tiempo_real(
    frame: UploadFile = File(...),
    avatar_id: str = "profesional"
):
    """
    Endpoint optimizado para frames de video en tiempo real.
    Recibe un frame de la cámara y devuelve el frame con el swap aplicado.
    """
    contenido = await frame.read()
    imagen_base64 = base64.b64encode(contenido).decode("utf-8")
    source_url = f"data:image/jpeg;base64,{imagen_base64}"
    target_url = AVATARES.get(avatar_id, list(AVATARES.values())[0])

    try:
        resultado_url = await run_face_swap(source_url, target_url)
        return JSONResponse({
            "success": True,
            "frame_url": resultado_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from payments import crear_checkout_session, verificar_pago

@app.get("/planes")
def listar_planes():
    from payments import PLANES
    return {"planes": PLANES}

@app.post("/crear-pago")
async def crear_pago(plan_id: str, email: str):
    try:
        url = crear_checkout_session(plan_id, email)
        return {"success": True, "checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/verificar-pago")
async def verificar(session_id: str):
    try:
        resultado = verificar_pago(session_id)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
