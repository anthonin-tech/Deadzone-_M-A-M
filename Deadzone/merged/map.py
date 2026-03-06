from dataclasses import dataclass
import os
import pygame

try:
    import pytmx
    import pyscroll
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR    = os.path.join(PROJECT_ROOT, "asset")

@dataclass
class Portal:
    from_world:    str
    origin_point:  str
    target_world:  str
    teleport_point: str

@dataclass
class Map:
    name:     str
    walls:    list
    group:    object
    tmx_data: object
    portals:  list

class MapManager:

    def __init__(self, screen, player):
        self.maps        = dict()
        self.screen      = screen
        self.player      = player
        self.current_map = "map"
        self._last_teleport_time = 0
        self._teleport_cooldown  = 800

        if not MAP_AVAILABLE:
            return

        for tmx_file in os.listdir(ASSET_DIR):
            if tmx_file.endswith(".tmx"):
                self._repair_tileset_images(os.path.join(ASSET_DIR, tmx_file))

        self.register_map("map", portals=[
            Portal("map", "enter_cave",   "cave-1",      "spawn_cave"),
            Portal("map", "enter_bunker", "Bunker",       "spawn_bunker"),
            Portal("map", "enter_church", "church",       "spawn_church"),
            Portal("map", "enter_camp",   "Camp",         "spawn_camp"),
            Portal("map", "enter_school", "School-hall",  "spawn_school"),
        ])
        self.register_map("cave-1", portals=[
            Portal("cave-1", "exit_cave",    "map",    "enter_cave_exit"),
            Portal("cave-1", "enter_cave_2", "cave-2", "spawn_cave_2"),
        ])
        self.register_map("cave-2", portals=[
            Portal("cave-2", "exit_cave_2", "cave-1", "enter_cave_2_exit"),
        ])
        self.register_map("Bunker", portals=[
            Portal("Bunker", "exit_bunker", "map", "enter_bunker_exit"),
        ])
        self.register_map("church", portals=[
            Portal("church", "exit_church", "map", "enter_church_exit"),
        ])
        self.register_map("Camp", portals=[
            Portal("Camp", "exit_camp", "map", "enter_camp_exit"),
        ])
        self.register_map("School-hall", portals=[
            Portal("School-hall", "exit_school",          "map",            "enter_school_exit"),
            Portal("School-hall", "enter_school_canteen", "School-canteen", "spawn_school_canteen"),
            Portal("School-hall", "enter_school_desk",    "School-desk",    "spawn_school_desk"),
            Portal("School-hall", "enter_school_class",   "School-class",   "spawn_school_class"),
        ])
        self.register_map("School-canteen", portals=[
            Portal("School-canteen", "exit_school_canteen", "School-hall", "enter_school_canteen_exit"),
        ])
        self.register_map("School-desk", portals=[
            Portal("School-desk", "exit_school_desk", "School-hall", "enter_school_desk_exit"),
        ])
        self.register_map("School-class", portals=[
            Portal("School-class", "exit_school_class", "School-hall", "enter_school_class_exit"),
        ])

        if self.maps:
            self.teleport_player("player")

    def register_map(self, name, portals=[]):
        tmx_path = os.path.join(ASSET_DIR, f"{name}.tmx")
        if not os.path.exists(tmx_path):
            return

        try:
            tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        except Exception as e:
            return

        map_data  = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 3

        walls = []
        for obj in tmx_data.objects:

            obj_type = getattr(obj, "type", None)
            if not obj_type and hasattr(obj, "properties"):
                obj_type = obj.properties.get("type")

            if obj_type == "collision" and not getattr(obj, "name", ""):
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=10)
        group.add(self.player)

        self.maps[name] = Map(name, walls, group, tmx_data, portals)

    def teleport_player(self, name):
        try:
            point = self.get_object(name)
        except Exception:
            return

        self.player.position.x = point.x
        self.player.position.y = point.y
        self.player.rect.center = (int(point.x), int(point.y))
        self.player.save_location()

    def check_collisions(self):
        if not self.maps:
            return

        now = pygame.time.get_ticks()
        if now - self._last_teleport_time >= self._teleport_cooldown:
            for portal in self.get_map().portals:
                if portal.from_world == self.current_map:
                    try:
                        point = self.get_object(portal.origin_point)
                    except Exception:
                        continue
                    w = max(int(getattr(point, "width",  0) or 48), 48)
                    h = max(int(getattr(point, "height", 0) or 48), 48)
                    rect = pygame.Rect(int(point.x), int(point.y), w, h)
                    if self.player.feet.colliderect(rect):
                        self.current_map = portal.target_world
                        self.teleport_player(portal.teleport_point)
                        self._last_teleport_time = now
                        break

        for sprite in self.get_group().sprites():
            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def get_map(self):
        if self.current_map not in self.maps:
            if not self.maps:
                return None
            self.current_map = next(iter(self.maps))
        return self.maps[self.current_map]

    def get_group(self): return self.get_map().group
    def get_walls(self): return self.get_map().walls
    def get_object(self, name): return self.get_map().tmx_data.get_object_by_name(name)

    def get_player_screen_pos(self):

        if not self.maps:
            return None
        group = self.get_group()

        map_layer = getattr(group, '_map_layer', None) or getattr(group, 'map_layer', None)
        if map_layer is None:
            return self.screen.get_width() // 2, self.screen.get_height() // 2
        view = map_layer.view_rect
        zoom = map_layer.zoom
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        sx = sw // 2 + int((self.player.position.x - view.centerx) * zoom)
        sy = sh // 2 + int((self.player.position.y - view.centery) * zoom)
        return sx, sy

    def draw(self):
        if not MAP_AVAILABLE or not self.maps:
            return

        self.get_group().center(self.player.rect.center)
        self.get_group().draw(self.screen)

    def update(self):
        if not MAP_AVAILABLE or not self.maps:
            return
        self.get_group().update()
        self.check_collisions()

    def _repair_tileset_images(self, tmx_path):
        import xml.etree.ElementTree as ET
        try:
            for ts_elem in ET.parse(tmx_path).findall(".//tileset"):
                src = ts_elem.get("source")
                if not src:
                    continue
                tsx_path = os.path.join(ASSET_DIR, src)
                if not os.path.exists(tsx_path):
                    continue
                for img_elem in ET.parse(tsx_path).findall(".//image"):
                    img_src = img_elem.get("source")
                    if not img_src:
                        continue
                    img_path = os.path.join(ASSET_DIR, img_src)
                    if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
                        w = int(img_elem.get("width",  16))
                        h = int(img_elem.get("height", 16))
                        self._create_placeholder_image(img_path, w, h)
        except Exception:
            pass

    @staticmethod
    def _create_placeholder_image(path, w, h):
        import struct, zlib
        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(c[4:]) & 0xFFFFFFFF)
        raw = zlib.compress(b"".join(b"\x00" + b"\x80\x80\x80" * w for _ in range(h)))
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", raw)
               + chunk(b"IEND", b""))
        open(path, "wb").write(png)
