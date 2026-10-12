import pygame as pg


class Bomba:
    def __init__(self, col, row, rango=2, tiempo_vida=140):
        self.col = col
        self.row = row
        self.rango = rango
        self.tiempo_vida = tiempo_vida  # Fotogramas restantes antes de detonar
        self.activa = True

    def actualizar(self):
        if self.activa:
            self.tiempo_vida -= 1
            if self.tiempo_vida <= 0:
                self.activa = False

    def dibujar(self, screen, hud_height, tile_size, frames_bomba):
        if self.activa and frames_bomba:
            # Latido más rápido cuando está a punto de explotar
            velocidad = 5 if self.tiempo_vida < 40 else 10
            frame_idx = (self.tiempo_vida // velocidad) % len(frames_bomba)
            img = frames_bomba[frame_idx]
            screen.blit(img, (self.col * tile_size, hud_height + self.row * tile_size))


def explotar_bomba(bomba, nivel_actual, lista_bombas_activas, snd_boom=None):
    """
    Realiza la explosión propagando fuego en 4 direcciones.
    Retorna (casillas_fuego, muros_destruidos)
    donde casillas_fuego son dicts con 'col', 'row', 'tipo' y 'duracion'.
    """
    if snd_boom:
        try:
            snd_boom.play()
        except Exception:
            pass

    bx, by = bomba.col, bomba.row
    rango = bomba.rango
    casillas_fuego = [{"col": bx, "row": by, "tipo": "centr", "duracion": 28}]
    muros_destruidos = []

    # Limpiamos la casilla de la bomba en la matriz
    if nivel_actual[by][bx] == "B":
        nivel_actual[by][bx] = " "

    direcciones = [
        ("abajo", 0, 1),
        ("arrib", 0, -1),
        ("derec", 1, 0),
        ("izqui", -1, 0),
    ]

    for d_nombre, dx, dy in direcciones:
        for i in range(1, rango + 1):
            nx, ny = bx + (dx * i), by + (dy * i)

            # Verificar límites
            if ny < 0 or ny >= len(nivel_actual) or nx < 0 or nx >= len(nivel_actual[ny]):
                break

            celda = nivel_actual[ny][nx]

            if celda == "*":
                # Muro indestructible detiene el fuego por completo
                break

            elif celda == "-":
                # Muro destructible: el fuego lo alcanza y lo quema
                tipo_fuego = f"{d_nombre}_{2 if i == rango else 1}"
                casillas_fuego.append({"col": nx, "row": ny, "tipo": tipo_fuego, "duracion": 28})
                nivel_actual[ny][nx] = "D"  # Estado de destrucción
                muros_destruidos.append((nx, ny))
                break

            elif celda == "B":
                # Reacción en cadena con otra bomba
                for otra in lista_bombas_activas:
                    if otra.col == nx and otra.row == ny and otra.activa:
                        otra.tiempo_vida = 0
                tipo_fuego = f"{d_nombre}_{2 if i == rango else 1}"
                casillas_fuego.append({"col": nx, "row": ny, "tipo": tipo_fuego, "duracion": 28})
                break

            else:
                # Espacio libre o salida
                es_punta = (i == rango)
                tipo_fuego = f"{d_nombre}_{2 if es_punta else 1}"
                casillas_fuego.append({"col": nx, "row": ny, "tipo": tipo_fuego, "duracion": 28})

    return casillas_fuego, muros_destruidos