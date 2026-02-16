import arcade

global_background_music = None
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1920
SCREEN_TITLE = "проект"
PLAYER_SPEED = 5
GRAVITY = 0.6
JUMP_SPEED = 15
ENEMY_SPEED = 2

LEVELS = [
    ("C:/Users/ersov/PycharmProjects/PythonProject/resources/tiled_maps/level_1.json", arcade.color.DARK_GREEN, "1 УРОВЕНЬ"),
    ("C:/Users/ersov/PycharmProjects/PythonProject/resources/tiled_maps/map2_level_1.json",arcade.color.DARK_PASTEL_PURPLE, "2 УРОВЕНЬ"),
    ("C:/Users/ersov/PycharmProjects/PythonProject/resources/tiled_maps/map2_level_2.json",arcade.color.SKY_BLUE, "3 УРОВЕНЬ")
]



# начальный экран
class StartView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.draw_text("ПЛАТФОРМЕР-ПРОЕКТ", self.window.width / 2, self.window.height / 2 + 100,
                         arcade.color.WHITE, font_size=50, anchor_x="center", bold=True)
        arcade.draw_text("Нажмите ПРОБЕЛ, чтобы начать", self.window.width / 2, self.window.height / 2,
                         arcade.color.GRAY, font_size=30, anchor_x="center")
        arcade.draw_text("Управление: ←↑→", self.window.width / 2, self.window.height / 2 - 50,
                         arcade.color.LIGHT_GRAY, font_size=20, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.SPACE:
            test_sound = arcade.Sound("C:/Users/ersov/PycharmProjects/PythonProject/resources/music/1918.mp3")
            test_sound.play(volume=0.5, loop=True)

            game_view = GameView()
            game_view.setup(level_index=0)
            self.window.show_view(game_view)


# враг
class Enemy(arcade.Sprite):
    def __init__(self, x, y, enemy_type="bee"):
        super().__init__()
        self.enemy_type = enemy_type
        self.setup_sprite()
        self.center_x = x
        self.center_y = y
        self.change_x = ENEMY_SPEED
        self.boundary_left = x - 100
        self.boundary_right = x + 100

    def setup_sprite(self):
        if self.enemy_type == "bee":
            self.texture = arcade.load_texture("C:/Users/ersov/PycharmProjects/PythonProject/resources/images/enemies/bee.png")
            self.scale = 0.7
        elif self.enemy_type == "slime":
            self.texture = arcade.load_texture("C:/Users/ersov/PycharmProjects/PythonProject/resources/images/enemies/slimeBlue.png")
            self.scale = 0.8
        elif self.enemy_type == "worm":
            self.texture = arcade.load_texture("C:/Users/ersov/PycharmProjects/PythonProject/resources/images/enemies/wormGreen.png")
            self.scale = 0.6
            self.alpha = 180

    def update(self, delta_time=1/60):
        super().update()
        if self.change_x < 0:
            self.scale_x = abs(self.scale_x)
        elif self.change_x > 0:
            self.scale_x = -abs(self.scale_x)
        if self.center_x < self.boundary_left or self.center_x > self.boundary_right:
            self.change_x *= -1


class GameOverView(arcade.View):

    def on_draw(self):
        arcade.set_background_color(arcade.color.RED)
        self.clear()
        arcade.draw_text("ПОРАЖЕНИЕ", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.BLACK, font_size=60, anchor_x="center", bold=True)
        arcade.draw_text("Герой погиб!", self.window.width / 2, self.window.height / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")
        arcade.draw_text("Нажмите R, чтобы начать сначала", self.window.width / 2, self.window.height / 2 - 50,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.R:
            game_view = GameView()
            game_view.setup(level_index=0)
            self.window.show_view(game_view)


# победа
class WinView(arcade.View):
    def __init__(self, final_score):
        super().__init__()
        self.final_score = final_score

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.GOLD)
        arcade.draw_text("ПОБЕДА!", self.window.width / 2, self.window.height / 2 + 100,
                         arcade.color.DARK_RED, font_size=60, anchor_x="center", bold=True)
        arcade.draw_text("Вы прошли все уровни!", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.BLACK, font_size=30, anchor_x="center")
        arcade.draw_text(f"Ваш счёт: {self.final_score}", self.window.width / 2, self.window.height / 2,
                         arcade.color.DARK_BLUE, font_size=40, anchor_x="center", bold=True)
        arcade.draw_text("Нажмите R, чтобы начать заново", self.window.width / 2, self.window.height / 2 - 80,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_key_press(self, key, _):
        if key == arcade.key.R:
            game_view = GameView()
            game_view.setup(level_index=0, score=0)
            self.window.show_view(game_view)



# Снаряд
class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction):
        super().__init__("C:/Users/ersov/PycharmProjects/PythonProject/resources/images/space_shooter/laserBlue01.png", 0.8)
        self.center_x = x
        self.center_y = y
        self.change_x = 12 * direction

    def update(self, delta_time=1/60):
        super().update()
        if self.right < 0:
            self.remove_from_sprite_lists()


# игра
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.shoot_sound = None
        self.player = None
        self.player_spritelist = None
        self.scene = None
        self.physics_engine = None
        self.score = 0
        self.enemy_list = None
        self.score_text = None
        self.level_name_text = None
        self.collect_coin_sound = None
        self.hit_enemy_sound = None
        self.walk_textures = []
        self.idle_texture = None
        self.jump_texture = None
        self.walk_frame = 0
        self.walk_speed = 0.15
        self.camera = None
        self.gui_camera = None
        self.health = 100
        self.max_health = 100
        self.projectile_list = arcade.SpriteList()
        self.coin_list = None

    def setup(self, level_index, score=0):
        self.level_index = level_index
        self.health = 100
        self.score = score
        # Текст
        self.score_text = arcade.Text(f"Score: {self.score}", 10, self.window.height - 30, arcade.color.WHITE, 24)
        self.level_name_text = arcade.Text("", self.window.width / 2, self.window.height - 30,
                                           arcade.color.YELLOW, 28, anchor_x="center")

        # Звуки
        self.shoot_sound = arcade.load_sound("C:/Users/ersov/PycharmProjects/PythonProject/resources/sounds/laser1.wav")
        self.collect_coin_sound = arcade.Sound("C:/Users/ersov/PycharmProjects/PythonProject/resources/sounds/coin5.wav")
        self.hit_enemy_sound = arcade.Sound("C:/Users/ersov/PycharmProjects/PythonProject/resources/sounds/hurt5.wav")

        # Анимации
        self.idle_texture = arcade.load_texture(
            "C:/Users/ersov/PycharmProjects/PythonProject/resources/images/animated_characters/robot/robot_idle.png"
        )
        self.walk_textures.clear()
        for i in range(8):
            texture = arcade.load_texture(
                f"C:/Users/ersov/PycharmProjects/PythonProject/resources/images/animated_characters/robot/robot_walk{i:02d}.png"
            )
            self.walk_textures.append(texture)
        self.jump_texture = arcade.load_texture(
            "C:/Users/ersov/PycharmProjects/PythonProject/resources/images/animated_characters/robot/robot_jump.png"
        )

        # Игрок
        if self.player is None:
            self.player = arcade.Sprite()
            self.player.scale = 0.5
        self.player.center_x = 300
        self.player.center_y = 300
        self.player.texture = self.idle_texture

        if self.player_spritelist is None:
            self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        # Уровень
        map_name, bg_color, level_name = LEVELS[level_index]
        arcade.set_background_color(bg_color)
        self.tile_map = arcade.load_tilemap(map_name, scaling=0.5)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        if "Platforms" not in self.scene:
            self.scene.add_sprite_list("Platforms")
        if "Players" not in self.scene:
            self.scene.add_sprite_list("Players")
        self.scene["Players"].append(self.player)

        # Монеты
        if "Coins" in self.scene:
            self.coin_list = self.scene["Coins"]
        else:
            self.coin_list = arcade.SpriteList()

        # Враги
        self.enemy_list = arcade.SpriteList()
        left_edge = 400
        right_edge = int(self.tile_map.width * self.tile_map.tile_width * 0.5)

        if self.level_index == 0:
            enemy_type = "bee"
            spacing = 300
        elif self.level_index == 1:
            enemy_type = "slime"
            spacing = 250
        else:  # уровень 2
            enemy_type = "worm"
            spacing = 200

        for x in range(left_edge, right_edge, spacing):
            enemy = Enemy(x, 600, enemy_type=enemy_type)
            self.enemy_list.append(enemy)
        for x in range(left_edge, right_edge, spacing):
            enemy = Enemy(x, 300, enemy_type=enemy_type)
            self.enemy_list.append(enemy)
        # Физика
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.scene["Platforms"]
        )

        # Камера
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.camera.zoom = 1

        # Обновляем текст
        self.score_text.text = f"Score: {self.score}"
        self.level_name_text.text = level_name

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.enemy_list.draw()
        self.player_spritelist.draw()
        self.projectile_list.draw()
        self.gui_camera.use()

        self.score_text.draw()
        self.level_name_text.draw()

        # Полоса здоровья
        health_width = 200
        current_health_width = (self.health / self.max_health) * health_width
        bar_height = 20
        x = 10
        y = self.window.height - 60
        arcade.draw_lrbt_rectangle_filled(x, x + health_width, y, y + bar_height, arcade.color.RED)
        arcade.draw_lrbt_rectangle_filled(x, x + current_health_width, y, y + bar_height, arcade.color.GREEN)
        arcade.draw_lrbt_rectangle_outline(x, x + health_width, y, y + bar_height, arcade.color.BLACK, 2)
        arcade.draw_text(f"Здоровье: {self.health}", x, y - 30, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.enemy_list.update()
        self.projectile_list.update()
        for projectile in self.projectile_list:
            hit_list = arcade.check_for_collision_with_list(projectile, self.enemy_list)
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                projectile.remove_from_sprite_lists()
                self.score += 2
                self.collect_coin_sound.play(volume=0.3)
        self.update_player_animation()

        # Сбор монет
        coins = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins:
            coin.remove_from_sprite_lists()
            self.score += 1
            self.collect_coin_sound.play(volume=0.3)

        if len(self.coin_list) == 0:
            if self.level_index < len(LEVELS) - 1:
                next_view = GameView()
                next_view.setup(level_index=self.level_index + 1, score=self.score)
                self.window.show_view(next_view)
            else:
                win_view = WinView(final_score=self.score)
                self.window.show_view(win_view)

        # Столкновение с врагами
        enemies = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for enemy in enemies:
            self.health -= 1
            self.hit_enemy_sound.play(volume=0.2)
            if self.health <= 0:
                self.window.show_view(GameOverView())
                return

        self.score_text.text = f"Score: {self.score}"

        # Камера
        target_x = self.player.center_x
        target_y = self.player.center_y
        current_x, current_y = self.camera.position
        smoothed_x = current_x * 0.9 + target_x * 0.1
        smoothed_y = current_y * 0.9 + target_y * 0.1
        self.camera.position = (smoothed_x, smoothed_y)
        if self.player.center_y < -100:
            self.window.show_view(GameOverView())
            return

        self.score_text.text = f"Score: {self.score}"

    def update_player_animation(self):
        if not self.physics_engine.can_jump():
            self.player.texture = self.jump_texture
            self.player.scale_x = -0.5 if self.player.change_x < 0 else 0.5
        elif abs(self.player.change_x) > 0.1:
            self.walk_frame += self.walk_speed
            if self.walk_frame >= len(self.walk_textures):
                self.walk_frame = 0
            self.player.texture = self.walk_textures[int(self.walk_frame)]
            self.player.scale_x = -0.5 if self.player.change_x < 0 else 0.5
        else:
            self.player.texture = self.idle_texture

    def attack(self):
        direction = 1 if self.player.scale_x > 0 else -1
        offset_x = 40 if direction == 1 else -40
        projectile = Projectile(self.player.center_x + offset_x, self.player.center_y, direction)
        self.projectile_list.append(projectile)
        self.shoot_sound.play(volume=0.5)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP and self.physics_engine.can_jump():
            self.player.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.F:  # Стрельба
            self.attack()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player.change_x = 0
        if key == arcade.key.UP:
            self.player.change_y = 0


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
