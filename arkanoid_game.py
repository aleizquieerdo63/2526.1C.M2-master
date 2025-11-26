"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from pathlib import Path
from arkanoid_core import *
import os
import sys
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    # - Comprueba que `self.level_path` existe y es fichero.
    ruta = Path(self.level_path)
    if not ruta.is_file():
        raise FileNotFoundError(f"no  existe el fichero de nivel:{self.level_path}")
    # - Lee su contenido, filtra líneas vacías y valida que todas tienen el mismo ancho.
    texto = ruta.read_text(encoding="utf-8")
    filas = [fila for fila in texto.splitlines() if fila.strip()]
    if not filas:
        raise ValueError("El fichero de nivel está vacío")
    ancho = len(filas[0])
    for fila in filas:
        if len(fila) != ancho:
            raise ValueError("Todas las filas del nivel deben tener la misma longitud")
    # - Guarda el resultado en `self.layout` y devuélvelo.
    self.layout = filas
    return filas
    
@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.
    self.paddle = self.crear_rect(0, 0, *self.PADDLE_SIZE)
    ###CENTRAR PALETA
    self.paddle.midbottom =(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.PADDLE_OFFSET)
    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    self.score = 0
    self.lives = 3
    self.end_message = ""
    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.reiniciar_bola()
    ##raise NotImplementedError

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()
    # - Recorre `self.layout` para detectar símbolos de bloque.
    for fila_indice, fila in enumerate(self.layout):
        for columna_indice, simbolo in enumerate(fila):
            if simbolo == ".":
                continue 
            if simbolo not in self.BLOCK_COLORS:
                continue
    # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
            rect = self.calcular_posicion_bloque(fila_indice, columna_indice)
            self.blocks.append(rect)
            self.block_colors.append(self.BLOCK_COLORS[simbolo])
            self.block_symbols.append(simbolo)
    ##raise NotImplementedError

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    teclas = self.obtener_estado_teclas()
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha. 
    desplazamiento = 0.0
    if teclas[self.KEY_LEFT] or teclas[self.KEY_A]:
        desplazamiento -= self.PADDLE_SPEED
    if teclas[self.KEY_RIGHT] or teclas[self.KEY_D]:
        desplazamiento += self.PADDLE_SPEED
    # aplicar desplazamiento
    self.paddle.x += desplazamiento
    # - Limita la posición para que no salga de la pantalla.
    if self.paddle.left < 0:
        self.paddle.left = 0
    if self.paddle.right > self.SCREEN_WIDTH:
        self.paddle.right = self.SCREEN_WIDTH

    ###raise NotImplementedError
@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()

    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
    if ball_rect.left <= 0:
        ball_rect.left = 0
        self.ball_velocity.x *= -1
        self.ball_pos.x = ball_rect.centerx

    if ball_rect.right >= self.SCREEN_WIDTH:
        ball_rect.right = self.SCREEN_WIDTH
        self.ball_velocity.x *= -1
        self.ball_pos.x = ball_rect.centerx

    if ball_rect.top <= 0:
        ball_rect.top = 0
        self.ball_velocity.y *= -1
        self.ball_pos.y = ball_rect.centery

    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.
    if ball_rect.top >= self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives > 0:
            # colocar bola sobre la paleta y continuar
            self.reiniciar_bola((0, -1))
        else:
            self.running = False
            self.end_message = "GAME OVER"
        return

    # rebote con la paleta
    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        ball_rect.bottom = self.paddle.top
        self.ball_pos.y = ball_rect.centery
        self.ball_velocity.y *= -1
        offset = (ball_rect.centerx - self.paddle.centerx) / (self.paddle.width / 2)
        self.ball_velocity.x += offset * 2.0

    # normalizar velocidad de la bola
    if self.ball_velocity.length_squared() > 0:
        self.ball_velocity = self.ball_velocity.normalize() * self.BALL_SPEED

    # colisión con bloques
    for i, block in enumerate(self.blocks):
        if ball_rect.colliderect(block):
            symbol = self.block_symbols[i]
            self.score += self.BLOCK_POINTS.get(symbol, 0)
            del self.blocks[i]
            del self.block_colors[i]
            del self.block_symbols[i]
            self.ball_velocity.y *= -1
            self.ball_pos.x = ball_rect.centerx
            self.ball_pos.y = ball_rect.centery
            break

    if not self.blocks and not self.end_message:
        self.end_message = "¡HAS GANADO!"
        self.running = False
###raise NotImplementedError 

@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    if not self.screen:
        return
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    self.screen.fill(self.BACKGROUND_COLOR)
    for rect, color in zip(self.blocks, self.block_colors):
        self.dibujar_rectangulo(rect, color)
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    self.dibujar_circulo((int(self.ball_pos.x), int(self.ball_pos.y)), self.BALL_RADIUS, self.BALL_COLOR)
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    self.dibujar_texto(f"Puntuación: {self.score}", (20, 20))
    self.dibujar_texto(f"Vidas: {self.lives}", (20, 50))
    if self.end_message:
        self.dibujar_texto(
            self.end_message,
            (self.SCREEN_WIDTH // 2 - 120, self.SCREEN_HEIGHT // 2),
            grande=True,
        )
    ###raise NotImplementedError

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    if sys.platform.startswith("win") and "DISPLAY" not in os.environ and "SDL_VIDEODRIVER" not in os.environ:
        os.environ["DISPLAY"] = "1"
    self.inicializar_pygame()
    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()
    self.running = True
    # - Procesa eventos de `self.iterar_eventos()` y llama a los métodos de actualización/dibujo.
    while self.running:
        for event in self.iterar_eventos():
            if event.type == self.EVENT_QUIT:
                self.running = False
            elif event.type == self.EVENT_KEYDOWN and event.key == self.KEY_ESCAPE:
                self.running = False
        self.procesar_input()
        self.actualizar_bola()
        self.dibujar_escena()
    # - Refresca la pantalla con `self.actualizar_pantalla()` y cierra con `self.finalizar_pygame()`.
        self.actualizar_pantalla()
        if self.clock is not None:
            self.clock.tick(self.FPS)
# Mantener la pantalla final (mensaje de victoria/derrota) visible
    # hasta que el jugador pulse una tecla, cierre la ventana o pasen 3 segundos.
    try:
        import pygame as _pygame
    except Exception:
        _pygame = None

    if self.end_message and self.screen:
        wait_ms = 3000 #  3 * 1000
        start = _pygame.time.get_ticks() if _pygame else 0
        waiting = True
        while waiting:
            for event in self.iterar_eventos():
                if event.type == self.EVENT_QUIT:
                    waiting = False
                elif event.type == self.EVENT_KEYDOWN:
                    waiting = False
            # Redibujar la escena para asegurar que el mensaje se vea
            self.dibujar_escena()
            self.actualizar_pantalla()
            if self.clock is not None:
                self.clock.tick(self.FPS)
            if _pygame and (_pygame.time.get_ticks() - start) >= wait_ms:
                waiting = False
    self.finalizar_pygame()
    ###raise NotImplementedError



def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        help="Ruta al fichero de nivel (texto con # para bloques y . para huecos).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()
