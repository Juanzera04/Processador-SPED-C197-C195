const BACKEND = "https://SEU-BACKEND.onrender.com";

// mostrar desafio
function ativarSistema() {
    document.getElementById("desafio").style.display = "block";
}

// validar conta e acordar backend
async function validar() {
    const resposta = document.getElementById("resposta").value;

    if (resposta != 10) {
        alert("Resposta incorreta!");
        return;
    }

    // 🔥 chama backend (acorda ele)
    try {
        await fetch(BACKEND);
    } catch (e) {}

    document.getElementById("entrada").style.display = "none";
    document.getElementById("sistema").style.display = "flex";
}

// mostrar nome dos arquivos
document.getElementById("excel").addEventListener("change", (e) => {
    let nome = e.target.files[0]?.name;
    let box = document.getElementById("excel-info");
    box.innerText = nome;
    box.classList.add("mostrar");
});

document.getElementById("sped").addEventListener("change", (e) => {
    let nome = e.target.files[0]?.name;
    let box = document.getElementById("sped-info");
    box.innerText = nome;
    box.classList.add("mostrar");
});

// processar
async function processar() {

    const sped = document.getElementById("sped").files[0];
    const excel = document.getElementById("excel").files[0];
    const status = document.getElementById("status");

    if (!sped || !excel) {
        alert("Selecione os dois arquivos!");
        return;
    }

    let formData = new FormData();
    formData.append("sped", sped);
    formData.append("excel", excel);

    status.className = "status processo mostrar";
    status.innerHTML = '<span class="loader"></span> Processando...';

    try {
        const response = await fetch(`${BACKEND}/processar/`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        status.className = "status sucesso mostrar";
        status.innerText = data.mensagem;

    } catch (error) {
        status.className = "status erro mostrar";
        status.innerText = "Erro ao processar!";
    }
}