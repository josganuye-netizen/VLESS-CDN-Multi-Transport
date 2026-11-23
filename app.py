import json, os, subprocess, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

CONFIG_PATH = "/app/config.json"
DOMAIN = os.environ.get("DOMAIN", "wokcandy.joss.cc.cd")

def load_clients():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    return data["inbounds"][0]["settings"]["clients"]

def save_and_reload(clients):
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    for ib in data["inbounds"]:
        ib["settings"]["clients"] = clients
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    subprocess.run(["pkill", "-x", "xray"])

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clients = load_clients()
        rows = ""
        for c in clients:
            uid = c["id"]
            name = c.get("email", "user")
            l_xhttp_tls = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=xhttp&host={DOMAIN}&path=%2Fxhttp&mode=auto#{name}-XHTTP-443"
            l_httpup_tls = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=httpupgrade&host={DOMAIN}&path=%2Fhttpup#{name}-HTTPUp-443"
            l_ws_tls = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=ws&host={DOMAIN}&path=%2Fvless#{name}-WS-443"
            l_xhttp_80 = f"vless://{uid}@{DOMAIN}:80?encryption=none&security=none&type=xhttp&host={DOMAIN}&path=%2Fxhttp&mode=auto#{name}-XHTTP-80"
            l_httpup_80 = f"vless://{uid}@{DOMAIN}:80?encryption=none&security=none&type=httpupgrade&host={DOMAIN}&path=%2Fhttpup#{name}-HTTPUp-80"
            l_ws_80 = f"vless://{uid}@{DOMAIN}:80?encryption=none&security=none&type=ws&host={DOMAIN}&path=%2Fvless#{name}-WS-80"

            rows += f"""
            <div class="card">
              <div class="top"><b>{name}</b><form method="POST" action="/delete" style="margin:0">
              <input type="hidden" name="id" value="{uid}"><button class="del">Hapus</button></form></div>
              <small>{uid}</small>
              <div class="lbl">TLS (Port 443)</div>
              <div class="btns">
                <button onclick="copy('{l_xhttp_tls}')">XHTTP 443</button>
                <button onclick="copy('{l_httpup_tls}')">HTTPUp 443</button>
                <button onclick="copy('{l_ws_tls}')">WS 443</button>
              </div>
              <div class="lbl">Non-TLS (Port 80)</div>
              <div class="btns ntls">
                <button onclick="copy('{l_xhttp_80}')">XHTTP 80</button>
                <button onclick="copy('{l_httpup_80}')">HTTPUp 80</button>
                <button onclick="copy('{l_ws_80}')">WS 80</button>
              </div>
            </div>"""

        html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:16px;max-width:540px;margin:auto}}
        .box{{background:#1e293b;padding:16px;border-radius:12px;margin-bottom:16px}}
        input{{width:68%;padding:10px;border-radius:8px;border:none}}
        .add{{width:29%;padding:10px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-weight:bold}}
        .card{{background:#1e293b;padding:14px;border-radius:12px;margin-bottom:10px}}
        .top{{display:flex;justify-content:space-between;align-items:center}}
        small{{color:#94a3b8;word-break:break-all;display:block;margin:6px 0}}
        .lbl{{font-size:11px;color:#cbd5e1;margin:8px 0 4px}}
        .btns{{display:flex;gap:6px}}.btns button{{flex:1;padding:8px;border:none;border-radius:6px;background:#3b82f6;color:#fff;font-size:12px}}
        .ntls button{{background:#0ea5e9}}
        .del{{background:#ef4444;color:#fff;border:none;padding:5px 10px;border-radius:6px;font-size:12px}}</style></head>
        <body><h3>Xray Simple UI ({DOMAIN})</h3>
        <div class="box"><form method="POST" action="/add">
        <input type="text" name="name" placeholder="Nama akun (misal: hp1)" required>
        <button class="add" type="submit">+ Buat</button></form></div>
        {rows}
        <script>function copy(t){{navigator.clipboard.writeText(t);alert('Link berhasil disalin!');}}</script>
        </body></html>"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = parse_qs(self.rfile.read(length).decode())
        clients = load_clients()
        if self.path == "/add":
            name = body.get("name", ["user"])[0].strip() or "user"
            clients.append({"id": str(uuid.uuid4()), "email": name})
            save_and_reload(clients)
        elif self.path == "/delete":
            uid = body.get("id", [""])[0]
            clients = [c for c in clients if c["id"] != uid]
            save_and_reload(clients)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

HTTPServer(("0.0.0.0", 2053), Handler).serve_forever()
