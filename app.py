import os
import base64
from datetime import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)


# --- Imagem de marca d’água opcional ---
encoded_image = ""
IMAGE_PATH = "UploadedImage0.jpg"
try:
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
except FileNotFoundError:
    encoded_image = ""  # Sem imagem, o app continua normalmente

# --- Catálogo de clientes e cores de destaque ---
CLIENTES = {
    "zaffari": {"nome": "ZAFFARI", "accent": "#22c55e", "emoji": "🟢"},
    "klabin":  {"nome": "KLABIN",  "accent": "#06b6d4", "emoji": "🔷"},
    "axa":     {"nome": "AXA",     "accent": "#6366f1", "emoji": "🟣"},
}
DEFAULT_ACCENT = "#22c55e"  # cor padrão quando não houver cliente

# --- Templates ---

home_template = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>CRISES - TM (TICKET MANAGEMENT)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root { --bg:#0f172a; --fg:#e2e8f0; --muted:#94a3b8; --card:#111827; --accent:#38bdf8; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--bg); color:var(--fg); }
    a { color:inherit; text-decoration:none; }
    .nav { display:flex; gap:1rem; align-items:center; padding:1rem 1.25rem; border-bottom:1px solid #1f2937; background:#0b1227cc; position:sticky; top:0; backdrop-filter: blur(6px); }
    .brand { font-weight:700; letter-spacing:.2px; }
    .spacer { flex:1; }
    .btn { display:inline-block; padding:.7rem 1rem; border-radius:.6rem; background:var(--accent); color:#001018; font-weight:600; border:none; cursor:pointer; }
    .btn.secondary { background:#1f2937; color:var(--fg); }
    .container { max-width:1050px; margin:0 auto; padding:2rem 1.25rem; }
    .hero { display:grid; grid-template-columns:1.1fr .9fr; gap:2rem; align-items:center; padding:2rem 0; }
    .card { background:linear-gradient(180deg, #0b1227, #0b1227), var(--card); border:1px solid #1f2937; border-radius:1rem; padding:1.25rem; }
    .list li{ margin:.5rem 0; color:var(--muted); }
    .footer { color:var(--muted); font-size:.9rem; padding:2rem 0; }
    .watermark {
      width:100%; aspect-ratio:4/3; border-radius:.8rem; border:1px dashed #334155;
      display:flex; align-items:center; justify-content:center; overflow:hidden; background:#0b1227;
    }
    .watermark img{ max-width:100%; max-height:100%; opacity:.2; }
    @media (max-width: 900px) {
      .hero { grid-template-columns:1fr; }
    }
  </style>
</head>
<body>
  <nav class="nav">
    <div class="brand">🛠️ CRISES TM - TICKET MANAGEMENT</div>
    <div class="spacer"></div>
    <a class="btn secondary" href="{{ url_for('home') }}">INÍCIO</a>
    <a class="btn" href="{{ url_for('gerador') }}">AXA</a>
    <a class="btn" href="{{ url_for('gerador') }}">KLABIN</a>
    <a class="btn" href="{{ url_for('gerador') }}">ZAFFARI</a>
  </nav>

  <main class="container">
    <section class="hero">
      <div class="card">
        <h1 style="margin:.25rem 0 1rem;">CRISES - TM (TICKET MANAGEMENT)</h1>
        <p style="color:var(--muted); line-height:1.6;">
          Centralize as informações essenciais de um incidente em um texto padronizado, pronto para
          ser compartilhado em canais internos (ex.: War Room, chats, e-mail).
        </p>
        <ul class="list">
          <li>Preencha os campos chave do incidente.</li>
          <li>Inclua status e ações em formato multilinha.</li>
          <li>Gere o texto e copie com um clique.</li>
        </ul>
        <div style="display:flex; gap:.75rem; margin-top:1.25rem; flex-wrap:wrap;">
          <a class="btn" href="{{ url_for('gerador') }}?cliente=zaffari">ZAFFARI</a>
          <a class="btn" href="{{ url_for('gerador') }}?cliente=klabin">KLABIN</a>
          <a class="btn" href="{{ url_for('gerador') }}?cliente=axa">AXA</a>
        </div>
      </div>
    </section>

    <section id="como-usar" class="card">
      <h2>Como usar</h2>
      <ol style="line-height:1.9; color:var(--muted);">
        <li>Clique em <strong>ZAFFARI</strong>, <strong>KLABIN</strong> ou <strong>AXA</strong> para abrir o gerador com o cliente selecionado.</li>
        <li>Preencha os campos do incidente.</li>
        <li>Clique em <strong>Gerar Máscara</strong> e depois em <strong>Copiar</strong>.</li>
      </ol>
      <p style="color:var(--muted);">Apenas os campos preenchidos entram no resultado.</p>
    </section>

    <div class="footer">© {{ year }} • Sala de Crise • Home</div>
  </main>
</body>
</html>
"""

gerador_template = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Gerador • Máscara de Sala de Crise</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root { --bg:#0f172a; --fg:#e2e8f0; --muted:#94a3b8; --card:#111827; --accent: {{ accent }}; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--bg); color:var(--fg); }
    a { color:inherit; text-decoration:none; }
    .nav { display:flex; gap:1rem; align-items:center; padding:1rem 1.25rem; border-bottom:1px solid #1f2937; background:#0b1227cc; position:sticky; top:0; backdrop-filter: blur(6px); }
    .brand { font-weight:700; letter-spacing:.2px; }
    .spacer { flex:1; }
    .btn { display:inline-block; padding:.7rem 1rem; border-radius:.6rem; background:var(--accent); color:#00140b; font-weight:600; border:none; cursor:pointer; }
    .btn.secondary { background:#1f2937; color:var(--fg); }
    .btn.ghost { background:transparent; border:1px solid #334155; color:var(--fg); }
    .container { max-width:1100px; margin:0 auto; padding:2rem 1.25rem; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
    .card { background:linear-gradient(180deg, #0b1227, #0b1227), var(--card); border:1px solid #1f2937; border-radius:1rem; padding:1.25rem; }
    .badge {
      display:inline-flex; align-items:center; gap:.5rem;
      padding:.45rem .7rem; border-radius:999px; background:rgba(255,255,255,.06);
      border:1px solid #334155; font-weight:600;
    }
    label { display:block; margin:.35rem 0 .2rem; color:#cbd5e1; font-weight:600; }
    input, textarea { width:100%; padding:.75rem .8rem; border-radius:.6rem; border:1px solid #334155; background:#0b1227; color:var(--fg); }
    textarea { min-height:110px; resize:vertical; }
    .row { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
    .actions { display:flex; gap:.75rem; margin-top:1rem; }
    .switch { display:flex; gap:.5rem; flex-wrap:wrap; }
    .switch a { background:#0b1227; border:1px solid #334155; color:var(--fg); padding:.45rem .7rem; border-radius:.6rem; }
    .result { white-space:pre-wrap; background:#0b1227; border:1px solid #334155; border-radius:.75rem; padding:1rem; font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; color:#e5e7eb; }
    @media (max-width: 900px) {
      .grid { grid-template-columns:1fr; }
      .row { grid-template-columns:1fr; }
    }
  </style>
</head>
<body>
  <nav class="nav">
    <div class="brand">🛠️ Gerador de Máscara</div>
    <div class="spacer"></div>
    <a class="btn secondary" href="{{ url_for('home') }}">Home</a>
    <a class="btn" href="{{ url_for('gerador', cliente=cliente or None) }}">Gerador</a>
  </nav>

  <main class="container">
    <div class="card" style="margin-bottom:1rem;">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
        <div class="badge">
          {% if cliente %}
            <span>{{ emoji }}</span>
            <span>Cliente:</span>
            <strong style="color:var(--accent)">{{ cliente_nome }}</strong>
          {% else %}
            <span>Cliente não selecionado</span>
          {% endif %}
        </div>
        <div class="switch">
          <span style="color:#94a3b8;align-self:center;">Trocar cliente:</span>
          <a href="{{ url_for('gerador') }}?cliente=zaffari">ZAFFARI</a>
          <a href="{{ url_for('gerador') }}?cliente=klabin">KLABIN</a>
          <a href="{{ url_for('gerador') }}?cliente=axa">AXA</a>
        </div>
      </div>
    </div>

    <div class="grid">
      <section class="card">
        <h1 style="margin:.25rem 0 1rem;">Gerador de Máscara de Sala de Crise</h1>
        <form method="POST" action="{{ url_for('gerador') }}">
          <!-- Manter o cliente selecionado no POST -->
          <input type="hidden" name="cliente" value="{{ cliente or '' }}">

          <label for="incidente">Incidente</label>
          <input id="incidente" name="incidente" value="{{ form_data.get('incidente','') }}" placeholder="Ex.: Intermitência API Pagamentos">

          <label for="times">Times Envolvidos</label>
          <input id="times" name="times" value="{{ form_data.get('times','') }}" placeholder="Ex.: SRE, Pagamentos, Rede, Parceiros">

          <label for="gestor">Gestor de Crise</label>
          <input id="gestor" name="gestor" value="{{ form_data.get('gestor','') }}" placeholder="Ex.: Maria Silva">

          <label for="prazo">Prazo estimado para resolução</label>
          <input id="prazo" name="prazo" value="{{ form_data.get('prazo','') }}" placeholder="Ex.: 45 minutos">

          <label for="area">Área do acionamento</label>
          <input id="area" name="area" value="{{ form_data.get('area','') }}" placeholder="Ex.: Operações Digitais">

          <label for="falha">Detalhe da Falha</label>
          <textarea id="falha" name="falha" placeholder="Descreva o que foi identificado...">{{ form_data.get('falha','') }}</textarea>

          <div class="row">
            <div>
              <label for="inicio">Data/Horário de início</label>
              <input id="inicio" name="inicio" value="{{ form_data.get('inicio','') }}" placeholder="Ex.: 25/08/2025 14:20">
            </div>
            <div>
              <label for="fim">Data/Horário do fim</label>
              <input id="fim" name="fim" value="{{ form_data.get('fim','') }}" placeholder="Ex.: 25/08/2025 15:05">
            </div>
          </div>

          <label for="impacto">Impacto</label>
          <textarea id="impacto" name="impacto" placeholder="Ex.: 12% das transações rejeitadas...">{{ form_data.get('impacto','') }}</textarea>

          <label for="status">Status Atual da(s) área(s) afetada(s)</label>
          <textarea id="status" name="status" placeholder="Atualizações contínuas...">{{ form_data.get('status','') }}</textarea>

          <label for="acoes">Ações realizadas</label>
          <textarea id="acoes" name="acoes" placeholder="Lista de ações executadas...">{{ form_data.get('acoes','') }}</textarea>

          <div class="actions">
            <button class="btn" type="submit">Gerar Máscara</button>
            <a class="btn ghost" href="{{ url_for('gerador', cliente=cliente or None) }}">Limpar</a>
          </div>
        </form>
      </section>

      <section class="card">
        <h2 style="margin:.25rem 0 1rem;">Resultado</h2>
        {% if resultado %}
          <div id="resultado" class="result">{{ resultado }}</div>
          <div class="actions">
            <button class="btn" type="button" onclick="copiar()">Copiar</button>
          </div>
        {% else %}
          <p style="color:var(--muted);">Preencha o formulário e clique em <strong>Gerar Máscara</strong> para ver o resultado aqui.</p>
        {% endif %}
        {% if image %}
          <p style="color:var(--muted); margin-top:.75rem;">Marca d’água disponível ({{ image_path }})</p>
        {% endif %}
      </section>
    </div>
  </main>

  <script>
    function copiar() {
      const el = document.getElementById('resultado');
      if (!el) return;
      const range = document.createRange();
      range.selectNodeContents(el);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      try { document.execCommand('copy'); } catch (e) {}
      sel.removeAllRanges();
      const original = document.title;
      document.title = "✔ Copiado!";
      setTimeout(() => document.title = original, 1200);
    }
  </script>
</body>
</html>
"""

# --- Lógica de composição do texto ---

def montar_resultado(form_data: dict, cliente: str = "") -> str:
    """
    Monta o texto do resultado exibindo apenas campos preenchidos (não vazios).
    Blocos multilinha (status/acoes) aparecem somente se tiver conteúdo.
    Inclui o cliente (se informado).
    """
    campos_simples = [
        ("⚠️Incidente", "incidente"),
        ("🔴Times Envolvidos", "times"),
        ("🟢Gestor de Crise", "gestor"),
        ("🕐Prazo estimado para resolução", "prazo"),
        ("🔉Área do acionamento", "area"),
        ("📍Detalhe da Falha", "falha"),
        ("‼️Impacto", "impacto"),
        ("📅Data/Horário de início", "inicio"),
        ("📅Data/Horário do fim", "fim"),
    ]

    partes = ["🚨 *SALA DE CRISE*"]
    if cliente:
        partes.append(f"*Cliente:* {cliente.upper()}")

    for label, key in campos_simples:
        valor = (form_data.get(key) or "").strip()
        if valor:
            partes.append(f"*{label}:* {valor}")

    status = (form_data.get("status") or "").strip()
    if status:
        partes.append("*Status Atual da(s) área(s) afetada(s):*")
        partes.append(status)

    acoes = (form_data.get("acoes") or "").strip()
    if acoes:
        partes.append("*Ações realizadas:")
        partes.append(acoes)

    return "\n".join(partes)

# --- Helpers ---

def resolver_cliente():
    """
    Retorna (slug, meta) do cliente. slug pode ser '' se não houver.
    meta contém nome, accent e emoji.
    """
    slug = (request.args.get("cliente") or request.form.get("cliente") or "").lower().strip()
    meta = CLIENTES.get(slug)
    return (slug if meta else ""), (meta or {"nome": "", "accent": DEFAULT_ACCENT, "emoji": ""})

# --- Rotas ---

@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        home_template,
        image=encoded_image,
        image_path=IMAGE_PATH,
        year=datetime.now().year
    )

@app.route("/gerador", methods=["GET", "POST"])
def gerador():
    cliente_slug, meta = resolver_cliente()
    resultado = ""
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()
        resultado = montar_resultado(form_data, cliente_slug)

    return render_template_string(
        gerador_template,
        resultado=resultado,
        image=encoded_image,
        image_path=IMAGE_PATH,
        form_data=form_data,
        cliente=cliente_slug,
        cliente_nome=meta["nome"],
        accent=meta["accent"],
        emoji=meta["emoji"]
    )

# Execução local / Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)