"""
TIROS LIBRES - Juego de fútbol en Python con Pygame
Jugadores seleccionables: Lionel Messi, Cristiano Ronaldo y Kylian Mbappé.

Instalación:
    py -m pip install pygame

Ejecución:
    py futbol.py
"""

import math
import sys
import pygame

pygame.init()

# Ventana y colores
ANCHO, ALTO = 1000, 650
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tiros Libres - Python")
RELOJ = pygame.time.Clock()

BLANCO = (245, 245, 245)
NEGRO = (20, 25, 30)
VERDE = (36, 130, 68)
VERDE_CLARO = (45, 150, 78)
AZUL = (40, 110, 220)
ROJO = (220, 50, 55)
AMARILLO = (255, 220, 65)
GRIS = (100, 110, 120)

FUENTE = pygame.font.SysFont("arial", 22, bold=True)
FUENTE_PEQUENA = pygame.font.SysFont("arial", 16)
FUENTE_GRANDE = pygame.font.SysFont("arial", 38, bold=True)

JUGADORES = [
    {"nombre": "Lionel Messi", "equipo": "Inter Miami", "numero": 10, "color": (26, 92, 214), "jersey": (18, 71, 195), "short": (200, 210, 220), "calzado": (22, 22, 22)},
    {"nombre": "Cristiano Ronaldo", "equipo": "Al Nassr", "numero": 7, "color": (244, 196, 48), "jersey": (239, 197, 55), "short": (250, 250, 250), "calzado": (24, 24, 24)},
    {"nombre": "Kylian Mbappé", "equipo": "Real Madrid", "numero": 10, "color": (78, 89, 176), "jersey": (95, 108, 197), "short": (238, 238, 240), "calzado": (19, 19, 19)},
]

# Campo y portería
PORTERIA = pygame.Rect(ANCHO // 2 - 180, 60, 360, 110)
JUGADOR_X = PORTERIA.centerx
JUGADOR_Y = 420
LINEA_META_Y = PORTERIA.bottom
CAMPO = pygame.Rect(300, LINEA_META_Y, 400, 610 - LINEA_META_Y)
AREA_GRANDE = pygame.Rect(310, LINEA_META_Y, 380, 170)
AREA_CHICA = pygame.Rect(370, LINEA_META_Y, 260, 60)
PUNTO_PENAL = (PORTERIA.centerx, LINEA_META_Y + 100)
POS_BALON_INICIAL = PUNTO_PENAL
BALON_RADIO = 11

jugador_actual = 0
jugador_x = JUGADOR_X - 30
jugador_y = JUGADOR_Y
corriendo = False
fase_carrera = 0.0
disparo_pendiente = False
goles = 0
tiros = 0
mensaje = "Flechas: apunta | Mantén ESPACIO para correr y cargar; suelta para patear."
potencia = 0
cargando = False
pateando = 0
angulo_objetivo = (PORTERIA.centerx, PORTERIA.top + 40)
balon_x, balon_y = POS_BALON_INICIAL
balon_z = 0.0
vel_x = 0.0
vel_y = 0.0
vel_z = 0.0
disparando = False
tiempo_vuelo = 0
resultado_timer = 0
resultado = ""
arquero_x = ANCHO // 2
arquero_direccion = 1
arquero_velocidad = 3.2
pared = [(445, 345), (482, 345), (519, 345), (556, 345)]


def texto(superficie, contenido, x, y, fuente=FUENTE, color=BLANCO, centrado=False):
    imagen = fuente.render(contenido, True, color)
    rect = imagen.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    superficie.blit(imagen, rect)


def dibujar_campo():
    PANTALLA.fill(VERDE)
    # Franjas del césped
    for i in range(8):
        if i % 2 == 0:
            franja_x = CAMPO.left + i * CAMPO.width // 8
            pygame.draw.rect(PANTALLA, VERDE_CLARO, (franja_x, CAMPO.top, CAMPO.width // 8, CAMPO.height))
    pygame.draw.rect(PANTALLA, BLANCO, CAMPO, 3)
    mitad_y = (LINEA_META_Y + CAMPO.bottom) // 2
    pygame.draw.line(PANTALLA, BLANCO, (CAMPO.left, mitad_y), (CAMPO.right, mitad_y), 2)
    pygame.draw.circle(PANTALLA, BLANCO, (PORTERIA.centerx, mitad_y), 52, 2)
    pygame.draw.circle(PANTALLA, BLANCO, (PORTERIA.centerx, mitad_y), 4)
    pygame.draw.rect(PANTALLA, BLANCO, AREA_GRANDE, 3)
    pygame.draw.rect(PANTALLA, BLANCO, AREA_CHICA, 3)
    pygame.draw.circle(PANTALLA, BLANCO, PUNTO_PENAL, 5)
    clip_anterior = PANTALLA.get_clip()
    PANTALLA.set_clip(pygame.Rect(CAMPO.left, AREA_GRANDE.bottom, CAMPO.width, CAMPO.bottom - AREA_GRANDE.bottom))
    radio_arco_penal = 80
    pygame.draw.arc(
        PANTALLA,
        BLANCO,
        (
            PUNTO_PENAL[0] - radio_arco_penal,
            PUNTO_PENAL[1] - radio_arco_penal,
            radio_arco_penal * 2,
            radio_arco_penal * 2,
        ),
        0,
        math.pi,
        2,
    )
    PANTALLA.set_clip(clip_anterior)
    pygame.draw.arc(PANTALLA, BLANCO, (CAMPO.left - 16, CAMPO.top - 16, 32, 32), 0, math.pi / 2, 2)
    pygame.draw.arc(PANTALLA, BLANCO, (CAMPO.right - 16, CAMPO.top - 16, 32, 32), math.pi / 2, math.pi, 2)
    pygame.draw.arc(PANTALLA, BLANCO, (CAMPO.left - 16, CAMPO.bottom - 16, 32, 32), 3 * math.pi / 2, 2 * math.pi, 2)
    pygame.draw.arc(PANTALLA, BLANCO, (CAMPO.right - 16, CAMPO.bottom - 16, 32, 32), math.pi, 3 * math.pi / 2, 2)
    # Vista frontal: marco rectangular y red detrás, centrados con el pateador.
    pygame.draw.ellipse(PANTALLA, (25, 83, 43), (PORTERIA.left - 8, PORTERIA.bottom - 3, PORTERIA.width + 16, 18))
    for x in range(PORTERIA.left + 12, PORTERIA.right, 18):
        pygame.draw.line(PANTALLA, (200, 220, 205), (x, PORTERIA.top + 5), (x, PORTERIA.bottom - 4), 1)
    for y in range(PORTERIA.top + 12, PORTERIA.bottom, 14):
        pygame.draw.line(PANTALLA, (200, 220, 205), (PORTERIA.left + 4, y), (PORTERIA.right - 4, y), 1)
    pygame.draw.rect(PANTALLA, BLANCO, PORTERIA, 6)
    pygame.draw.line(PANTALLA, (190, 190, 185), (PORTERIA.left + 5, PORTERIA.bottom + 3), (PORTERIA.right + 5, PORTERIA.bottom + 3), 3)


def dibujar_balon():
    cx, cy = int(balon_x), int(balon_y)
    pygame.draw.ellipse(PANTALLA, (42, 75, 48), (cx - 12, cy + 8, 25, 8))
    pygame.draw.circle(PANTALLA, (225, 225, 220), (cx, cy), BALON_RADIO + 2)
    pygame.draw.circle(PANTALLA, (250, 250, 245), (cx - 2, cy - 2), BALON_RADIO)
    pygame.draw.polygon(PANTALLA, (35, 38, 42), [
        (cx, cy - 7), (cx + 6, cy - 4), (cx + 5, cy + 2),
        (cx, cy + 5), (cx - 5, cy + 2), (cx - 6, cy - 4),
    ])
    for puntos in (
        [(cx, cy - 10), (cx - 4, cy - 8), (cx - 6, cy - 4), (cx - 3, cy - 2), (cx, cy - 5)],
        [(cx + 9, cy - 5), (cx + 10, cy - 1), (cx + 7, cy + 3), (cx + 5, cy + 2), (cx + 6, cy - 3)],
        [(cx + 4, cy + 8), (cx, cy + 10), (cx - 4, cy + 8), (cx - 5, cy + 5), (cx, cy + 5)],
        [(cx - 10, cy + 2), (cx - 9, cy - 3), (cx - 6, cy - 4), (cx - 5, cy + 2), (cx - 7, cy + 5)],
    ):
        pygame.draw.polygon(PANTALLA, (35, 38, 42), puntos)
    pygame.draw.circle(PANTALLA, (255, 255, 255), (cx - 4, cy - 5), 2)
    pygame.draw.circle(PANTALLA, (45, 45, 45), (cx, cy), BALON_RADIO + 2, 1)


def dibujar_portero():
    x = int(arquero_x)
    y = PORTERIA.bottom - 39
    pygame.draw.ellipse(PANTALLA, (55, 70, 58), (x - 22, PORTERIA.bottom - 7, 44, 8))
    pygame.draw.circle(PANTALLA, (218, 166, 132), (x, y - 25), 10)
    pygame.draw.arc(PANTALLA, (45, 35, 30), (x - 10, y - 37, 20, 18), 0, math.pi, 4)
    pygame.draw.circle(PANTALLA, (30, 30, 30), (x - 3, y - 26), 1)
    pygame.draw.circle(PANTALLA, (30, 30, 30), (x + 3, y - 26), 1)
    pygame.draw.rect(PANTALLA, (235, 190, 45), (x - 13, y - 14, 26, 31), border_radius=5)
    pygame.draw.line(PANTALLA, BLANCO, (x - 11, y - 10), (x - 23, y + 3), 5)
    pygame.draw.line(PANTALLA, BLANCO, (x + 11, y - 10), (x + 23, y + 3), 5)
    pygame.draw.circle(PANTALLA, (245, 245, 245), (x - 23, y + 3), 4)
    pygame.draw.circle(PANTALLA, (245, 245, 245), (x + 23, y + 3), 4)
    pygame.draw.line(PANTALLA, (35, 45, 55), (x - 7, y + 17), (x - 10, y + 37), 6)
    pygame.draw.line(PANTALLA, (35, 45, 55), (x + 7, y + 17), (x + 10, y + 37), 6)
    pygame.draw.line(PANTALLA, (20, 20, 20), (x - 10, y + 37), (x - 17, y + 39), 5)
    pygame.draw.line(PANTALLA, (20, 20, 20), (x + 10, y + 37), (x + 17, y + 39), 5)


def dibujar_jugador():
    jugador = JUGADORES[jugador_actual]
    x = int(jugador_x)
    y = int(jugador_y)
    avance = min(1, max(0, pateando) / 10)
    balanceo = math.sin(fase_carrera) if corriendo else 0.0

    piel = (218, 166, 132)
    sombra_piel = (178, 119, 91)
    pelo = (55, 39, 31)
    pygame.draw.ellipse(PANTALLA, piel, (x - 14, y - 62, 28, 36))
    pygame.draw.ellipse(PANTALLA, sombra_piel, (x + 5, y - 54, 7, 20))
    pygame.draw.polygon(PANTALLA, pelo, [
        (x - 14, y - 45), (x - 16, y - 57), (x - 10, y - 65),
        (x + 2, y - 67), (x + 12, y - 61), (x + 15, y - 50),
        (x + 11, y - 43), (x + 5, y - 50), (x - 3, y - 52),
        (x - 10, y - 48),
    ])
    pygame.draw.ellipse(PANTALLA, piel, (x - 17, y - 49, 5, 9))
    pygame.draw.ellipse(PANTALLA, piel, (x + 12, y - 49, 5, 9))
    pygame.draw.line(PANTALLA, sombra_piel, (x, y - 31), (x, y - 25), 8)

    pygame.draw.ellipse(PANTALLA, (65, 70, 67), (x - 27, y + 112, 56, 12))
    hip_izq = (x - 10, y + 67)
    hip_der = (x + 10, y + 67)
    if corriendo:
        paso = math.sin(fase_carrera)
        piernas = (
            (hip_izq, (x - 10 + int(paso * 15), y + 88), (x - 8 + int(paso * 30), y + 105)),
            (hip_der, (x + 10 - int(paso * 15), y + 88), (x + 12 - int(paso * 30), y + 105)),
        )
    elif pateando > 0:
        piernas = (
            (hip_izq, (x - 12, y + 88), (x - 12, y + 106)),
            (hip_der, (x + 10 + int(10 * avance), y + 88 - int(6 * avance)), (x + 10 + int(14 * avance), y + 106 + int(4 * avance))),
        )
    else:
        piernas = (
            (hip_izq, (x - 12, y + 88), (x - 12, y + 106)),
            (hip_der, (x + 10 + int(24 * avance), y + 88 - int(10 * avance)), (x + 14 + int(30 * avance), y + 106 - int(10 * avance))),
        )
    for cadera, rodilla, tobillo in piernas:
        pygame.draw.line(PANTALLA, (35, 39, 45), (cadera[0], cadera[1] + 2), rodilla, 10)
        pygame.draw.line(PANTALLA, (245, 245, 240), rodilla, tobillo, 9)
        pygame.draw.circle(PANTALLA, (230, 230, 225), rodilla, 5)
        pie_x = tobillo[0] + 10 if pateando > 0 and cadera == hip_der else tobillo[0] + 12
        pie_y = tobillo[1] + 2 if pateando > 0 and cadera == hip_der else tobillo[1] + 3
        pygame.draw.line(PANTALLA, jugador["calzado"], tobillo, (pie_x, pie_y), 6)

    pygame.draw.polygon(PANTALLA, jugador["jersey"], [
        (x - 17, y - 29), (x - 27, y - 23), (x - 23, y + 12),
        (x - 18, y + 17), (x + 18, y + 17), (x + 23, y + 12),
        (x + 27, y - 23), (x + 17, y - 29),
    ])
    pygame.draw.polygon(PANTALLA, jugador["color"], [
        (x - 17, y - 29), (x - 27, y - 23), (x - 23, y - 13),
        (x - 12, y - 18), (x - 8, y - 29),
    ])
    pygame.draw.polygon(PANTALLA, jugador["color"], [
        (x + 17, y - 29), (x + 27, y - 23), (x + 23, y - 13),
        (x + 12, y - 18), (x + 8, y - 29),
    ])
    pygame.draw.polygon(PANTALLA, jugador["short"], [
        (x - 19, y + 15), (x + 19, y + 15), (x + 17, y + 40),
        (x + 3, y + 39), (x, y + 34), (x - 4, y + 39), (x - 17, y + 40),
    ])
    pygame.draw.line(PANTALLA, (235, 235, 225), (x, y - 24), (x, y + 13), 2)
    pygame.draw.line(PANTALLA, (225, 225, 220), (x - 18, y + 41), (x - 17, y + 64), 8)
    pygame.draw.line(PANTALLA, (225, 225, 220), (x + 16, y + 41), (x + 15, y + 64), 8)
    pygame.draw.line(PANTALLA, jugador["jersey"], (x - 20, y + 52), (x - 14, y + 52), 3)
    pygame.draw.line(PANTALLA, jugador["jersey"], (x + 12, y + 52), (x + 18, y + 52), 3)
    texto(PANTALLA, str(jugador["numero"]), x, y - 5, FUENTE_PEQUENA, BLANCO, True)

    brazo_izq = y + 3 + int(balanceo * 8)
    brazo_der = y + 3 - int(balanceo * 8)
    pygame.draw.line(PANTALLA, jugador["jersey"], (x - 22, y - 20), (x - 30, y + 1), 10)
    pygame.draw.line(PANTALLA, piel, (x - 30, y + 1), (x - 36, brazo_izq + 22), 7)
    pygame.draw.circle(PANTALLA, piel, (x - 36, brazo_izq + 22), 4)
    pygame.draw.line(PANTALLA, jugador["jersey"], (x + 22, y - 20), (x + 30, y + 1), 10)
    pygame.draw.line(PANTALLA, piel, (x + 30, y + 1), (x + 36, brazo_der + 22), 7)
    pygame.draw.circle(PANTALLA, piel, (x + 36, brazo_der + 22), 4)

    texto(PANTALLA, f"{jugador['nombre']} #{jugador['numero']} • {jugador['equipo']}", 25, 20, FUENTE_PEQUENA)


def dibujar_selector_jugadores():
    for i, jugador in enumerate(JUGADORES):
        x = 280 + i * 220
        rect = pygame.Rect(x, 575, 180, 50)
        color = jugador["color"] if i == jugador_actual else (120, 120, 120)
        pygame.draw.rect(PANTALLA, color, rect)
        texto(PANTALLA, jugador["nombre"], rect.centerx, rect.centery + 2, FUENTE_PEQUENA, BLANCO, True)


def dibujar_hud():
    texto(PANTALLA, f"Goles: {goles}", 25, 60)
    texto(PANTALLA, f"Tiros: {tiros}", 25, 90)
    texto(PANTALLA, f"Potencia: {int(potencia)}%", 25, 120)
    texto(PANTALLA, mensaje, 25, 610, FUENTE_PEQUENA, BLANCO)
    if resultado:
        texto(PANTALLA, resultado, ANCHO // 2, 40, FUENTE_GRANDE, AMARILLO, True)


def reiniciar_tirada():
    global balon_x, balon_y, vel_x, vel_y, vel_z, disparando, potencia, cargando, resultado_timer, resultado, mensaje, pateando, jugador_x, jugador_y, corriendo, fase_carrera, disparo_pendiente
    balon_x, balon_y = POS_BALON_INICIAL
    jugador_x = JUGADOR_X - 30
    jugador_y = JUGADOR_Y
    corriendo = False
    fase_carrera = 0.0
    disparo_pendiente = False
    vel_x = 0.0
    vel_y = 0.0
    vel_z = 0.0
    disparando = False
    potencia = 0
    cargando = False
    pateando = 0
    resultado_timer = 0
    resultado = ""
    mensaje = "Flechas: apunta | Mantén ESPACIO para correr y cargar; suelta para patear."


def lanzar_disparo():
    global disparando, vel_x, vel_y, vel_z, tiros, tiempo_vuelo, mensaje, angulo_objetivo, pateando, corriendo, disparo_pendiente, balon_x, balon_y
    if disparando:
        return

    corriendo = False
    disparo_pendiente = False
    dx = angulo_objetivo[0] - balon_x
    dy = angulo_objetivo[1] - balon_y
    distancia = max(1, math.hypot(dx, dy))
    fuerza = 8 + potencia * 0.18

    vel_x = (dx / distancia) * fuerza
    vel_y = (dy / distancia) * fuerza
    vel_z = 0.0
    disparando = True
    pateando = 10
    tiempo_vuelo = 0
    tiros += 1
    mensaje = f"{JUGADORES[jugador_actual]['nombre']} dispara al arco con {int(potencia)}% de potencia."


def actualizar_juego():
    global arquero_x, arquero_direccion, resultado_timer, resultado, goles, mensaje, disparando, balon_x, balon_y, vel_x, vel_y, vel_z, potencia, cargando, pateando, jugador_x, jugador_y, corriendo, fase_carrera, disparo_pendiente, tiempo_vuelo

    if pateando > 0:
        pateando -= 1

    if not disparando:
        arquero_x += arquero_velocidad * arquero_direccion
        if arquero_x >= PORTERIA.right - 38 or arquero_x <= PORTERIA.left + 38:
            arquero_direccion *= -1
        if cargando:
            potencia = min(100, potencia + 2.2)
        if corriendo:
            fase_carrera += 0.55
            jugador_y = max(jugador_y - 5, balon_y - 110)
            if jugador_y <= balon_y - 110:
                corriendo = False
                if disparo_pendiente:
                    lanzar_disparo()
        return

    balon_x += vel_x
    balon_y += vel_y
    vel_y += 0.24
    vel_x *= 0.995
    tiempo_vuelo += 1

    if balon_y > ALTO + 40 or balon_x < -50 or balon_x > ANCHO + 50:
        disparando = False
        resultado = "Se fue fuera"
        resultado_timer = 90
        mensaje = resultado
        return

    # Portero
    if abs(balon_x - arquero_x) < 28 and PORTERIA.top <= balon_y <= PORTERIA.bottom:
        disparando = False
        resultado = "¡Arquero salva!"
        resultado_timer = 90
        mensaje = resultado
        return

    # GOL
    if PORTERIA.left <= balon_x <= PORTERIA.right and PORTERIA.top <= balon_y <= PORTERIA.bottom:
        if abs(balon_x - arquero_x) > 35:
            goles += 1
            resultado = "¡GOOOOOOOL!"
        else:
            resultado = "¡Arquero tapa!"
        disparando = False
        resultado_timer = 110
        mensaje = resultado
        return


def dibujar_escena():
    dibujar_campo()
    dibujar_portero()
    dibujar_jugador()
    if disparando and pateando >= 7:
        cx, cy = int(balon_x), int(balon_y)
        pygame.draw.line(PANTALLA, AMARILLO, (cx - 17, cy - 6), (cx - 12, cy - 3), 2)
        pygame.draw.line(PANTALLA, AMARILLO, (cx - 17, cy + 6), (cx - 12, cy + 3), 2)
    dibujar_balon()
    dibujar_selector_jugadores()
    dibujar_hud()

    if not disparando:
        destino = (int(angulo_objetivo[0]), int(angulo_objetivo[1]))
        pygame.draw.line(PANTALLA, AMARILLO, (int(balon_x), int(balon_y)), destino, 2)
        pygame.draw.circle(PANTALLA, AMARILLO, destino, 9, 2)
        pygame.draw.line(PANTALLA, AMARILLO, (destino[0] - 5, destino[1]), (destino[0] + 5, destino[1]), 2)
        pygame.draw.line(PANTALLA, AMARILLO, (destino[0], destino[1] - 5), (destino[0], destino[1] + 5), 2)


def seleccionar_jugador_por_tecla(tecla):
    global jugador_actual
    if tecla == pygame.K_1:
        jugador_actual = 0
    elif tecla == pygame.K_2:
        jugador_actual = 1
    elif tecla == pygame.K_3:
        jugador_actual = 2


def ajustar_direccion(tecla):
    global angulo_objetivo
    if disparando or corriendo:
        return

    x, y = angulo_objetivo
    if tecla == pygame.K_LEFT:
        x -= 12
    elif tecla == pygame.K_RIGHT:
        x += 12
    elif tecla == pygame.K_UP:
        y -= 10
    elif tecla == pygame.K_DOWN:
        y += 10
    else:
        return

    angulo_objetivo = (
        max(PORTERIA.left + 12, min(PORTERIA.right - 12, x)),
        max(PORTERIA.top + 10, min(PORTERIA.bottom - 10, y)),
    )


# Bucle principal
jugando = True
while jugando:
    RELOJ.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                seleccionar_jugador_por_tecla(evento.key)
            ajustar_direccion(evento.key)
            if evento.key == pygame.K_SPACE and not disparando and not cargando:
                cargando = True
                potencia = 20
                corriendo = True
            if evento.key == pygame.K_r:
                reiniciar_tirada()
        elif evento.type == pygame.KEYUP:
            if evento.key == pygame.K_SPACE and cargando:
                cargando = False
                if corriendo:
                    disparo_pendiente = True
                else:
                    lanzar_disparo()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            x, y = evento.pos
            for i, jugador in enumerate(JUGADORES):
                rect = pygame.Rect(280 + i * 220, 575, 180, 50)
                if rect.collidepoint(x, y):
                    jugador_actual = i
                    mensaje = f"Seleccionado: {jugador['nombre']}"
                    break

    if resultado_timer > 0:
        resultado_timer -= 1
        if resultado_timer == 0:
            reiniciar_tirada()

    actualizar_juego()
    dibujar_escena()
    pygame.display.flip()

pygame.quit()
sys.exit()