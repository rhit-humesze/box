import random

class BoxphoneGame:
    def __init__(self, players):
        self.players = players
        self.player_order = []
        self.randomize_player_order()
        self.seed = random.randint(0, len(players))
        self.text_prompts = []  # ascii text
        self.image_prompts = []  # png or jpg

    def randomize_player_order(self):
        self.player_order = []
        num_players = len(self.players)
        for k in range(num_players):
            self.player_order.append(k)
        random.shuffle(self.player_order)

    """Loops through players, asking each player to put text prompt or image prompt. 
    Each player has 1 response in chain
    """
    def telephone_game_loop(self):
        num_players = len(self.players)
        for k in range(num_players):
            curplayer = self.players(k)
            if k == 0:
                # first player in chain
                self.display_instructions(curplayer, "text")
                self.request_text_prompt(curplayer)
            elif (k % 2) == 0:
                # even players (0 indexed)
                self.display_last_image_prompt(curplayer)
                self.display_instructions(curplayer, "text")
                self.request_text_prompt(curplayer)
            else:
                # odd players (0 indexed)
                self.display_last_text_prompt(curplayer)
                self.display_instructions(curplayer, "image")
                self.request_image_prompt(curplayer)

    def request_text_prompt(self, player):
        # get input of type text (or ascii or whatever)
        text = input("Enter prompt: ")
        self.text_prompts.append(text)

    def request_image_prompt(self, player):
        # get input of type png or jpg
        image_path = input("Enter image path: ")
        self.image_prompts.append(image_path)

    def display_instructions(self, player, instruction_type):
        if instruction_type == "text":
            print("Please type a text prompt")
        elif instruction_type == "image":
            print("Please submit an image prompt (JPG or PNG)")


    '''Displays the final results of the game'''
    def display_results(self):
        num_players = len(self.players)
        # some header "Results"
        num_responses = len(self.text_prompts) + len(self.image_prompts)
        for k in range(num_players):
            for j in range(num_responses):
                if (k % 2) == 0:
                    # even players (0 indexed)
                    text = self.text_prompts[k]
                    # display it to each player
                else:
                    # odd players (0 indexed)
                    image = self.image_prompts[k]
                    # display it to each player

    def display_last_image_prompt(self, curplayer):
        pass

    def display_last_text_prompt(self, curplayer):
        pass