from enum import Enum

from numpy.distutils.fcompiler import none
import itertools
from itertools import product

class Card(object):
    def __init__(self):
        self.p_value = [1, 2, 3, 4, 5]  # possible value
        self.p_color = ["Green", "Yellow", "Red", "Blue", "White"]  # possible value

    def hint(self, value=-1, color=""):
        if value != -1:
            self.p_value = [value]
        if color != "":
            self.p_color = [color]

    def negative_hint(self, value=-1, color=""):
        # removes color and values from cards that did not receive a certain hint
        if value != -1:
            self.p_value = filter(lambda n: n != value, self.p_value)
        if color != "":
            self.p_color = filter(lambda n: n != color, self.p_color)


class Player(object):
    def __init__(self, name):
        self.hand = []
        self.personal_hand = []
        self.name = name

    def give_card(self, card):
        self.hand.push(card)
        carta = Card
        self.personal_hand.push(carta)

    def remove_card(self, position):
        del self.hand[position]
        del self.personal_hand[position]

    def give_card_last(self, card):
        self.hand.append(card)
        carta = Card
        self.personal_hand.append(carta)


class Board(object):
    #TODO insert a way to keep track of previous status like what are the last moves each player made
    #maybe implement an ordered list of boards and each time a move is made add the new board to the list
    #considering the last one as the current live one?
    def __init__(self):
        players = []
        fireworks = [-1, -1, -1, -1, -1]
        discard_pile = []
        hand = []
        blue_tokens = 8
        red_tokens = 0
        deck = []
        for _ in range(1, 5):
            carta = Card
            hand.add(carta)
        for color,value in product(["red","yellow","green","blue", "white"], [1,1,1,2,2,3,3,4,4,5]):
            carta = Card
            carta.hint(value= value, color = color)
            deck.push(carta)

    def set_firework(self, color, value):
        match color:
            case "red":
                if self.fireworks[0] + 1 == value:
                    self.fireworks[0] = value
                else:
                    self.red_tokens += 1
            case "yellow":
                if self.fireworks[1] + 1 == value:
                    self.fireworks[1] = value
                else:
                    self.red_tokens += 1
            case "green":
                if self.fireworks[2] + 1 == value:
                    self.fireworks[2] = value
                else:
                    self.red_tokens += 1
            case "blue":
                if self.fireworks[3] + 1 == value:
                    self.fireworks[3] = value
                else:
                    self.red_tokens += 1
            case "white":
                if self.fireworks[4] + 1 == value:
                    self.fireworks[4] = value
                else:
                    self.red_tokens += 1

    def add_player(self, name):
        player = Player(name)
        self.players.push(player)

    def give_card_to_player(self, name, value, color):
        for player in self.players:
            if player.name == name:
                break
        card = Card()
        card.hint(value, color)
        player.give_card(card)
        for index in self.deck.size():
            if self.deck[index].p_color[0] == color and self.deck[index].p_value == value:
                del self.deck[index]
                break

    def player_plays_card(self, name, id):
        for player in self.players:
            if player.name == name:
                break
        self.set_firework(player.hand[id].color[0], player.hand[id].value[0])
        self.discard_pile.push(player.hand[id])
        #una carta giocata entra nella discard pile in quanto non è più disponibile? si può rimuovere se è ridondante
        player.remove_card(id)

    def player_discards_card(self, name, id):
        for player in self.players:
            if player.name == name:
                break
        self.discard_pile.push(player.hand[id])
        player.remove_card(id)
        if self.blue_tokens < 8:
            self.blue_tokens += 1

    def play_card(self,  id):
        #TODO chiamare set_fireworks dopo aver scoperto effettivamente il colore e il valore della carta
        #TODO aggiungere la carta alla discard pile
        del self.hand[id]

    def player_discards_card(self,  id):
        # TODO aggiungere la carta alla discard pile
        del self.hand[id]
        if self.blue_tokens < 8:
            self.blue_tokens += 1

    def give_hint(self, ids, value=-1, color=-1):
        if self.blue_tokens <= 0:
            return -1
        for i in range(self.hand.size()):
            if ids.contains(i):
                self.hand[id].hint(value, color)
            else:
                self.hand[id].negative_hint(value, color)
        self.blue_tokens -= 1

    def give_hint_to_player(self, name, value=-1, color=-1):
        if self.blue_tokens <= 0:
            return -1
        for player in self.players:
            if player.name == name:
                break
        for i in range(player.hand.size()):
            if player.hand[i].value == value or player.hand[i].value == value:
                player.personal_hand[i].hint(value, color)
            else:
                player.personal_hand[i].hint(value, color)
        self.blue_tokens -= 1

    def print_board(self):
        for player in self.players:
            print(player.name)
            i = 0
            for card in player.hand:
                print(i)
                print(card.p_color)
                print(card.p_value)
            i += 1
