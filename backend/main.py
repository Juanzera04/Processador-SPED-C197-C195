from fastapi import FastAPI, UploadFile, File
import shutil
import os
from service import processar_sped

app = FastAPI()

UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔥 ROTA PRA ACORDAR O BACKEND
@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/processar/")
async def processar(sped: UploadFile = File(...), excel: UploadFile = File(...)):

    sped_path = f"{UPLOAD_DIR}/{sped.filename}"
    excel_path = f"{UPLOAD_DIR}/{excel.filename}"
    saida_path = f"{UPLOAD_DIR}/resultado.txt"

    with open(sped_path, "wb") as f:
        shutil.copyfileobj(sped.file, f)

    with open(excel_path, "wb") as f:
        shutil.copyfileobj(excel.file, f)

    processar_sped(sped_path, excel_path, saida_path)

    return {"mensagem": "Processado com sucesso"}