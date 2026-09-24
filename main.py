import pygame as pg
import sys

#INIT
pg.init()

#SCREEN SETTINGS
WIDTH = 1200
HEIGHT = 720
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

TAMANO_BLOQUE = 48

# Cargar imágenes (ajusta los nombres de tus archivos reales)
img_muro = pg.image.load("imagenes/muro_duro.png").convert()
img_muro = pg.transform.scale(img_muro, (TAMANO_BLOQUE, TAMANO_BLOQUE))

img_caja = pg.image.load("imagenes/muro_suave.png").convert()
img_caja = pg.transform.scale(img_caja, (TAMANO_BLOQUE, TAMANO_BLOQUE))

img_cesped = pg.image.load("imagenes/cesped.png").convert()
img_cesped = pg.transform.scale(img_cesped, (TAMANO_BLOQUE, TAMANO_BLOQUE))

# Cargamos el nivel 1 de ejemplo
nivel_actual = cargar_nivel("Levels/L93.txt")



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
    screen.fill((0,0,0))
    # Renderizar el mapa fila por fila, columna por columna
    for fila_idx, fila in enumerate(nivel_actual):
        for col_idx, caracter in enumerate(fila):
            x = col_idx * TAMANO_BLOQUE
            y = fila_idx * TAMANO_BLOQUE

            # Dibujar el suelo de fondo por defecto
            screen.blit(img_cesped, (x, y))

            # Dibujar elementos según el símbolo del archivo txt
            if caracter == '*':
                screen.blit(img_muro, (x, y))
            elif caracter == '-':
                screen.blit(img_caja, (x, y))
            elif caracter in ['1', '2', '3', '4']:
                # Aquí puedes ubicar las posiciones iniciales de los jugadores
                pass
            elif caracter == '5':
                # Aquí puedes ubicar los enemigos o salidas
                pass

    #screen update
    pg.display.flip()

    #clock FPS
    clock.tick(FPS)

#kil game
pg.quit()
sys.exit()

