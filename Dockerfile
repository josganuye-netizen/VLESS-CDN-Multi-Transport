FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl unzip python3 procps \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip \
    && unzip /tmp/xray.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/xray \
    && rm -f /tmp/xray.zip

RUN curl -L -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x /usr/local/bin/cloudflared

WORKDIR /app
COPY config.json /app/config.json
COPY app.py /app/app.py

CMD ["sh", "-c", "xray run -c /app/config.json & python3 /app/app.py & if [ -n \"$CF_TOKEN\" ]; then cloudflared tunnel --no-autoupdate run --token \"$CF_TOKEN\"; else tail -f /dev/null; fi"]
