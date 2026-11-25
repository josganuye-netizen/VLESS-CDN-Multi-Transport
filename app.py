import base64, json, os, subprocess, uuid
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, unquote

CONFIG_PATH = "/app/config.json"
USERS_PATH = "/app/users.json"
ENV_DOMAIN = os.environ.get("DOMAIN", "").strip()

def load_users():
    if os.path.exists(USERS_PATH):
        with open(USERS_PATH, "r") as f:
            users = json.load(f)
        cleaned = [u for u in users if u.get("domain") != "domain-kamu.com" and u.get("id") != "b61ccee6-5850-499a-8b0a-1509d2d11202"]
        if len(cleaned) != len(users):
            save_users(cleaned)
        return cleaned
    return []

def save_users(users):
    with open(USERS_PATH, "w") as f:
        json.dump(users, f, indent=2)
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    uuid_clients = [{"id": u["id"], "email": u["name"]} for u in users]
    trojan_clients = [{"password": u["id"], "email": u["name"]} for u in users]
    for ib in data["inbounds"]:
        if ib.get("protocol") == "trojan":
            ib["settings"]["clients"] = trojan_clients
        else:
            ib["settings"]["clients"] = uuid_clients
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    subprocess.run(["pkill", "-x", "xray"])

def make_vmess(uid, dom, port, net, path, tls, ps):
    obj = {
        "v": "2",
        "ps": ps,
        "add": dom,
        "port": str(port),
        "id": uid,
        "aid": "0",
        "scy": "auto",
        "net": net,
        "type": "auto" if net == "xhttp" else "none",
        "host": dom,
        "path": path,
        "tls": "tls" if tls else "",
        "sni": dom if tls else ""
    }
    raw = json.dumps(obj, separators=(",", ":")).encode()
    return "vmess://" + base64.b64encode(raw).decode()

class Handler(BaseHTTPRequestHandler):
    def get_saved_domain(self):
        cookie_header = self.headers.get("Cookie", "")
        if cookie_header:
            c = SimpleCookie()
            c.load(cookie_header)
            if "user_domain" in c:
                val = unquote(c["user_domain"].value).strip()
                if val:
                    return val
        return ENV_DOMAIN

    def do_GET(self):
        users = load_users()
        saved_dom = self.get_saved_domain()
        rows = ""
        for u in reversed(users):
            uid = u["id"]
            name = u["name"]
            dom = u["domain"]

            # VLESS
            vl_x_443 = f"vless://{uid}@{dom}:443?encryption=none&security=tls&sni={dom}&type=xhttp&host={dom}&path=%2Fxhttp&mode=auto#{name}-VLESS-XHTTP-443"
            vl_h_443 = f"vless://{uid}@{dom}:443?encryption=none&security=tls&sni={dom}&type=httpupgrade&host={dom}&path=%2Fhttpup#{name}-VLESS-HTTPUp-443"
            vl_w_443 = f"vless://{uid}@{dom}:443?encryption=none&security=tls&sni={dom}&type=ws&host={dom}&path=%2Fvless#{name}-VLESS-WS-443"
            vl_x_80 = f"vless://{uid}@{dom}:80?encryption=none&security=none&type=xhttp&host={dom}&path=%2Fxhttp&mode=auto#{name}-VLESS-XHTTP-80"
            vl_h_80 = f"vless://{uid}@{dom}:80?encryption=none&security=none&type=httpupgrade&host={dom}&path=%2Fhttpup#{name}-VLESS-HTTPUp-80"
            vl_w_80 = f"vless://{uid}@{dom}:80?encryption=none&security=none&type=ws&host={dom}&path=%2Fvless#{name}-VLESS-WS-80"

            # VMess
            vm_x_443 = make_vmess(uid, dom, 443, "xhttp", "/vmess-xhttp", True, f"{name}-VMess-XHTTP-443")
            vm_h_443 = make_vmess(uid, dom, 443, "httpupgrade", "/vmess-httpup", True, f"{name}-VMess-HTTPUp-443")
            vm_w_443 = make_vmess(uid, dom, 443, "ws", "/vmess", True, f"{name}-VMess-WS-443")
            vm_x_80 = make_vmess(uid, dom, 80, "xhttp", "/vmess-xhttp", False, f"{name}-VMess-XHTTP-80")
            vm_h_80 = make_vmess(uid, dom, 80, "httpupgrade", "/vmess-httpup", False, f"{name}-VMess-HTTPUp-80")
            vm_w_80 = make_vmess(uid, dom, 80, "ws", "/vmess", False, f"{name}-VMess-WS-80")

            # Trojan
            tr_x_443 = f"trojan://{uid}@{dom}:443?security=tls&sni={dom}&type=xhttp&host={dom}&path=%2Ftrojan-xhttp&mode=auto#{name}-Trojan-XHTTP-443"
            tr_h_443 = f"trojan://{uid}@{dom}:443?security=tls&sni={dom}&type=httpupgrade&host={dom}&path=%2Ftrojan-httpup#{name}-Trojan-HTTPUp-443"
            tr_w_443 = f"trojan://{uid}@{dom}:443?security=tls&sni={dom}&type=ws&host={dom}&path=%2Ftrojan#{name}-Trojan-WS-443"
            tr_x_80 = f"trojan://{uid}@{dom}:80?security=none&type=xhttp&host={dom}&path=%2Ftrojan-xhttp&mode=auto#{name}-Trojan-XHTTP-80"
            tr_h_80 = f"trojan://{uid}@{dom}:80?security=none&type=httpupgrade&host={dom}&path=%2Ftrojan-httpup#{name}-Trojan-HTTPUp-80"
            tr_w_80 = f"trojan://{uid}@{dom}:80?security=none&type=ws&host={dom}&path=%2Ftrojan#{name}-Trojan-WS-80"

            rows += f"""
            <div class="card">
              <div class="top"><b>{name}</b><span class="tag">{dom}</span></div>
              <small>{uid}</small>

              <div class="proto">VLESS</div>
              <div class="lbl">Port TLS 443</div>
              <div class="btns">
                <button onclick="copy('{vl_x_443}')">XHTTP 443</button>
                <button onclick="copy('{vl_h_443}')">HTTPUp 443</button>
                <button onclick="copy('{vl_w_443}')">WS 443</button>
              </div>
              <div class="lbl">Port Non-TLS 80</div>
              <div class="btns ntls">
                <button onclick="copy('{vl_x_80}')">XHTTP 80</button>
                <button onclick="copy('{vl_h_80}')">HTTPUp 80</button>
                <button onclick="copy('{vl_w_80}')">WS 80</button>
              </div>

              <div class="proto vm">VMess</div>
              <div class="lbl">Port TLS 443</div>
              <div class="btns vm-btn">
                <button onclick="copy('{vm_x_443}')">XHTTP 443</button>
                <button onclick="copy('{vm_h_443}')">HTTPUp 443</button>
                <button onclick="copy('{vm_w_443}')">WS 443</button>
              </div>
              <div class="lbl">Port Non-TLS 80</div>
              <div class="btns vm-ntls">
                <button onclick="copy('{vm_x_80}')">XHTTP 80</button>
                <button onclick="copy('{vm_h_80}')">HTTPUp 80</button>
                <button onclick="copy('{vm_w_80}')">WS 80</button>
              </div>

              <div class="proto tr">Trojan</div>
              <div class="lbl">Port TLS 443</div>
              <div class="btns tr-btn">
                <button onclick="copy('{tr_x_443}')">XHTTP 443</button>
                <button onclick="copy('{tr_h_443}')">HTTPUp 443</button>
                <button onclick="copy('{tr_w_443}')">WS 443</button>
              </div>
              <div class="lbl">Port Non-TLS 80</div>
              <div class="btns tr-ntls">
                <button onclick="copy('{tr_x_80}')">XHTTP 80</button>
                <button onclick="copy('{tr_h_80}')">HTTPUp 80</button>
                <button onclick="copy('{tr_w_80}')">WS 80</button>
              </div>
            </div>"""

        if not rows:
            rows = '<div class="empty">Belum ada akun terdaftar. Silakan buat akun di atas.</div>'

        html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Generator Akun Multi-Protokol</title>
        <style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:16px;max-width:540px;margin:auto}}
        .box{{background:#1e293b;padding:16px;border-radius:12px;margin-bottom:16px}}
        input{{width:100%;padding:11px;border-radius:8px;border:none;margin-bottom:10px;box-sizing:border-box}}
        .add{{width:100%;padding:11px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-weight:bold;font-size:14px}}
        .card{{background:#1e293b;padding:14px;border-radius:12px;margin-bottom:12px}}
        .empty{{text-align:center;color:#94a3b8;padding:20px;font-size:13px}}
        .top{{display:flex;justify-content:space-between;align-items:center;gap:8px}}
        .tag{{background:#334155;color:#38bdf8;font-size:11px;padding:3px 8px;border-radius:6px;word-break:break-all}}
        small{{color:#94a3b8;word-break:break-all;display:block;margin:6px 0}}
        .proto{{font-size:12px;font-weight:bold;color:#60a5fa;margin-top:12px;padding-top:8px;border-top:1px solid #334155}}
        .proto.vm{{color:#c084fc}}.proto.tr{{color:#fb923c}}
        .lbl{{font-size:11px;color:#cbd5e1;margin:6px 0 4px}}
        .btns{{display:flex;gap:6px}}.btns button{{flex:1;padding:8px;border:none;border-radius:6px;background:#3b82f6;color:#fff;font-size:12px}}
        .ntls button{{background:#0ea5e9}}
        .vm-btn button{{background:#9333ea}}.vm-ntls button{{background:#a855f7}}
        .tr-btn button{{background:#ea580c}}.tr-ntls button{{background:#f97316}}</style></head>
        <body><h3>Generator Akun VLESS / VMess / Trojan</h3>
        <div class="box"><form method="POST" action="/add" onsubmit="saveDom()">
        <input type="text" name="name" maxlength="20" placeholder="Nama akun (misal: user1)" required>
        <input type="text" id="domInput" name="domain" maxlength="60" value="{saved_dom}" placeholder="Domain Zero Trust (misal: sub.domain.com)" required>
        <button class="add" type="submit">+ Buat Akun</button></form></div>
        {rows}
        <script>
        (function(){{
          var el=document.getElementById('domInput');
          if(!el.value){{
            var saved=localStorage.getItem('vless_user_domain');
            if(saved){{el.value=saved;}}
          }}
        }})();
        function saveDom(){{
          var val=document.getElementById('domInput').value.trim();
          if(val){{localStorage.setItem('vless_user_domain',val);}}
        }}
        function copy(t){{
          if(navigator.clipboard){{navigator.clipboard.writeText(t).then(()=>alert('Link berhasil disalin!')).catch(()=>fallback(t));}}
          else{{fallback(t);}}
        }}
        function fallback(t){{
          var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');document.body.removeChild(a);alert('Link berhasil disalin!');
        }}
        </script>
        </body></html>"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = parse_qs(self.rfile.read(length).decode())
        users = load_users()
        dom = ""
        if self.path == "/add":
            name = "".join(c for c in body.get("name", ["user"])[0] if c.isalnum() or c in "-_")[:20] or "user"
            raw_dom = body.get("domain", [""])[0].strip().lower()
            raw_dom = raw_dom.replace("https://", "").replace("http://", "").split("/")[0]
            dom = "".join(c for c in raw_dom if c.isalnum() or c in ".-")[:60]
            if dom:
                users.append({"id": str(uuid.uuid4()), "name": name, "domain": dom})
                save_users(users)
        self.send_response(302)
        if dom:
            self.send_header("Set-Cookie", f"user_domain={quote(dom)}; Path=/; Max-Age=31536000")
        self.send_header("Location", "/")
        self.end_headers()

HTTPServer(("0.0.0.0", 2053), Handler).serve_forever()
