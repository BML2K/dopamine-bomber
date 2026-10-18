# 💣 Dopamine Bomber

<p align="center">
  <img src="imagenes/bomba_0.png" width="96" alt="Dopamine Bomber Icon" />
</p>

<p align="center">
  <strong>Un tributo arcade frenético, moderno y personalizable al clásico Bomberman de NES.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13%2B-blue.svg?logo=python&logoColor=white" alt="Python 3.13+">
  <img src="https://img.shields.io/badge/Pygame--CE-2.5.8-green.svg?logo=pygame&logoColor=white" alt="Pygame-CE">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Build-PyInstaller%20Ready-orange.svg" alt="PyInstaller Ready">
</p>

---

## 🎮 Acerca del Juego

**Dopamine Bomber** combina la jugabilidad táctica y nostálgica del clásico Bomberman retro con un giro moderno y adictivo: modos de juego dinámicos, efectos de sonido inmersivos, más de 60 niveles progresivos, mejoras acumulables y sistema de guardado persistente.

---

## ✨ Características Principales

### 🕹️ Modos de Juego
Elige tu ritmo desde el menú principal:
* **Modo Clásico**: La experiencia original y nostálgica de la era 8-bits. Velocidad balanceada, temporizadores calculados y banda sonora retro clásica.
* **Modo Dopamínico 🔥**: Acción al límite con todo **x2** (velocidad de movimiento, velocidad de enemigos y multiplicador de puntuación), bombas ultrarrápidas y efectos de sonido virales.

### ⚡ Power-Ups y Mejoras
Al destruir cajas destructibles podrás descubrir valiosos potenciadores ocultos:
* 💣 **Bomba Extra**: Aumenta la cantidad máxima de bombas que puedes plantar al mismo tiempo.
* 🔥 **Llama / Fuego**: Incrementa el radio de alcance de las explosiones.
* 👟 **Patín de Velocidad**: Aumenta la velocidad de desplazamiento del personaje.
* 👻 **Atravesar Muros**: Habilidad especial para caminar a través de las cajas suaves sin destruirlas.

### 🚪 Salida Oculta y Puntuación
* **Puerta Secreta**: Oculta bajo una de las cajas de cada nivel. Al derrotar a todos los enemigos, la losa de salida se habilitará para avanzar al siguiente nivel.
* **Puntuaciones Flotantes**: Bonificaciones acumulativas estilo arcade de 100 a 8.000 puntos al eliminar enemigos consecutivamente.
* **Guardado Automático**: Tu récord, nivel máximo alcanzado y mejoras se guardan de forma persistente en `progreso.json`.

---

## 🗺️ Leyenda de Símbolos del Mapa

Todos los mapas del juego se cargan desde archivos de texto editables en la carpeta `Levels/`. Puedes crear o modificar cualquier nivel usando esta sintaxis:

* **`*`** : **Muro indestructible (Piedra):** Delimita los bordes y estructuras fijas que las bombas no pueden destruir.
* **`-`** : **Caja destructible:** Obstáculos que deben destruirse con bombas para abrir caminos y encontrar power-ups.
* **` ` (Espacio)** : **Césped / Camino libre:** Pasillos vacíos por donde transitan los jugadores y enemigos.
* **`1`, `2`, `3`, `4`** : **Puntos de aparición (*Spawns*):** Coordenadas iniciales de los jugadores (el `1` es tu personaje principal).
* **`5`** : **Enemigo o salida:** Posición de aparición de un enemigo o ubicación de la puerta oculta.

---

## 🕹️ Controles

| Acción | Teclas |
| :--- | :--- |
| **Moverse** | `Flechas de dirección` o `W`, `A`, `S`, `D` |
| **Plantar Bomba** | `Espacio` |
| **Pausar / Menú** | `P` o `Escape` |
| **Reanudar Partida** | `Espacio`, `Enter`, `P` o `Escape` |
| **Reiniciar Nivel (en Pausa/Game Over)** | `R` |
| **Volver al Menú Principal** | `M` |
| **Reiniciar desde Nivel 1 (en Game Over)** | `1` |
| **Navegar Menús** | `W`/`S` o `Arriba`/`Abajo` (Cambiar modo: `A`/`D` o `Izquierda`/`Derecha`) |

---

## 🚀 Cómo Jugar

### Opción A: Descargar el Ejecutable (.exe) para Windows
No necesitas tener Python instalado:
1. Ve a la sección [**Releases**](../../releases/latest) del repositorio.
2. Descarga el archivo **`DopamineBomber.exe`**.
3. ¡Haz doble clic y juega!

### Opción B: Ejecutar desde Código Fuente (Recomendado con `uv`)

Requisitos: **Python 3.13+**

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/dopamine-bomber.git
   cd dopamine-bomber
   ```

2. **Instalar dependencias y ejecutar:**
   * Con [`uv`](https://github.com/astral-sh/uv) (rápido y recomendado):
     ```bash
     uv sync
     uv run python main.py
     ```
   * O con `pip` estándar:
     ```bash
     pip install pygame-ce
     python main.py
     ```

---

## 🛠️ Compilación a Ejecutable (.exe)

El proyecto incluye soporte nativo y configuración de **PyInstaller** lista para usar:

* **Compilación con un clic en Windows:**
  Ejecuta el script incluido:
  ```bash
  compilar.bat
  ```
* **O compilar desde la terminal:**
  ```bash
  uv run pyinstaller DopamineBomber.spec --noconfirm
  ```

El ejecutable independiente se generará automáticamente en la carpeta `dist/DopamineBomber.exe` con todos los recursos (sprites, sonidos, fuentes y niveles) empaquetados.

---

## 📂 Estructura del Proyecto

```text
dopamine-bomber/
├── clases/
│   ├── Entities/        # Lógica del Jugador, Bombas, Enemigos y Colisiones
│   │   ├── bomba.py
│   │   ├── enemy.py
│   │   ├── entities.py
│   │   └── player.py
│   └── Game/            # Motor de juego, bucle principal y modos
│       ├── game.py
│       └── gamemode.py
├── fuentes/             # Tipografía retro pixelada (.ttf)
├── imagenes/            # Sprites del juego, animaciones y tiles
├── sonidos/             # Efectos de sonido (SFX) y música temática
├── Levels/              # Más de 60 archivos de niveles editables (.TXT)
├── DopamineBomber.spec  # Configuración de compilación para PyInstaller
├── compilar.bat         # Script automatizado de compilación a .exe
├── main.py              # Punto de entrada del juego
├── pyproject.toml       # Dependencias y metadatos del proyecto
└── README.md            # Documentación del proyecto
```

---

## 📜 Créditos y Tecnologías

* Desarrollado en **Python 3.13** utilizando el motor **[pygame-ce](https://pyga.me/)**.
* Inspirado en la saga clásica **Bomberman** de Hudson Soft / Konami.
* Gestor de paquetes ultrarrápido **[uv](https://docs.astral.sh/uv/)**.