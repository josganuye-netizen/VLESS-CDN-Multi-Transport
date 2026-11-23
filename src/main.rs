use async_trait::async_trait;
use pingora::prelude::*;
use pingora::proxy::{http_proxy_service, ProxyHttp, Session};
use pingora::upstreams::peer::HttpPeer;
use std::process::Command;

pub struct XrayL7Proxy {
    pub xray_port: u16,
}

#[async_trait]
impl ProxyHttp for XrayL7Proxy {
    type CTX = ();
    fn new_ctx(&self) -> Self::CTX {}

    async fn upstream_peer(
        &self,
        _session: &mut Session,
        _ctx: &mut Self::CTX,
    ) -> Result<Box<HttpPeer>> {
        let peer = Box::new(HttpPeer::new(
            ("127.0.0.1", self.xray_port),
            false,
            String::new(),
        ));
        Ok(peer)
    }

    async fn upstream_request_filter(
        &self,
        _session: &mut Session,
        upstream_request: &mut RequestHeader,
        _ctx: &mut Self::CTX,
    ) -> Result<()> {
        upstream_request.insert_header("Host", "127.0.0.1")?;
        Ok(())
    }
}

fn main() {
    Command::new("xray")
        .args(["run", "-c", "config.json"])
        .spawn()
        .expect("Gagal menjalankan Xray");

    let mut server = Server::new(None).unwrap();
    server.bootstrap();

    let mut proxy = http_proxy_service(
        &server.configuration,
        XrayL7Proxy { xray_port: 10000 },
    );
    proxy.add_tcp("0.0.0.0:8080");

    println!("Pingora L7 HTTP/WS Proxy aktif di 0.0.0.0:8080 -> Xray 127.0.0.1:10000");
    server.add_service(proxy);
    server.run_forever();
}
