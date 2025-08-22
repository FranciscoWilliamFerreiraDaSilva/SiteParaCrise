import os
import base64
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Tenta carregar a imagem como base64 (evita falha se o arquivo não existir no servidor)
encoded_image = ""
IMAGE_PATH = "UploadedImage0.jpg"
try:
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
except FileNotFoundError:
    # Sem imagem, o app continua funcionando
    encoded_image = ""

html_template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gerador de Máscara de Sala de Crise</title>
    <style>
        body {
            background-color: #e6f0ff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 800px;
            margin: 20px auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            position: relative;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        h1 {
            text-align: center;
            color: #003366;
        }
        label {
            font-weight: 600;
            display: block;
            margin-top: 10px;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 8px 10px;
            margin-top: 4px;
            border: 1px solid #c8d4e7;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        textarea {
            resize: vertical;
        }
        .form-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        button[type="submit"],
        .btn-outline {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        button[type="submit"] {
            background-color: #003366;
            color: white;
            border: none;
        }
        button[type="submit"]:hover {
            background-color: #0a4a8a;
        }
        .btn-outline {
            background: #f7f9fc;
            color: #003366;
            border: 1px solid #c8d4e7;
        }
        .btn-outline:hover {
            background: #eef3fb;
        }
        .watermark {
            position: absolute;
            bottom: 10px;
            right: 10px;
            opacity: 0.2;
        }

        /* Modal escondido por padrão */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            inset: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
        }
        .modal-content {
            background-color: #fff;
            margin: 8% auto;
            padding: 20px 24px;
            border: 1px solid #888;
            width: 90%;
            max-width: 700px;
            border-radius: 8px;
            white-space: pre-wrap; /* preserva quebras de linha */
            line-height: 1.35rem;
        }
        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 10px;
        }
        .modal-title {
            font-size: 18px;
            font-weight: 700;
            color: #003366;
        }
        .close {
            color: #777;
            font-size: 28px;
            font-weight: bold;
            border: none;
            background: none;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover,
        .close:focus {
            color: #000;
        }
        .modal-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            justify-content: flex-end;
        }
        .btn-secondary {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #c8d4e7;
            background: #f7f9fc;
            cursor: pointer;
        }
        .btn-secondary:hover {
            background: #eef3fb;
        }
        .btn-primary {
            padding: 8px 12px;
            border-radius: 6px;
            border: none;
            background: #0a4a8a;
            color: #fff;
            cursor: pointer;
        }
        .btn-primary:hover {
            background: #0d5aa6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gerador de Máscara de Sala de Crise</h1>
        <form method="post" id="formMascara">
            <label>Incidente:</label>
            <input type="text" name="incidente" value="{{ form_data.get('incidente','') }}">

            <label>Times Envolvidos:</label>
            <input type="text" name="times" value="{{ form_data.get('times','') }}">

            <label>Gestor de Crise:</label>
            <input type="text" name="gestor" value="{{ form_data.get('gestor','') }}">

            <label>Prazo estimado para resolução:</label>
            <input type="text" name="prazo" value="{{ form_data.get('prazo','') }}">

            <label>Área do acionamento:</label>
            <input type="text" name="area" value="{{ form_data.get('area','') }}">

            <label>Detalhe da Falha:</label>
            <input type="text" name="falha" value="{{ form_data.get('falha','') }}">

            <label>Impacto:</label>
            <input type="text" name="impacto" value="{{ form_data.get('impacto','') }}">

            <label>Data/Horário de início:</label>
            <input type="text" name="inicio" value="{{ form_data.get('inicio','') }}">

            <label>Data/Horário do fim:</label>
            <input type="text" name="fim" value="{{ form_data.get('fim','') }}">

            <label>Status Atual da(s) área(s) afetada(s):</label>
            <textarea name="status" rows="3">{{ form_data.get('status','') }}</textarea>

            <label>Ações realizadas:</label>
            <textarea name="acoes" rows="4">{{ form_data.get('acoes','') }}</textarea>

            <div class="form-actions">
                <button type="submit">Gerar Máscara</button>
                <button type="button" class="btn-outline" id="btnLimpar">Limpar</button>
            </div>
        </form>

        <!-- Marca d'água 500% maior (de 120px para 600px) -->
        {% if image %}
        <img src="data:image/jpeg;base64,{{ image }}" class="watermark" width="600" alt="Marca d'água">
        {% endif %}
    </div>

    {% if resultado %}
    <div id="resultadoModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="resultadoTitulo">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div id="resultadoTitulo" class="modal-title">Resultado da Máscara</div>
                <button class="close" aria-label="Fechar" onclick="fecharModal()">&times;</button>
            </div>
            <div id="resultadoTexto">{{ resultado }}</div>

            <div class="modal-actions">
                <button class="btn-secondary" onclick="copiar()">Copiar</button>
                <button class="btn-primary" onclick="fecharModal()">Fechar</button>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        function abrirModal() {
            const m = document.getElementById('resultadoModal');
            if (m) m.style.display = 'block';
        }
        function fecharModal() {
            const m = document.getElementById('resultadoModal');
            if (m) m.style.display = 'none';
        }
        // Fecha ao clicar fora do conteúdo
        document.addEventListener('click', function(e) {
            const modal = document.getElementById('resultadoModal');
            if (!modal) return;
            if (e.target === modal) fecharModal();
        });
        function copiar() {
            const texto = document.getElementById('resultadoTexto')?.innerText || '';
            navigator.clipboard.writeText(texto).then(() => {
                alert('Conteúdo copiado!');
            }).catch(() => {
                alert('Não foi possível copiar automaticamente.');
            });
        }

        // Abre o modal automaticamente após POST com resultado
        {% if resultado %}
        window.addEventListener('DOMContentLoaded', abrirModal);
        {% endif %}

        // Botão LIMPAR: zera todos os campos do formulário
        document.getElementById('btnLimpar')?.addEventListener('click', function () {
            const form = document.getElementById('formMascara');
            if (!form) return;

            form.querySelectorAll('input, textarea').forEach(el => {
                if (el.type === 'button' || el.type === 'submit' || el.type === 'reset') return;
                if (el.type === 'checkbox' || el.type === 'radio') {
                    el.checked = false;
                } else {
                    el.value = '';
                }
            });

            // Opcional: fecha o modal, se estiver aberto
            fecharModal();
        });
    </script>
</body>
</html>
"""

def montar_resultado(form_data: dict) -> str:
    """
    Monta o texto do resultado exibindo apenas campos preenchidos (não vazios).
    Campos são 'limpos' com strip(). Blocos multilinha (status/acoes) aparecem
    somente se tiver conteúdo.
    """
    campos_simples = [
        ("Incidente", "incidente"),
        ("Times Envolvidos", "times"),
        ("Gestor de Crise", "gestor"),
        ("Prazo estimado para resolução", "prazo"),
        ("Área do acionamento", "area"),
        ("Detalhe da Falha", "falha"),
        ("Impacto", "impacto"),
        ("Data/Horário de início", "inicio"),
        ("Data/Horário do fim", "fim"),
    ]

    partes = ["🚨 *SALA DE CRISE*"]

    # Adiciona apenas os campos que têm valor
    for label, key in campos_simples:
        valor = (form_data.get(key) or "").strip()
        if valor:
            partes.append(f"*{label}:* {valor}")

    # Blocos multilinha
    status = (form_data.get("status") or "").strip()
    if status:
        partes.append("*Status Atual da (s) área (s) afetada (s):*\n")
        partes.append(status)

    acoes = (form_data.get("acoes") or "").strip()
    if acoes:
        partes.append("*Ações realizadas:*\n")
        partes.append(acoes)

    return "\n".join(partes)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""
    form_data = {}
    if request.method == "POST":
        form_data = request.form.to_dict()
        resultado = montar_resultado(form_data)

    return render_template_string(
        html_template,
        resultado=resultado,
        image=encoded_image,
        form_data=form_data
    )

# ---- Execução local / Render ----
# No Render, a plataforma define a variável de ambiente PORT (geralmente 10000).
# Precisamos ouvir em 0.0.0.0 e na porta PORT para evitar 502 Bad Gateway.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
