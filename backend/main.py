from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from service import processar_sped

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


# 🚀 processamento
@app.post("/processar/")
async def processar(sped: UploadFile = File(...), excel: UploadFile = File(...)):

    caminho_sped = os.path.join(UPLOAD_DIR, sped.filename)
    caminho_excel = os.path.join(UPLOAD_DIR, excel.filename)
    caminho_saida = os.path.join(UPLOAD_DIR, "resultado.txt")

    # salvar arquivos enviados
    with open(caminho_sped, "wb") as f:
        shutil.copyfileobj(sped.file, f)

    with open(caminho_excel, "wb") as f:
        shutil.copyfileobj(excel.file, f)

    # processar
    processar_sped(caminho_sped, caminho_excel, caminho_saida)

    return {"mensagem": "Processado com sucesso!"}