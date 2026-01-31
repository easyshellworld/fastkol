import http.server
import socketserver

PORT = 8095
Handler = http.server.SimpleHTTPRequestHandler

try:
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"serving at port {PORT}")
        # Just serve one request then exit, or just listen and exit
        # for checking, just binding is enough.
        print("Success binding!")
except Exception as e:
    print(f"Failed to bind: {e}")
