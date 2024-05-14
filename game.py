import pygame
import random
import sys
import string
from queue import Queue

from host import Host

highlightColor = "#88BABA"
fontColor = "#3F88C8"
darkColor = "#512929"
medColor = "#D38433"
lightColor = "#E6C25D"

assetPath = 'client_website/public/assets/'

class Game:
    def __init__(self, code, join_q: Queue, disc_q: Queue, width=1200, height=800):
        '''initialize Game'''
        pygame.init()
        self.WIDTH:  int = width
        self.HEIGHT: int = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Box")
        self.game_state: str = 'start-screen'
        self.running = False
        self.code = code
        self.players = {}
        self._circle_cache = {}

        self.join_q = join_q
        self.disc_q = disc_q
    
    # font outlining provided by https://stackoverflow.com/questions/54363047/how-to-draw-outline-on-the-fontpygame
    def _circlepoints(self, r):
        self._circle_cache = {}
        r = int(round(r))
        if r in self._circle_cache:
            return self._circle_cache[r]
        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    def renderText(self, text, textcolor, textsize, outlinecolor, outlinewidth):
        font = pygame.font.SysFont("lucida console", textsize)
        textsurface = font.render(text, True, pygame.Color(textcolor)).convert_alpha()
        w = textsurface.get_width() + 2 * outlinewidth
        h = font.get_height()

        osurf = pygame.Surface((w, h + 2 * outlinewidth)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()

        osurf.blit(font.render(text, True, pygame.Color(outlinecolor)).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(outlinewidth):
            surf.blit(osurf, (dx + outlinewidth, dy + outlinewidth))

        surf.blit(textsurface, (outlinewidth, outlinewidth))
        return surf

    def handle_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == 'start-screen':
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if self.WIDTH / 2 - 60 <= mouse_x <= self.WIDTH / 2 + 60 and self.HEIGHT / 2 - 35 <= mouse_y <= self.HEIGHT / 2 + 35:
                            self.game_state = 'code-screen'
                    elif self.game_state == 'code-screen':
                        pass
                    else:
                        #for future
                        pass

    def recv_players(self):
        '''get player names from the message queue and add them'''
        while not self.join_q.empty():
            player_dict_entry = self.join_q.get()
            self.players.update(player_dict_entry)

    def check_disc_players(self):
        '''checks if a player has disconnected and removes them'''
        while not self.disc_q.empty():
            sid = self.disc_q.get()
            self.players.pop(sid)

    def game_loop(self):
        '''main loop for the game screen'''
        self.running = True

        while self.running:
            # create background image tiling
            self.fillWindowBg()

            self.handle_events()
            
            if self.game_state == 'start-screen':
                pygame.draw.rect(self.screen, pygame.Color(fontColor), (self.WIDTH / 2 - 60, self.HEIGHT / 2 - 35, 120, 70))
                pygame.draw.rect(self.screen, pygame.Color(highlightColor), (self.WIDTH / 2 - 50, self.HEIGHT / 2 - 25, 100, 50))
                start_text = self.renderText("START", darkColor, 32, fontColor, 2)
                start_rect = start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
                self.screen.blit(start_text, start_rect)
            elif self.game_state == 'code-screen':
                self.createPanelBg(40, 40, self.WIDTH - 80, self.HEIGHT - 80, 10)
                self.recv_players()
                self.check_disc_players()
                # Display generated code
                text = self.renderText("Box code: " + self.code, fontColor, 64, darkColor, 3)
                text_rect = text.get_rect(center=(self.WIDTH // 2, 100))
                self.screen.blit(text, text_rect)
                
                for idx, (sid, player_name) in enumerate(self.players.items()):
                    player_text = self.renderText(player_name, fontColor, 48, darkColor, 3)
                    player_rect = player_text.get_rect(center=(self.WIDTH // 2, 100 + idx * 30))
                    self.screen.blit(player_text, player_rect)
                
            pygame.display.flip()

        self.stop()

    def stop(self):
        pygame.quit()
        sys.exit()

    def fillWindowBg(self):
        self.screen.fill(pygame.Color(medColor))
        bgTile = pygame.image.load(assetPath + 'box_tile.png')
        bgTile_w, bgTile_h = bgTile.get_size()
        for x in range(0, self.WIDTH, bgTile_w):
            for y in range(0, self.HEIGHT, bgTile_h):
                self.screen.blit(bgTile, (x, y))

    def createPanelBg(self, xpos, ypos, width, height, outlinewidth):
        pygame.draw.rect(self.screen, pygame.Color(darkColor), (xpos, ypos, width, height))
        panelBg = pygame.image.load(assetPath + 'box_panel.png')
        panelBg = pygame.transform.scale(panelBg, (width + xpos, height + ypos))
        self.screen.blit(panelBg, (xpos + outlinewidth, ypos + outlinewidth), (xpos + outlinewidth, ypos + outlinewidth, width - 2 * outlinewidth, height - 2 * outlinewidth))
