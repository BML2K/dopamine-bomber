import sys
import os
import pygame as pg
from clases.Entities.entites import *
from clases.Entities.bomba import *
from clases.Entities.enemy import *
from clases.Entities.player import *


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

    #nivel
    self.nivel_completado = False
    self.posicion_puerta = None # (col, row) donde está la puerta oculta
    self.puerta_revelada = False

    #bombas
    self.imagen_bomba = pg.image.load("imagenes/bomba_1.png").convert_alpha()
    self.imagen_bomba = pg.transform.scale(self.imagen_bomba, (self.tile_size, self.tile_size))
    self.bombas_activas = [] #Lista global de bombas del juego
    self.fuegos_activos = [] # Lista visual para las llamas

    # Cargar recursos gráficos
    self.cargar_recursos()

    # Cargar nivel y entidades
    self.nivel_actual = []
    self.jugadores = []
    self.enemigos = []
    self.cargar_nivel("Levels/L01.txt")

  def cargar_imagen(self, ruta, con_colorkey=False):
    #img = pg.image.load(ruta).convert()
    img = pg.image.load((ruta)).convert()
    if con_colorkey:
      img.set_colorkey(img.get_at((0, 0)))
    return pg.transform.scale(img, (self.tile_size, self.tile_size))


  def cargar_musica(self, ruta):
      self.ruta = ruta
      pg.mixer.music.load(ruta)
      pg.mixer.music.play(-1)
  

  def cargar_recursos(self):
    # Imágenes del mapa
    self.img_muro = self.cargar_imagen("imagenes/muro_duro.png")
    self.img_caja = self.cargar_imagen("imagenes/muro_suave.png")
    self.img_cesped = self.cargar_imagen("imagenes/cesped.png")
    self.img_salida = self.cargar_imagen("imagenes/losa_puerta.png", con_colorkey=True)

    # Imágenes de entidades (eliminación de fondo verde con colorkey)
    self.img_jugador = self.cargar_imagen("imagenes/player_abajo_1.png", con_colorkey=True)
    self.img_enemigo = self.cargar_imagen("imagenes/globo_derec_0.png", con_colorkey=True)

    #musica 
    self.music_theme = self.cargar_musica("sonidos/03_Stage_Theme.wav")

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

  def dibujar_game_over(screen, ancho, alto):
    # Crear una superficie para el fondo oscuro/semi-transparente
    s = pg.Surface((ancho, alto))
    s.set_alpha(128)  # Nivel de transparencia (0-255)
    s.fill((0, 0, 0)) # Color negro
    screen.blit(s, (0, 0))
    
    # Dibujar el rectángulo central de la interfaz de Game Over
    ancho_rect, alto_rect = 400, 200
    x_rect = (ancho - ancho_rect) // 2
    y_rect = (alto - alto_rect) // 2
    pg.draw.rect(screen, (50, 50, 50), (x_rect, y_rect, ancho_rect, alto_rect))
    pg.draw.rect(screen, (255, 255, 255), (x_rect, y_rect, ancho_rect, alto_rect), 3) # Borde blanco 



  def ejecutar(self):
    running = True
    while running:
      # 1. Eventos
      for event in pg.event.get():
        if event.type == pg.QUIT:
          running = False
        elif event.type == pg.KEYDOWN:
          if event.key == pg.K_SPACE:
            # El jugador presiona espacio para poner bomba
              for j in self.jugadores:
                if j.is_alive:
                  j.poner_bomba(self.nivel_actual, self.bombas_activas)


      # 2. Lógica del juego
      for j in self.jugadores:
        j.actualizar(self.nivel_actual)
      for e in self.enemigos:
        e.actualizar(self.nivel_actual)


      # Actualizar bombas activas
      for bomba in self.bombas_activas[:]:
        bomba.actualizar()
        if not bomba.activa:
          # ¡La bomba explota! Llamamos a la función de explosión
          casillas_afectadas = explotar_bomba(bomba, self.nivel_actual, self.bombas_activas)
                    
          for fx, fy in casillas_afectadas:
            self.fuegos_activos.append({"col": fx, "row": fy, "duracion": 30})
                        
            # Daño a jugadores
            for j in self.jugadores:
              if j.get_rect().colliderect(pg.Rect(fx * self.tile_size, self.hud_height + fy * self.tile_size, self.tile_size, self.tile_size)):
                j.recibir_dano()

            # 2. NUEVO: Daño a enemigos por el fuego
            for e in self.enemigos:
              if e.is_alive and e.get_rect().colliderect(pg.Rect(fx * self.tile_size, self.hud_height + fy * self.tile_size, self.tile_size, self.tile_size)):
                e.recibir_dano()
      #self.bombas_activas.remove(bomba)
      self.bombas_activas = [b for b in self.bombas_activas if b.activa]

      # Actualizar duración del fuego visual
      for fuego in self.fuegos_activos[:]:
        fuego["duracion"] -= 1
        if fuego["duracion"] <= 0:
          self.fuegos_activos.remove(fuego) 

      # En la fase de actualización del juego:
      for e in self.enemigos[:]:
         e.actualizar(self.nivel_actual)

      # Eliminar enemigos muertos de la lista global del juego
      self.enemigos = [e for e in self.enemigos if e.is_alive]    

      self.verificar_colisiones()

      # 3. Dibujado
      self.screen.fill((255, 0, 0))
      self.dibujar_hud()
      self.dibujar_mapa()


      # Dibujar bombas y fuego antes de las entidades
      for bomba in self.bombas_activas:
        bomba.dibujar(self.screen, self.hud_height, self.tile_size, self.imagen_bomba) # Asegúrate de tener cargada self.imagen_bomba
            
      for fuego in self.fuegos_activos:
        rect_fuego = pg.Rect(fuego["col"] * self.tile_size, self.hud_height + fuego["row"] * self.tile_size, self.tile_size, self.tile_size)
        pg.draw.rect(self.screen, (255, 100, 0), rect_fuego)


      # Dibujar entidades dinámicas
      for j in self.jugadores:
        j.dibujar(self.screen, self.hud_height)
      for e in self.enemigos:
        e.dibujar(self.screen, self.hud_height)

      pg.display.flip()
      self.clock.tick(self.fps)

    pg.quit()
    sys.exit()

  def verificar_colisiones(self):
    for j in self.jugadores:
      if not j.is_alive:
        continue
      rect_j = j.get_rect()
      for e in self.enemigos:
        if e.is_alive:
          rect_e = e.get_rect()
          if rect_j.colliderect(rect_e):
            j.recibir_dano()

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
        self.screen.blit(self.img_cesped, (x, y))

        if caracter == "*":
          self.screen.blit(self.img_muro, (x, y))
        elif caracter == "-":
          self.screen.blit(self.img_caja, (x, y))
        elif caracter == "5":
          self.screen.blit(self.img_salida, (x, y))