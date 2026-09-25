import pygame as pg
import sys

#INIT
pg.init()

#SCREEN SETTINGS
WIDTH = 720
HUD_HEIGHT = 60
HEIGHT = 624 + HUD_HEIGHT
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("DOPAMINE BOMBER")

def cargar_nivel(ruta):
    matriz = []
    with open(ruta, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.rstrip('\n')
            if linea.startswith('*'):
                matriz.append(list(linea))
    return matriz

TILE_SIZE = 48
HUD_FONT = pg.font.Font("fuentes/pixeled.ttf", 22)
HUD_FONT.set_bold(True)

#variables juego
vidas = 3
tiempo_restante = 100
puntaje = 100

# Cargar imágenes (ajusta los nombres de tus archivos reales)
img_muro = pg.image.load("imagenes/muro_duro.png").convert()
img_muro = pg.transform.scale(img_muro, (TILE_SIZE, TILE_SIZE))

img_caja = pg.image.load("imagenes/muro_suave.png").convert()
img_caja = pg.transform.scale(img_caja, (TILE_SIZE, TILE_SIZE))

img_cesped = pg.image.load("imagenes/cesped.png").convert()
img_cesped = pg.transform.scale(img_cesped, (TILE_SIZE, TILE_SIZE))

img_jugador = pg.image.load("imagenes/player_abajo_1.png").convert()
img_jugador = pg.transform.scale(img_jugador, (TILE_SIZE, TILE_SIZE))

img_enemigo = pg.image.load("imagenes/globo_derec_0.png").convert()
img_enemigo = pg.transform.scale(img_enemigo, (TILE_SIZE, TILE_SIZE))

img_salida = pg.image.load("imagenes/losa_puerta.png").convert()
img_salida = pg.transform.scale(img_salida, (TILE_SIZE, TILE_SIZE))

# Cargamos el nivel 1 de ejemplo
nivel_actual = cargar_nivel("Levels/L01.txt")



#CLOCK
clock = pg.time.Clock()
FPS = 60

#game loop
running = True
while running:
    #events manage
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    #game logic


    #draw and render screen
    screen.fill((255,0,0))

    #textos hud
    hud_rect = pg.Rect(0, 0, WIDTH, HUD_HEIGHT)
    pg.draw.rect(screen, (40, 40, 45), hud_rect)
    pg.draw.line(screen, (200, 200, 200), (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

    txt_vidas = HUD_FONT.render(f"VIDAS: {vidas}", True, (255, 255, 255))
    txt_tiempo = HUD_FONT.render(f"TIEMPO: {tiempo_restante}", True, (255, 255, 255))
    txt_puntos = HUD_FONT.render(f"PTS: {puntaje}", True, (255, 255, 255))

    rect_vidas = txt_vidas.get_rect(midleft=(20, HUD_HEIGHT // 2))
    rect_tiempo = txt_tiempo.get_rect(center=(WIDTH // 2, HUD_HEIGHT // 2))
    rect_puntos = txt_puntos.get_rect(midright=(WIDTH - 20, HUD_HEIGHT // 2))


    screen.blit(txt_vidas, rect_vidas)
    screen.blit(txt_tiempo, rect_tiempo)
    screen.blit(txt_puntos, rect_puntos)

    # Renderizar el mapa fila por fila, columna por columna
    for fila_idx, fila in enumerate(nivel_actual):
        for col_idx, caracter in enumerate(fila):
            x = col_idx * TILE_SIZE
            y = HUD_HEIGHT + (fila_idx * TILE_SIZE)

            # Dibujar el suelo de fondo por defecto
            screen.blit(img_cesped, (x, y))

            # Dibujar elementos según el símbolo del archivo txt
            if caracter == '*':
                screen.blit(img_muro, (x, y))
            elif caracter == '-':
                screen.blit(img_caja, (x, y))
            elif caracter == '1':
                #posicion inicial de los jugador
                screen.blit(img_jugador, (x,y))
            elif caracter in ['2', '3', '4']:
                screen.blit(img_enemigo, (x,y))
            elif caracter == '5':
                #salidas
                screen.blit(img_salida, (x,y))

    #screen update
    pg.display.flip()

    #clock FPS
    clock.tick(FPS)

#kil game
pg.quit()
sys.exit()

