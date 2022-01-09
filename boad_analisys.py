from enum import Enum

from numpy.distutils.fcompiler import none
import itertools
from itertools import product

RED = 0
YELLOW = 1
GREEN = 2
BLUE = 3
WHITE = 4
DECK_COMPOSITION = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]


class Card(object):
    possible_card = []
    color = -1  # -1 = unknown
    value = 1  # -1 = unknown
    age=0 # expresses how old a card is, the lower the yunger

    def __init__(self):
        self.possible_card = [[True, True, True, True, True],
                              [True, True, True, True, True]
                              [True, True, True, True, True]
                              [True, True, True, True, True]
                              [True, True, True, True, True]]  # rows from 1 (top) to 5 (bottom)
        # possible cards a card can be

    def hint(self, value=-1, color=-1):
        for val in range(0, 4):
            for col in range(RED, WHITE):
                if value != -1:
                    self.value = value
                    if val != value - 1:
                        self.possible_card[val][col] = False
                if color != -1:
                    self.color = color
                    if col != color:
                        self.possible_card[val][col] = False

    def negative_hint(self, value=-1, color=-1):
        # removes color and values from cards that did not receive a certain hint
        for val in range(0, 4):
            for col in range(RED, WHITE):
                if value != -1 and val == value - 1:
                    self.possible_card[val][col] = False
                if color != -1 and col == color:
                    self.possible_card[val][col] = False


class Player(object):
    hand = []
    personal_hand = []
    name = ""

    def __init__(self, name):
        self.hand = []
        self.personal_hand = []
        self.name = name

    def give_card(self, card):
        for cards in self.hand:
            cards.age+=1
        self.hand.push(card)
        carta = Card
        for cards in self.personal_hand:
            cards.age+=1
        self.personal_hand.push(carta)



    def remove_card(self, position):
        del self.hand[position]
        del self.personal_hand[position]

    def give_card_last(self, card):
        self.hand.append(card)
        carta = Card
        self.personal_hand.append(carta)


class Board(object):
    # TODO insert a way to keep track of previous status like what are the last moves each player made
    # maybe implement an ordered list of boards and each time a move is made add the new board to the list
    # considering the last one as the current live one?
    players = []
    fireworks = [0, 0, 0, 0, 0]
    discard_pile = []
    hand = []
    blue_tokens = 8
    red_tokens = 0
    deck = []

    def __init__(self):

        for _ in range(1, 5):
            carta = Card
            self.hand.add(carta)
        for color, value in product([RED, YELLOW, GREEN, BLUE, WHITE], [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]):
            carta = Card
            carta.hint(value=value, color=color)
            self.deck.push(carta)

    def set_firework(self, color, value):
            if self.fireworks[color] + 1 == value:
                self.fireworks[color] = value
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
        # una carta giocata entra nella discard pile in quanto non è più disponibile? si può rimuovere se è ridondante
        player.remove_card(id)

    def player_discards_card(self, name, id):
        for player in self.players:
            if player.name == name:
                break
        self.discard_pile.push(player.hand[id])
        player.remove_card(id)
        if self.blue_tokens < 8:
            self.blue_tokens += 1

    def play_card(self, id):
        # TODO chiamare set_fireworks dopo aver scoperto effettivamente il colore e il valore della carta
        # TODO aggiungere la carta alla discard pile
        del self.hand[id]

    def player_discards_card(self, id):
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

    def isPlayable(self, card):
        total_count = 0
        playable_count = 0
        for col in range(RED, WHITE):
            for val in range(0, 4):
                if not card.possible_card[val][col]: continue
                total_count += 1
                if val == self.fireworks[val] + 1: playable_count += 1;
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    def isWorthless(self, card):
        # a card is worthless when it can't be played
        # whether cos it's too small or all other smaller cards of it's color have been discarded

        if card.color == -1 and card.value != -1:
            cnt = 0
            for col in range(RED, WHITE):
                if card.value < self.fireworks[col]: cnt += 1
            if cnt == 5: return True  # card is too small to be played on any firework
        if card.value == -1 and card.color != -1:
            if self.fireworks[
                card.color] == 5: return True  # the firework of the card's color has been completed already
        if card.color == -1 or card.value == -1: return False  # too many unknow to determin
        if card.value < self.fireworks[card.color] + 1: return True  # card is too small to be played
        val = card.value
        while val > self.fireworks[card.color] + 1:
            val -= 1
            if self.cardsRemainingOutsideDiscard(val,
                                                 card.color) == 0: return True  # all smaller cards have been discarded
        return False

    def cardsRemainingOutsideDiscard(self, value, color):
        cout = 2
        cnt = 0
        if value == 1: cout += 1
        if value == 5: cout -= 1
        for card in self.discard_pile:
            if card.color == color and card.value == value:
                cnt += 1
        return cout - cnt

    def worthlessProbability(self, card):
        total_count = 0
        playable_count = 0
        for col in range(RED, WHITE):
            for val in range(0, 4):
                if not card.possible_card[val][col]: continue
                total_count += 1
                carta = Card()
                carta.hint(val, col)
                if self.isWorthless(carta): playable_count += 1;
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    def isValuable(self, card):
        if card.value != -1 and card.color != -1:
            if self.cardsRemainingOutsideDiscard(card.value,
                                                 card.color) == 1: return True  # the card is the last of it's kind
        return not self.isWorthless(card)

    def findNewestPlayable(self):
        # finds the newest playable card, if tied chooses the one with the smallest value
        best_card = none
        best_player = none

        for player in self.players:
            for card in player.hand:
                if self.isPlayable(card) == 1:
                    if best_card == none or card.age<best_card.age or (card.age==best_card.age and card.value<best_card.value):
                        best_card = card
                        best_player = player
        return player,card

    def findBestHint(self,player,index):
        # retun value: 1 for color, -1 for value, 0 for none
        if player.personal_hand[index].color!=-1:
            return "value"
        if player.personal_hand[index].value!=-1:
            return "color"
        # if the card is a 5 you might want to warn the player
        if player.hand[index].value == 5: return "value"
        cnt = 0
        for i in range(player.hand.size()):
            if i == index: continue
            if player.hand[i].value == player.hand[index].value and player.personal_hand[i].value==-1:
                cnt += 1
        # if no other card have the same value the hint is good as it cannot be miss interpreted
        # cards with already a known value don't count
        if cnt == 0: return "value"
        cnt = 0
        for i in range(player.hand.size()):
            if i == index: continue
            if player.hand[i].color == player.hand[index].color and player.personal_hand[i].color==-1:
                cnt += 1
        if cnt == 0: return "color"
        cnt = 0
        for i in range(index):
            if player.hand[i].value == player.hand[index].value and player.personal_hand[i].value == -1:
                cnt += 1
        # as a last attempt, if the card is the newest one of it's kind hint that
        if cnt == 0:
            return "value"
        cnt = 0
        for i in range(index):
            if player.hand[i].color == player.hand[index].color and player.personal_hand[i].color == -1:
                cnt += 1
        if cnt == 0:
            return "color"
        # if all else fail ---> return value
        return "value"
