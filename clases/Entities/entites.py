import random
import pygame as pg


def obtener_baldosas_solidas(rect, nivel_actual, tile_size):
  """Retorna una lista de (col, row) para baldosas sólidas (*) o (-) o fuera de mapa que colisionan con rect."""
  solidas = []
  min_col = int(rect.left // tile_size)
  max_col = int((rect.right - 0.001) // tile_size)
  min_row = int(rect.top // tile_size)
  max_row = int((rect.bottom - 0.001) // tile_size)

  filas = len(nivel_actual)
  for r in range(min_row, max_row + 1):
    if r < 0 or r >= filas:
      solidas.append((min_col, r))
      continue
    cols = len(nivel_actual[r])
    for c in range(min_col, max_col + 1):
      if c < 0 or c >= cols:
        solidas.append((c, r))
        continue
      if nivel_actual[r][c] in ["*", "-"]:
        solidas.append((c, r))
  return solidas


def es_posicion_valida(rect, nivel_actual, tile_size):
  """Comprueba si un rectángulo no colisiona con ningún obstáculo."""
  return len(obtener_baldosas_solidas(rect, nivel_actual, tile_size)) == 0


class Entidad:

  def __init__(self, x, y, tile_size, imagen):
    self.tile_size = tile_size
    self.offset = 3
    self.width = tile_size - (self.offset * 2)
    self.height = tile_size - (self.offset * 2)

    # Posición física en píxeles (relativa al área del juego sin HUD)
    self.x = float(x * tile_size)
    self.y = float(y * tile_size)
    self.start_x = self.x
    self.start_y = self.y

    self.image = imagen
    self.is_alive = True
    self.speed = 2.0

  def get_rect(self):
    return pg.Rect(
        self.x + self.offset, self.y + self.offset, self.width, self.height
    )

  def get_rect_at(self, px, py):
    return pg.Rect(px + self.offset, py + self.offset, self.width, self.height)

  def dibujar(self, screen, hud_height):
    if self.is_alive:
      screen.blit(self.image, (round(self.x), round(hud_height + self.y)))


class Jugador(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)
    self.vidas = 3
    self.puntaje = 100
    self.speed = 3.0
    self.invulnerable = False
    self.tiempo_invulnerable = 0

  def recibir_dano(self):
    if not self.invulnerable and self.is_alive:
      self.vidas -= 1
      if self.vidas <= 0:
        self.is_alive = False
      else:
        self.invulnerable = True
        self.tiempo_invulnerable = 120  # 2 segundos a 60 fps
        # Respawn a posición inicial
        self.x = self.start_x
        self.y = self.start_y

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


class Enemigo(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)
    self.speed = 1.5
    self.direccion = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])

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
