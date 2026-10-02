import pygame as pg


class Entidad:

  def __init__(self, x, y, tile_size, imagen):
    self.x = x
    self.y = y
    self.tile_size = tile_size
    self.image = imagen
    self.is_alive = True

  def dibujar(self, screen, hud_height):
    if self.is_alive:
      # Calculamos la posición en pantalla sumando el HUD
      screen.blit(
          self.image,
          (self.x * self.tile_size, hud_height + (self.y * self.tile_size)),
      )


class Jugador(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)
    self.vidas = 3
    self.puntaje = 100

  def actualizar(self):
    # Lógica de movimiento del jugador por teclado irá aquí
    teclas = pg.key.get_pressed()
  


class Enemigo(Entidad):

  def __init__(self, x, y, tile_size, imagen):
    super().__init__(x, y, tile_size, imagen)

  def actualizar(self):
    # Lógica de movimiento de la IA del enemigo irá aquí
    pass