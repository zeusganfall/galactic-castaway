# engine.py
import json, sys, os, time
from world import World

SAVE_PATH = "save.json"

def clear():
    # simple clear screen
    os.system("cls" if os.name=="nt" else "clear")

def clamp(v,a,b): return max(a,min(b,v))

def render(world, player_x, player_y, view_radius):
    clear()
    symbols = {b["id"]: b.get("symbol","?") for b in world.content["biomes"]}
    sym_player = world.meta["symbols"]["player"]
    w = world.width; h = world.height
    vr = view_radius
    for dy in range(-vr, vr+1):
        line = []
        y = player_y + dy
        for dx in range(-vr, vr+1):
            x = player_x + dx
            if not world.in_bounds(x,y):
                line.append(" ")
            else:
                if (x,y)==(player_x,player_y):
                    line.append(sym_player)
                else:
                    tile = world.grid[y][x]
                    if tile.landmark:
                        line.append("X")
                    else:
                        line.append(symbols.get(tile.biome, "?"))
        print("".join(line))
    # basic HUD
    print("\nSeed:", world.seed, " Crash:", world.crash_pos)
    print("Commands: w/a/s/d move, S save, q quit")

def simple_loop():
    w = World()
    # try load save
    loaded = w.load_from(SAVE_PATH)
    player = {"x": w.width//2, "y": w.height//2, "hp": 100, "hunger": 0}
    if loaded:
        # If save existed, place player at crash site
        player = loaded.get("player", player)
    else:
        w.generate()
        # start player near crash
        player["x"], player["y"] = w.crash_pos
    view_radius = w.meta.get("view_radius", 8)

    while True:
        render(w, player["x"], player["y"], view_radius)
        cmd = input("> ").strip().lower()
        if cmd == "q":
            print("Quitting without save.")
            break
        if cmd == "s":
            w.save_to(SAVE_PATH, player_state=player)
            print("Saved.")
            time.sleep(0.5)
            continue
        dx = dy = 0
        if cmd == "w": dy = -1
        elif cmd == "s": dy = 1
        elif cmd == "a": dx = -1
        elif cmd == "d": dx = 1
        if dx or dy:
            nx = clamp(player["x"] + dx, 0, w.width-1)
            ny = clamp(player["y"] + dy, 0, w.height-1)
            player["x"], player["y"] = nx, ny

if __name__=="__main__":
    simple_loop()
