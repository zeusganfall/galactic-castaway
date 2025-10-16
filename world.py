# world.py
import json, random, math, os

class Tile:
    def __init__(self, biome_id):
        self.biome = biome_id
        self.landmark = None
        self.creatures = []

class World:
    def __init__(self, content_path="content.json", meta_path="meta.json"):
        self.content = json.load(open(content_path))
        self.meta = json.load(open(meta_path))
        self.width = self.meta["map_width"]
        self.height = self.meta["map_height"]
        self.grid = [[None for _ in range(self.width)] for __ in range(self.height)]
        self.seed = None
        self.crash_pos = None

    def generate(self, seed=None):
        if seed is None:
            seed = random.randint(0, 2**30)
        self.seed = seed
        rnd = random.Random(seed)
        # choose biome centers (simple Voronoi)
        centers = []
        biome_choices = []
        # build weighted list
        for b in self.content["biomes"]:
            biome_choices.extend([b["id"]] * max(1, int(b.get("weight",1)*10)))
        for _ in range(self.meta.get("biome_centers", 8)):
            x = rnd.randrange(self.width)
            y = rnd.randrange(self.height)
            biome = rnd.choice(biome_choices)
            centers.append((x,y,biome))
        # assign each tile to nearest center
        for y in range(self.height):
            for x in range(self.width):
                best = None
                bestd = None
                for cx,cy,biome in centers:
                    d = (cx-x)**2 + (cy-y)**2
                    if bestd is None or d < bestd:
                        bestd = d; best = biome
                self.grid[y][x] = Tile(best)
        # crash epicenter near center
        cx = self.width//2 + rnd.randint(-self.meta.get("crash_epicenter_variance",5), self.meta.get("crash_epicenter_variance",5))
        cy = self.height//2 + rnd.randint(-self.meta.get("crash_epicenter_variance",5), self.meta.get("crash_epicenter_variance",5))
        self.crash_pos = (max(0,min(self.width-1,cx)), max(0,min(self.height-1,cy)))
        self.grid[self.crash_pos[1]][self.crash_pos[0]].landmark = "crash_wreck"
        # place a couple tech fragments (rare)
        for node in self.content.get("tech_nodes", []):
            if rnd.random() < node.get("rarity", 0.02):
                # pick a tile in a random place of matching biome (or anywhere)
                tries=0
                while tries<200:
                    tx = rnd.randrange(self.width); ty = rnd.randrange(self.height)
                    if (tx,ty) != self.crash_pos:
                        self.grid[ty][tx].landmark = node["node_id"]
                        break
                    tries += 1

    def in_bounds(self,x,y):
        return 0<=x<self.width and 0<=y<self.height

    def save_to(self, path="save.json", player_state=None):
        data = {
            "seed": self.seed,
            "crash_pos": self.crash_pos,
            "player": player_state or {}
        }
        with open(path,"w") as f:
            json.dump(data, f, indent=2)

    def load_from(self, path="save.json"):
        if not os.path.exists(path):
            return None
        data = json.load(open(path))
        self.generate(data.get("seed"))
        # optionally restore player elsewhere -- engine handles player_state
        return data
