import sys
import pygame as pg
from clases.Entities.entites import *


class Game:

  def __init__(self):
    pg.init()
    self.width = 720
    self.hud_height = 60
    self.height = 624 + self.hud_height
    self.screen = pg.display.set_mode((self.width, self.height))
    pg.display.set_caption("DOPAMINE BOMBER")

    self.clock = pg.time.Clock()
    self.fps = 60
    self.tile_size = 48

    self.hud_font = pg.font.Font("fuentes/pixeled.ttf", 22)
    self.hud_font.set_bold(True)

    self.tiempo_restante = 100

    # Cargar recursos gráficos
    self.cargar_recursos()

    # Cargar nivel y entidades
    self.nivel_actual = []
    self.jugadores = []
    self.enemigos = []
    self.cargar_nivel("Levels/L01.txt")

  def cargar_recursos(self):
    # Imágenes del mapa
    self.img_muro = pg.transform.scale(
        pg.image.load("imagenes/muro_duro.png").convert(),
        (self.tile_size, self.tile_size),
    )
    self.img_caja = pg.transform.scale(
        pg.image.load("imagenes/muro_suave.png").convert(),
        (self.tile_size, self.tile_size),
    )
    self.img_cesped = pg.transform.scale(
        pg.image.load("imagenes/cesped.png").convert(),
        (self.tile_size, self.tile_size),
    )
    self.img_salida = pg.transform.scale(
        pg.image.load("imagenes/losa_puerta.png").convert(),
        (self.tile_size, self.tile_size),
    )

    # Imágenes de entidades
    self.img_jugador = pg.transform.scale(
        pg.image.load("imagenes/player_abajo_1.png").convert(),
        (self.tile_size, self.tile_size),
    )
    self.img_enemigo = pg.transform.scale(
        pg.image.load("imagenes/globo_derec_0.png").convert(),
        (self.tile_size, self.tile_size),
    )

  def cargar_nivel(self, ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
      for fila_idx, linea in enumerate(archivo):
        linea = linea.rstrip("\n")
        if linea.startswith("*"):
          fila_lista = list(linea)
          self.nivel_actual.append(fila_lista)

          # Detectar entidades dinámicas basadas en los caracteres del mapa
          for col_idx, caracter in enumerate(fila_lista):
            if caracter == "1":
              self.jugadores.append(
                  Jugador(col_idx, fila_idx, self.tile_size, self.img_jugador)
              )
              fila_lista[
                  col_idx
              ] = " "  # Limpiamos la matriz para que quede césped debajo
            elif caracter in ["2", "3", "4"]:
              self.enemigos.append(
                  Enemigo(col_idx, fila_idx, self.tile_size, self.img_enemigo)
              )
              fila_lista[col_idx] = " "
            elif caracter == "5":
              pass  # La salida se queda en la matriz

  def ejecutar(self):
    running = True
    while running:
      # 1. Eventos
      for event in pg.event.get():
        if event.type == pg.QUIT:
          running = False

      # 2. Lógica del juego
      for j in self.jugadores:
        j.actualizar()
      for e in self.enemigos:
        e.actualizar()

      # 3. Dibujado
      self.screen.fill((255, 0, 0))
      self.dibujar_hud()
      self.dibujar_mapa()

      # Dibujar entidades dinámicas
      for j in self.jugadores:
        j.dibujar(self.screen, self.hud_height)
      for e in self.enemigos:
        e.dibujar(self.screen, self.hud_height)

      pg.display.flip()
      self.clock.tick(self.fps)

    pg.quit()
    sys.exit()

  def dibujar_hud(self):
    hud_rect = pg.Rect(0, 0, self.width, self.hud_height)
    pg.draw.rect(self.screen, (40, 40, 45), hud_rect)
    pg.draw.line(
        self.screen,
        (200, 200, 200),
        (0, self.hud_height),
        (self.width, self.hud_height),
        2,
    )

    # Tomamos los datos del primer jugador como referencia para el HUD
    vidas = self.jugadores[0].vidas if self.jugadores else 0
    puntaje = self.jugadores[0].puntaje if self.jugadores else 0

    txt_vidas = self.hud_font.render(f"VIDAS: {vidas}", True, (255, 255, 255))
    txt_tiempo = self.hud_font.render(
        f"TIEMPO: {self.tiempo_restante}", True, (255, 255, 255)
    )
    txt_puntos = self.hud_font.render(f"PTS: {puntaje}", True, (255, 255, 255))

    rect_vidas = txt_vidas.get_rect(midleft=(20, self.hud_height // 2))
    rect_tiempo = txt_tiempo.get_rect(
        center=(self.width // 2, self.hud_height // 2)
    )
    rect_puntos = txt_puntos.get_rect(
        midright=(self.width - 20, self.hud_height // 2)
    )

    self.screen.blit(txt_vidas, rect_vidas)
    self.screen.blit(txt_tiempo, rect_tiempo)
    self.screen.blit(txt_puntos, rect_puntos)

  def dibujar_mapa(self):
    for fila_idx, fila in enumerate(self.nivel_actual):
      for col_idx, caracter in enumerate(fila):
        x = col_idx * self.tile_size
        y = self.hud_height + (fila_idx * self.tile_size)

        # Suelo por defecto
        self.screen.blit(img_cesped if "img_cesped" in locals() else self.img_cesped, (x, y)) # type: ignore

        if caracter == "*":
          self.screen.blit(self.img_muro, (x, y))
        elif caracter == "-":
          self.screen.blit(self.img_caja, (x, y))
        elif caracter == "5":
          self.screen.blit(self.img_salida, (x, y))