FROM rust:latest AS builder
RUN apt-get update && apt-get install -y cmake pkg-config clang libclang-dev g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y curl unzip ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY --from=builder /usr/src/app/target/release/xray-pingora-l7 /app/xray-pingora-l7
RUN chmod +x /app/xray-pingora-l7

RUN curl -L -o xray.zip https://github.com/XTLS/Xray-core/releases/download/v26.11.9/Xray-linux-64.zip \
    && unzip xray.zip xray && rm xray.zip && chmod +x xray

RUN curl -L -o cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x cloudflared

COPY config.json /app/config.json

CMD sh -c "./xray run -c config.json & ./xray-pingora-l7 & exec ./cloudflared tunnel --protocol http2 run --token \$CF_TOKEN"
