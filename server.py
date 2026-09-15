"""A tiny local web server that shows an animated bouncing ball.

Run: python server.py
Open: http://localhost:8065
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Timer
import webbrowser


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ball Screen</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: radial-gradient(circle at top, #233b67, #0b1020 65%);
      color: #eaf2ff;
      font-family: system-ui, sans-serif;
    }
    main { width: min(92vw, 760px); text-align: center; }
    h1 { margin: 0 0 .35rem; font-size: clamp(1.6rem, 4vw, 2.6rem); }
    p { margin: 0 0 1.25rem; color: #b7c8e7; }
    #court {
      position: relative;
      height: min(62vw, 430px);
      overflow: hidden;
      border: 3px solid #8fb7ff;
      border-radius: 18px;
      background: linear-gradient(135deg, #12305d, #0a1a36);
      box-shadow: 0 20px 60px #0008, inset 0 0 50px #62a1ff22;
    }
    #ball {
      position: absolute;
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: radial-gradient(circle at 32% 28%, #fff9b3, #ffc107 38%, #e76f00 72%);
      box-shadow: 0 10px 20px #0008;
    }
    #message { margin-top: 1rem; font-weight: 600; }
  </style>
</head>
<body>
  <main>
    <h1>Ball Screen Server</h1>
    <p>Served locally by Python on port 8065.</p>
    <div id="court" aria-label="Animated bouncing ball"><div id="ball"></div></div>
    <div id="message">Ball speed: normal</div>
  </main>
  <script>
    const court = document.querySelector('#court');
    const ball = document.querySelector('#ball');
    const message = document.querySelector('#message');
    const size = 54;
    let x = 40, y = 40, dx = 3.8, dy = 3.1;

    function animate() {
      const maxX = court.clientWidth - size;
      const maxY = court.clientHeight - size;
      x += dx; y += dy;
      if (x <= 0 || x >= maxX) dx *= -1;
      if (y <= 0 || y >= maxY) dy *= -1;
      x = Math.max(0, Math.min(maxX, x));
      y = Math.max(0, Math.min(maxY, y));
      ball.style.transform = `translate(${x}px, ${y}px)`;
      requestAnimationFrame(animate);
    }

    court.addEventListener('click', () => {
      dx *= 1.35; dy *= 1.35;
      message.textContent = 'Ball speed: boosted! Click again for more.';
    });
    animate();
  </script>
</body>
</html>
"""


class BallScreenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Page not found")
            return

        content = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("localhost", 8065), BallScreenHandler)
    print("Ball Screen Server running at http://localhost:8065")
    # Delay slightly so the server is ready before the browser requests the page.
    Timer(0.5, lambda: webbrowser.open("http://localhost:8065")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
    finally:
        server.server_close()
