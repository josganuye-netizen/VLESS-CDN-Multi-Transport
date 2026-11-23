FROM ghcr.io/mhsanaei/3x-ui:latest

RUN apk add --no-cache curl ca-certificates

# Install cloudflared versi terbaru
RUN curl -L -o /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x /usr/local/bin/cloudflared

# Jalankan 3x-ui (port default 2053) bersamaan dengan cloudflared
ENTRYPOINT ["sh", "-c", "/app/x-ui & if [ -n \"$CF_TOKEN\" ]; then cloudflared tunnel --no-autoupdate run --token \"$CF_TOKEN\"; else tail -f /dev/null; fi"]
