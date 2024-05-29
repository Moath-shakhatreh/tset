import pygame
import random
import sqlite3
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up the title of the window
pygame.display.set_caption("Survival Game")

# Set up the player
player = pygame.Rect(screen_width / 2, screen_height / 2, 50, 50)

# Set up the monsters
monsters = [pygame.Rect(random.choice([-100, screen_width]), random.randint(0, screen_height), 50, 50) for _ in range(5)]

# Set up the red heart
red_heart = pygame.Rect(-100, random.randint(0, screen_height), 50, 50)

# Set up the timer
start_time = time.time()
font = pygame.font.Font(None, 36)

# Set up the survival time
survival_time = 0
best_survival_time = 0

# Connect to the database
conn = sqlite3.connect("survival_game.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS survival_time (time REAL)")
conn.commit()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.y -= 5
    if keys[pygame.K_DOWN]:
        player.y += 5
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5

    # Move the monsters
    for monster in monsters:
        if monster.x < 0:
            monster.x = screen_width
        elif monster.x > screen_width:
            monster.x = -100
        else:
            monster.x += random.choice([-5, 5])

    # Move the red heart
    if red_heart.x < 0:
        red_heart.x = screen_width
    else:
        red_heart.x -= 10

    # Collision detection
    for monster in monsters:
        if player.colliderect(monster):
            survival_time = time.time() - start_time
            cursor.execute("INSERT INTO survival_time VALUES (?)", (survival_time,))
            conn.commit()
            cursor.execute("SELECT MAX(time) FROM survival_time")
            best_survival_time = cursor.fetchone()[0]
            print(f"Game over! Survival time: {survival_time:.2f} seconds. Best survival time: {best_survival_time:.2f} seconds.")
            running = False

    # Draw everything
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 255), player)
    for monster in monsters:
        pygame.draw.rect(screen, (255, 0, 0), monster)
    pygame.draw.rect(screen, (255, 0, 0), red_heart)
    timer_text = font.render(f"Survival time: {time.time() - start_time:.2f} seconds", True, (0, 0, 0))
    screen.blit(timer_text, (10, 10))
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.delay(1000 // 60)

# Quit Pygame
pygame.quit()
