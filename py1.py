import pygame
import random
import sqlite3

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PLAYER_SIZE = 50
MONSTER_SIZE = 50
HEART_SIZE = 20
PLAYER_SPEED = 5
MONSTER_SPEED = 2
HEART_SPEED = 10

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the player
player = pygame.Rect(WIDTH / 2, HEIGHT / 2, PLAYER_SIZE, PLAYER_SIZE)

# Set up the monsters
monsters = [pygame.Rect(random.choice([-MONSTER_SIZE, WIDTH]), random.randint(0, HEIGHT - MONSTER_SIZE), MONSTER_SIZE, MONSTER_SIZE) for _ in range(10)]

# Set up the heart
heart = pygame.Rect(-HEART_SIZE, random.randint(0, HEIGHT - HEART_SIZE), HEART_SIZE, HEART_SIZE)
heart_appear_time = 0

# Set up the game variables
lives = 1
score = 0
best_score = 0

# Connect to the database
conn = sqlite3.connect('survival_game.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS scores (score REAL)')
conn.commit()

# Get the best score from the database
c.execute('SELECT MAX(score) FROM scores')
row = c.fetchone()
if row[0] is not None:
    best_score = row[0]

# Game loop
running = True
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        player.y += PLAYER_SPEED
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED

    # Move the monsters
    for monster in monsters:
        if monster.x < player.x:
            monster.x += MONSTER_SPEED
        elif monster.x > player.x:
            monster.x -= MONSTER_SPEED
        if monster.y < player.y:
            monster.y += MONSTER_SPEED
        elif monster.y > player.y:
            monster.y -= MONSTER_SPEED

    # Check for collisions with monsters
    for monster in monsters:
        if player.colliderect(monster):
            if lives > 0:
                lives -= 1
            else:
                running = False

    # Move the heart
    if heart.x < WIDTH:
        heart.x += HEART_SPEED
    else:
        heart.x = -HEART_SIZE
        heart.y = random.randint(0, HEIGHT - HEART_SIZE)
        heart_appear_time = pygame.time.get_ticks() + 30000

    # Check for collision with the heart
    if player.colliderect(heart):
        lives += 1
        heart.x = -HEART_SIZE
        heart.y = random.randint(0, HEIGHT - HEART_SIZE)
        heart_appear_time = pygame.time.get_ticks() + 30000

    # Check if the heart should appear
    if pygame.time.get_ticks() > heart_appear_time:
        heart.x = -HEART_SIZE
        heart.y = random.randint(0, HEIGHT - HEART_SIZE)
        heart_appear_time = pygame.time.get_ticks() + 30000

    # Check if the monsters should speed up
    if pygame.time.get_ticks() - start_time > 10000:
        MONSTER_SPEED += 1
        start_time = pygame.time.get_ticks()

    # Check if new monsters should be added
    if len(monsters) < 10 + (pygame.time.get_ticks() - start_time) // 10000:
        monsters.append(pygame.Rect(random.choice([-MONSTER_SIZE, WIDTH]), random.randint(0, HEIGHT - MONSTER_SIZE), MONSTER_SIZE, MONSTER_SIZE))

    # Remove monsters that are off the screen
    monsters = [monster for monster in monsters if 0 < monster.x < WIDTH]

    # Draw everything
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, WHITE, player)
    for monster in monsters:
        pygame.draw.rect(screen, WHITE, monster)
    pygame.draw.rect(screen, RED, heart)
    text = font.render(f'Time: {(pygame.time.get_ticks() - start_time) / 1000:.2f} seconds', True, WHITE)
    screen.blit(text, (10, 10))
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Save the score to the database
c.execute('INSERT INTO scores VALUES (?)', ((pygame.time.get_ticks() - start_time) / 1000,))
conn.commit()

# Get the best score from the database
c.execute('SELECT MAX(score) FROM scores')
row = c.fetchone()
if row[0] is not None:
    best_score = row[0]

# Show the game over screen
screen.fill((0, 0, 0))
text = font.render('Game Over', True, WHITE)
screen.blit(text, (WIDTH / 2 - 50, HEIGHT / 2 - 50))
text = font.render(f'You survived for {(pygame.time.get_ticks() - start_time) / 1000:.2f} seconds', True, WHITE)
screen.blit(text, (WIDTH / 2 - 100, HEIGHT / 2))
text = font.render(f'Best survival time: {best_score:.2f} seconds', True, WHITE)
screen.blit(text, (WIDTH / 2 - 100, HEIGHT / 2 + 50))
pygame.display.flip()
pygame.time.wait(2000)

# Quit Pygame
pygame.quit()
