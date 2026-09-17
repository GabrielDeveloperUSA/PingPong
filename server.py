"""A tiny local web server that hosts a playable Pong game.

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
  <title>Ping Pong</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      padding: 1.5rem 0;
      display: grid;
      place-items: center;
      background:
        linear-gradient(#080b1fdd, #080b1fdd),
        repeating-linear-gradient(0deg, #fff1 0 1px, transparent 1px 5px),
        radial-gradient(circle at top, #462767, #080b1f 68%);
      color: #edf8ff;
      font-family: ui-monospace, "Cascadia Code", "SFMono-Regular", Consolas, monospace;
    }
    main {
      width: min(96vw, 1120px);
      padding: clamp(.9rem, 2vw, 1.5rem);
      text-align: center;
      border: 1px solid #8291c855;
      border-radius: 20px;
      background: #111735cc;
      box-shadow: 0 24px 70px #000a, inset 0 1px #ffffff14;
    }
    h1 {
      margin: 0 0 .4rem;
      color: #ffed71;
      font-size: clamp(1.8rem, 4vw, 3rem);
      letter-spacing: .12em;
      text-shadow: 3px 3px 0 #bb3c80, 0 0 20px #ffdf5f88;
    }
    p { margin: 0 0 1.15rem; color: #b7c8e7; font-size: .88rem; }
    #court {
      position: relative;
      height: min(68vw, 620px);
      overflow: hidden;
      border: 3px solid #ffed71;
      border-radius: 10px;
      background:
        linear-gradient(90deg, #152453 0 49.8%, #241b50 50.2% 100%),
        #101835;
      box-shadow: 0 16px 40px #0009, 0 0 18px #ffed7144, inset 0 0 70px #04081988;
    }
    #court::after {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: repeating-linear-gradient(to bottom, transparent 0 16px, #ffed71aa 16px 30px, transparent 30px 46px) center / 3px 100% no-repeat;
    }
    .paddle {
      position: absolute;
      z-index: 1;
      width: 16px;
      height: 92px;
      border-radius: 3px;
      box-shadow: 0 5px 15px #0008, inset 0 0 0 2px #ffffff55;
    }
    #left-paddle { background: linear-gradient(90deg, #f4ffff, #48e7f4); }
    #right-paddle { background: linear-gradient(90deg, #ff79bd, #fff0fa); }
    .paddle.hit {
      background: #ffffff;
      box-shadow: 0 0 12px 5px #8be9ff, 0 0 28px 9px #4f9dff99;
      animation: paddle-flash .22s ease-out;
    }
    #left-paddle { left: 22px; }
    #right-paddle { right: 22px; }
    #ball {
      position: absolute;
      z-index: 2;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: radial-gradient(circle at 32% 28%, #ffffff, #ffed71 38%, #ff9b36 72%);
      box-shadow: 0 5px 14px #0009, 0 0 12px #ffcf5c99;
    }
    #ball.hit { animation: ball-pop .24s ease-out; }
    .impact {
      position: absolute;
      z-index: 3;
      width: 18px;
      height: 18px;
      border: 3px solid #b9f6ff;
      border-radius: 50%;
      pointer-events: none;
      box-shadow: 0 0 12px #56cfff;
      transform: translate(-50%, -50%);
      animation: impact-ring .34s ease-out forwards;
    }
    @keyframes paddle-flash {
      50% { filter: brightness(1.8); }
    }
    @keyframes ball-pop {
      45% { filter: brightness(1.8) drop-shadow(0 0 9px #c9f7ff); }
    }
    @keyframes impact-ring {
      to { opacity: 0; transform: translate(-50%, -50%) scale(3.4); }
    }
    #score { margin: .85rem 0 .5rem; color: #ffed71; font-size: 1.7rem; font-weight: 800; letter-spacing: .24em; text-shadow: 0 0 12px #ffcf5c88; }
    #powers { display: flex; justify-content: center; gap: .8rem; margin: .45rem 0; }
    .power-card {
      min-width: 190px;
      padding: .38rem .6rem;
      border: 1px solid #6675b2;
      border-radius: 4px;
      background: #0b1230;
      color: #cfe2ff;
      font-size: .82rem;
    }
    .power-card.ready { border-color: #7bf6ff; box-shadow: 0 0 12px #44ceff66; color: #efffff; }
    .power-card strong { color: #7bf6ff; }
    #message { min-height: 1.25rem; margin-top: .6rem; color: #b9c8e9; font-size: .86rem; font-weight: 600; }
    kbd { padding: .1rem .3rem; border: 1px solid #98a9dc; border-radius: 3px; background: #252c52; color: #ffed71; font-family: inherit; font-size: .8em; }
    #sound-toggle {
      margin-top: .45rem;
      padding: .32rem .65rem;
      border: 1px solid #6675b2;
      border-radius: 4px;
      background: #0b1230;
      color: #cfe2ff;
      cursor: pointer;
      font: inherit;
      font-size: .75rem;
    }
    #sound-toggle:hover, #sound-toggle:focus-visible { border-color: #7bf6ff; color: #efffff; outline: none; }
  </style>
</head>
<body>
  <main>
    <h1>Ping Pong</h1>
    <p>Left: <kbd>W</kbd>/<kbd>S</kbd>, power <kbd>D</kbd> &nbsp; Right: <kbd>↑</kbd>/<kbd>↓</kbd>, power <kbd>L</kbd></p>
    <div id="court" aria-label="Playable Ping Pong court">
      <div class="paddle" id="left-paddle"></div>
      <div class="paddle" id="right-paddle"></div>
      <div id="ball"></div>
    </div>
    <div id="score">0 : 0</div>
    <div id="powers">
      <div class="power-card" id="left-power">Left <kbd>D</kbd>: waiting for power…</div>
      <div class="power-card" id="right-power">Right <kbd>L</kbd>: waiting for power…</div>
    </div>
    <div id="message">Press a movement key to serve.</div>
    <button id="sound-toggle" type="button" aria-pressed="true">Sound: on</button>
  </main>
  <script>
    const court = document.querySelector('#court');
    const ball = document.querySelector('#ball');
    const leftPaddle = document.querySelector('#left-paddle');
    const rightPaddle = document.querySelector('#right-paddle');
    const message = document.querySelector('#message');
    const score = document.querySelector('#score');
    const leftPowerDisplay = document.querySelector('#left-power');
    const rightPowerDisplay = document.querySelector('#right-power');
    const soundToggle = document.querySelector('#sound-toggle');
    const ballSize = 24, paddleHeight = 92, paddleWidth = 16, paddleInset = 22;
    const keys = new Set();
    const powerOptions = ['Speed Shot', 'Paddle Stretch'];
    let x, y, dx, dy, leftY, rightY, leftScore = 0, rightScore = 0, serving = true;
    let leftPaddleHeight = paddleHeight, rightPaddleHeight = paddleHeight;
    let leftPowers = [], rightPowers = [];
    let audioContext, soundOn = true;

    function getAudioContext() {
      if (!soundOn) return null;
      if (!audioContext) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return null;
        audioContext = new AudioContext();
      }
      if (audioContext.state === 'suspended') audioContext.resume();
      return audioContext;
    }

    function playPaddleSound() {
      const ctx = getAudioContext();
      if (!ctx) return;
      const oscillator = ctx.createOscillator();
      const filter = ctx.createBiquadFilter();
      const gain = ctx.createGain();
      const now = ctx.currentTime;
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(1250, now);
      oscillator.frequency.exponentialRampToValueAtTime(720, now + .09);
      filter.type = 'bandpass';
      filter.frequency.value = 930;
      filter.Q.value = 2.5;
      gain.gain.setValueAtTime(.0001, now);
      gain.gain.exponentialRampToValueAtTime(.075, now + .006);
      gain.gain.exponentialRampToValueAtTime(.0001, now + .12);
      oscillator.connect(filter).connect(gain).connect(ctx.destination);
      oscillator.start(now);
      oscillator.stop(now + .13);
    }

    function playHorn(frequency, startTime) {
      const ctx = getAudioContext();
      if (!ctx) return;
      const oscillator = ctx.createOscillator();
      const filter = ctx.createBiquadFilter();
      const gain = ctx.createGain();
      oscillator.type = 'sawtooth';
      oscillator.frequency.setValueAtTime(frequency, startTime);
      oscillator.frequency.exponentialRampToValueAtTime(frequency * .9, startTime + .25);
      filter.type = 'lowpass';
      filter.frequency.value = 1100;
      gain.gain.setValueAtTime(.0001, startTime);
      gain.gain.exponentialRampToValueAtTime(.045, startTime + .025);
      gain.gain.exponentialRampToValueAtTime(.0001, startTime + .29);
      oscillator.connect(filter).connect(gain).connect(ctx.destination);
      oscillator.start(startTime);
      oscillator.stop(startTime + .3);
    }

    function playPointLostSound() {
      const ctx = getAudioContext();
      if (!ctx) return;
      playHorn(660, ctx.currentTime);
      playHorn(330, ctx.currentTime + .32);
    }

    function resetBall(direction = Math.random() < .5 ? -1 : 1) {
      x = (court.clientWidth - ballSize) / 2;
      y = (court.clientHeight - ballSize) / 2;
      dx = 4.5 * direction;
      dy = (Math.random() * 4) - 2;
      serving = true;
    }

    function updateScore() {
      score.textContent = `${leftScore} : ${rightScore}`;
    }

    function scorePoint(player) {
      if (player === 'left') leftScore++; else rightScore++;
      updateScore();
      playPointLostSound();
      message.textContent = `${player === 'left' ? 'Left' : 'Right'} player scores! Press a movement key to serve.`;
      resetBall(player === 'left' ? -1 : 1);
    }

    function renderPowers() {
      const leftName = leftPowers[0] || 'waiting for power…';
      const rightName = rightPowers[0] || 'waiting for power…';
      leftPowerDisplay.innerHTML = `Left <kbd>D</kbd>: ${leftPowers.length ? `<strong>${leftName}</strong> (${leftPowers.length})` : leftName}`;
      rightPowerDisplay.innerHTML = `Right <kbd>L</kbd>: ${rightPowers.length ? `<strong>${rightName}</strong> (${rightPowers.length})` : rightName}`;
      leftPowerDisplay.classList.toggle('ready', leftPowers.length > 0);
      rightPowerDisplay.classList.toggle('ready', rightPowers.length > 0);
    }

    function grantPower(player) {
      const powers = player === 'left' ? leftPowers : rightPowers;
      if (powers.length < 3) powers.push(powerOptions[Math.floor(Math.random() * powerOptions.length)]);
      renderPowers();
      message.textContent = 'New powers are ready! Use D for left or L for right.';
    }

    function stretchPaddle(player) {
      const paddle = player === 'left' ? leftPaddle : rightPaddle;
      const setHeight = (height) => {
        if (player === 'left') leftPaddleHeight = height; else rightPaddleHeight = height;
        paddle.style.height = `${height}px`;
      };
      setHeight(142);
      setTimeout(() => setHeight(paddleHeight), 4000);
    }

    function usePower(player) {
      const powers = player === 'left' ? leftPowers : rightPowers;
      const power = powers.shift();
      if (!power) return;
      if (power === 'Speed Shot') {
        dx = Math.sign(dx || (player === 'left' ? 1 : -1)) * Math.min(Math.abs(dx || 4.5) * 1.75, 14);
        dy = Math.max(-9, Math.min(9, dy * 1.45));
      } else {
        stretchPaddle(player);
      }
      renderPowers();
      message.textContent = `${player === 'left' ? 'Left' : 'Right'} used ${power}!`;
    }

    function movePaddles() {
      const paddleSpeed = 6.5;
      if (keys.has('w')) leftY -= paddleSpeed;
      if (keys.has('s')) leftY += paddleSpeed;
      if (keys.has('arrowup')) rightY -= paddleSpeed;
      if (keys.has('arrowdown')) rightY += paddleSpeed;
      leftY = Math.max(0, Math.min(court.clientHeight - leftPaddleHeight, leftY));
      rightY = Math.max(0, Math.min(court.clientHeight - rightPaddleHeight, rightY));
      leftPaddle.style.transform = `translateY(${leftY}px)`;
      rightPaddle.style.transform = `translateY(${rightY}px)`;
    }

    function showImpact(paddle, direction) {
      paddle.classList.remove('hit');
      void paddle.offsetWidth;
      paddle.classList.add('hit');
      ball.classList.remove('hit');
      void ball.offsetWidth;
      ball.classList.add('hit');
      setTimeout(() => {
        paddle.classList.remove('hit');
        ball.classList.remove('hit');
      }, 240);
      const impact = document.createElement('div');
      impact.className = 'impact';
      impact.style.left = `${direction > 0 ? paddleInset + paddleWidth : court.clientWidth - paddleInset - paddleWidth}px`;
      impact.style.top = `${y + ballSize / 2}px`;
      court.append(impact);
      impact.addEventListener('animationend', () => impact.remove());
    }

    function hitPaddle(paddle, paddleY, direction) {
      const currentHeight = paddle === leftPaddle ? leftPaddleHeight : rightPaddleHeight;
      const impact = ((y + ballSize / 2) - (paddleY + currentHeight / 2)) / (currentHeight / 2);
      dx = direction * Math.min(Math.abs(dx) + .35, 10);
      dy = impact * 6;
      x += direction * 3;
      showImpact(paddle, direction);
      playPaddleSound();
    }

    function animate() {
      const maxX = court.clientWidth - ballSize;
      const maxY = court.clientHeight - ballSize;
      movePaddles();
      if (!serving) { x += dx; y += dy; }
      if (y <= 0 || y >= maxY) dy *= -1;
      y = Math.max(0, Math.min(maxY, y));
      const leftEdge = paddleInset + paddleWidth;
      const rightEdge = court.clientWidth - paddleInset - paddleWidth;
      if (dx < 0 && x <= leftEdge && x + ballSize >= paddleInset && y + ballSize >= leftY && y <= leftY + leftPaddleHeight) {
        hitPaddle(leftPaddle, leftY, 1);
      }
      if (dx > 0 && x + ballSize >= rightEdge && x <= rightEdge + paddleWidth && y + ballSize >= rightY && y <= rightY + rightPaddleHeight) {
        hitPaddle(rightPaddle, rightY, -1);
      }
      if (x + ballSize < 0) scorePoint('right');
      if (x > maxX + ballSize) scorePoint('left');
      y = Math.max(0, Math.min(maxY, y));
      ball.style.transform = `translate(${x}px, ${y}px)`;
      requestAnimationFrame(animate);
    }

    window.addEventListener('keydown', (event) => {
      const key = event.key.toLowerCase();
      if (['w', 's', 'arrowup', 'arrowdown', 'd', 'l'].includes(key)) getAudioContext();
      if (['w', 's', 'arrowup', 'arrowdown'].includes(key)) {
        event.preventDefault();
        keys.add(key);
        if (serving) {
          serving = false;
          message.textContent = 'Rally in progress!';
        }
      }
      if (!event.repeat && key === 'd') usePower('left');
      if (!event.repeat && key === 'l') usePower('right');
    });
    window.addEventListener('keyup', (event) => {
      keys.delete(event.key.toLowerCase());
    });
    soundToggle.addEventListener('click', () => {
      soundOn = !soundOn;
      soundToggle.textContent = `Sound: ${soundOn ? 'on' : 'off'}`;
      soundToggle.setAttribute('aria-pressed', String(soundOn));
      if (soundOn) getAudioContext();
    });
    leftY = rightY = (court.clientHeight - paddleHeight) / 2;
    resetBall();
    renderPowers();
    setInterval(() => {
      grantPower('left');
      grantPower('right');
    }, 5000);
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
