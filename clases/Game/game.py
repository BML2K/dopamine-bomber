import sys
import os
import json
import random
import pygame as pg
from clases.Entities.entities import Entidad, obtener_baldosas_solidas, es_posicion_valida
from clases.Entities.bomba import Bomba, explotar_bomba
from clases.Entities.enemy import Enemigo
from clases.Entities.player import Jugador


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.width = 720
        self.hud_height = 60
        self.height = 624 + self.hud_height  # 13 filas de 48px + 60px HUD
        self.screen = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("DOPAMINE BOMBER")

        self.clock = pg.time.Clock()
        self.fps = 60
        self.tile_size = 48
        self.nes_colorkey = (56, 135, 0)

        # Tipografía
        self.font_hud = pg.font.Font("fuentes/pixeled.ttf", 12)
        self.font_banner = pg.font.Font("fuentes/pixeled.ttf", 22)
        self.font_sub = pg.font.Font("fuentes/pixeled.ttf", 12)

        # Memoria y persistencia de progreso
        self.archivo_guardado = "progreso.json"
        progreso = self.cargar_progreso()
        self.nivel_numero = progreso.get("nivel_actual", 1)
        self.max_nivel_alcanzado = progreso.get("max_nivel", self.nivel_numero)
        self.mejor_puntaje = progreso.get("mejor_puntaje", 0)
        self.guardado_bombas = progreso.get("max_bombas", 1)
        self.guardado_rango = progreso.get("rango_bombas", 2)
        self.guardado_speed = progreso.get("speed", 3.0)
        self.guardado_atravesar = progreso.get("atravesar_muros", False)

        # Recursos gráficos y sonoros
        self.cargar_recursos()

        # Estado del juego
        # Posibles estados: "INTRO_NIVEL", "JUGANDO", "NIVEL_COMPLETADO", "GAME_OVER", "VICTORIA"
        self.estado = "INTRO_NIVEL"
        self.timer_estado = 0
        self.tiempo_restante = 200
        self.contador_segundos = 0

        # Nivel y entidades
        self.nivel_actual = []
        self.jugadores = []
        self.enemigos = []
        self.bombas_activas = []
        self.fuegos_activos = []
        self.muros_destruccion = []
        self.posicion_puerta = None

        # Elementos interactivos
        self.powerups_ocultos = {}    # {(col, row): tipo}
        self.powerups_revelados = []  # [{"col": c, "row": r, "tipo": tipo}]
        self.puntos_flotantes = []    # [{"x": x, "y": y, "img": img, "duracion": d}]

        # Cargar el nivel guardado en memoria
        self.iniciar_nivel(
            self.nivel_numero,
            max_bombas=self.guardado_bombas,
            rango_bombas=self.guardado_rango,
            speed=self.guardado_speed,
            atravesar_muros=self.guardado_atravesar,
        )

    def cargar_progreso(self):
        """Carga el progreso guardado desde progreso.json si existe."""
        if os.path.exists(self.archivo_guardado):
            try:
                with open(self.archivo_guardado, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    if isinstance(datos, dict):
                        return datos
            except Exception:
                pass
        return {
            "nivel_actual": 1,
            "max_nivel": 1,
            "mejor_puntaje": 0,
            "max_bombas": 1,
            "rango_bombas": 2,
            "speed": 3.0,
            "atravesar_muros": False,
        }

    def guardar_progreso(self):
        """Guarda en disco el último nivel alcanzado, récords y mejoras obtenidas."""
        j = self.jugadores[0] if self.jugadores else None
        puntaje_actual = j.puntaje if j else 0
        self.max_nivel_alcanzado = max(getattr(self, "max_nivel_alcanzado", 1), self.nivel_numero)
        self.mejor_puntaje = max(getattr(self, "mejor_puntaje", 0), puntaje_actual)

        datos = {
            "nivel_actual": self.nivel_numero,
            "max_nivel": self.max_nivel_alcanzado,
            "mejor_puntaje": self.mejor_puntaje,
            "max_bombas": j.max_bombas if j else getattr(self, "guardado_bombas", 1),
            "rango_bombas": j.rango_bombas if j else getattr(self, "guardado_rango", 2),
            "speed": j.speed if j else getattr(self, "guardado_speed", 3.0),
            "atravesar_muros": j.atravesar_muros if j else getattr(self, "guardado_atravesar", False),
        }
        try:
            with open(self.archivo_guardado, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4)
        except Exception as err:
            print(f"Error al guardar progreso: {err}")

    def cargar_imagen(self, ruta, con_colorkey=False):
        img = pg.image.load(ruta).convert()
        if con_colorkey:
            img.set_colorkey(self.nes_colorkey)
        return pg.transform.scale(img, (self.tile_size, self.tile_size))

    def cargar_recursos(self):
        # 1. Tiles del mapa
        self.img_cesped = self.cargar_imagen("imagenes/cesped.png")
        self.img_muro = self.cargar_imagen("imagenes/muro_duro.png")
        self.img_caja = self.cargar_imagen("imagenes/muro_suave.png")
        self.img_salida = self.cargar_imagen("imagenes/losa_puerta.png", con_colorkey=True)

        # 2. Sprites del Jugador
        self.sprites_jugador = {
            "abajo": [
                self.cargar_imagen(f"imagenes/player_abajo_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "arriba": [
                self.cargar_imagen(f"imagenes/player_arrib_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "derecha": [
                self.cargar_imagen(f"imagenes/player_derec_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "izquierda": [
                self.cargar_imagen(f"imagenes/player_izqui_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "muere": [
                self.cargar_imagen(f"imagenes/player_muere_{i}.png", con_colorkey=True)
                for i in range(8)
            ],
        }

        # 3. Sprites del Enemigo (Globo)
        self.sprites_enemigo = {
            "derecha": [
                self.cargar_imagen(f"imagenes/globo_derec_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "izquierda": [
                self.cargar_imagen(f"imagenes/globo_izqui_{i}.png", con_colorkey=True)
                for i in range(3)
            ],
            "muere": [
                self.cargar_imagen(f"imagenes/globo_muere_{i}.png", con_colorkey=True)
                for i in range(5)
            ],
        }

        # 4. Sprites de Bomba (latido)
        self.sprites_bomba = [
            self.cargar_imagen(f"imagenes/bomba_{i}.png", con_colorkey=True)
            for i in range(3)
        ]

        # 5. Sprites de Fuego (4 frames por cada dirección y centro)
        self.sprites_fuego = []
        for f in range(4):
            frame_dict = {
                "centr": self.cargar_imagen(f"imagenes/exp_{f}_centr.png", con_colorkey=True)
            }
            for d in ["abajo", "arrib", "derec", "izqui"]:
                for seg in [1, 2]:
                    frame_dict[f"{d}_{seg}"] = self.cargar_imagen(
                        f"imagenes/exp_{f}_{d}_{seg}.png", con_colorkey=True
                    )
            self.sprites_fuego.append(frame_dict)

        # 6. Muro suave en destrucción
        self.sprites_muro_destruccion = [
            self.cargar_imagen(f"imagenes/explosion_muro_suave_{i}.png", con_colorkey=True)
            for i in range(6)
        ]

        # 7. Sprites de Puntos Flotantes
        self.sprites_puntos = {}
        for valor in [100, 200, 400, 800, 1000, 2000, 4000, 8000]:
            ruta = f"imagenes/{valor}pt.png"
            if os.path.exists(ruta):
                self.sprites_puntos[valor] = self.cargar_imagen(ruta, con_colorkey=True)

        # 8. Sprites de Power-Ups (Losas)
        self.sprites_powerups = {
            "bomba": self.cargar_imagen("imagenes/losa_bomba_extra.png"),
            "fuego": self.cargar_imagen("imagenes/losa_incrementa_llama.png"),
            "velocidad": self.cargar_imagen("imagenes/losa_incrementa_vel_bomberman.png"),
            "atravesar": self.cargar_imagen("imagenes/losa_atravesar_muros.png"),
        }

        # 9. Sonidos y Música
        self.snd_poner_bomba = pg.mixer.Sound("sonidos/poner_bomba.wav")
        self.snd_boom = pg.mixer.Sound("sonidos/boom.wav")
        self.snd_stage_start = pg.mixer.Sound("sonidos/02_Stage_Start.wav")
        self.musica_tema = "sonidos/03_Stage_Theme.wav"

    def obtener_ruta_nivel(self, num_nivel):
        ruta = f"Levels/L{num_nivel:02d}.TXT"
        if not os.path.exists(ruta):
            ruta = f"Levels/L{num_nivel}.TXT"
        if not os.path.exists(ruta):
            ruta = f"Levels/L-NEW{num_nivel:02d}.TXT"
        return ruta if os.path.exists(ruta) else None

    def crear_punto_flotante(self, x, y, valor):
        img = self.sprites_puntos.get(valor, self.sprites_puntos.get(200))
        if img:
            self.puntos_flotantes.append({
                "x": float(x),
                "y": float(y),
                "img": img,
                "duracion": 50,
            })

    def iniciar_nivel(
        self,
        num_nivel,
        vidas_previas=None,
        puntaje_previo=None,
        max_bombas=None,
        rango_bombas=None,
        speed=None,
        atravesar_muros=None,
    ):
        ruta_nivel = self.obtener_ruta_nivel(num_nivel)
        if not ruta_nivel:
            self.estado = "VICTORIA"
            return

        self.nivel_numero = num_nivel
        self.nivel_actual = []
        self.jugadores = []
        self.enemigos = []
        self.bombas_activas = []
        self.fuegos_activos = []
        self.muros_destruccion = []
        self.posicion_puerta = None
        self.tiempo_restante = 200
        self.contador_segundos = 0

        # Reiniciar interactivos
        self.powerups_revelados = []
        self.puntos_flotantes = []

        # Cargar contenido del mapa
        cajas_pos = []
        with open(ruta_nivel, "r", encoding="utf-8") as archivo:
            for fila_idx, linea in enumerate(archivo):
                linea = linea.rstrip("\r\n")
                if linea.startswith("*"):
                    fila_lista = list(linea)
                    self.nivel_actual.append(fila_lista)

                    for col_idx, caracter in enumerate(fila_lista):
                        if caracter == "1":
                            jugador = Jugador(
                                col_idx,
                                fila_idx,
                                self.tile_size,
                                sprites=self.sprites_jugador,
                            )
                            if vidas_previas is not None:
                                jugador.vidas = vidas_previas
                            if puntaje_previo is not None:
                                jugador.puntaje = puntaje_previo
                            if max_bombas is not None:
                                jugador.max_bombas = max_bombas
                            elif hasattr(self, "guardado_bombas"):
                                jugador.max_bombas = self.guardado_bombas

                            if rango_bombas is not None:
                                jugador.rango_bombas = rango_bombas
                            elif hasattr(self, "guardado_rango"):
                                jugador.rango_bombas = self.guardado_rango

                            if speed is not None:
                                jugador.speed = speed
                            elif hasattr(self, "guardado_speed"):
                                jugador.speed = self.guardado_speed

                            if atravesar_muros is not None:
                                jugador.atravesar_muros = atravesar_muros
                            elif hasattr(self, "guardado_atravesar"):
                                jugador.atravesar_muros = self.guardado_atravesar

                            self.jugadores.append(jugador)
                            fila_lista[col_idx] = " "
                        elif caracter in ["2", "3", "4"]:
                            self.enemigos.append(
                                Enemigo(
                                    col_idx,
                                    fila_idx,
                                    self.tile_size,
                                    sprites=self.sprites_enemigo,
                                )
                            )
                            fila_lista[col_idx] = " "
                        elif caracter == "-":
                            cajas_pos.append((col_idx, fila_idx))
                        elif caracter == "5":
                            self.posicion_puerta = (col_idx, fila_idx)

        # Ubicar la puerta si no venía en el archivo (o si por error estaba sobre un muro duro)
        puerta_invalida = False
        if self.posicion_puerta is not None:
            px, py = self.posicion_puerta
            if self.nivel_actual[py][px] == "*":
                puerta_invalida = True

        if self.posicion_puerta is None or puerta_invalida:
            # En Bomberman, la puerta se oculta bajo una caja destructible que se descubre al explotarla
            cajas_lejos = [
                (c, r) for c, r in cajas_pos
                if abs(c - 1) > 2 or abs(r - 1) > 2
            ]
            if cajas_lejos:
                self.posicion_puerta = random.choice(cajas_lejos)
            elif cajas_pos:
                self.posicion_puerta = random.choice(cajas_pos)
            else:
                espacios_libres = [
                    (c, r)
                    for r, row in enumerate(self.nivel_actual)
                    for c, val in enumerate(row)
                    if val == " " and (c, r) != (1, 1)
                ]
                self.posicion_puerta = random.choice(espacios_libres) if espacios_libres else (1, 2)

        # Distribuir power-ups aleatorios bajo las cajas destructibles
        self.powerups_ocultos = {}
        if cajas_pos:
            cajas_elegibles = [c for c in cajas_pos if c != self.posicion_puerta]
            random.shuffle(cajas_elegibles)
            tipos_pool = ["bomba", "fuego", "velocidad", "atravesar"]
            num_items = min(len(cajas_elegibles), random.randint(2, 4))
            for i in range(num_items):
                tipo = tipos_pool[i % len(tipos_pool)]
                self.powerups_ocultos[cajas_elegibles[i]] = tipo

        # Guardar automáticamente el nivel alcanzado en disco
        self.guardar_progreso()

        # Transición al estado de inicio del nivel con jingle
        self.estado = "INTRO_NIVEL"
        self.timer_estado = 150  # 2.5 segundos a 60 FPS
        pg.mixer.music.stop()
        try:
            self.snd_stage_start.play()
        except Exception:
            pass

    def comenzar_partida(self):
        try:
            pg.mixer.music.load(self.musica_tema)
            pg.mixer.music.play(-1)
        except Exception:
            pass
        self.estado = "JUGANDO"

    def reiniciar_juego(self, nivel=None):
        """Reinicia la partida desde el nivel indicado o nivel guardado."""
        lvl = nivel if nivel is not None else self.nivel_numero
        self.iniciar_nivel(
            lvl,
            vidas_previas=3,
            puntaje_previo=0,
            max_bombas=1 if lvl == 1 else getattr(self, "guardado_bombas", 1),
            rango_bombas=2 if lvl == 1 else getattr(self, "guardado_rango", 2),
            speed=3.0 if lvl == 1 else getattr(self, "guardado_speed", 3.0),
        )

    def ejecutar(self):
        running = True
        while running:
            # 1. Gestión de Eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if self.estado == "JUGANDO":
                        if event.key in [pg.K_p, pg.K_ESCAPE]:
                            self.estado = "PAUSA"
                            pg.mixer.music.pause()
                        elif event.key == pg.K_SPACE:
                            for j in self.jugadores:
                                if j.is_alive and not j.muriendo:
                                    j.poner_bomba(
                                        self.nivel_actual,
                                        self.bombas_activas,
                                        snd_poner_bomba=self.snd_poner_bomba,
                                    )
                    elif self.estado == "PAUSA":
                        if event.key in [pg.K_p, pg.K_ESCAPE, pg.K_RETURN, pg.K_SPACE]:
                            self.estado = "JUGANDO"
                            pg.mixer.music.unpause()
                        elif event.key == pg.K_r:
                            self.reiniciar_juego(self.nivel_numero)
                        elif event.key == pg.K_q:
                            running = False
                    elif self.estado in ["GAME_OVER", "VICTORIA"]:
                        if event.key in [pg.K_RETURN, pg.K_r, pg.K_SPACE]:
                            self.reiniciar_juego(self.nivel_numero)
                        elif event.key == pg.K_1:
                            self.reiniciar_juego(1)
                        elif event.key == pg.K_ESCAPE:
                            running = False
                    elif self.estado in ["INTRO_NIVEL", "NIVEL_COMPLETADO"]:
                        if event.key == pg.K_ESCAPE:
                            running = False

            # 2. Actualización de Lógica según Estado
            if self.estado == "INTRO_NIVEL":
                self.timer_estado -= 1
                if self.timer_estado <= 0:
                    self.comenzar_partida()

            elif self.estado == "JUGANDO":
                self.actualizar_juego()

            elif self.estado == "NIVEL_COMPLETADO":
                self.timer_estado -= 1
                if self.timer_estado <= 0:
                    j = self.jugadores[0] if self.jugadores else None
                    vidas = j.vidas if j else 3
                    puntaje = j.puntaje if j else 0
                    m_bombas = j.max_bombas if j else 1
                    r_bombas = j.rango_bombas if j else 2
                    spd = j.speed if j else 3.0

                    self.iniciar_nivel(
                        self.nivel_numero + 1,
                        vidas_previas=vidas,
                        puntaje_previo=puntaje,
                        max_bombas=m_bombas,
                        rango_bombas=r_bombas,
                        speed=spd,
                        atravesar_muros=j.atravesar_muros if j else False,
                    )

            # 3. Dibujado en pantalla
            self.screen.fill((20, 20, 25))
            self.dibujar_hud()
            self.dibujar_mapa()
            self.dibujar_entidades()

            # Capas superpuestas según el estado
            if self.estado == "INTRO_NIVEL":
                self.dibujar_banner_intro()
            elif self.estado == "NIVEL_COMPLETADO":
                self.dibujar_banner_completado()
            elif self.estado == "PAUSA":
                self.dibujar_pausa()
            elif self.estado == "GAME_OVER":
                self.dibujar_game_over()
            elif self.estado == "VICTORIA":
                self.dibujar_victoria()

            pg.display.flip()
            self.clock.tick(self.fps)

        pg.quit()
        sys.exit()

    def actualizar_juego(self):
        # Cuenta regresiva del reloj
        self.contador_segundos += 1
        if self.contador_segundos >= self.fps:
            self.contador_segundos = 0
            if self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                if self.tiempo_restante <= 0:
                    for j in self.jugadores:
                        j.recibir_dano()

        # Actualizar jugador
        for j in self.jugadores:
            j.actualizar(self.nivel_actual)

        # Actualizar enemigos (solo UNA vez por fotograma)
        for e in self.enemigos:
            e.actualizar(self.nivel_actual)

        # Actualizar bombas activas y detonaciones
        for bomba in self.bombas_activas[:]:
            bomba.actualizar()
            if not bomba.activa:
                casillas_afectadas, muros_rotos = explotar_bomba(
                    bomba,
                    self.nivel_actual,
                    self.bombas_activas,
                    snd_boom=self.snd_boom,
                )

                # Registrar fuegos visuales
                for cf in casillas_afectadas:
                    self.fuegos_activos.append(cf)

                    # Daño a jugadores
                    rect_fuego = pg.Rect(
                        cf["col"] * self.tile_size,
                        cf["row"] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                    for j in self.jugadores:
                        if j.is_alive and not j.muriendo:
                            if j.get_rect().colliderect(rect_fuego):
                                j.recibir_dano()

                    # Daño a enemigos por el fuego
                    for e in self.enemigos:
                        if e.is_alive and not e.muriendo:
                            if e.get_rect().colliderect(rect_fuego):
                                e.recibir_dano()
                                if self.jugadores:
                                    self.jugadores[0].puntaje += e.puntos
                                    # Generar cartelito de puntos flotantes
                                    self.crear_punto_flotante(e.x, e.y, e.puntos)

                    # Destruir power-ups en el suelo si los alcanza el fuego
                    for pu in self.powerups_revelados[:]:
                        if pu["col"] == cf["col"] and pu["row"] == cf["row"]:
                            self.powerups_revelados.remove(pu)

                # Iniciar animación de desmoronamiento de ladrillos
                for mx, my in muros_rotos:
                    self.muros_destruccion.append(
                        {"col": mx, "row": my, "frame": 0, "timer": 0}
                    )

        self.bombas_activas = [b for b in self.bombas_activas if b.activa]

        # Actualizar duración del fuego visual
        for fuego in self.fuegos_activos[:]:
            fuego["duracion"] -= 1
            if fuego["duracion"] <= 0:
                self.fuegos_activos.remove(fuego)

        # Actualizar animación de muros destructibles en demolición
        for muro in self.muros_destruccion[:]:
            muro["timer"] += 1
            if muro["timer"] >= 4:
                muro["timer"] = 0
                muro["frame"] += 1
                if muro["frame"] >= len(self.sprites_muro_destruccion):
                    c, r = muro["col"], muro["row"]
                    self.nivel_actual[r][c] = " "
                    self.muros_destruccion.remove(muro)

                    # Revelar power-up si había uno oculto en esta casilla
                    if (c, r) in self.powerups_ocultos:
                        tipo_pu = self.powerups_ocultos.pop((c, r))
                        self.powerups_revelados.append({"col": c, "row": r, "tipo": tipo_pu})

        # Recoger power-ups revelados
        for j in self.jugadores:
            if not j.is_alive or j.muriendo:
                continue
            rect_j = j.get_rect()
            for pu in self.powerups_revelados[:]:
                pu_rect = pg.Rect(
                    pu["col"] * self.tile_size + 6,
                    pu["row"] * self.tile_size + 6,
                    self.tile_size - 12,
                    self.tile_size - 12,
                )
                if rect_j.colliderect(pu_rect):
                    tipo = pu["tipo"]
                    if tipo == "bomba":
                        j.max_bombas += 1
                    elif tipo == "fuego":
                        j.rango_bombas += 1
                    elif tipo == "velocidad":
                        j.speed = min(4.5, j.speed + 0.5)
                    elif tipo == "atravesar":
                        j.atravesar_muros = True

                    j.puntaje += 1000
                    self.crear_punto_flotante(pu["col"] * self.tile_size, pu["row"] * self.tile_size, 1000)
                    self.powerups_revelados.remove(pu)

        # Actualizar y mover puntos flotantes hacia arriba
        for p in self.puntos_flotantes[:]:
            p["duracion"] -= 1
            p["y"] -= 0.5
            if p["duracion"] <= 0:
                self.puntos_flotantes.remove(p)

        # Eliminar enemigos muertos una vez concluida su animación de defunción
        self.enemigos = [e for e in self.enemigos if not e.muerte_terminada]

        # Colisiones de contacto entre enemigos y jugador
        self.verificar_colisiones()

        # Comprobar muerte o reaparición del jugador
        for j in self.jugadores:
            if j.muerte_terminada:
                if j.vidas > 0:
                    j.respawn()
                else:
                    self.estado = "GAME_OVER"
                    pg.mixer.music.stop()
                    self.guardar_progreso()

        # Comprobar si se superó el nivel
        self.verificar_pasar_de_nivel()

    def verificar_colisiones(self):
        for j in self.jugadores:
            if not j.is_alive or j.muriendo or j.invulnerable:
                continue
            rect_j = j.get_rect()
            for e in self.enemigos:
                if e.is_alive and not e.muriendo:
                    if rect_j.colliderect(e.get_rect()):
                        j.recibir_dano()

    def verificar_pasar_de_nivel(self):
        # La puerta se activa únicamente tras eliminar a todos los enemigos
        puerta_abierta = len(self.enemigos) == 0

        if not puerta_abierta or not self.posicion_puerta:
            return

        px, py = self.posicion_puerta
        puerta_rect = pg.Rect(
            px * self.tile_size + 8,
            py * self.tile_size + 8,
            self.tile_size - 16,
            self.tile_size - 16,
        )

        for j in self.jugadores:
            if j.is_alive and not j.muriendo:
                if j.get_rect().colliderect(puerta_rect):
                    # Nivel completado con éxito
                    bonus = self.tiempo_restante * 10
                    j.puntaje += bonus
                    self.estado = "NIVEL_COMPLETADO"
                    self.timer_estado = 120  # 2 segundos de pausa
                    pg.mixer.music.stop()
                    self.guardar_progreso()

    def dibujar_hud(self):
        hud_rect = pg.Rect(0, 0, self.width, self.hud_height)
        pg.draw.rect(self.screen, (25, 28, 36), hud_rect)
        pg.draw.line(
            self.screen,
            (70, 75, 95),
            (0, self.hud_height),
            (self.width, self.hud_height),
            2,
        )

        j = self.jugadores[0] if self.jugadores else None
        vidas = j.vidas if j else 0
        puntaje = j.puntaje if j else 0
        bombas = j.max_bombas if j else 1
        rango = j.rango_bombas if j else 2
        puerta_abierta = len(self.enemigos) == 0

        txt_vidas = self.font_hud.render(f"VIDAS: {vidas}", True, (255, 220, 80))
        txt_tiempo = self.font_hud.render(f"TIME: {self.tiempo_restante:03d}", True, (255, 255, 255))
        txt_stage = self.font_hud.render(f"STG: {self.nivel_numero:02d}", True, (100, 210, 255))
        extra_w = " W" if j and j.atravesar_muros else ""
        txt_items = self.font_hud.render(f"B:{bombas} F:{rango}{extra_w}", True, (255, 180, 80))

        color_puerta = (80, 255, 120) if puerta_abierta else (255, 80, 80)
        estado_puerta = "OPEN" if puerta_abierta else f"ENM: {len(self.enemigos)}"
        txt_puerta = self.font_hud.render(estado_puerta, True, color_puerta)
        txt_puntos = self.font_hud.render(f"PTS: {puntaje}", True, (255, 255, 255))

        self.screen.blit(txt_vidas, (16, 12))
        self.screen.blit(txt_tiempo, (140, 12))
        self.screen.blit(txt_stage, (270, 12))
        self.screen.blit(txt_items, (380, 12))
        self.screen.blit(txt_puerta, (490, 12))
        self.screen.blit(txt_puntos, (self.width - txt_puntos.get_width() - 16, 12))

    def dibujar_mapa(self):
        for fila_idx, fila in enumerate(self.nivel_actual):
            for col_idx, caracter in enumerate(fila):
                x = col_idx * self.tile_size
                y = self.hud_height + (fila_idx * self.tile_size)

                # 1. Fondo de césped siempre presente debajo
                self.screen.blit(self.img_cesped, (x, y))

                # 2. Puerta de salida si corresponde a esta casilla
                if (col_idx, fila_idx) == self.posicion_puerta:
                    self.screen.blit(self.img_salida, (x, y))
                    if len(self.enemigos) == 0:
                        glow_rect = pg.Rect(x, y, self.tile_size, self.tile_size)
                        pg.draw.rect(self.screen, (100, 255, 120), glow_rect, 2)

                # 3. Obstáculos fijos o destructibles
                if caracter == "*":
                    self.screen.blit(self.img_muro, (x, y))
                elif caracter == "-":
                    self.screen.blit(self.img_caja, (x, y))

    def dibujar_entidades(self):
        # 1. Power-ups revelados en el suelo (debajo de entidades y bombas)
        for pu in self.powerups_revelados:
            img = self.sprites_powerups.get(pu["tipo"])
            if img:
                x = pu["col"] * self.tile_size
                y = self.hud_height + (pu["row"] * self.tile_size)
                self.screen.blit(img, (x, y))

        # 2. Muros en desmoronamiento
        for muro in self.muros_destruccion:
            idx = min(muro["frame"], len(self.sprites_muro_destruccion) - 1)
            img = self.sprites_muro_destruccion[idx]
            x = muro["col"] * self.tile_size
            y = self.hud_height + (muro["row"] * self.tile_size)
            self.screen.blit(img, (x, y))

        # 3. Bombas activas con animación de latido
        for bomba in self.bombas_activas:
            bomba.dibujar(
                self.screen,
                self.hud_height,
                self.tile_size,
                self.sprites_bomba,
            )

        # 4. Llamas de fuego animadas (4 fotogramas auténticos de NES)
        for fuego in self.fuegos_activos:
            frame_idx = (28 - fuego["duracion"]) // 7
            frame_idx = max(0, min(3, frame_idx))
            tipo = fuego["tipo"]

            img_fuego = self.sprites_fuego[frame_idx].get(tipo)
            if img_fuego:
                x = fuego["col"] * self.tile_size
                y = self.hud_height + (fuego["row"] * self.tile_size)
                self.screen.blit(img_fuego, (x, y))

        # 5. Enemigos
        for e in self.enemigos:
            e.dibujar(self.screen, self.hud_height)

        # 6. Jugadores
        for j in self.jugadores:
            j.dibujar(self.screen, self.hud_height)

        # 7. Cartelitos de puntos flotantes (en la capa superior)
        for p in self.puntos_flotantes:
            px = round(p["x"])
            py = round(self.hud_height + p["y"])
            self.screen.blit(p["img"], (px, py))

    def dibujar_banner_intro(self):
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))

        txt = self.font_banner.render(f"STAGE {self.nivel_numero:02d}", True, (255, 255, 255))
        rect = txt.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(txt, rect)

        txt_sub = self.font_sub.render("¡ELIMINA A LOS ENEMIGOS Y CRUZA LA PUERTA!", True, (150, 220, 255))
        rect_sub = txt_sub.get_rect(center=(self.width // 2, self.height // 2 + 35))
        self.screen.blit(txt_sub, rect_sub)

    def dibujar_banner_completado(self):
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 190))
        self.screen.blit(s, (0, 0))

        txt = self.font_banner.render("STAGE CLEAR!", True, (80, 255, 120))
        rect = txt.get_rect(center=(self.width // 2, self.height // 2 - 30))
        self.screen.blit(txt, rect)

        bonus = self.tiempo_restante * 10
        txt_bonus = self.font_sub.render(f"BONUS DE TIEMPO: +{bonus} PTS", True, (255, 230, 80))
        rect_bonus = txt_bonus.get_rect(center=(self.width // 2, self.height // 2 + 25))
        self.screen.blit(txt_bonus, rect_bonus)

    def dibujar_pausa(self):
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 190))
        self.screen.blit(s, (0, 0))

        ancho_box, alto_box = 460, 240
        box_x = (self.width - ancho_box) // 2
        box_y = (self.height - alto_box) // 2

        pg.draw.rect(self.screen, (25, 28, 38), (box_x, box_y, ancho_box, alto_box))
        pg.draw.rect(self.screen, (100, 210, 255), (box_x, box_y, ancho_box, alto_box), 3)

        txt_titulo = self.font_banner.render("PAUSA", True, (255, 220, 50))
        rect_titulo = txt_titulo.get_rect(center=(self.width // 2, box_y + 40))
        self.screen.blit(txt_titulo, rect_titulo)

        txt_res = self.font_sub.render("[P / ENTER / ESC] REANUDAR", True, (255, 255, 255))
        rect_res = txt_res.get_rect(center=(self.width // 2, box_y + 105))
        self.screen.blit(txt_res, rect_res)

        txt_reiniciar = self.font_sub.render(f"[R] REINICIAR NIVEL {self.nivel_numero}", True, (150, 220, 255))
        rect_reiniciar = txt_reiniciar.get_rect(center=(self.width // 2, box_y + 145))
        self.screen.blit(txt_reiniciar, rect_reiniciar)

        txt_salir = self.font_sub.render("[Q] SALIR DEL JUEGO", True, (255, 100, 100))
        rect_salir = txt_salir.get_rect(center=(self.width // 2, box_y + 185))
        self.screen.blit(txt_salir, rect_salir)

    def dibujar_game_over(self):
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 210))
        self.screen.blit(s, (0, 0))

        ancho_box, alto_box = 480, 260
        box_x = (self.width - ancho_box) // 2
        box_y = (self.height - alto_box) // 2

        pg.draw.rect(self.screen, (30, 25, 30), (box_x, box_y, ancho_box, alto_box))
        pg.draw.rect(self.screen, (220, 50, 50), (box_x, box_y, ancho_box, alto_box), 3)

        txt = self.font_banner.render("GAME OVER", True, (255, 60, 60))
        rect = txt.get_rect(center=(self.width // 2, box_y + 45))
        self.screen.blit(txt, rect)

        puntaje = self.jugadores[0].puntaje if self.jugadores else 0
        txt_pts = self.font_sub.render(f"PUNTOS: {puntaje}   RECORD: {self.mejor_puntaje}", True, (255, 255, 255))
        rect_pts = txt_pts.get_rect(center=(self.width // 2, box_y + 105))
        self.screen.blit(txt_pts, rect_pts)

        txt_stg = self.font_sub.render(f"NIVEL ALCANZADO: {self.nivel_numero}", True, (180, 180, 200))
        rect_stg = txt_stg.get_rect(center=(self.width // 2, box_y + 140))
        self.screen.blit(txt_stg, rect_stg)

        txt_retry = self.font_sub.render(f"[ENTER] NIVEL {self.nivel_numero}   [1] NIVEL 1", True, (255, 220, 50))
        rect_retry = txt_retry.get_rect(center=(self.width // 2, box_y + 190))
        self.screen.blit(txt_retry, rect_retry)

        txt_esc = self.font_sub.render("[ESC] SALIR", True, (200, 200, 200))
        rect_esc = txt_esc.get_rect(center=(self.width // 2, box_y + 225))
        self.screen.blit(txt_esc, rect_esc)

    def dibujar_victoria(self):
        s = pg.Surface((self.width, self.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 220))
        self.screen.blit(s, (0, 0))

        txt = self.font_banner.render("¡VICTORIA TOTAL!", True, (255, 220, 50))
        rect = txt.get_rect(center=(self.width // 2, self.height // 2 - 40))
        self.screen.blit(txt, rect)

        puntaje = self.jugadores[0].puntaje if self.jugadores else 0
        txt_pts = self.font_sub.render(f"HAS COMPLETADO TODOS LOS NIVELES CON {puntaje} PTS", True, (255, 255, 255))
        rect_pts = txt_pts.get_rect(center=(self.width // 2, self.height // 2 + 15))
        self.screen.blit(txt_pts, rect_pts)

        txt_re = self.font_sub.render("[ENTER] JUGAR DE NUEVO   [ESC] SALIR", True, (100, 220, 255))
        rect_re = txt_re.get_rect(center=(self.width // 2, self.height // 2 + 65))
        self.screen.blit(txt_re, rect_re)