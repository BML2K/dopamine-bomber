class ModoJuego:
    """Clase base de los modos de juego. Todos los valores por defecto son neutros."""

    clave = "clasico"
    nombre = "CLASICO"
    velocidad_mult = 1.0   # multiplicador de velocidad del jugador
    enemigo_mult = 1.0     # multiplicador de velocidad de los enemigos
    puntuacion_mult = 1    # multiplicador de puntos obtenidos
    bomba_tiempo_vida = 140  # fotogramas antes de que la bomba explote
    ruta_musica = "sonidos/03_Stage_Theme.wav"
    ruta_poner_bomba = "sonidos/poner_bomba.wav"
    ruta_boom = "sonidos/boom.wav"
    ruta_stage_start = "sonidos/02_Stage_Start.wav"
    ruta_stage_victoria = "sonidos/victory.mp3"
    ruta_stage_die = "sonidos/bomberman-death-sound.mp3"
    ruta_stage_powerup = "sonidos/bomberman-fx-2.mp3"


class ModoClasico(ModoJuego):
    """La experiencia original de Bomberman."""

    clave = "clasico"
    nombre = "CLASICO"


class ModoDopaminico(ModoJuego):
    """Todo x2: velocidad, enemigos, puntos y bombas más rápidas con música y SFX virales."""

    clave = "dopaminico"
    nombre = "DOPAMINICO"
    velocidad_mult = 2
    enemigo_mult = 2
    puntuacion_mult = 2
    bomba_tiempo_vida = 80

    ruta_musica = "sonidos/dompanine-theme.mp3"
    ruta_poner_bomba = "sonidos/bomb-has-been-planted.mp3"
    ruta_boom = "sonidos/exploded.mp3"
    ruta_stage_start = "sonidos/start_dp.mp3"

    ruta_stage_victoria = "sonidos/victory.mp3"
    ruta_stage_die = "sonidos/die.mp3"
    ruta_stage_powerup = "sonidos/power-up.mp3"


def obtener_modo(clave):
    """Devuelve una instancia de modo a partir de su clave ('clasico' / 'dopaminico')."""
    if clave == "dopaminico":
        return ModoDopaminico()
    return ModoClasico()
