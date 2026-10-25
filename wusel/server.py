"""Production HTTP listener shared by the app and network integration checks."""
import logging
from waitress import create_server


def create_http_server(application, port=8099):
    # A wildcard creates separate IPv4 and IPv6 sockets where supported.
    # Host networking in the HA app manifest exposes these on the Pi itself.
    return create_server(application, listen=f'*:{port}', ipv4=True, ipv6=True,
                         threads=4, max_request_body_size=16384)


def serve_production(application):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    server = create_http_server(application)
    server.print_listen('Wusel listening on http://{}:{}')
    print('Wusel ready: HTTP port 8099. Health endpoint: /health', flush=True)
    try:
        server.run()
    finally:
        server.close()
