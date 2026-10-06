class Bomba:
    def __init__(self, col, row, rango, tiempo_vida=120): # 180 frames = 3 segundos a 60 FPS
        self.col = col
        self.row = row
        self.rango = rango
        self.tiempo_vida = tiempo_vida  # Cuenta regresiva en fotogramas
        self.activa = True

    def actualizar(self):
        if self.activa:
            self.tiempo_vida -= 1
            if self.tiempo_vida <= 0:
                self.activa = False

    def dibujar(self, screen, hud_height, tile_size, imagen_bomba):
        if self.activa:
            screen.blit(imagen_bomba, (self.col * tile_size, hud_height + self.row * tile_size))


def explotar_bomba(bomba, nivel_actual, lista_bombas_activas):
    """
    Realiza la explosión propagando fuego en 4 direcciones.
    Retorna una lista de casillas (col, row) afectadas por el fuego.
    """
    bx, by = bomba.col, bomba.row
    rango = bomba.rango
    casillas_fuego = [(bx, by)] # El centro de la bomba siempre se quema

    # Si la celda de la bomba era un espacio libre, la limpiamos de la matriz temporalmente
    if nivel_actual[by][bx] == "B":
        nivel_actual[by][bx] = " "

    direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Abajo, Arriba, Derecha, Izquierda

    for dx, dy in direcciones:
        for i in range(1, rango + 1):
            nx, ny = bx + (dx * i), by + (dy * i)

            # Verificar límites del nivel
            if ny < 0 or ny >= len(nivel_actual) or nx < 0 or nx >= len(nivel_actual[ny]):
                break

            celda = nivel_actual[ny][nx]

            if celda == "*":  # Muro indestructible
                break
            elif celda == "-":  # Muro destructible / ladrillo
                casillas_fuego.append((nx, ny))
                nivel_actual[ny][nx] = " " # Destruimos el ladrillo convirtiéndolo en espacio libre
                break
            elif celda == "B":  # Reacción en cadena con otra bomba
                # Buscamos la otra bomba y forzamos su explosión inmediata
                for otra_bomba in lista_bombas_activas:
                    if otra_bomba.col == nx and otra_bomba.row == ny and otra_bomba.activa:
                        otra_bomba.tiempo_vida = 0
                casillas_fuego.append((nx, ny))
                break
            else:
                # Espacio libre u otro elemento transitable
                casillas_fuego.append((nx, ny))

    return casillas_fuego