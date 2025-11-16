import pygame
import sys
import random
import os
import json
from pygame.locals import *

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Brick Break - Quebre os Tijolos!')

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Configurações do jogo
FPS = 60
clock = pygame.time.Clock()

# Arquivo para salvar o ranking
RANKING_FILE = "ranking.json"

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        self.color = BLUE
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = 5 * random.choice([-1, 1])
        self.dy = -5
        self.color = RED
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # Colisão com as paredes
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius:
            self.dy *= -1
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.dx = 5 * random.choice([-1, 1])
        self.dy = -5

class Brick:
    def __init__(self, x, y, color, points):
        self.width = 80
        self.height = 30
        self.x = x
        self.y = y
        self.color = color
        self.points = points
        self.visible = True
    
    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_state = "menu"  # menu, playing, game_over
        self.player_name = ""
        self.create_bricks()
    
    def create_bricks(self):
        self.bricks = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        points = [10, 8, 6, 4, 2, 1]
        
        for row in range(6):
            for col in range(9):
                brick_x = col * 85 + 20
                brick_y = row * 35 + 50
                self.bricks.append(Brick(brick_x, brick_y, colors[row], points[row]))
    
    def check_collisions(self):
        # Colisão com a raquete
        if (self.ball.y + self.ball.radius >= self.paddle.y and 
            self.ball.x >= self.paddle.x and 
            self.ball.x <= self.paddle.x + self.paddle.width and
            self.ball.dy > 0):
            
            # Ajusta a direção da bola baseado na posição de impacto na raquete
            relative_intersect_x = (self.paddle.x + (self.paddle.width / 2)) - self.ball.x
            normalized_relative_intersect_x = relative_intersect_x / (self.paddle.width / 2)
            bounce_angle = normalized_relative_intersect_x * 0.8  # Limita o ângulo
            
            self.ball.dx = -bounce_angle * 7
            self.ball.dy *= -1
        
        # Colisão com os tijolos
        for brick in self.bricks:
            if brick.visible:
                if (self.ball.x + self.ball.radius >= brick.x and 
                    self.ball.x - self.ball.radius <= brick.x + brick.width and
                    self.ball.y + self.ball.radius >= brick.y and 
                    self.ball.y - self.ball.radius <= brick.y + brick.height):
                    
                    brick.visible = False
                    self.score += brick.points
                    
                    # Determina de qual lado a bola colidiu
                    if (self.ball.x < brick.x or self.ball.x > brick.x + brick.width):
                        self.ball.dx *= -1
                    else:
                        self.ball.dy *= -1
                    
                    break
        
        # Verifica se a bola caiu
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives > 0:
                self.ball.reset()
            else:
                self.game_state = "game_over"
                self.save_score()
        
        # Verifica se todos os tijolos foram quebrados
        if all(not brick.visible for brick in self.bricks):
            self.level += 1
            self.create_bricks()
            self.ball.reset()
            self.paddle.width = max(50, self.paddle.width - 10)  # Diminui a raquete a cada nível
    
    def save_score(self):
        # Carrega o ranking existente
        ranking = self.load_ranking()
        
        # Adiciona a nova pontuação
        ranking.append({"name": self.player_name, "score": self.score})
        
        # Ordena por pontuação (maior primeiro)
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        # Mantém apenas os 10 melhores
        ranking = ranking[:10]
        
        # Salva no arquivo
        with open(RANKING_FILE, 'w') as f:
            json.dump(ranking, f)
    
    def load_ranking(self):
        if os.path.exists(RANKING_FILE):
            with open(RANKING_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def draw_menu(self):
        # Fundo
        screen.fill(BLACK)
        
        # Título
        font_title = pygame.font.SysFont('Arial', 64)
        title_text = font_title.render('BRICK BREAK', True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Instruções
        font_instructions = pygame.font.SysFont('Arial', 24)
        instructions = [
            "Use as teclas ← → para mover a raquete",
            "Pressione ESPAÇO para iniciar o jogo",
            "Quebre todos os tijolos para avançar de nível"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_instructions.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i*40))
        
        # Ranking
        ranking = self.load_ranking()
        if ranking:
            font_ranking = pygame.font.SysFont('Arial', 28)
            ranking_title = font_ranking.render("TOP PONTUAÇÕES:", True, YELLOW)
            screen.blit(ranking_title, (SCREEN_WIDTH//2 - ranking_title.get_width()//2, 400))
            
            for i, entry in enumerate(ranking[:5]):
                rank_text = font_instructions.render(f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE)
                screen.blit(rank_text, (SCREEN_WIDTH//2 - rank_text.get_width()//2, 440 + i*30))
    
    def draw_game_over(self):
        # Fundo
        screen.fill(BLACK)
        
        # Título
        font_title = pygame.font.SysFont('Arial', 64)
        title_text = font_title.render('FIM DE JOGO', True, RED)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # Pontuação
        font_score = pygame.font.SysFont('Arial', 36)
        score_text = font_score.render(f'Pontuação: {self.score}', True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))
        
        # Instruções
        font_instructions = pygame.font.SysFont('Arial', 24)
        instructions = [
            "Pressione R para jogar novamente",
            "Pressione M para voltar ao menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_instructions.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300 + i*40))
    
    def draw_playing(self):
        # Fundo
        screen.fill(BLACK)
        
        # Desenha elementos do jogo
        self.paddle.draw()
        self.ball.draw()
        
        for brick in self.bricks:
            brick.draw()
        
        # Informações do jogo
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f'Pontuação: {self.score}', True, WHITE)
        lives_text = font.render(f'Vidas: {self.lives}', True, WHITE)
        level_text = font.render(f'Nível: {self.level}', True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 10))
    
    def draw(self):
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.draw_playing()
        elif self.game_state == "game_over":
            self.draw_game_over()
    
    def update(self):
        if self.game_state == "playing":
            self.ball.move()
            self.check_collisions()
    
    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.create_bricks()

def main():
    game = Game()
    input_active = False
    
    # Loop principal do jogo
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if game.game_state == "menu":
                    if event.key == K_SPACE:
                        game.game_state = "playing"
                
                elif game.game_state == "playing":
                    if event.key == K_ESCAPE:
                        game.game_state = "menu"
                
                elif game.game_state == "game_over":
                    if event.key == K_r:
                        game.reset_game()
                        game.game_state = "playing"
                    if event.key == K_m:
                        game.reset_game()
                        game.game_state = "menu"
        
        # Movimento contínuo da raquete
        keys = pygame.key.get_pressed()
        if game.game_state == "playing":
            if keys[K_LEFT]:
                game.paddle.move("left")
            if keys[K_RIGHT]:
                game.paddle.move("right")
        
        # Atualiza e desenha o jogo
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()