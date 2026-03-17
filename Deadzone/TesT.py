import os, unittest, sys, pygame
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from systems.inventory import Inventory
from scenes.gameplay_scene import Gameplay_Scene, MAP_ZOOM
from sprites.dropped_item import DroppedItem
from sprites.library_item import (
    CARE_KIT,
    WATER,
    ITEMS_BY_NAME,
    HELMET_SOLDAT,
    CHESPLATE_SOLDAT,
    BOTTS_SOLDAT,
)
from sprites.enemy import Enemy
from sprites.player import Player


class _DummyGame:
    def __init__(self):
        self.screen = pygame.Surface((800, 600))

    def change_scene(self, _scene):
        pass


class _DummyPlayer:
    def __init__(self, x=400, y=300):
        self.position = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = (int(x), int(y))
        self.health = 100
        self.inventory = Inventory(capacity=35)


class _DummyMapManager:
    def __init__(self, pcx=400, pcy=300):
        self._pcx = pcx
        self._pcy = pcy

    def get_player_screen_pos(self):
        return self._pcx, self._pcy


class GameplaySceneUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _make_scene_without_spawns(self):
        original_try_init_map = Gameplay_Scene._try_init_map
        original_spawn_enemies = Gameplay_Scene._spawn_enemies
        original_spawn_test_items = Gameplay_Scene._spawn_test_items
        try:
            Gameplay_Scene._try_init_map = lambda *_args, **_kwargs: None
            Gameplay_Scene._spawn_enemies = lambda *_args, **_kwargs: None
            Gameplay_Scene._spawn_test_items = lambda *_args, **_kwargs: None
            return Gameplay_Scene(_DummyGame(), _DummyPlayer())
        finally:
            Gameplay_Scene._try_init_map = original_try_init_map
            Gameplay_Scene._spawn_enemies = original_spawn_enemies
            Gameplay_Scene._spawn_test_items = original_spawn_test_items

    def test_world_to_screen_without_map_manager_returns_identity(self):
        scene = self._make_scene_without_spawns()
        scene.map_manager = None
        self.assertEqual(scene.world_to_screen(12.7, 99.2), (12, 99))

    def test_screen_to_world_without_map_manager_returns_identity(self):
        scene = self._make_scene_without_spawns()
        scene.map_manager = None
        self.assertEqual(scene.screen_to_world(12, 99), (12.0, 99.0))

    def test_world_to_screen_with_map_manager_uses_player_offset_and_zoom(self):
        scene = self._make_scene_without_spawns()
        scene.map_manager = _DummyMapManager(pcx=200, pcy=100)
        scene.player.position.xy = (10, 20)
        sx, sy = scene.world_to_screen(10 + 5, 20 - 3)
        self.assertEqual((sx, sy), (int(5 * MAP_ZOOM + 200), int(-3 * MAP_ZOOM + 100)))

    def test_screen_to_world_with_map_manager_is_inverse_of_world_to_screen(self):
        scene = self._make_scene_without_spawns()
        scene.map_manager = _DummyMapManager(pcx=300, pcy=200)
        scene.player.position.xy = (50, 60)
        wx = 50 + (37 / MAP_ZOOM)
        wy = 60 + (-19 / MAP_ZOOM)
        sx, sy = scene.world_to_screen(wx, wy)
        wx2, wy2 = scene.screen_to_world(sx, sy)
        self.assertAlmostEqual(wx2, wx, places=6)
        self.assertAlmostEqual(wy2, wy, places=6)

    def test_save_then_load_restores_player_and_inventory(self):
        scene = self._make_scene_without_spawns()
        scene.enemies.clear()
        scene.dropped_items.clear()
        scene.player.position.xy = (111, 222)
        scene.player.health = 77
        scene.player.inventory.add_item(CARE_KIT)
        scene.player.inventory.add_item(WATER)

        import scenes.gameplay_scene as gameplay_scene_module

        captured = {}

        def _capture_dump(data, _fp):
            captured["data"] = data

        with (
            mock.patch.object(gameplay_scene_module, "open", mock.mock_open(), create=True),
            mock.patch.object(gameplay_scene_module.json, "dump", side_effect=_capture_dump),
        ):
            scene.save_game()

        new_scene = self._make_scene_without_spawns()
        with (
            mock.patch.object(gameplay_scene_module.os.path, "exists", return_value=True),
            mock.patch.object(gameplay_scene_module, "open", mock.mock_open(read_data="{}"), create=True),
            mock.patch.object(gameplay_scene_module.json, "load", return_value=captured["data"]),
        ):
            new_scene.load_game()

        self.assertEqual(int(new_scene.player.position.x), 111)
        self.assertEqual(int(new_scene.player.position.y), 222)
        self.assertEqual(new_scene.player.health, 77)
        self.assertTrue(new_scene.player.inventory.has_item(CARE_KIT.name))
        self.assertTrue(new_scene.player.inventory.has_item(WATER.name))

    def test_items_by_name_contains_known_items(self):
        self.assertIs(ITEMS_BY_NAME["CARE_KIT"], CARE_KIT)
        self.assertIs(ITEMS_BY_NAME["WATER"], WATER)

    def test_check_nearby_items_picks_closest_near_item(self):
        scene = self._make_scene_without_spawns()
        scene.map_manager = None
        scene.player.position.xy = (100, 100)

        far = DroppedItem(CARE_KIT, 100 + 40, 100)  
        near = DroppedItem(WATER,   100 + 10, 100) 
        scene.dropped_items = [far, near]

        scene.check_nearby_items()
        self.assertIs(scene.nearby_item, near)

    def test_try_pickup_item_removes_item_when_inventory_accepts(self):
        scene = self._make_scene_without_spawns()
        scene.player.position.xy = (100, 100)
        dropped = DroppedItem(CARE_KIT, 100, 100)
        scene.dropped_items = [dropped]
        scene.nearby_item = dropped

        scene.try_pickup_item()
        self.assertIsNone(scene.nearby_item)
        self.assertEqual(scene.dropped_items, [])
        self.assertTrue(scene.player.inventory.has_item(CARE_KIT.name))

    def test_try_pickup_item_keeps_item_when_inventory_full(self):
        scene = self._make_scene_without_spawns()
        scene.player.inventory = Inventory(capacity=0)
        dropped = DroppedItem(CARE_KIT, 100, 100)
        scene.dropped_items = [dropped]
        scene.nearby_item = dropped

        scene.try_pickup_item()
        self.assertIs(scene.nearby_item, dropped)
        self.assertEqual(scene.dropped_items, [dropped])

    def test_remove_dead_enemies_removes_and_counts(self):
        scene = self._make_scene_without_spawns()

        class _E:
            def __init__(self, health):
                self.health = health

        alive = _E(10)
        dead1 = _E(0)
        dead2 = _E(-5)
        scene.enemies = [alive, dead1, dead2]
        scene.enemies_killed = 0

        scene._remove_dead_enemies()
        self.assertEqual(scene.enemies, [alive])
        self.assertEqual(scene.enemies_killed, 2)


class _DummyPlayerForEnemy:
    def __init__(self, x=0, y=0):
        self.position = pygame.Vector2(x, y)
        self.taken = []

    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        self.taken.append((amount, attacker_x, attacker_y))


class PlayerEnemyUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_player_take_damage_consumes_shield_then_health(self):
        p = Player()
        p.health = 100
        p.shield = 10
        p.take_damage(6)
        self.assertEqual(p.shield, 4)
        self.assertEqual(p.health, 100)

        p.take_damage(10)
        self.assertEqual(p.shield, 0)
        self.assertEqual(p.health, 94)
        self.assertTrue(p.is_hit)
        self.assertGreater(p.hit_timer, 0)
        self.assertEqual(p.time_since_last_damage, 0)

    def test_player_take_damage_sets_knockback_direction(self):
        p = Player(x=100, y=100)
        p.knockback_velocity.xy = (0, 0)
        p.take_damage(1, attacker_x=80, attacker_y=100)
        self.assertGreater(p.knockback_velocity.x, 0)
        self.assertAlmostEqual(p.knockback_velocity.y, 0, places=6)

    def test_player_equip_armor_updates_shield_capacity(self):
        p = Player()
        p.shield = 0
        p.max_shield = 0

        p.inventory.add_item(HELMET_SOLDAT)
        p.inventory.add_item(CHESPLATE_SOLDAT)
        p.inventory.add_item(BOTTS_SOLDAT)

        self.assertTrue(p.equip_item(HELMET_SOLDAT, "helmet"))
        self.assertEqual(p.max_shield, 15)
        self.assertEqual(p.shield, 15)

        self.assertTrue(p.equip_item(CHESPLATE_SOLDAT, "chestplate"))
        self.assertEqual(p.max_shield, 45)
        self.assertEqual(p.shield, 45)

        self.assertTrue(p.unequip_item("helmet"))
        self.assertEqual(p.max_shield, 30)
        self.assertEqual(p.shield, 30)

    def test_enemy_attack_calls_player_take_damage_when_off_cooldown(self):
        e = Enemy(10, 20)
        p = _DummyPlayerForEnemy()
        with mock.patch("sprites.enemy.pygame.time.get_ticks", return_value=2000):
            e.last_attack = 0
            e.attack(p)
        self.assertEqual(p.taken, [(e.damage, e.x, e.y)])

    def test_enemy_update_moves_towards_player_in_detection_range(self):
        e = Enemy(0, 0)
        p = _DummyPlayerForEnemy(x=100, y=0)
        e.detection_radius = 200
        e.attack_distance = 10
        e.update(dt=1.0, player=p, enemies=[], projectiles=[])
        self.assertTrue(e._moving)
        self.assertGreater(e.x, 0)

    def test_enemy_update_when_player_none_only_advances_hit_timer(self):
        e = Enemy(0, 0)
        e.take_hit()
        self.assertTrue(e._hit)
        e.update(dt=0.2, player=None, enemies=[], projectiles=[])
        self.assertFalse(e._hit)


if __name__ == "__main__":
    unittest.main()
