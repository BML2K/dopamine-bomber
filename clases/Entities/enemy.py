import pygame as pg
from clases.Entities.entites import *


class Enemigo(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)
    self.speed = 0.8
    self.direccion = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])

  def recibir_dano(self):
        self.is_alive = False

  def actualizar(self, nivel_actual):
    if not self.is_alive:
      return

    dx = self.direccion[0] * self.speed
    dy = self.direccion[1] * self.speed

    test_rect = self.get_rect_at(self.x + dx, self.y + dy)
    solidas = obtener_baldosas_solidas(
        test_rect, nivel_actual, self.tile_size
    )

    if not solidas:
      self.x += dx
      self.y += dy

      aligned_x = round(self.x / self.tile_size) * self.tile_size
      aligned_y = round(self.y / self.tile_size) * self.tile_size
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
          if opciones_sin_inversa and random.random() < 0.2:
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

      # Buscar nueva dirección válida desde la posición ajustada
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