"""
Module:

    Cross-Origin Isolated Local Development Server

Description:

    A lightweight, zero-dependency development server built on top of 
    Python's http.server module. It injects mandatory Cross-Origin Opener 
    Policy (COOP) and Cross-Origin Embedder Policy (COEP) headers into all 
    responses, enabling the use of modern JavaScript APIs like `SharedArrayBuffer` 
    and advanced WebAssembly tools within remote environments (e.g., GitHub Codespaces).

Features:

    - Automatically enables SharedArrayBuffer support via strict header injection.
    - Suppresses internal browser noise and DevTools background logs.
    - Prevents port lockout on sudden restarts (SO_REUSEADDR integration).
    - Robust error trapping for busy Linux sockets.

Usage Examples:

    1. Start the server on default host (127.0.0.1) and port (8000):
       $ python server.py

    2. Start the server on a custom port configuration:
       $ python server.py 8080

    3. Terminate the active instance smoothly:
       Press Ctrl + C in the running terminal panel.
"""

import http.server
import sys

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Inject the mandatory isolation headers for SharedArrayBuffer
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

    def log_message(self, format, *args):
        # Ignore the Chrome DevTools probe to keep the console clean
        if len(args) > 0 and ".well-known" in str(args):
            return
        # Print all other normal file requests
        super().log_message(format, *args)

# Bypasses the Linux TIME_WAIT socket cooling-off state
class InstantHTTPServer(http.server.HTTPServer):
    allow_reuse_address = True

def start_server(host, port, handler_class):
    try:
        server_address = (host, port)
        with InstantHTTPServer(server_address, handler_class) as httpd:
            actual_port = httpd.server_port
            print(f"🚀 Running custom quiet server on http://{host}:{actual_port}")
            httpd.serve_forever()
    except OSError as e:
        # Linux Error 98 = EADDRINUSE (Address already in use)
        if e.errno == 98:
            print(f"❌ Error: Port {port} is busy. Clear the process or choose another port.")
            sys.exit(1) # Exit with failure status code
        else:
            raise e
    except KeyboardInterrupt:
        print("\n🛑 Server stopped cleanly.")
        sys.exit(0)

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8000
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid port number '{sys.argv[1]}'. Falling back to default.")
            port = 8000

    start_server(host, port, QuietHandler)
