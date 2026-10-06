import random
import pygame as pg
from clases.Entities.bomba import Bomba


def obtener_baldosas_solidas(rect, nivel_actual, tile_size):
    """Retorna una lista de (col, row) para baldosas sólidas que colisionan con rect."""
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
            
            tipo_tile = nivel_actual[r][c]
            
            if tipo_tile in ["*", "-"]:
                # Muros indestructibles o destructibles siempre son sólidos
                solidas.append((c, r))
            elif tipo_tile == "B":
                # REGLA DE LA BOMBA: Solo es sólida si el rectángulo del jugador 
                # ya salió completamente de la casilla de la bomba.
                tile_rect = pg.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
                
                # Si el jugador YA NO está colisionando con el tile de la bomba, ahora sí lo bloquea
                if not rect.colliderect(tile_rect):
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







