import pygame
import random
import sys
import string
from queue import Queue
from typing import Tuple

from host import Host
from models import DrawingData

highlightColor = "#88BABA"
fontColor = "#3F88C8"
darkColor = "#512929"
medColor = "#D38433"
lightColor = "#E6C25D"

assetPath = 'client_website/public/assets/'

class Game:
    def __init__(self, code, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue,
                 width=1200, height=800):
        '''initialize Game'''
        pygame.init()
        self.WIDTH:  int = width
        self.HEIGHT: int = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Box")
        pygame.mixer.init()
        pygame.mixer.music.load(f"{assetPath}music_light_funky.mp3")
        pygame.mixer.music.set_volume(0.7) 
        pygame.mixer.music.play(loops=-1)
        self.newMusic = False
        self.game_state: str = 'start-screen'
        self.running = False
        self.code = code
        self.players = {}
        self.drawings = {}
        self.drawing_votes = {}

        self.start_ticks_lock = False

        #drawing game bools
        self.left_occupied = False
        self.right_occupied = False
        self.round_over = False
        self.intermission_over = True
        self.broadcast_vote = False

        #drawing game vars
        self.left_drawing = None
        self.right_drawing = None
        self.left_sid = None
        self.right_sid = None
        self.round_time = 0
        self.intermission_time = 0
        self.draw_some_winner = DrawingData('test_img3.png', 'test3', 'big kimmy j')

        self._circle_cache = {}
        self.clock = pygame.time.Clock()
        self.start_ticks = 0

        #intake queues
        self.join_q = join_q
        self.disc_q = disc_q
        self.draw_q = draw_q
        self.vote_q = vote_q

        #msg queue
        self.msg_q = msg_q

    
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
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.game_state == 'start-screen':
                        if self.check_within_bounds((self.WIDTH / 2 - 60, self.HEIGHT / 2 - 35), (120, 70), mouse_x, mouse_y, "topleft"):
                            self.game_state = 'code-screen'
                    elif self.game_state == 'code-screen':
                        if len(self.players) >= 3 and self.check_within_bounds((800,100),(280,120), mouse_x, mouse_y, "topleft"):
                            self.game_state = 'select-screen'
                    elif self.game_state == 'select-screen':
                        if self.check_within_bounds((300,400),(280,120), mouse_x, mouse_y, "center"):
                            self.start_ticks = pygame.time.get_ticks()
                            #send msg to host
                            self.msg_q.put(0)
                            self.game_state = 'draw-some-screen'
                            self.newMusic = False
                    else:
                        pass
        

    def check_within_bounds(self, coords: Tuple[float, float], width_height: Tuple[float, float], posx, posy, method: str) -> bool:
        '''checks whether floats x and y are within given bounds. 'method' specifies if the provided coords are the center of the bounding box or the top left.'''
        width=width_height[0]
        height=width_height[1]
        cx = coords[0]
        cy = coords[1]
        
        if method == "topleft":
            cx = cx + width / 2
            cy = cy + height / 2
        elif method != "center":
            print("Error: Method must be specified as either 'topleft' or 'center'.")
            pass 

        return cx - width / 2 <= posx <= cx + width / 2 and cy - height / 2 <= posy <= cy + height / 2 


    def create_button(self, coords: Tuple[float, float], width_height: Tuple[float, float], text="", 
                      btn_color=highlightColor, highlight_color=darkColor, text_color=fontColor, text_highlight=darkColor, 
                      method="topleft", font_size=32):
        '''draws button rectangles at specified coordinates'''
        if method == "topleft":
            center = (coords[0] + width_height[0] / 2, coords[1] + width_height[1] / 2)
            inner_rec = pygame.Rect((coords[0] + 5, coords[1] + 5), (width_height[0] - 10, width_height[1] - 10))
            outer_rec = pygame.Rect(coords, width_height)
            pygame.draw.rect(self.screen, highlight_color, outer_rec)
            pygame.draw.rect(self.screen, btn_color, inner_rec)
            temp_text = self.renderText(text, text_color, font_size, text_highlight, 2)
            temp_rect = temp_text.get_rect(center=center)
            self.screen.blit(temp_text, temp_rect)
        elif method == "center":
            topleft = (coords[0] - width_height[0] / 2, coords[1] - width_height[1] / 2)
            inner_rec = pygame.Rect((topleft[0] + 5, topleft[1] + 5), (width_height[0] - 10, width_height[1] - 10))
            outer_rec = pygame.Rect(topleft, width_height)
            pygame.draw.rect(self.screen, highlight_color, outer_rec)
            pygame.draw.rect(self.screen, btn_color, inner_rec)
            temp_text = self.renderText(text, text_color, font_size, text_highlight, 2)
            temp_rect = temp_text.get_rect(center=coords)
            self.screen.blit(temp_text, temp_rect)
        else:
            print("Error: Method must be either 'topleft' or 'center'.")
            return
        return
    
    def timer(self, start_time, coords, font_size) -> int:
        '''creates and runs a timer object. returns the time remaining.'''
        elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        elapsed_seconds = elapsed_ticks // 1000
        time_left = start_time - elapsed_seconds
        if elapsed_seconds >= 0:
            timer_text = self.renderText(f"{time_left}", fontColor, font_size, darkColor, 3)
            text_rect = timer_text.get_rect(center=coords)
            self.screen.blit(timer_text, text_rect)
        return time_left

    def recv_players(self):
        '''get player names from the message queue and add them'''
        while not self.join_q.empty():
            player_dict_entry = self.join_q.get()
            self.players.update(player_dict_entry)

    def recv_drawings(self):
        while not self.draw_q.empty():
            img_dict_entry = self.draw_q.get()
            self.drawings.update(img_dict_entry)

    def check_disc_players(self):
        '''checks if a player has disconnected and removes them'''
        while not self.disc_q.empty():
            sid = self.disc_q.get()
            self.players.pop(sid)

    def game_loop(self):
        '''main loop for the game screen'''
        self.running = True
        ### DEBUGGING PURPOSES ###
        # for i in range(1, 4):
        #     self.drawings.update({i:DrawingData('test_img' + str(i) + '.png', 'test' + str(i), 'player')})
        # print(len(self.drawings))
        # self.game_state = 'draw-some-won-screen'

        while self.running:
            # create background image tiling
            self.fillWindowBg()
            self.handle_events()
            
            if self.game_state == 'start-screen':
                self.create_button((self.WIDTH / 2 - 60, self.HEIGHT / 2 - 35), (120, 70), text="START")
            elif self.game_state == 'code-screen':
                self.createPanelBg(40, 40, self.WIDTH - 80, self.HEIGHT - 80, 10)
                self.recv_players()
                self.check_disc_players()
                # Display generated code
                text = self.renderText("Box #:" + self.code, fontColor, 96, darkColor, 3)
                text_rect = text.get_rect(topleft=(120,100))
                self.screen.blit(text, text_rect)
                # Check here if len players >= 3
                if len(self.players) < 3:
                    text = self.renderText("You need at least 3 players to start!", fontColor, 28, darkColor, 3)
                    text_rect = text.get_rect(topleft=(120,185))
                    self.screen.blit(text, text_rect)
                else:
                    self.create_button((800,100),(280,120),text="Start game", font_size=42)
                text = self.renderText("Players:", fontColor, 42, darkColor, 3)
                text_rect = text.get_rect(topleft=(120, 220))
                self.screen.blit(text, text_rect)
                
                #player stuff
                horizontal_spacing = 100 
                vertical_spacing = 40 
                top_margin = 270  
                left_margin = 120  
                x_pos = left_margin
                y_pos = top_margin
                row = 0
                for idx, (sid, player_name) in enumerate(self.players.items()):
                    player_text = self.renderText(player_name, fontColor, 32, darkColor, 3)
                    player_rect = player_text.get_rect()

                    if x_pos + player_rect.width > self.WIDTH - left_margin:
                        row += 1
                        x_pos = left_margin
                        y_pos = top_margin + row * vertical_spacing

                    player_rect.topleft = (x_pos, y_pos)
                    
                    self.screen.blit(player_text, player_rect)
                    x_pos += player_rect.width + horizontal_spacing
            elif self.game_state == 'select-screen':
                self.create_button((300,400),(280,80),text="Draw Some", method="center",font_size=32)
                self.create_button((900,400),(280,80),text="Box Phone", method="center",font_size=32)
            elif self.game_state == 'draw-some-screen':
                if(not self.newMusic):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(f"{assetPath}music_heavy_electric.mp3")
                    pygame.mixer.music.play(loops=-1)
                    self.newMusic = True
                text = self.renderText("Draw some!", fontColor, 128, darkColor, 3)
                text_rect = text.get_rect(center=(self.WIDTH / 2,100))
                self.screen.blit(text, text_rect)
                time_left = self.timer(120, (600,500), 400)
                self.recv_drawings()
                if time_left == 0:
                    self.msg_q.put(1)
                    self.game_state = "draw-some-tournament-screen"
                    self.newMusic = False
                    self.start_ticks = pygame.time.get_ticks()
            elif self.game_state == "draw-some-tournament-screen":
                if(not self.newMusic):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(f"{assetPath}music_light_electric.mp3")
                    pygame.mixer.music.play(loops=-1)
                    self.newMusic = True
                self.draw_some_tournament()
            elif self.game_state == "draw-some-won-screen":
                if(not self.newMusic):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(f"{assetPath}music_light_funky.mp3")
                    pygame.mixer.music.play(loops=-1)
                    self.newMusic = True
                text = self.renderText("Winner: " + self.draw_some_winner.player_name + "!", fontColor, 80, darkColor, 3)
                text_rect = text.get_rect(center=(self.WIDTH / 2,100))
                self.screen.blit(text, text_rect)
                border_rect = pygame.Rect(0, 0, 520, 520)
                border_rect.center = (self.WIDTH / 2, self.HEIGHT / 2 + 50)
                pygame.draw.rect(self.screen, pygame.Color(darkColor), border_rect)
                self.render_drawing(self.draw_some_winner.image, (self.WIDTH / 2, self.HEIGHT / 2 + 50), (500,500))
                text = self.renderText(self.draw_some_winner.title, fontColor, 60, darkColor, 3)
                text_rect = text.get_rect(center=(self.WIDTH / 2, 750))
                self.screen.blit(text, text_rect)
            else:
                pass
            pygame.display.flip()
            self.clock.tick(60)
        self.stop()


    def draw_some_tournament(self):
        if(len(self.drawings) == 1):
            self.msg_q.put(self.draw_some_winner.image)
            self.game_state = "draw-some-won-screen"
            self.newMusic = False
            return

        ### DEBUG ###
        # self.drawing_votes.update({1:1})

        img_rect1 = pygame.Rect(0, 0, 400, 400)
        left_center = (300, 400)
        img_rect1.center = left_center
        img_rect2 = pygame.Rect(0, 0, 400, 400)
        right_center = (900, 400)
        img_rect2.center = right_center

        pygame.draw.rect(self.screen, pygame.Color(darkColor), img_rect1)
        pygame.draw.rect(self.screen, pygame.Color(darkColor), img_rect2)

        temp_text = self.renderText("VS.", fontColor, 96, darkColor, 2)
        temp_rect = temp_text.get_rect(center=(self.WIDTH / 2, self.HEIGHT / 2))
        self.screen.blit(temp_text, temp_rect)

        if not (self.left_occupied and self.right_occupied):   
            # print(self.round_time) 
            for idx, (sid, drawing) in enumerate(self.drawings.items()):
                # print(len(self.drawings))
                if (drawing == self.left_drawing) or drawing == (self.right_drawing):
                    continue 
                if not self.left_occupied:
                    self.left_occupied = True
                    self.left_drawing = drawing
                    self.left_sid = sid
                elif not self.right_occupied:
                    self.right_occupied = True
                    self.right_drawing = drawing
                    self.right_sid = sid
                if self.right_occupied and self.left_occupied:
                    break
        
        #draw left drawing
        self.render_drawing(self.left_drawing.image, left_center, (380, 380))
        temp_text = self.renderText(self.left_drawing.title, fontColor, 64, darkColor, 2)
        temp_rect = temp_text.get_rect(center=(left_center[0], left_center[1] - 240))
        self.screen.blit(temp_text, temp_rect)

        #draw right drawing
        temp_text = self.render_drawing(self.right_drawing.image, right_center, (380, 380))
        temp_text = self.renderText(self.right_drawing.title, fontColor, 64, darkColor, 2)
        temp_rect = temp_text.get_rect(center=(right_center[0], right_center[1] - 240))
        self.screen.blit(temp_text, temp_rect)

        #recv votes
        self.recv_draw_votes()

        percent_left, percent_right = self.get_vote_percents()
        # draw percentage text
        temp_text = self.renderText(str(percent_left) + '%', fontColor, 48, darkColor, 2)
        temp_rect = temp_text.get_rect(center=(left_center[0], left_center[1] + 250))
        self.screen.blit(temp_text, temp_rect)

        temp_text = self.renderText(str(percent_right) + '%', fontColor, 48, darkColor, 2)
        temp_rect = temp_text.get_rect(center=(right_center[0], right_center[1] + 250))
        self.screen.blit(temp_text, temp_rect)

        #logic that happens while round is not done yet
        if not self.round_over:
            self.round_time = self.timer(10, (self.WIDTH / 2, 100), 96)
            temp_text = self.renderText("King of the hill! Pick your favorite!", fontColor, 48, darkColor, 2)
            temp_rect = temp_text.get_rect(center=(self.WIDTH / 2, 720))
            self.screen.blit(temp_text, temp_rect)
            #add a bool field and require it to be true for this to happen 
            if not self.broadcast_vote:
                self.msg_q.put(2)
                self.broadcast_vote = True
        else:
            #declare winner
            #0 for left 1 for right
            winner_side = None
            if percent_left < percent_right:
                winner = self.right_drawing
                winner_side = 1
            elif percent_left > percent_right:
                winner = self.left_drawing
                winner_side = 0
            else:
                winner = self.left_drawing
                winner_side = 0
            self.draw_some_winner = winner
            #wait a bit
            if not self.intermission_over:
                #disallow timer to be set
                self.start_ticks_lock = True
                self.intermission_time = self.timer(3, (0,0), 0)
                # print(self.intermission_time)
                temp_text = self.renderText("Round winner: " + winner.title + "!", fontColor, 48, darkColor, 2)
                temp_rect = temp_text.get_rect(center=(self.WIDTH / 2, 720))
                self.screen.blit(temp_text, temp_rect)
            
            #end intermission
            if (self.intermission_time < 0):
                self.drawing_votes = {}
                self.broadcast_vote = False
                #send msg that intermission is over
                #allow timer to be set
                self.start_ticks_lock = False
                self.start_ticks = pygame.time.get_ticks()
                #reset bools
                self.intermission_over = True
                self.round_over = False
                self.round_time = 0
                if winner_side == 0:
                    self.drawings.pop(self.right_sid)
                    self.right_occupied = False
                elif winner_side == 1:
                    self.drawings.pop(self.left_sid)
                    self.left_occupied = False

        # (len(self.drawing_votes) == len(self.players))
        if (self.round_time < 0):
            if not self.start_ticks_lock:
                #send msg that round is over
                self.msg_q.put(1)
                self.start_ticks = pygame.time.get_ticks()
            self.round_over = True
            self.intermission_over = False

    def recv_draw_votes(self):
        '''get votes from the votes queue and add them'''
        while not self.vote_q.empty():
            vote_entry = self.vote_q.get()
            self.drawing_votes.update(vote_entry)


    def get_vote_percents(self):
        votes_left = 0
        votes_right = 0
        for idx, (sid, vote) in enumerate(self.drawing_votes.items()):
            if not vote:
                votes_left += 1
            else:
                votes_right += 1
        total = votes_left + votes_right
        if total == 0:
            return 0, 0
        else:
            return round((votes_left / total) * 100, 3), round((votes_right / total) * 100, 3)


    def render_drawing(self, image_path, coords, dimensions):
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, dimensions)
        image_rect = image.get_rect(center=coords)
        self.screen.blit(image, image_rect)


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
