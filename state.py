import pygame
import pygame.locals
import pygame.freetype
import random
import time
import sys
import toml
from collections import Counter
from typing import List
from dataclasses import dataclass

from vars import GameVars, Colours

@dataclass
class AlphabetItem():
    long_ver: str
    short_ver: str
    difficulty: int = 0

if len(sys.argv) < 2:
    raise Exception("Not enough arguments. Pass the name of a toml alphabet file. e.g. \n$ python game.py my_alphabet.toml")

with open(sys.argv[1], "r") as f:
    ITEMS_TO_TRAIN = toml.loads(f.read())

LETTERS = [AlphabetItem(long, short) for long, short in ITEMS_TO_TRAIN.items()]

GAME_FONT = pygame.freetype.SysFont(GameVars.FONT, GameVars.FONT_SIZE)

SCORE = 0


class Letter():
    def __init__(self, item: AlphabetItem, speed: int) -> None:
        self.item = item
        self.speed = speed

        self.x = random.randint(75, GameVars.X_MAX-75)
        self.y = -10

        self.fading = False
        self.finished = False

        self.colour = Colours.BLACK

        self.letter = item.short_ver
        d_rng = random.randint(0, 100)
        if item.difficulty < d_rng:
            # e.g. "sit"
            self.text = item.long_ver
            self.reward = GameVars.SMALL_REWARD
        else:
            # e.g. "i"
            self.reward = GameVars.BIG_REWARD
            self.text = item.short_ver


    def __repr__(self):
        return f"Letter({self.letter}, {self.text}, {self.speed}, ({self.x}, {self.y}))"


    def step(self, key_events: Counter) -> int:
        if self.y >= GameVars.Y_MAX:
            # Letter fell off the bottom of the screen
            self.item.difficulty -= GameVars.PROBABILITY_DIFFICULT_STEP
            self.finished = True
            return -GameVars.PUNISHMENT
        elif self.fading and self.colour[2] < 250:
            # Fading, haven't finished yet
            c1 = min(self.colour[1]+GameVars.FADE_AMOUNT, 255)
            c2 = min(self.colour[2]+GameVars.FADE_AMOUNT, 255)
            self.colour = (255, c1, c2)
        elif self.fading and self.colour[2] >= 250:
            # Done fading
            self.finished = True
        elif key_events[self.letter] > 0:
            # Popped
            key_events[self.letter] -= 1
            self.colour = Colours.RED
            self.fading = True
            self.item.difficulty += GameVars.PROBABILITY_DIFFICULT_STEP
            return self.reward
        else:
            # Move downwards
            self.y += self.speed

        return 0


    def render(self, screen) -> None:
        to_render = self.letter if self.fading else self.text
        GAME_FONT.render_to(screen, (self.x, self.y), to_render, self.colour)


class GameState():

    def __init__(self, screen) -> None:
        self.screen = screen
        self.letters_in_flight: List[Letter] = []
        self.score = 0
        self.score_pos = (GameVars.X_MAX//2, GameVars.Y_MAX-50)

        self.frame_wait = GameVars.FRAME_WAIT


    def add_to_score(self, v):
        if (self.score + v) // GameVars.DIFFICULTY_STEP > self.score // GameVars.DIFFICULTY_STEP:
            self.frame_wait -= 1
        self.score += v


    def generate_new_letters(self) -> None:
        if random.random() < GameVars.PROBABILITY_NEW_LETTER:
            l_idx = random.randint(0, len(LETTERS)-1)
            new = Letter(LETTERS[l_idx], GameVars.SCROLL_SPEED)
            self.letters_in_flight.append(new)


    def handle_keys(self, key_events: Counter) -> None:
        new_letters = []
        for letter in self.letters_in_flight:
            if not letter.finished:
                self.add_to_score(letter.step(key_events))
                letter.render(self.screen)
                new_letters.append(letter)
        self.letters_in_flight = new_letters


    def render_score(self) -> None:
        GAME_FONT.render_to(self.screen, self.score_pos, str(self.score), Colours.BLACK)


    def run(self) -> None:
        running = True
        while running:
            time.sleep(self.frame_wait/1000)
            self.screen.fill(Colours.WHITE)

            keys = Counter()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keys[event.unicode] += 1
            self.handle_keys(keys)

            self.generate_new_letters()
            self.render_score()

            pygame.display.flip()
