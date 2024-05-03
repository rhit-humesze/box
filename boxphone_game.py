import random

class BoxphoneGame:
    def __init__(self, players):
        self.players = players
        self.player_order = []
        self.randomize_player_order()
        self.seed = random.randint(0, len(players))

    def randomize_player_order(self):
        self.player_order = []
        num_players = len(self.players)
        for k in range(num_players):
            self.player_order.append(k)
        random.shuffle(self.player_order)

    def telephone_game_loop(self):
        # Ask each player to create a prompt, then
        text_prompts = []  # ascii text
        image_prompts = []  # png or jpg
        sound_prompts = []  # mp3
        num_players = len(self.players)
        for k in range(num_players):
            player_num = self.player_order[k]
            current = self.players[player_num]
            self.send_instructions(current)
            self.request_text_prompt(current, text_prompts)

        for k in range(num_players):
            if k == (num_players - 1):
                player_num = self.player_order[1]
            else:
                player_num = self.player_order[k + 1]
            current = self.players[player_num]
            self.request_image_prompt(current, image_prompts)

        for k in range(num_players):
            if k == (num_players - 2):
                player_num = self.player_order[1]
            elif k == (num_players - 1):
                player_num = self.player_order[2]
            else:
                player_num = self.player_order[k + 2]
            current = self.players[player_num]
            self.request_sound_prompt(current, sound_prompts)

        self.display_results(text_prompts, image_prompts, sound_prompts)
        self.request_votes()

    def request_text_prompt(self, player, text_prompts):
        # get input of type text (or ascii or whatever)
        text = input("Enter prompt: ")
        text_prompts.append(text)

    def request_image_prompt(self, player, image_prompts):
        image_path = input("Enter image path: ")
        image_prompts.append(image_path)

    def request_sound_prompt(self, player, sound_prompts):
        sound_path = input("Enter sound path: ")
        sound_prompts.append(sound_path)

    def send_instructions(self, current):
        pass

    def display_results(self, text_prompts, image_prompts, sound_prompts):
        num_players = len(self.players)
        for k in range(num_players):
            # display text
            # display image
            # display sound
    def request_votes(self):
        # request votes for best text prompt, best image, best sound, best overall
        # maybe ranking system
        # this might be useless
        pass
