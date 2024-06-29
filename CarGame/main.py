import random
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Creating the window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Car game")

# Colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# Game settings
gameover = False
speed = 2
score = 0

# Marker Size
marker_width = 10
marker_height = 50

# Road and edge markers
road = (100, 0, 300, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# X: Coordinates of lanes
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# For animating movement of the lane marker
lane_marker_move_y = 0

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        super().__init__()
        
        # Scale the image down so it's not wider than the lane
        image_scale = 45 / image.get_rect().width
        new_width = int(image.get_rect().width * image_scale)
        new_height = int(image.get_rect().height * image_scale)
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load('Cargame/images/car.png').convert_alpha()  # Corrected image path
        super().__init__(image, x, y)

# Create the starting position
player_x = 250
player_y = 400

# Create the player's car
player_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# Load the other vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('Cargame/images/' + image_filename).convert_alpha()
    vehicle_images.append(image)

# Sprite group for vehicles
vehicle_group = pygame.sprite.Group()

# Load the crash image
crash = pygame.image.load('Cargame/images/crash.png').convert_alpha()
crash_rect = crash.get_rect()

# Load sounds
point_sound = pygame.mixer.Sound('Cargame/point.wav')
point_sound.set_volume(1.0)  # Ensure the volume is set appropriately

crash_sound = pygame.mixer.Sound('Cargame/Crash.wav')
crash_sound.set_volume(1.0)  # Ensure the volume is set appropriately

# Game loop
clock = pygame.time.Clock()
FPS = 120
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100

            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    gameover = True
                    # Place the player's car next to other vehicle
                    # and determine where to position the crash image
                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

    # Draw the grass
    screen.fill(green)

    # Draw the road
    pygame.draw.rect(screen, gray, road)

    # Draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
   
    # Draw the lane markers
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0

    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))   

    # Draw the player's car
    player_group.draw(screen)

    # Add up to two vehicles
    if len(vehicle_group) < 2:
        # Ensure there's enough gap
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False
        
        if add_vehicle:
            # Select a random lane
            lane = random.choice(lanes)
            # Select a random vehicle image
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        # Remove the vehicle once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()
            # Add score 
            point_sound.play()
            score += 1
            # Speed up the game after passing 8 vehicles
            if score > 0 and score % 8 == 0:
                speed += 1

    # Draw the vehicles
    vehicle_group.draw(screen)

    # Display the score
    font = pygame.font.Font(None, 16)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, 450)
    screen.blit(text, text_rect)

    # Check if there's a head-on collision
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]
            
    # Display game over
    if gameover:
        crash_sound.play()
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

    pygame.display.update()

    # Wait for user's input to play again or exit
    while gameover:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False
            # Get the user's input (y or n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # Reset the game
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # Exit the loops
                    gameover = False
                    running = False

pygame.quit()