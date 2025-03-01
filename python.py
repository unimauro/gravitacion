import pygame
import sys
import math
import numpy as np

# Inicializar pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pelota rebotando en hexágono giratorio")

# Colores
BLACK = (0, 0, 0)
BLUE = (65, 105, 225)
RED = (255, 107, 107)
WHITE = (255, 255, 255)

# Parámetros de física
FPS = 60
GRAVITY = 0.5
FRICTION = 0.99
BOUNCE_DAMPING = 0.8
ROTATION_SPEED = 0.01

# Clase para la pelota
class Ball:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_x = 0
        self.velocity_y = 0
        self.color = RED
    
    def update(self):
        # Aplicar gravedad
        self.velocity_y += GRAVITY
        
        # Aplicar fricción
        self.velocity_x *= FRICTION
        self.velocity_y *= FRICTION
        
        # Actualizar posición
        self.x += self.velocity_x
        self.y += self.velocity_y
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Clase para el hexágono
class Hexagon:
    def __init__(self, center_x, center_y, radius=200):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.rotation = 0
        self.color = BLUE
        self.vertices = self.calculate_vertices()
    
    def calculate_vertices(self):
        vertices = []
        for i in range(6):
            angle = self.rotation + i * (2 * math.pi / 6)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def update(self):
        self.rotation += ROTATION_SPEED
        self.vertices = self.calculate_vertices()
    
    def draw(self):
        pygame.draw.polygon(screen, self.color, self.vertices, 3)

# Función para comprobar colisión entre la pelota y un segmento de línea
def check_collision(ball, p1, p2):
    # Vector de la línea
    line_vector = (p2[0] - p1[0], p2[1] - p1[1])
    line_length = math.sqrt(line_vector[0]**2 + line_vector[1]**2)
    line_unit = (line_vector[0] / line_length, line_vector[1] / line_length)
    
    # Vector desde p1 a la pelota
    to_ball = (ball.x - p1[0], ball.y - p1[1])
    
    # Proyección de to_ball sobre line_unit
    projection_length = to_ball[0] * line_unit[0] + to_ball[1] * line_unit[1]
    
    # Punto más cercano en la línea a la pelota
    if projection_length < 0:
        closest_point = p1
    elif projection_length > line_length:
        closest_point = p2
    else:
        closest_point = (
            p1[0] + line_unit[0] * projection_length,
            p1[1] + line_unit[1] * projection_length
        )
    
    # Distancia entre la pelota y el punto más cercano
    dist_x = ball.x - closest_point[0]
    dist_y = ball.y - closest_point[1]
    distance = math.sqrt(dist_x**2 + dist_y**2)
    
    # Si hay colisión
    if distance <= ball.radius:
        # Vector normal al segmento (perpendicular)
        normal = (-line_unit[1], line_unit[0])
        
        # Asegurarse de que la normal apunta hacia la pelota
        dot_product = normal[0] * dist_x + normal[1] * dist_y
        if dot_product < 0:
            normal = (-normal[0], -normal[1])
        
        # Mover la pelota fuera del segmento
        overlap = ball.radius - distance
        ball.x += normal[0] * overlap
        ball.y += normal[1] * overlap
        
        # Calcular la componente de la velocidad en la dirección normal
        velocity_normal = ball.velocity_x * normal[0] + ball.velocity_y * normal[1]
        
        # Aplicar rebote solo si la pelota se está moviendo hacia el segmento
        if velocity_normal < 0:
            # Reflejar la velocidad en la dirección normal y aplicar amortiguación
            ball.velocity_x -= 2 * velocity_normal * normal[0] * BOUNCE_DAMPING
            ball.velocity_y -= 2 * velocity_normal * normal[1] * BOUNCE_DAMPING
            
            return True
    
    return False

# Inicializar objetos
ball = Ball(WIDTH//2, HEIGHT//2)
hexagon = Hexagon(WIDTH//2, HEIGHT//2)

# Dar un impulso inicial a la pelota
ball.velocity_x = 5
ball.velocity_y = -8

# Reloj para controlar FPS
clock = pygame.time.Clock()

# Bucle principal
running = True
while running:
    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Actualizar objetos
    ball.update()
    hexagon.update()
    
    # Comprobar colisiones con los lados del hexágono
    for i in range(6):
        p1 = hexagon.vertices[i]
        p2 = hexagon.vertices[(i + 1) % 6]
        check_collision(ball, p1, p2)
    
    # Dibujar
    screen.fill(BLACK)
    hexagon.draw()
    ball.draw()
    
    # Mostrar información
    font = pygame.font.SysFont(None, 24)
    info_text = f"Velocidad X: {ball.velocity_x:.2f}, Velocidad Y: {ball.velocity_y:.2f}"
    text_surface = font.render(info_text, True, WHITE)
    screen.blit(text_surface, (10, 10))
    
    # Actualizar la pantalla
    pygame.display.flip()
    
    # Controlar la velocidad del juego
    clock.tick(FPS)

# Salir de pygame
pygame.quit()
sys.exit()
