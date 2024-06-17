from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)

PORT = 8000

with HTTPServer(('', PORT), CustomHandler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
