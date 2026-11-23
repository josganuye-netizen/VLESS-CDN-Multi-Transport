use async_trait::async_trait;
use pingora::prelude::*;

pub struct L7Proxy;

#[async_trait]
impl ProxyHttp for L7Proxy {
    type CTX = ();
    fn new_ctx(&self) -> Self::CTX {}

    async fn upstream_peer(
        &self,
        _session: &mut Session,
        _ctx: &mut Self::CTX,
    ) -> Result<Box<HttpPeer>> {
        let peer = Box::new(HttpPeer::new(("127.0.0.1", 10000), false, String::new()));
        Ok(peer)
    }

    async fn upstream_request_filter(
        &self,
        _session: &mut Session,
        upstream_request: &mut RequestHeader,
        _ctx: &mut Self::CTX,
    ) -> Result<()> {
        upstream_request.insert_header("Host", "127.0.0.1:10000")?;
        Ok(())
    }
}

fn main() {
    let mut server = Server::new(None).unwrap();
    server.bootstrap();

    let mut proxy_service = http_proxy_service(&server.configuration, L7Proxy);
    proxy_service.add_tcp("127.0.0.1:8080");

    server.add_service(proxy_service);
    println!("Pingora L7 HTTP/WS Proxy aktif di 127.0.0.1:8080 -> Xray 127.0.0.1:10000");
    server.run_forever();
}
