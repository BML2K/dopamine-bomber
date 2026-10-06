import pygame as pg
from clases.Entities.bomba import Bomba
from clases.Entities.entites import *

class Jugador(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)
    self.vidas = 3
    self.puntaje = 100
    self.speed = 3.0
    self.invulnerable = False
    self.tiempo_invulnerable = 0


    # atributos para las bombas
    self.max_bombas = 1
    self.rango_bombas = 2
    self.bombas_activas = []

  def recibir_dano(self):
    if not self.invulnerable and self.is_alive:
      self.vidas -= 1
      if self.vidas <= 0:
        self.is_alive = False
        #self.morir()
        self.dibujar_game_over()
      else:
        self.invulnerable = True
        self.tiempo_invulnerable = 120  # 2 segundos a 60 fps

  # def morir(self):
  #     self.dibujar_game_over()



  def poner_bomba(self, nivel_actual, lista_global_bombas):
    # 1. Verificar si ya alcanzó su límite máximo de bombas simultáneas
    # Limpiamos primero las que ya no estén activas de su lista interna
    self.bombas_activas = [b for b in self.bombas_activas if b.activa]
    
    if len(self.bombas_activas) >= self.max_bombas:
      return

    # 2. Calcular la celda exacta (Grid Snap) basada en el centro del jugador
    centro_x = self.x + self.width / 2
    centro_y = self.y + self.height / 2
          
    col = int(centro_x // self.tile_size)
    row = int(centro_y // self.tile_size)

    # 3. Verificar que la celda esté dentro de los límites y esté vacía
    if 0 <= row < len(nivel_actual) and 0 <= col < len(nivel_actual[row]):
      if nivel_actual[row][col] == " ": # Asumiendo que " " es espacio vacío
          # Marcar la celda en la matriz para que actúe como obstáculo sólido opcional (o "B")
            nivel_actual[row][col] = "B"
                  
          # Crear la bomba
            nueva_bomba = Bomba(col, row, self.rango_bombas)
            self.bombas_activas.append(nueva_bomba)
            lista_global_bombas.append(nueva_bomba)

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
        if es_posicion_valida(test_rect, nivel_actual, self.tile_size):
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
        if es_posicion_valida(test_rect, nivel_actual, self.tile_size):
          step_x = self.speed if diff_x > 0 else -self.speed
          if abs(diff_x) < abs(step_x):
            self.x = float(aligned_x)
          else:
            self.x += step_x

    # Movimiento en eje X con colisión exacta
    if dx != 0:
      test_rect_x = self.get_rect_at(self.x + dx, self.y)
      solidas_x = obtener_baldosas_solidas(
          test_rect_x, nivel_actual, self.tile_size
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

    # Movimiento en eje Y con colisión exacta
    if dy != 0:
      test_rect_y = self.get_rect_at(self.x, self.y + dy)
      solidas_y = obtener_baldosas_solidas(
          test_rect_y, nivel_actual, self.tile_size
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

    if self.invulnerable:
      self.tiempo_invulnerable -= 1
      if self.tiempo_invulnerable <= 0:
        self.invulnerable = False

    teclas = pg.key.get_pressed()
    dx = 0
    dy = 0

    if teclas[pg.K_LEFT] or teclas[pg.K_a]:
      dx -= self.speed
    if teclas[pg.K_RIGHT] or teclas[pg.K_d]:
      dx += self.speed
    if teclas[pg.K_UP] or teclas[pg.K_w]:
      dy -= self.speed
    if teclas[pg.K_DOWN] or teclas[pg.K_s]:
      dy += self.speed

    if dx != 0 and dy != 0:
      dy = 0

    self.mover(dx, dy, nivel_actual)

  def dibujar(self, screen, hud_height):
    if self.is_alive:
      if self.invulnerable and (self.tiempo_invulnerable // 6) % 2 == 0:
        return
      super().dibujar(screen, hud_height)