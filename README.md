# Ping Pong

A small, dependency-free Pong game served from a local Python web server. It runs entirely in the browser: Python delivers the page, while HTML, CSS, and JavaScript render and control the game.

## Run the project

From this project folder, start the server:

```powershell
python server.py
```

The app opens your default browser automatically at [http://localhost:8065](http://localhost:8065). You can also use the **PingPong Ball Screen** shortcut created on the Windows desktop.

If the regular `python` command is not installed on Windows, use the bundled runtime:

```powershell
C:\Users\Gabe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe server.py
```

To stop the server, return to its terminal window and press `Ctrl+C`.

## How it works

`server.py` uses Python's built-in `ThreadingHTTPServer`, so no packages need to be installed. It listens only on `localhost` at port `8065` and returns the same game page for `/` and `/index.html`.

The web page contains:

- HTML for the court, two paddles, ball, score, controls, and sound button.
- CSS for the neon arcade visual style, hit flashes, and impact animations.
- JavaScript for animation, collision detection, scoring, keyboard input, temporary power-ups, and browser-generated sound effects.

The ball begins in a serve state. Pressing a paddle movement key starts play. When it reaches a paddle, its vertical direction changes according to where it hits the paddle. Missing the ball awards one point to the other player.

## Controls

| Player | Move | Use power |
| --- | --- | --- |
| Left | `W` / `S` | `D` |
| Right | `Up Arrow` / `Down Arrow` | `L` |

Each player receives a random power-up every five seconds. Available power-ups are:

- **Speed Shot**: sends the ball away faster.
- **Paddle Stretch**: makes the player's paddle taller for four seconds.

Use the on-page **Sound** button to turn game sounds on or off.
