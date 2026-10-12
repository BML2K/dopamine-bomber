import random
import pygame as pg
from clases.Entities.entities import Entidad, obtener_baldosas_solidas, es_posicion_valida


class Enemigo(Entidad):
    def __init__(self, x, y, tile_size, sprites=None, imagen_fallback=None):
        super().__init__(x, y, tile_size, imagen_fallback)
        self.sprites = sprites or {}
        self.speed = 1.0
        self.direccion = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])

        # Animación de patrullaje
        self.anim_frame = 0
        self.anim_timer = 0

        # Muerte y recompensa
        self.muriendo = False
        self.frame_muerte = 0
        self.contador_muerte = 0
        self.muerte_terminada = False
        self.puntos = 200

    def recibir_dano(self, snd_morir=None):
        if not self.muriendo and self.is_alive:
            self.muriendo = True
            self.frame_muerte = 0
            self.contador_muerte = 0
            if snd_morir:
                try:
                    snd_morir.play()
                except Exception:
                    pass

    def actualizar(self, nivel_actual):
        if not self.is_alive:
            return

        # Animación de muerte
        if self.muriendo:
            self.contador_muerte += 1
            if self.contador_muerte >= 6:
                self.contador_muerte = 0
                self.frame_muerte += 1
                if self.frame_muerte >= 5:
                    self.is_alive = False
                    self.muerte_terminada = True
            return

        # Animación de flotar/caminar
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 3

        # Movimiento en cuadrícula
        dx = self.direccion[0] * self.speed
        dy = self.direccion[1] * self.speed

        test_rect = self.get_rect_at(self.x + dx, self.y + dy)
        solidas = obtener_baldosas_solidas(test_rect, nivel_actual, self.tile_size)

        if not solidas:
            self.x += dx
            self.y += dy

            aligned_x = round(self.x / self.tile_size) * self.tile_size
            aligned_y = round(self.y / self.tile_size) * self.tile_size

            # En intersecciones, evaluar posibles cambios de dirección
            if (
                abs(self.x - aligned_x) < self.speed
                and abs(self.y - aligned_y) < self.speed
            ):
                direcciones_posibles = []
                for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    rect_d = self.get_rect_at(
                        aligned_x + d[0] * self.speed, aligned_y + d[1] * self.speed
                    )
                    if es_posicion_valida(rect_d, nivel_actual, self.tile_size):
                        direcciones_posibles.append(d)

                if direcciones_posibles:
                    opciones_sin_inversa = [
                        d
                        for d in direcciones_posibles
                        if d != (-self.direccion[0], -self.direccion[1])
                    ]
                    if opciones_sin_inversa and random.random() < 0.25:
                        self.direccion = random.choice(opciones_sin_inversa)
        else:
            # Ajustar posición exactamente contra la pared
            if dx > 0:
                min_col = min(c for c, r in solidas)
                self.x = float(min_col * self.tile_size - self.offset - self.width)
            elif dx < 0:
                max_col = max(c for c, r in solidas)
                self.x = float((max_col + 1) * self.tile_size - self.offset)

            if dy > 0:
                min_row = min(r for c, r in solidas)
                self.y = float(min_row * self.tile_size - self.offset - self.height)
            elif dy < 0:
                max_row = max(r for c, r in solidas)
                self.y = float((max_row + 1) * self.tile_size - self.offset)

            # Buscar nueva dirección válida
            direcciones_validas = []
            for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                rect_d = self.get_rect_at(
                    self.x + d[0] * self.speed, self.y + d[1] * self.speed
                )
                if es_posicion_valida(rect_d, nivel_actual, self.tile_size):
                    direcciones_validas.append(d)

            if direcciones_validas:
                self.direccion = random.choice(direcciones_validas)
            else:
                self.direccion = (-self.direccion[0], -self.direccion[1])

    def dibujar(self, screen, hud_height):
        if not self.is_alive and not self.muriendo:
            return

        px = round(self.x)
        py = round(hud_height + self.y)

        if self.muriendo:
            frames_muerte = self.sprites.get("muere", [])
            idx = min(self.frame_muerte, len(frames_muerte) - 1)
            if frames_muerte:
                screen.blit(frames_muerte[idx], (px, py))
            return

        dir_key = "izquierda" if self.direccion[0] < 0 else "derecha"
        frames_dir = self.sprites.get(dir_key, [])
        if frames_dir:
            img = frames_dir[self.anim_frame % len(frames_dir)]
            screen.blit(img, (px, py))
        elif self.image:
            screen.blit(self.image, (px, py))