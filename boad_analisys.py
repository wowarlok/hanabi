from enum import Enum

from numpy.distutils.fcompiler import none
import itertools
from itertools import product
import copy
import GameData
import socket
from constants import *
import os

RED = 0
YELLOW = 1
GREEN = 2
BLUE = 3
WHITE = 4
DECK_COMPOSITION = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]


class Card(object):
    def __init__(self):
        self.possible_card = [[True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True]]  # rows from 1 (top) to 5 (bottom)
        # possible cards a card can be
        self.color = -1  # -1 = unknown
        self.value = -1  # -1 = unknown
        self.age = 0  # expresses how old a card is, the lower the yunger
        self.playable = -1
        self.valuable = -1
        self.worthless = -1

    def hint(self, value=-1, color=-1):
        for val in range(0, 5):
            for col in range(RED, WHITE + 1):
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
        for val in range(0, 5):
            for col in range(RED, WHITE + 1):
                if value != -1 and val == value - 1:
                    self.possible_card[val][col] = False
                if color != -1 and col == color:
                    self.possible_card[val][col] = False

    def increaceAge(self):
        self.age += 1

    def setAge(self, val):
        self.age = val

    def getColor(self):
        return self.color

    def getValue(self):
        return self.value

    def setColor(self, color):
        self.color = color

    def setValue(self, value):
        self.value = value

    def setPlayable(self, val):
        self.playable = val

    def getPlayable(self):
        return self.playable

    def setValuable(self, val):
        self.valuable = val

    def getValuable(self):
        return self.valuable

    def setworthless(self, val):
        self.worthless = val

    def getWorthless(self):
        return self.worthless

    def getAge(self):
        return self.age


class Player(object):

    def __init__(self, name=""):
        self.hand = []
        self.personal_hand = []
        self.name = name

    def give_card(self, card):
        for cards in self.hand:
            cards.age += 1
        self.hand.push(card)
        carta = Card
        for cards in self.personal_hand:
            cards.age += 1
        self.personal_hand.push(carta)

    def remove_card(self, position):
        del self.hand[position]
        del self.personal_hand[position]

    def give_card_last(self, card):
        if len(self.hand) > 0:
            for index in range(len(self.hand)):
                self.hand[index].increaceAge()
                self.personal_hand[index].increaceAge()
        self.hand.append(card)
        carta = Card()
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
    current_player_name = ""
    my_name = ""

    def __init__(self):
        temp = []
        for _ in range(0, 5):
            self.hand.insert(0, Card())
            self.hand[0].setAge(_)
        for color, value in product([RED, YELLOW, GREEN, BLUE, WHITE], [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]):
            temp.append(Card())
            carta = temp[-1]
            carta.hint(value=value, color=color)
            self.deck.append(carta)

    def set_firework(self, color, value):
        if self.fireworks[color] + 1 == value:
            self.fireworks[color] = value
        else:
            self.red_tokens += 1

    def add_player(self, name):
        player = Player(name)
        self.players.append(player)
        if len(self.players) >= 3:
            del self.hand[4]
            # if there a re 4 or more players, hands are composed of only 4 cards

    def give_card_to_player(self, name, value, color):
        for player in self.players:
            if player.name == name:
                break
        card = Card()
        card.hint(value, color)
        player.give_card_last(card)
        for index in range(len(self.deck)):
            if self.deck[index].getColor() == color and self.deck[index].getValue() == value:
                del self.deck[index]
                break

    def player_plays_card(self, name, id):
        for player in self.players:
            if player.name == name:
                break
        self.set_firework(player.hand[id].getColor(), player.hand[id].getValue())
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
        del self.hand[id]

    def discards_card(self, id, value, color):
        del self.hand[id]
        if self.blue_tokens < 8:
            self.blue_tokens += 1
        card = Card()
        card.hint(value, color)
        self.discard_pile.append(card)

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
            if player.hand[i].getValue() == value or player.hand[i].getColor() == color:
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
                print(card.color)
                print(card.value)
            i += 1
        print(self.current_player_name)

    def isPlayable(self, card):
        if card.getPlayable() == 1:
            return 1
        total_count = 0
        playable_count = 0
        for col in range(RED, WHITE + 1):
            for val in range(0, 5):
                if not card.possible_card[val][col]: continue
                total_count += 1
                if val == self.fireworks[col]:
                    playable_count += 1;
        if playable_count == total_count: card.playable = 1
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    def isWorthless(self, card):
        # a card is worthless when it can't be played
        # whether cos it's too small or all other smaller cards of it's color have been discarded
        if card.getWorthless() == 1: return True
        if card.color == -1 and card.value != -1:
            cnt = 0
            for col in range(RED, WHITE):
                if card.value < self.fireworks[col]: cnt += 1
            if cnt == 5:
                card.setWorthless(1)
                return True  # card is too small to be played on any firework
        if card.value == -1 and card.color != -1:
            if self.fireworks[card.color] == 5:
                card.setWorthless(1)
                return True  # the firework of the card's color has been completed already
        if card.color == -1 or card.value == -1: return False  # too many unknow to determin
        if card.value < self.fireworks[card.color] + 1:
            card.setWorthless(1)
            return True  # card is too small to be played
        val = card.value
        while val > self.fireworks[card.color] + 1:
            val -= 1
            if self.cardsRemainingOutsideDiscard(val,
                                                 card.color) == 0:
                card.setWorthless(1)
                return True  # all smaller cards have been discarded
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
        for col in range(RED, WHITE + 1):
            for val in range(0, 5):
                if not card.possible_card[val][col]: continue
                total_count += 1
                carta = Card()
                carta.hint(val, col)
                if self.isWorthless(carta): playable_count += 1;
        if playable_count == total_count: card.setWorthless(1)
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    def isValuable(self, card):
        if card.getValuable() == 1: return True
        if card.value != -1 and card.color != -1:
            if self.cardsRemainingOutsideDiscard(card.value,
                                                 card.color) == 1:
                card.setValuable(1)
                return True  # the card is the last of it's kind
        if not self.isWorthless(card):
            card.setValuable(1)
            return True
        else:
            card.setWorthless(1)
            return False

    def findNewestPlayable(self):
        # finds the newest playable card, if tied chooses the one with the smallest value
        best_card = none
        best_player = none

        for player in self.players:
            for index in player.hand.size:
                if self.isPlayable(player.hand[index]) == 1:
                    if best_card == none or player.hand[index].getAge < best_card.age or (
                            player.hand[index].getAge == best_card.age and player.hand[
                        index].getValue() < best_card.value):
                        best_card = player.hand[index]
                        best_player = player
        return player, index

    def findBestHint(self, player, index):
        # retun value: 1 for color, -1 for value, 0 for none
        if player.personal_hand[index].getColor() != -1:
            return "value"
        if player.personal_hand[index].getValue() != -1:
            return "color"
        # if the card is a 5 you might want to warn the player
        if player.hand[index].getValue() == 5: return "value"
        cnt = 0
        for i in range(player.hand.size()):
            if i == index: continue
            if player.hand[i].getValue() == player.hand[index].getValue() and player.personal_hand[i].getValue() == -1:
                cnt += 1
        # if no other card have the same value the hint is good as it cannot be miss interpreted
        # cards with already a known value don't count
        if cnt == 0: return "value"
        cnt = 0
        for i in range(player.hand.size()):
            if i == index: continue
            if player.hand[i].color == player.hand[index].color and player.personal_hand[i].color == -1:
                cnt += 1
        if cnt == 0: return "color"
        cnt = 0
        for i in range(index):
            if player.hand[i].getValue() == player.hand[index].getValue() and player.personal_hand[i].getValue() == -1:
                cnt += 1
        # as a last attempt, if the card is the newest one of it's kind hint that
        if cnt == 0:
            return "value"
        cnt = 0
        for i in range(index):
            if player.hand[i].getColor() == player.hand[index].getColor() and player.personal_hand[i].getColor() == -1:
                cnt += 1
        if cnt == 0:
            return "color"
        # if all else fail ---> return value
        return "value"

    def isHintMisleading(self, player, value=-2, color=-2):
        indexes = []
        for index in range(player.hand.size):
            if player.hand[index].getValue() == value or player.hand[index].getColor() == color:
                if player.personal_hand[index].getvalue() != value and player.personal_hand[index].getColor() != color:
                    # count how many cards will receive information with this hint
                    indexes.append(index)
        if len(indexes) == 0: return True
        if len(indexes) == 1 and self.isPlayable(player.hand[indexes[0]]): return False
        # if the hint identifies a single card and it can be played, it's not misleading
        card = none
        for index in indexes:
            if card == none or card.age > player.hand[index]:
                card = player.hand[index]
        if self.isPlayable(card): return False

    def findBestDiscard(self, hand):
        if self.blue_tokens == 8: return none
        for index in range(len(hand)):
            # if a card is worthless you can discard it
            if self.isWorthless(hand[index]): return index
        val = 0
        for index in range(len(hand)):
            if val == 0 or (hand[index].getAge > hand[val].getAge and hand[index].getClor == -1 and hand[
                index].getValue() == -1):
                val = index
        # discard the oldest unknown card
        if val != 0: return val
        for index in range(len(hand)):
            if val == 0 or (hand[index].getAge > hand[val].getAge and self.isValuable(hand[index]) < 1):
                val = index
        # if the oldest unknow card is the newst one, discard the oldest one that isn't absolutely valuable
        return val

    def findValuableWarning(self, player):
        # TODO implement warning based on who's next to play
        if self.blue_tokens != 0:
            val = self.findBestDiscard(player.personal_hand)
            if val != none and self.isValuable(player.hand[val]):
                # if the next discard (based on our strategy) is a valuable card, warn them
                return val
            # otherwise no need to warn them
        return -1

    def receiveColorHint(self, fromPlayer, toPlayer, color, indexes):
        # when receiving a color hint, if no card is found to be obviusly playable after the hint then the newst card is playable
        # TODO make the warning detection using players order
        if toPlayer == none:
            hand = self.hand
        else:
            hand = toPlayer.personal_hand
        foundPlayableCard = False
        foundIndex = -1
        for index in range(len(hand)):
            oldStatus = self.isPlayable(hand[index])
            if index in indexes:
                hand[index].hint(color=color)
                if oldStatus < 1 and oldStatus > 0:
                    # the card was maybe playable, but not certain
                    if self.isPlayable(hand[index]) == 1:
                        # we found a card that is now playable, the hint must have been about this card
                        foundPlayableCard = True
                    else:
                        if self.isPlayable(hand[index]) > 0:
                            if foundIndex == -1 or hand[index].getAge() < hand[foundIndex].getAge():
                                # if the newest card to receive a hint is still playable after the hint the it must be playable
                                foundIndex = index
            else:
                hand[index].negative_hint(color=color)
                if oldStatus < 1 and oldStatus > 0:
                    # if the card was maybe playable
                    self.isPlayable(hand[index])  # this sets playable to True if the card is found playable
        if not foundPlayableCard and foundIndex != -1:
            # if no card was found as obvious hint the newest card is set as playable
            hand[foundIndex].setPlayable(1)

        # TODO if the player wasn't the one who's supposed to give hind set the next discardable card valuable to false
        # as no valuable hint was given
        # not needed |
        #           v
        # if toPlayer == none: self.hand = hand
        # else:  toPlayer.personal_hand = hand

    def receiveValueHint(self, fromPlayer, toPlayer, value, indexes):
        if toPlayer == none:
            hand = self.hand
        else:
            hand = toPlayer.personal_hand
        nextDiscard = self.findBestDiscard(hand)
        warning = False
        if nextDiscard in indexes and self.couldBeValuableWithVal(hand[nextDiscard], value):
            warning = True
            hand[nextDiscard].setValuable(1)

        foundPlayableCard = False
        foundIndex = -1
        for index in range(len(hand)):
            oldStatus = self.isPlayable(hand[index])
            if index in indexes:
                hand[index].hint(value=value)
                if oldStatus < 1 and oldStatus > 0:
                    # the card was maybe playable, but not certain
                    if self.isPlayable(hand[index]) == 1:
                        # we found a card that is now playable, the hint must have been about this card
                        foundPlayableCard = True
                    else:
                        if self.isPlayable(hand[index]) > 0:
                            if foundIndex == -1 or hand[index].getAge() < hand[foundIndex]:
                                # if the newest card to receive a hint is still playable after the hint the it must be playable
                                foundIndex = index
            else:
                hand[index].negative_hint(value=value)
                if oldStatus < 1 and oldStatus > 0:
                    # if the card was maybe playable
                    self.isPlayable(hand[index])  # this sets playable to True if the card is found playable

        if not warning and not foundPlayableCard and foundIndex != -1:
            # if it wasn't a warning and no card was identified as obvious playable then the newes one is playable
            hand[foundIndex].setPlayable(1)

    def couldBeValuableWithVal(self, card, value):
        if card.getValuable() == 1: return True
        cpCard = copy(card)
        cpCard.hint(value=value)
        return self.isValuable(cpCard)

    # connection to client section
    def updateBoardAfterPlay(self, data, player):  # data is show data
        for index in range(len(player.hand)):
            old = player.hand[index]
            new = data.cards[index]
            # TODO convertire in actual data depending os client-server payload format
            if old.color != new.color or old.value != new.value:
                self.player_plays_card(player.name, index)
        player.give_card_last(data.cards[len(data.cards) - 1])

    def updateBoardAfterDiscard(self, data, player):  # data is show data
        for index in range(len(player.hand)):
            old = player.hand[index]
            new = data.cards[index]
            # TODO convertire in actual data depending os client-server payload format
            if old.color != new.color or old.value != new.value:
                self.player_discards_card(player.name, index)
        player.give_card_last(data.cards[len(data.cards) - 1])

    def hanldeMove(self, data):  # data is status data
        is_me = False
        if self.current_player_name != self.my_name:
            for player in self.players:
                if player.name == self.current_player_name:
                    break
        else:
            is_me = True

        if type(data) is GameData.ServerHintData:
            for toPlayer in self.players:
                if toPlayer.name == data.destination:
                    break
            if is_me:
                player = none
            if data.destination == self.my_name:
                toPlayer = none
            if data.value in (1, 2, 3, 4, 5):
                self.receiveValueHint(player, toPlayer, data.value, data.positions)

                return
            else:
                if data.value == "green":
                    color = GREEN
                if data.value == "red":
                    color = RED
                if data.value == "blue":
                    color = BLUE
                if data.value == "yellow":
                    color = YELLOW
                if data.value == "white":
                    color = WHITE
                self.receiveColorHint(player, toPlayer, color, data.positions)

                return
        if is_me:
            if data.card.color == "green":
                color = GREEN
            if data.card.color == "red":
                color = RED
            if data.card.color == "blue":
                color = BLUE
            if data.card.color == "yellow":
                color = YELLOW
            if data.card.color == "white":
                color = WHITE
            if type(data) is GameData.ServerActionValid:
                self.discards_card(data.cardHandIndex, data.card.value, color)
            if type(data) is GameData.ServerPlayerMoveOk or type(data) is GameData.ServerPlayerThunderStrike:
                self.play_card(data.cardHandIndex)
                self.set_firework(color, data.card.value)
        else:
            if type(data) is GameData.ServerActionValid:
                self.player_discards_card(self.current_player_name, data.cardHandIndex)

                return
            if type(data) is GameData.ServerPlayerMoveOk or type(data) is GameData.ServerPlayerThunderStrike:
                self.player_plays_card(self.current_player_name, data.cardHandIndex)

                return

    def makeMove(self):
        # TODO if len(self.deck)-len(self.hand) == 0:
            # play best card
            # if no secure card, play the "most playable"
            # return
        if self.findValuableWarning(self.players[0]) != -1:  # TODO not player 0 but next player
            # hint them
            val = self.findBestDiscard(self.players[0].hand)
            return "hint", self.players[0].hand[val].getValue(), self.players[0].name, "value"
        # play best card
        for i in range(len(self.hand)):
            if self.isPlayable(self.hand[i])==1:
                return "play", i, none, none
        # give hint
        # TODO implement way of choosing a different hint if the best one is misleading with a cicle
        player, index = self.findNewestPlayable()
        type = self.findBestHint(player, index)
        if type == "color":
            if not self.isHintMisleading(player, color=player.hand[index].getColor()):
                # give hint
                return "hint", player.hand[index].getColor(), player.name, "color"
        else:
            if not self.isHintMisleading(player, value=player.hand[index].getValue()):
                # give hint
                return "value", player.hand[index].getValue(), player.name, "value"
        if self.blue_tokens < 8:
            val = self.findBestDiscard(self.hand)
            if val != -1:
                # discard it
                return "discard", val, none, none
        # ipotetico caso limite da gestire
        return "play", len(self.hand)-1
        # TODO gestire casi limite scartando la carta meno peggio
