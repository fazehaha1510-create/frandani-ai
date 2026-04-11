from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Frandani AI Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "mensaje": "Frandani AI backend funcionando", "version": "2.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# ── PLANES ──────────────────────────────────────────
@app.post("/crear-pago")
async def crear_pago(plan_id: str = Query(...), email: str = Query(...)):
    """Crea sesión de pago en Stripe para suscripción mensual"""
    try:
        from payments import crear_checkout_session
        url = crear_checkout_session(plan_id, email)
        if url == "gratis":
            return JSONResponse({"success": True, "checkout_url": "gratis", "plan": plan_id})
        return JSONResponse({"success": True, "checkout_url": url})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Stripe: {str(e)}")

@app.post("/comprar-creditos")
async def comprar_creditos(cantidad: int = Query(...), email: str = Query(...)):
    """Crea sesión de pago para compra de créditos extra"""
    try:
        from payments import crear_checkout_creditos
        url = crear_checkout_creditos(cantidad, email)
        return JSONResponse({"success": True, "checkout_url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/verificar-pago")
async def verificar_pago(session_id: str = Query(...)):
    try:
        from payments import verificar_pago
        resultado = verificar_pago(session_id)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ── FACE SWAP ────────────────────────────────────────
AVATARES = {
    "profesional": "https://replicate.delivery/pbxt/placeholder.jpg",
    "moda": "https://replicate.delivery/pbxt/placeholder.jpg",
    "casual": "https://replicate.delivery/pbxt/placeholder.jpg",
    "artistico": "https://replicate.delivery/pbxt/placeholder.jpg",
}

@app.post("/swap")
async def hacer_swap(
    foto_usuario: UploadFile = File(...),
    avatar_id: str = "profesional"
):
    if not foto_usuario.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    contenido = await foto_usuario.read()
    imagen_base64 = base64.b64encode(contenido).decode("utf-8")
    extension = foto_usuario.content_type.split("/")[1]
    source_url = f"data:image/{extension};base64,{imagen_base64}"
    target_url = AVATARES.get(avatar_id, list(AVATARES.values())[0])
    try:
        import replicate
        output = replicate.run(
            "lucataco/faceswap:9a4298548422074c3f57258c5d544497a19901a0bac3a977e2ded5b4f25e7b2",
            input={"target_image": target_url, "source_image": source_url}
        )
        return JSONResponse({"success": True, "resultado_url": str(output), "avatar_usado": avatar_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el swap: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
