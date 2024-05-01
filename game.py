import pygame
import random
import sys
import string

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Function to generate a random 6-digit code
def generate_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Code Generator")

# Font
font = pygame.font.SysFont(None, 36)

# Main loop
def main():
    running = True
    start_button_visible = True
    code_generated = False
    generated_code = None

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_visible:
                    # Check if the mouse click is on the "START" button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if WIDTH / 2 - 50 <= mouse_x <= WIDTH / 2 + 50 and HEIGHT / 2 - 25 <= mouse_y <= HEIGHT / 2 + 25:
                        # Generate code and hide "START" button
                        generated_code = generate_code()
                        start_button_visible = False
                        code_generated = True
                else:
                    # Do something else when code is generated (if needed)
                    pass

        if start_button_visible:
            # Display "START" button
            pygame.draw.rect(screen, BLACK, (WIDTH / 2 - 50, HEIGHT / 2 - 25, 100, 50))
            start_text = font.render("START", True, WHITE)
            start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start_text, start_rect)
        elif code_generated:
            # Display generated code
            text = font.render("Enter code: " + generated_code, True, BLACK)
            text_rect = text.get_rect(center=(WIDTH // 2, 50))
            screen.blit(text, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
