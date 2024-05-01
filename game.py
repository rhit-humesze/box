import pygame
import random
import sys
import string


class Game:
    def __init__(self, width=600, height=400):
        '''initialize game'''
        pygame.init()
        self.WIDTH:  int = width
        self.HEIGHT: int = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pygame.font.SysFont(None, 36)
        pygame.display.set_caption("Box")

    def generate_code(self):
        '''generates a random 6-digit alphanumeric code'''
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    # Main loop
    def game_loop(self):
        running = True
        start_button_visible = True
        code_generated = False
        generated_code = None

        while running:
            self.screen.fill(pygame.Color('white'))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button_visible:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if self.WIDTH / 2 - 50 <= mouse_x <= self.WIDTH / 2 + 50 and self.HEIGHT / 2 - 25 <= mouse_y <= self.HEIGHT / 2 + 25:
                            generated_code = self.generate_code()
                            start_button_visible = False
                            code_generated = True
                    else:
                        # Do something else when code is generated (if needed)
                        pass

            if start_button_visible:
                # Display "START" button
                pygame.draw.rect(self.screen, pygame.Color('black'), (self.WIDTH / 2 - 50, self.HEIGHT / 2 - 25, 100, 50))
                start_text = self.font.render("START", True, pygame.Color('white'))
                start_rect = start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
                self.screen.blit(start_text, start_rect)
            elif code_generated:
                # Display generated code
                text = self.font.render("Enter code: " + generated_code, True, pygame.Color('black'))
                text_rect = text.get_rect(center=(self.WIDTH // 2, 50))
                self.screen.blit(text, text_rect)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# if __name__ == "__main__":
#     game = Game()
#     game.game_loop()
