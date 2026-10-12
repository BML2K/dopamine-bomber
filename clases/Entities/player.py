import pygame as pg
from clases.Entities.entities import Entidad, obtener_baldosas_solidas, es_posicion_valida
from clases.Entities.bomba import Bomba


class Jugador(Entidad):
    def __init__(self, x, y, tile_size, sprites=None, imagen_fallback=None):
        super().__init__(x, y, tile_size, imagen_fallback)
        self.sprites = sprites or {}
        self.vidas = 3
        self.puntaje = 0
        self.speed = 3.0

        # Invulnerabilidad tras reaparecer o ser golpeado
        self.invulnerable = False
        self.tiempo_invulnerable = 0

        # Animación de movimiento
        self.direccion = "abajo"
        self.moviendose = False
        self.frame_caminar = 0
        self.contador_anim = 0

        # Estado de muerte y animación
        self.muriendo = False
        self.muerte_terminada = False
        self.frame_muerte = 0
        self.contador_muerte = 0

        # Atributos de bombas y habilidades especiales
        self.max_bombas = 1
        self.rango_bombas = 2
        self.bombas_activas = []
        self.atravesar_muros = False

    def recibir_dano(self):
        if not self.invulnerable and self.is_alive and not self.muriendo:
            self.muriendo = True
            self.frame_muerte = 0
            self.contador_muerte = 0
            self.moviendose = False

    def actualizar_muerte(self):
        """Avanza la animación de muerte del jugador."""
        self.contador_muerte += 1
        if self.contador_muerte >= 6:
            self.contador_muerte = 0
            self.frame_muerte += 1
            if self.frame_muerte >= 8:
                self.vidas -= 1
                self.muriendo = False
                self.muerte_terminada = True
                if self.vidas <= 0:
                    self.is_alive = False

    def respawn(self):
        """Reinicia la posición del jugador conservando sus vidas restantes."""
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.is_alive = True
        self.muriendo = False
        self.muerte_terminada = False
        self.frame_muerte = 0
        self.direccion = "abajo"
        self.moviendose = False
        self.invulnerable = True
        self.tiempo_invulnerable = 120  # 2 segundos a 60 FPS

    def poner_bomba(self, nivel_actual, lista_global_bombas, snd_poner_bomba=None):
        if self.muriendo or not self.is_alive:
            return

        # 1. Limpiar bombas inactivas de su lista interna
        self.bombas_activas = [b for b in self.bombas_activas if b.activa]

        if len(self.bombas_activas) >= self.max_bombas:
            return

        # 2. Grid Snap basado en el centro del jugador
        centro_x = self.x + self.width / 2
        centro_y = self.y + self.height / 2
        col = int(centro_x // self.tile_size)
        row = int(centro_y // self.tile_size)

        # 3. Colocar si la celda es transitable y no tiene ya una bomba
        if 0 <= row < len(nivel_actual) and 0 <= col < len(nivel_actual[row]):
            celda = nivel_actual[row][col]
            if celda in [" ", "5"]:  # Espacio libre o sobre la puerta
                nivel_actual[row][col] = "B"
                nueva_bomba = Bomba(col, row, self.rango_bombas)
                self.bombas_activas.append(nueva_bomba)
                lista_global_bombas.append(nueva_bomba)

                if snd_poner_bomba:
                    try:
                        snd_poner_bomba.play()
                    except Exception:
                        pass

    def mover(self, dx, dy, nivel_actual):
        if dx == 0 and dy == 0:
            return

        slide_margin = 16

        # Asistencia de deslizamiento en esquinas (corner sliding)
        if dx != 0 and dy == 0:
            aligned_y = round(self.y / self.tile_size) * self.tile_size
            diff_y = aligned_y - self.y
            if 0 < abs(diff_y) <= slide_margin:
                test_rect = self.get_rect_at(self.x + dx, aligned_y)
                if es_posicion_valida(test_rect, nivel_actual, self.tile_size, self.atravesar_muros):
                    step_y = self.speed if diff_y > 0 else -self.speed
                    if abs(diff_y) < abs(step_y):
                        self.y = float(aligned_y)
                    else:
                        self.y += step_y

        elif dy != 0 and dx == 0:
            aligned_x = round(self.x / self.tile_size) * self.tile_size
            diff_x = aligned_x - self.x
            if 0 < abs(diff_x) <= slide_margin:
                test_rect = self.get_rect_at(aligned_x, self.y + dy)
                if es_posicion_valida(test_rect, nivel_actual, self.tile_size, self.atravesar_muros):
                    step_x = self.speed if diff_x > 0 else -self.speed
                    if abs(diff_x) < abs(step_x):
                        self.x = float(aligned_x)
                    else:
                        self.x += step_x

        # Movimiento en eje X con colisión
        if dx != 0:
            test_rect_x = self.get_rect_at(self.x + dx, self.y)
            solidas_x = obtener_baldosas_solidas(
                test_rect_x, nivel_actual, self.tile_size, self.atravesar_muros
            )
            if not solidas_x:
                self.x += dx
            else:
                if dx > 0:
                    min_col = min(c for c, r in solidas_x)
                    self.x = float(min_col * self.tile_size - self.offset - self.width)
                else:
                    max_col = max(c for c, r in solidas_x)
                    self.x = float((max_col + 1) * self.tile_size - self.offset)

        # Movimiento en eje Y con colisión
        if dy != 0:
            test_rect_y = self.get_rect_at(self.x, self.y + dy)
            solidas_y = obtener_baldosas_solidas(
                test_rect_y, nivel_actual, self.tile_size, self.atravesar_muros
            )
            if not solidas_y:
                self.y += dy
            else:
                if dy > 0:
                    min_row = min(r for c, r in solidas_y)
                    self.y = float(min_row * self.tile_size - self.offset - self.height)
                else:
                    max_row = max(r for c, r in solidas_y)
                    self.y = float((max_row + 1) * self.tile_size - self.offset)

    def actualizar(self, nivel_actual):
        if not self.is_alive:
            return

        if self.muriendo:
            self.actualizar_muerte()
            return

        if self.invulnerable:
            self.tiempo_invulnerable -= 1
            if self.tiempo_invulnerable <= 0:
                self.invulnerable = False

        teclas = pg.key.get_pressed()
        dx = 0
        dy = 0

        if teclas[pg.K_LEFT] or teclas[pg.K_a]:
            dx -= self.speed
            self.direccion = "izquierda"
        elif teclas[pg.K_RIGHT] or teclas[pg.K_d]:
            dx += self.speed
            self.direccion = "derecha"
        elif teclas[pg.K_UP] or teclas[pg.K_w]:
            dy -= self.speed
            self.direccion = "arriba"
        elif teclas[pg.K_DOWN] or teclas[pg.K_s]:
            dy += self.speed
            self.direccion = "abajo"

        self.moviendose = (dx != 0 or dy != 0)

        # Animación de pasos al caminar
        if self.moviendose:
            self.contador_anim += 1
            if self.contador_anim >= 6:
                self.contador_anim = 0
                self.frame_caminar = (self.frame_caminar + 1) % 4
        else:
            self.contador_anim = 0
            self.frame_caminar = 1  # Pose neutra

        self.mover(dx, dy, nivel_actual)

    def dibujar(self, screen, hud_height):
        if not self.is_alive and not self.muriendo:
            return

        # Parpadeo durante invulnerabilidad
        if self.invulnerable and (self.tiempo_invulnerable // 5) % 2 == 0:
            return

        px = round(self.x)
        py = round(hud_height + self.y)

        if self.muriendo:
            frames_muerte = self.sprites.get("muere", [])
            idx = min(self.frame_muerte, len(frames_muerte) - 1)
            if frames_muerte:
                screen.blit(frames_muerte[idx], (px, py))
            return

        # Animación direccional
        secuencia = [0, 1, 2, 1]
        frame_idx = secuencia[self.frame_caminar % 4]
        frames_dir = self.sprites.get(self.direccion, [])
        if frames_dir:
            img = frames_dir[frame_idx % len(frames_dir)]
            screen.blit(img, (px, py))
        elif self.image:
            screen.blit(self.image, (px, py))