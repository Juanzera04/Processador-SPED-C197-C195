from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from service import processar_sped
from fastapi.responses import FileResponse

app = FastAPI()

# 🔥 CORS (OBRIGATÓRIO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois podemos restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 pasta temporária
UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ rota raiz (pro botão Entrar)
@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/processar/")
async def processar(sped: UploadFile = File(...), excel: UploadFile = File(...)):

    caminho_sped = os.path.join(UPLOAD_DIR, sped.filename)
    caminho_excel = os.path.join(UPLOAD_DIR, excel.filename)
    caminho_saida = os.path.join(UPLOAD_DIR, "resultado.txt")

    with open(caminho_sped, "wb") as f:
        shutil.copyfileobj(sped.file, f)

    with open(caminho_excel, "wb") as f:
        shutil.copyfileobj(excel.file, f)

    processar_sped(caminho_sped, caminho_excel, caminho_saida)

    # 🔥 RETORNAR ARQUIVO
    return FileResponse(
        caminho_saida,
        media_type="text/plain",
        filename="SPED_PROCESSADO.txt"
    )