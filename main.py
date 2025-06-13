import http.server
import urllib.parse
import urllib.request
import ssl

PASTEBIN_RAW_URL = "https://pastebin.com/raw/"
PASTEBIN_POST_URL = "https://pastebin.com/api/api_post.php"

ssl_context = ssl._create_unverified_context()

class PastebinProxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/raw/"):
            code = self.path[len("/raw/"):]
            url = PASTEBIN_RAW_URL + urllib.parse.quote(code)
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; PastebinProxy/1.0)"
                })
                with urllib.request.urlopen(req, context=ssl_context) as resp:
                    content = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(502, f"Error fetching paste: {e}")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/api_post.php":
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            try:
                req = urllib.request.Request(PASTEBIN_POST_URL, data=data, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; PastebinProxy/1.0)",
                    "Content-Type": "application/x-www-form-urlencoded"
                })
                with urllib.request.urlopen(req, context=ssl_context) as resp:
                    content = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(502, f"Error posting paste: {e}")
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 7779), PastebinProxy)
    print("Proxy server running at http://localhost:7779")
    server.serve_forever()
