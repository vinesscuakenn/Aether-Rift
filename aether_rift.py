import pygame
import random
import math
import asyncio
import platform
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aether Rift")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Game settings
PLAYER_SIZE = 20
GUARDIAN_SIZE = 25
PORTAL_SIZE = 15
PLAYER_SPEED = 4
GUARDIAN_SPEED = 2
PORTAL_ACTIVATION_RANGE = 50
FPS = 60

class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, keys: pygame.key.ScancodeWrapper):
        if keys[pygame.K_LEFT] and self.x > PLAYER_SIZE:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.x < WIDTH - PLAYER_SIZE:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.y > PLAYER_SIZE:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.y < HEIGHT - PLAYER_SIZE:
            self.y += PLAYER_SPEED

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), PLAYER_SIZE // 2)

class Guardian:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self, player_x: int, player_y: int):
        # Guardians move randomly unless player is close
        distance = math.hypot(player_x - self.x, player_y - self.y)
        if distance < 200:
            self.angle = math.atan2(player_y - self.y, player_x - self.x)
        else:
            self.angle += random.uniform(-0.1, 0.1)
        self.x += math.cos(self.angle) * GUARDIAN_SPEED
        self.y += math.sin(self.angle) * GUARDIAN_SPEED
        # Keep guardians within bounds
        self.x = max(GUARDIAN_SIZE, min(WIDTH - GUARDIAN_SIZE, self.x))
        self.y = max(GUARDIAN_SIZE, min(HEIGHT - GUARDIAN_SIZE, self.y))

    def draw(self):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), GUARDIAN_SIZE // 2)

class Portal:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.active = False

    def draw(self):
        color = PURPLE if self.active else WHITE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), PORTAL_SIZE // 2)

class Game:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.guardians: List[Guardian] = [Guardian(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(3)]
        self.portals: List[Portal] = []
        self.energy = 0
        self.font = pygame.font.SysFont("arial", 24)
        self.clock = pygame.time.Clock()
        self.portal_spawn_rate = 0.02
        self.setup_portals()

    def setup_portals(self):
        for _ in range(5):
            while True:
                x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
                too_close = False
                for portal in self.portals:
                    if math.hypot(x - portal.x, y - portal.y) < 100:
                        too_close = True
                        break
                if not too_close:
                    self.portals.append(Portal(x, y))
                    break

    def activate_portals(self):
        player_rect = pygame.Rect(self.player.x - PLAYER_SIZE // 2, self.player.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for portal in self.portals:
            if not portal.active:
                distance = math.hypot(self.player.x - portal.x, self.player.y - portal.y)
                if distance < PORTAL_ACTIVATION_RANGE:
                    portal.active = True
                    self.energy += 20

    def check_collisions(self) -> bool:
        player_rect = pygame.Rect(self.player.x - PLAYER_SIZE // 2, self.player.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for guardian in self.guardians:
            guardian_rect = pygame.Rect(guardian.x - GUARDIAN_SIZE // 2, guardian.y - GUARDIAN_SIZE // 2, GUARDIAN_SIZE, GUARDIAN_SIZE)
            if player_rect.colliderect(guardian_rect):
                return False
        return True

    def check_win_condition(self) -> bool:
        return all(portal.active for portal in self.portals)

    def draw(self):
        screen.fill(BLACK)
        self.player.draw()
        for guardian in self.guardians:
            guardian.draw()
        for portal in self.portals:
            portal.draw()
        energy_text = self.font.render(f"Energy: {self.energy}", True, WHITE)
        screen.blit(energy_text, (10, 10))
        portals_active = sum(1 for portal in self.portals if portal.active)
        portal_text = self.font.render(f"Portals: {portals_active}/{len(self.portals)}", True, WHITE)
        screen.blit(portal_text, (10, 40))

async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        game.player.move(keys)
        game.activate_portals()
        for guardian in game.guardians:
            guardian.move(game.player.x, game.player.y)
        if not game.check_collisions():
            running = False
        if game.check_win_condition():
            running = False  # Win condition
        if random.random() < game.portal_spawn_rate and len(game.portals) < 10:
            game.setup_portals()
        game.draw()
        pygame.display.flip()
        game.clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
