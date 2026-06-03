from js import document, window
from pyodide.ffi import create_proxy
import math
import random


canvas = document.getElementById("game")
ctx = canvas.getContext("2d")
status = document.getElementById("status")

WIDTH = canvas.width
HEIGHT = canvas.height
PLAYER_Y = HEIGHT - 58
PLAYER_W = 92
PLAYER_H = 22

keys = set()
last_time = 0

game = {
    "player_x": WIDTH / 2 - PLAYER_W / 2,
    "stars": [],
    "score": 0,
    "lives": 3,
    "spawn_timer": 0,
    "running": True,
}


def reset():
    game["player_x"] = WIDTH / 2 - PLAYER_W / 2
    game["stars"] = []
    game["score"] = 0
    game["lives"] = 3
    game["spawn_timer"] = 0
    game["running"] = True


def spawn_star():
    game["stars"].append({
        "x": random.randint(28, WIDTH - 28),
        "y": -24,
        "r": random.randint(12, 20),
        "speed": random.uniform(135, 230) + game["score"] * 4,
        "spin": random.uniform(0, math.tau),
    })


def draw_background():
    gradient = ctx.createLinearGradient(0, 0, 0, HEIGHT)
    gradient.addColorStop(0, "#19202b")
    gradient.addColorStop(1, "#0f1218")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, WIDTH, HEIGHT)

    ctx.fillStyle = "rgba(255,255,255,0.16)"
    for i in range(46):
        x = (i * 113) % WIDTH
        y = (i * 67) % HEIGHT
        ctx.fillRect(x, y, 2, 2)


def draw_star(star):
    ctx.save()
    ctx.translate(star["x"], star["y"])
    ctx.rotate(star["spin"])
    ctx.beginPath()
    for i in range(10):
        radius = star["r"] if i % 2 == 0 else star["r"] * 0.45
        angle = -math.pi / 2 + i * math.pi / 5
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        if i == 0:
            ctx.moveTo(x, y)
        else:
            ctx.lineTo(x, y)
    ctx.closePath()
    ctx.fillStyle = "#ffd166"
    ctx.shadowColor = "rgba(255,209,102,0.6)"
    ctx.shadowBlur = 18
    ctx.fill()
    ctx.restore()


def draw_player():
    x = game["player_x"]
    ctx.fillStyle = "#5eead4"
    ctx.shadowColor = "rgba(94,234,212,0.45)"
    ctx.shadowBlur = 16
    ctx.beginPath()
    ctx.roundRect(x, PLAYER_Y, PLAYER_W, PLAYER_H, 10)
    ctx.fill()
    ctx.shadowBlur = 0

    ctx.fillStyle = "#0f1720"
    ctx.fillRect(x + 18, PLAYER_Y + 7, PLAYER_W - 36, 5)


def draw_text():
    ctx.fillStyle = "#f4f7fb"
    ctx.font = "700 26px Segoe UI, sans-serif"
    ctx.fillText(f"Score {game['score']}", 24, 42)
    ctx.fillText(f"Lives {game['lives']}", WIDTH - 128, 42)

    if not game["running"]:
        ctx.fillStyle = "rgba(10,12,16,0.72)"
        ctx.fillRect(0, 0, WIDTH, HEIGHT)
        ctx.fillStyle = "#f4f7fb"
        ctx.textAlign = "center"
        ctx.font = "800 46px Segoe UI, sans-serif"
        ctx.fillText("Game Over", WIDTH / 2, HEIGHT / 2 - 18)
        ctx.font = "500 22px Segoe UI, sans-serif"
        ctx.fillText("Press Space to restart", WIDTH / 2, HEIGHT / 2 + 34)
        ctx.textAlign = "left"


def update(dt):
    if not game["running"]:
        return

    move = 0
    if "ArrowLeft" in keys or "a" in keys:
        move -= 1
    if "ArrowRight" in keys or "d" in keys:
        move += 1

    game["player_x"] += move * 420 * dt
    game["player_x"] = max(0, min(WIDTH - PLAYER_W, game["player_x"]))

    game["spawn_timer"] -= dt
    if game["spawn_timer"] <= 0:
        spawn_star()
        game["spawn_timer"] = max(0.28, 0.82 - game["score"] * 0.018)

    px = game["player_x"]
    kept = []
    for star in game["stars"]:
        star["y"] += star["speed"] * dt
        star["spin"] += dt * 2.4
        caught = (
            PLAYER_Y - 8 <= star["y"] + star["r"] <= PLAYER_Y + PLAYER_H + 8
            and px - star["r"] <= star["x"] <= px + PLAYER_W + star["r"]
        )
        if caught:
            game["score"] += 1
        elif star["y"] - star["r"] > HEIGHT:
            game["lives"] -= 1
            if game["lives"] <= 0:
                game["running"] = False
        else:
            kept.append(star)
    game["stars"] = kept


def frame(timestamp):
    global last_time
    if last_time == 0:
        last_time = timestamp
    dt = min(0.04, (timestamp - last_time) / 1000)
    last_time = timestamp

    update(dt)
    draw_background()
    for star in game["stars"]:
        draw_star(star)
    draw_player()
    draw_text()
    window.requestAnimationFrame(frame_proxy)


def on_keydown(event):
    keys.add(event.key)
    if event.key == " " and not game["running"]:
        reset()
    if event.key in ["ArrowLeft", "ArrowRight", " "]:
        event.preventDefault()


def on_keyup(event):
    keys.discard(event.key)


keydown_proxy = create_proxy(on_keydown)
keyup_proxy = create_proxy(on_keyup)
frame_proxy = create_proxy(frame)

window.addEventListener("keydown", keydown_proxy)
window.addEventListener("keyup", keyup_proxy)
status.textContent = "Ready"
window.requestAnimationFrame(frame_proxy)
