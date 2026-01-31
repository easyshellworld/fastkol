import socket

def find_free_port(start_port=7030, max_port=7100):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return None

if __name__ == "__main__":
    port = find_free_port()
    if port:
        print(port)
    else:
        print("No free port found")
