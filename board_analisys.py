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
        # Rows indicate the value, columns indicates the color.
        # 0-red, 1-yellow, 2-green, 3-blue, 4-white
        self.possible_card = [[True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True],
                              [True, True, True, True, True]]  # rows from 1 (top) to 5 (bottom)
        # possible cards a card can be
        self.color = -1  # -1 = unknown
        self.value = -1  # -1 = unknown
        self.age = 0  # expresses how old a card is, the lower the younger
        self.playable = -1
        self.valuable = -1
        self.worthless = -1

    # Forse si potrebbe mergeare hint e negative_hint in un unico metodo che gestisca gli hint su una carta ~ Marco
    def hint(self, value=-1, color=-1):
        """
            Updates the possible value/color of the card, based on a received hint.

            Parameters:
                value: the value of the card received. It can be 1, 2, 3, 4, 5 or -1 when no value hint is received on this card.
                color: the color of the card received. It can be It can be 0 (red), 1 (yellow), 2 (green), 3 (blue), 4 (white) or -1 when no color hint is received on this card
        """

        # Cycle through all possible combinations of colors and values
        for val in range(0, 5):
            for col in range(RED, WHITE + 1):
                if value != -1:  # if a value hint is given, then assign to this card that value and other possible values become false.
                    self.value = value
                    if val != value - 1:
                        self.possible_card[val][col] = False
                if color != -1:  # if a color hint is given, then assign to this card that color and other possible colors become false.
                    self.color = color
                    if col != color:
                        self.possible_card[val][col] = False

    def negative_hint(self, value=-1, color=-1):
        """
            Updates the possible value of a card that was not target by a hint, so that we can know by exclusion what a cards is.

            Parameters:
                value: the value of the card received. It can be 1, 2, 3, 4, 5 or -1 when no value hint is received on this card.
                color: the color of the card received. It can be It can be 0 (red), 1 (yellow), 2 (green), 3 (blue), 4 (white) or -1 when no color hint is received on this card
        """
        # removes color and values from cards that did not receive a certain hint
        for val in range(0, 5):
            for col in range(RED, WHITE + 1):
                if value != -1 and val == value - 1:
                    self.possible_card[val][col] = False
                if color != -1 and col == color:
                    self.possible_card[val][col] = False

    #Setters e vari metodi utility.
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

    def setWorthless(self, val):
        self.worthless = val

    def getWorthless(self):
        return self.worthless

    def getAge(self):
        return self.age


class Player(object):

    def __init__(self, name=""):
        self.hand = []
        self.personal_hand = []  # What the player knows of his hand
        self.name = name

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
    fireworks = [0, 0, 0, 0, 0]  # Contains the highest card on the board for each color (r, y, g, b, w)
    discard_pile = []
    hand = []
    blue_tokens = 8
    red_tokens = 0
    deck = []
    current_player_name = ""
    my_name = ""
    my_position = -1  # is the index of the player that comes right after us

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
        """
            Places a card with a given color - value on the board

            Parameters:
                color: the color of the placed card. It can be 0 (red), 1 (yellow), 2 (green), 3 (blue), 4 (white).
                value: the value of the placed card. It can be 1, 2, 3, 4, 5.
        """
        if self.fireworks[color] + 1 == value:  #Checks if card can be placed
            self.fireworks[color] = value
            if value == 5 and self.blue_tokens < 8: #Add a blue token in case a 5 is placed
                self.blue_tokens += 1
        else:   #If card cannot be placed
            self.red_tokens += 1

    def add_player(self, name):
        """
           Adds a new player to the game

           Parameters:
                name: name of the player
        """
        if name == self.my_name:
            self.my_position = len(self.players)
            return
        player = Player(name)
        self.players.append(player)
        if len(self.players) == 3:
            del self.hand[4]
            # if there a re 4 or more players, hands are composed of only 4 cards

    def give_card_to_player(self, name, value, color):
        """
            Associates a card to a given player.

            Parameters:
                name: name of the player that receives the card
                value: the value of the card received. It can be 1, 2, 3, 4, 5.
                color: the color of the placed card. It can be 0 (red), 1 (yellow), 2 (green), 3 (blue), 4 (white).
        """
        for player in self.players:  # Cosa fa questo ciclo?
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
        """
            Places the card of a player with a given name, with position at id, on the board.

            Parameters:
                name: name of the player whose card is going to be played
                id: index of the card in the hand of the player. It can be 0, 1, 2, 3, 4.
        """
        for player in self.players:  # Perchè questo ciclo?
            if player.name == name:
                break

        # Carta va sia sulla plancia che nella discard pile. Possibilmente fuorviante ~ Marco
        self.set_firework(player.hand[id].getColor(), player.hand[id].getValue())
        self.discard_pile.append(player.hand[id])
        # una carta giocata entra nella discard pile in quanto non è più disponibile? si può rimuovere se è ridondante
        player.remove_card(id)

    def player_discards_card(self, name, id):
        """
            Discards the card of a player with a given name.

            Parameters:
                name: name of the player whose card is going to be discarded
                id: index of the card in the hand of the player. It can be 0, 1, 2, 3, 4.
        """
        for player in self.players:
            if player.name == name:
                break
        # Mette la carta nella discard pile, rimuovendola dalla mano del giocatore, e aumenta il numero di blue token disponibili
        self.discard_pile.append(player.hand[id])
        player.remove_card(id)
        if self.blue_tokens < 8:
            self.blue_tokens += 1

    def play_card(self, id):
        """
            Play a card of the IA player, with a given id.

            Parameters:
                id: index of the card in the hand of the IA.
        """
        del self.hand[id]  # Rimuove la carta dalla mano del giocatore
        for card in self.hand:  # Aumenta l'età delle rimanenti carte in mano
            card.increaceAge()
        card = Card()  # Pesca una carta nuova
        if len(self.deck) - len(self.hand) >= 0:
            self.hand.append(card)

    def discards_card(self, id, value, color):
        del self.hand[id]  # Scarta la carta
        if self.blue_tokens < 8:
            self.blue_tokens += 1
        for card in self.hand: # Incrementa l'età delle altre carte
            card.increaceAge()
        card = Card() # Ripesca una carta
        if len(self.deck) - len(self.hand) >= 0:
            self.hand.append(card)
        card = Card()  # Pesca e riscarta una carta nota (?)
        card.hint(value, color)
        self.discard_pile.append(card)
        for index in range(len(self.deck)):
            if self.deck[index].getColor() == color and self.deck[index].getValue() == value:
                del self.deck[index]
                break

    def print_board(self):
        """
            Prints the state of the game.
        """
        for player in self.players:
            print(player.name)
            i = 0
            for card in player.hand:
                print(i)
                print("color:")
                print(card.color)
                print("value:")
                print(card.value)
                i += 1
        print(self.current_player_name)
        print("Blue tokens = " + str(self.blue_tokens))
        print("Red tokens = " + str(self.red_tokens))

    def isPlayable(self, card):
        """
            Returns a mark that states how "playable" a card is. The more a card is playable, the safer is to play it. If 1, it can be safely played.

            Parameters:
                card: the card that needs to be evaluated
        """
        if card.getPlayable() == 1 and self.red_tokens < 2:  # when red tokens =2 enter safe mode
            return 1
        total_count = 0
        playable_count = 0
        # Evaluates how many cards are still in game that can be played, and return a probability value of having a playable one.
        for col in range(RED, WHITE + 1):
            for val in range(0, 5):
                if not card.possible_card[val][col]: continue # Potrebbe basarsi non solo sul tipo di carte rimanenti in gioco, ma anche sul loro numero.
                total_count += 1
                if val == self.fireworks[col]:
                    playable_count += 1;
        if total_count == 0: return 0  # this should be possible, but sometimes it happens, will fix
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    def isWorthless(self, card):
        """
            Returns True if a card is "worthless" a card is. A card is worthless whenever:
            - It has already been placed
            - Its value is too small and it cannot be played.
            - It belongs to a color already completed
            - All smaller cards are already have been discarded, so this cannot be placed anymore

            Parameters:
                card: the card that has to be evaluated
        """
        # a card is worthless when it can't be played
        # whether cos it's too small or all other smaller cards of it's color have been discarded
        if card.getWorthless() == 1: return True  # Se già markata come worhtless, evita di ricomputare
        if card.color == -1 and card.value != -1:  # Se la carta non ha colore non noto e valore noto
            cnt = 0
            for col in range(RED, WHITE + 1):
                if card.value < self.fireworks[col]: cnt += 1  # FIX: Vedi su quali colonne andrebbe ancora bene. Possibile sostituire con <= ~ Marco
            if cnt == 5:
                card.setWorthless(1)
                return True  # card is too small to be played on any firework
        if card.value == -1 and card.color != -1:  # Se valore non noto e colore noto.
            if self.fireworks[card.color] == 5:
                card.setWorthless(1)
                return True  # the firework of the card's color has been completed already
        if card.color == -1 or card.value == -1: return False  # too many unknow to determin
        if card.value <= self.fireworks[card.color]:  # Caso valore e colore noti.
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
        """
            See how many cards of a given color/value are still not discarded

            Parameters:
                - value: the value of the card to check
                - color: the color of the card to check
        """
        count = 2
        cnt = 0
        if value == 1: count += 1
        if value == 5: count -= 1
        available_cards = []
        # FIX: Raggruppa le carte rimanenti in un array a parte. Possibilmente fallato, dato che la carta interessata potrebbe
        # essere in mano al giocatore. Forse sarebbe meglio contare a partire da una variabile che tiene conto del mazzo iniziale,
        # e rimuovendo le carte discardate ~ Marco
        for card in self.deck:
            available_cards.append(card)
        for player in self.players:
            for card in player.hand:
                available_cards.append(card)
        for card in available_cards:
            if card.color == color and card.value == value:
                cnt += 1
        return cnt

    def worthlessProbability(self, card):
        """
            Returns the probability of a given card of being a "worthless" card.

            Parameters:
                card: the card whose "worthless probability" will be evaluated
        """
        total_count = 0
        playable_count = 0
        for col in range(RED, WHITE + 1):   # Cicla su tutti i possibili valori di carte
            for val in range(0, 5):
                if not card.possible_card[val][col]: continue  # Se la carta non è possibile, vai avanti.
                total_count += 1
                carta = Card()
                carta.hint(val, col)
                if self.isWorthless(carta): playable_count += 1;  # FIX: Forse playable vuol dire in realtà worthless
        if playable_count == total_count: card.setWorthless(1) # Se tutte le carte rimanenti sono worthless, allora questa è sicuramente worthless
        return playable_count / total_count  # if return =1 card can be played 100% of the time, otherwise function retunrs

    # a probability of playability. if 0 card will never be usefull

    # Valuable looks redundant, since it's often opposite to worthless. May be simplified somehow.
    def isValuable(self, card):
        """
            Returns a score based on how "valuable" a card is. A card is valuable if:
            - It is still available
            - It can be played
            - It's not worthless

            It's 1 if valuable, 0 if not valuable (worthless), 0.5 if not valuable nor worthless

            Parameters:
                card: the card that has to be evaluated
        """
        if card.getValuable() == 1: return 1  # Evita di ricomputare il valore
        if card.getValuable() == 0: return 0
        if card.value != -1 and card.color != -1:  # Se colore e valore non noti
            if self.cardsRemainingOutsideDiscard(card.value,
                                                 card.color) == 1 and not self.isWorthless(card): # Se ne rimane almeno una e non è worthless, allora è valuable
                card.setValuable(1)
                return 1  # the card is the last of it's kind
        if self.isWorthless(card):
            card.setValuable(0)
            card.setWorthless(1)
            return 0
        # if it wasn't worthless
        return 0.5

    def findNewestPlayable(self):
        """
            Returns the newest card playable. If these characteristics are equal, the one with the lower value is chosen.

            Returns:
                A 2-tuple containing name of the player having the best card found and the index of that card.
        """
        # finds the newest playable card, if tied chooses the one with the smallest value
        best_card = None
        best_player = None
        best_index = None
        for playerIndex in range(len(self.players)):  # Cycle through players
            player = self.players[(playerIndex + self.my_position) % len(self.players)]
            for index in range(len(player.hand)):  # Cycle through its cards
                if self.isPlayable(player.hand[index]) == 1:
                    if best_card == None or player.hand[index].getAge() < best_card.getAge() or (
                            player.hand[index].getAge() == best_card.getAge() and player.hand[
                        index].getValue() < best_card.getValue()):
                        hint_type = self.findBestHint(player, index)
                        is_ok = False
                        if hint_type == "color":
                            if not self.isHintMisleading(player, color=player.hand[index].getColor()) and \
                                    not self.isSameCardKnownPlayable(player, index):
                                is_ok = True
                        if hint_type == "value":
                            if not self.isHintMisleading(player, value=player.hand[index].getValue()) and \
                                    not self.isSameCardKnownPlayable(player, index):
                                is_ok = True
                        if is_ok:
                            best_card = player.hand[index]
                            best_player = player
                            best_index = index
            if best_player != None:
                break
        return best_player, best_index

    def findBestHint(self, player, index):
        """
            Finds the most intelligent way to suggest a card with a given index to a given player.

            Parameters:
                player: the name of the player
                index: the index of the card

            Returns:
                "value" if a color hint should be given
                "color if a value hint should be given
        """
        # retun value: 1 for color, -1 for value, 0 for none
        if player.personal_hand[index].getColor() != -1:  # if he already knows the color, suggest the value
            return "value"
        if player.personal_hand[index].getValue() != -1:  # if he already knows the value, suggest the color
            return "color"
        # if the card is a 5 you might want to warn the player
        if player.hand[index].getValue() == 5: return "value"
        cnt = 0
        # Counts how many cards have the same color. If none, suggest that color
        for i in range(len(player.hand)):
            if i == index: continue
            if player.hand[i].color == player.hand[index].color and player.personal_hand[i].color == -1:
                cnt += 1
        if cnt == 0: return "color"

        # Counts how many cards have the same value. If none, suggest that value
        cnt = 0
        for i in range(len(player.hand)):
            if i == index: continue
            if player.hand[i].getValue() == player.hand[index].getValue() and player.personal_hand[i].getValue() == -1:
                cnt += 1
        # if no other card have the same value the hint is good as it cannot be miss interpreted
        # cards with already a known value don't count (maybe they should ~ Marco)
        if cnt == 0: return "value"

        # FIX: forse risulterà sempre 1, dato che non viene ignorata la carta in posizione "index"
        cnt = 0
        for i in range(index):
            if player.hand[i].getColor() == player.hand[index].getColor() and player.personal_hand[i].getColor() == -1:
                cnt += 1
        if cnt == 0:
            return "color"

        # FIX: forse risulterà sempre 1, dato che non viene ignorata la carta in posizione "index"
        cnt = 0
        for i in range(index):
            if player.hand[i].getValue() == player.hand[index].getValue() and player.personal_hand[i].getValue() == -1:
                cnt += 1
        # as a last attempt, if the card is the newest one of it's kind hint that
        if cnt == 0:
            return "value"

        # if all else fail ---> return value
        # Maybe it should be possible to return a sort of "not found" value ~ Marco
        return "value"

    def isSameCardKnownPlayable(self, player, index):
        for giocatore in self.players:
            for indice in range(len(giocatore.hand)):
                if giocatore.name == player.name and indice == index: continue
                if giocatore.hand[indice].getValue() == player.hand[index].getValue() and giocatore.hand[
                    indice].getColor() == player.hand[index].getColor():
                    if self.isPlayable(giocatore.personal_hand[indice]) == 1:
                        return True
        return False

    def isHintMisleading(self, player, value=-2, color=-2):
        indexes = []
        for index in range(len(player.hand)):
            if player.hand[index].getValue() == value or player.hand[index].getColor() == color:
                if player.personal_hand[index].getValue() != value and player.personal_hand[index].getColor() != color:
                    # count how many cards will receive information with this hint
                    indexes.append(index)
        if len(indexes) == 0: return True
        if len(indexes) == 1 and self.isPlayable(player.hand[indexes[0]]): return False
        # if the hint identifies a single card and it can be played, it's not misleading
        card = None
        for index in indexes:
            if card == None or card.getAge() > player.hand[index].getAge():
                card = player.hand[index]
        if self.isPlayable(card): return False
        return True

    def findBestDiscard(self, hand):
        for index in range(len(hand)):
            # if a card is worthless you can discard it
            if self.isWorthless(hand[index]): return index
        val = -1
        for index in range(len(hand)):
            if (val == -1 or hand[index].getAge() > hand[val].getAge()) and hand[index].getColor() == -1 and hand[
                index].getValue() == -1:
                val = index
        # discard the oldest unknown card
        if val != -1 and val != len(hand) - 1: return val
        for index in range(len(hand)):
            if (val == -1 or hand[index].getAge() > hand[val].getAge()) and self.isValuable(hand[index]) < 1:
                val = index
        # if the oldest unknow card is the newst one, discard the oldest one that isn't absolutely valuable
        return val

    def findValuableWarning(self, player):
        if self.blue_tokens != 0:
            val = self.findBestDiscard(player.personal_hand)
            if val != None and val != -1 and self.isValuable(player.hand[val]) == 1 and player.personal_hand[
                val].getValuable() < 1:
                # if the next discard (based on our strategy) is a valuable card, warn them
                return val
            # otherwise no need to warn them
        return -1

    def receiveColorHint(self, fromPlayer, toPlayer, color, indexes):
        """
            Used whenever a hint on a value is given to a player

            Parameters:
                fromPlayer: name of the player who gives the hint
                toPlayer: name of the player who receives the hint (None if the player is the AI itself)
                color: color of the hinted card. It can be 0 (red), 1 (yellow), 2 (green), 3 (blue), 4 (white)
                indexes: indexes with the value of the hinted cards
        """
        # when receiving a color hint, if no card is found to be obviusly playable after the hint then the newst card is playable
        # TODO make the warning detection using players order
        if toPlayer == None:
            hand = self.hand
        else:
            hand = toPlayer.personal_hand
        foundPlayableCard = False
        foundIndex = -1
        for index in range(len(hand) - 1, -1, -1):
            oldStatus = self.isPlayable(hand[index])
            if index in indexes:
                hand[index].hint(color=color)
                if oldStatus <= 1 and oldStatus > 0:
                    # the card was maybe playable, but not certain
                    if self.isPlayable(hand[index]) == 1:
                        # we found a card that is now playable, the hint must have been about this card
                        if not foundPlayableCard:
                            # the newest card found playable is considered playable, the others might be the same or not playable in the future
                            hand[index].setPlayable(1)
                            print("set card playable: " + str(index))
                        foundPlayableCard = True
                    else:
                        if self.isPlayable(hand[index]) > 0:
                            if foundIndex == -1 or hand[index].getAge() < hand[foundIndex].getAge():
                                # if the newest card to receive a hint is still playable after the hint the it must be playable
                                foundIndex = index
            else:
                hand[index].negative_hint(color=color)
        print("index identified = " + str(foundIndex))
        if not foundPlayableCard and foundIndex != -1:
            # if no card was found as obvious hint the newest card is set as playable
            print("index identified as playable= " + str(foundIndex))
            hand[foundIndex].playable = 1

        # TODO if the player wasn't the one who's supposed to give hind set the next discardable card valuable to false
        # as no valuable hint was given
        # not needed |
        #           v
        # if toPlayer == none: self.hand = hand
        # else:  toPlayer.personal_hand = hand

    def receiveValueHint(self, fromPlayer, toPlayer, value, indexes):
        """
            Used whenever a hint on a value is given to a player

            Parameters:
                fromPlayer: name of the player who gives the hint
                toPlayer: name of the player who receives the hint (None if the player is the AI itself)
                value: value of the hinted cards
                indexes: indexes with the value of the hinted cards
        """
        warning_partner = False
        if toPlayer == None:  # Case hint receiver is our AI
            hand = self.hand
            for index in range(len(self.players)):
                if self.players[index].name == fromPlayer.name:
                    if index == (self.my_position + len(self.players) - 1) % len(self.players):
                        warning_partner = True
        else:  # Case hint receiver is NOT our AI but another player
            hand = toPlayer.personal_hand
            for index in range(len(self.players)):
                if self.players[index].name == toPlayer.name:
                    if index == self.my_position and fromPlayer == None:
                        warning_partner = True
                    elif fromPlayer != None and fromPlayer.name == self.players[(index - 1) % len(self.players)].name:
                        warning_partner = True
        next_discard = self.findBestDiscard(hand)
        warning = False
        if warning_partner and next_discard in indexes and self.couldBeValuableWithVal(hand[next_discard], value):
            warning = True
            hand[next_discard].setValuable(1)

        foundPlayableCard = False
        foundIndex = -1
        for index in range(len(hand) - 1, -1, -1):
            oldStatus = self.isPlayable(hand[index])
            if index in indexes:
                if value == 5:
                    hand[index].setValuable(1)
                hand[index].hint(value=value)
                if oldStatus <= 1 and oldStatus > 0:
                    # the card was maybe playable, but not certain
                    if self.isPlayable(hand[index]) == 1:
                        # we found a card that is now playable, the hint must have been about this card
                        if not foundPlayableCard:
                            hand[index].setPlayable(1)
                            print("set card playable: " + str(index))
                        foundPlayableCard = True

                    else:
                        if self.isPlayable(hand[index]) > 0:
                            if foundIndex == -1 or hand[index].getAge() < hand[foundIndex].getAge():
                                # if the newest card to receive a hint is still playable after the hint the it must be playable
                                foundIndex = index
            else:
                hand[index].negative_hint(value=value)
        print("index identified = " + str(foundIndex))
        if not warning and not foundPlayableCard and foundIndex != -1:
            # if it wasn't a warning and no card was identified as obvious playable then the newes one is playable
            print("index identified as playable= " + str(foundIndex))
            hand[foundIndex].setPlayable(1)

    def couldBeValuableWithVal(self, tCard, value):
        if tCard.getValuable() == 1: return True
        cpCard = copy.copy(tCard)
        cpCard.hint(value=value)
        return self.isValuable(cpCard)

    def updatePlayerHand(self, player):
        cards_left = []
        for card in self.deck:
            cards_left.append(card)
        if player == None:
            hand = self.hand
        else:
            hand = player.personal_hand
            for card in player.hand:
                cards_left.append(card)
        for card in hand:
            for val in DECK_COMPOSITION:
                for color in range(RED, WHITE + 1):
                    stillIn = False
                    for carta in cards_left:
                        if carta.getValue() == val and carta.getColor() == color:
                            stillIn = True

                    if not stillIn:
                        card.possible_card[val - 1][color] = False

    def updateAllHands(self):
        self.updatePlayerHand(None)
        for player in self.players:
            self.updatePlayerHand(player)

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

    def findBestPlayable(self):
        best = None
        bestIndex = -1
        for index in range(len(self.hand) - 1, -1, -1):
            card = self.hand[index]
            if self.isPlayable(card) == 1:
                if best == None or best.getValue() < card.getValue():
                    best = card
                    bestIndex = index
        return bestIndex

    def findLastCardToPlay(self):
        bestIndex = -1
        best_fitness = 0
        for index in range(len(self.hand)):
            card = self.hand[index]
            fitness = self.isPlayable(card)
            if fitness > 0:
                if bestIndex == -1 or fitness > best_fitness:
                    best_fitness = fitness
                    bestIndex = index
        return bestIndex, best_fitness

    def handleMove(self, data):  # data is status data
        """
            Manages data incoming from the server

            Parameters:
                data: status data received from the server
        """
        # Understanding if move is directed towards another player, ot the agent itself
        is_me = False
        player = None
        toPlayer = None
        if self.current_player_name != self.my_name:  # dopo che cicla non succede niente
            for player in self.players:
                if player.name == self.current_player_name:
                    break
        else:
            is_me = True

        # Case is a hint
        if type(data) is GameData.ServerHintData:
            self.blue_tokens -= 1  # Remove a token
            for toPlayer in self.players:  # finding destination player, in that case do nothing
                if toPlayer.name == data.destination:
                    break
            if is_me:
                player = None
            if data.destination == self.my_name:
                toPlayer = None
            if data.value in (1, 2, 3, 4, 5):
                self.receiveValueHint(player, toPlayer, data.value, data.positions)
                self.updateAllHands()
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
                self.updateAllHands()
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
                for index in range(len(self.deck)):
                    if self.deck[index].getColor() == color and self.deck[index].getValue() == data.card.value:
                        del self.deck[index]
                        break
                self.set_firework(color, data.card.value)
        else:
            if type(data) is GameData.ServerActionValid:
                self.player_discards_card(self.current_player_name, data.cardHandIndex)
                self.updateAllHands()
                return
            if type(data) is GameData.ServerPlayerMoveOk or type(data) is GameData.ServerPlayerThunderStrike:
                self.player_plays_card(self.current_player_name, data.cardHandIndex)
                self.updateAllHands()
                return

    def makeMove(self):
        print("Size of the deck =" + str(len(self.deck)))
        print("Red tokens = " + str(self.red_tokens))
        print("knowledge about my hand: ")
        for card in self.hand:
            print("card value: " + str(card.value))
            print("card color: " + str(card.color))
            for val in range (0,5):
                for color in range (RED, WHITE+1):
                    if card.possible_card[val][color]:
                        print("Possible value = "+ str(val)+ "\nPossible color = "+ str(color))
            print("card playable: " + str(card.getPlayable()))
            print("card valuable: " + str(card.getValuable()))
            print("card worthless: " + str(card.getWorthless()))
            print("")
        if len(self.deck) <= len(self.hand):
            print("DECK IS EMPTY!")
            # YOU HAVE ONLY 1 TURN LEFT! PLAY A GOOD CARD!
            playable_card, fitness = self.findLastCardToPlay()
            if (fitness != 0 and self.red_tokens < 2) or fitness == 1:
                # if it's not a critical situation play tge best fitness card, but if it's playable play it
                print("PLAY THE BEST CARD! " + str(playable_card))
                if fitness == 1:
                    print("I'm sure this card is playable: " + str(playable_card))
                return "play", playable_card, None, None
        # play best card
        # if no secure card, play the "most playable"
        # return
        if self.findValuableWarning(self.players[self.my_position % len(self.players)]) != -1:
            # hint them
            val = self.findBestDiscard(self.players[self.my_position % len(self.players)].personal_hand)
            print("hint " + str(self.players[self.my_position % len(self.players)].hand[val].getValue()) + " " +
                  self.players[0].name + " value WARNING")
            return "hint", self.players[self.my_position % len(self.players)].hand[val].getValue(), self.players[
                self.my_position % len(self.players)].name, "value"
        # play best card
        playable_card = self.findBestPlayable()
        if playable_card != -1:
            return "play", playable_card, None, None
        # give hint
        # TODO implement way of choosing a different hint if the best one is misleading with a cicle
        player, index = self.findNewestPlayable()
        if player != None and index != None:
            type = self.findBestHint(player, index)
        else:
            type = ""
        if self.blue_tokens > 0:
            if type == "color":
                # give hint
                print("hint " + str(player.hand[index].getColor()) + " " + player.name + " color")
                return "hint", player.hand[index].getColor(), player.name, "color"
            else:
                if type == "value":
                    # give hint
                    print("hint " + str(player.hand[index].getValue()) + " " + player.name + " value")
                    return "hint", player.hand[index].getValue(), player.name, "value"
        if self.blue_tokens < 8:
            val = self.findBestDiscard(self.hand)
            if val != -1:
                # discard it
                return "discard", val, None, None
        # ipotetico caso limite da gestire
        if self.blue_tokens > 0:
            print("hint " + str(self.players[self.my_position % len(self.players)].hand[0].getValue()) + " " +
                  self.players[
                      0].name + " value LAST CHANCE")
            return "hint", self.players[self.my_position % len(self.players)].hand[0].getValue(), self.players[
                self.my_position % len(self.players)].name, "value"
        else:
            emergencyDiscard = 0
            for index in range(len(self.hand)):
                if self.hand[index].getValue() > self.hand[emergencyDiscard].getValue():
                    emergencyDiscard = index
            return "discard", emergencyDiscard, None, None

    def reset(self):
        self.players = []
        self.fireworks = [0, 0, 0, 0, 0]
        self.discard_pile = []
        self.hand = []
        self.blue_tokens = 8
        self.red_tokens = 0
        self.deck = []
        self.current_player_name = ""
        self.my_name = ""
        self.my_position = -1
        temp = []
        for _ in range(0, 5):
            self.hand.insert(0, Card())
            self.hand[0].setAge(_)
        for color, value in product([RED, YELLOW, GREEN, BLUE, WHITE], [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]):
            temp.append(Card())
            carta = temp[-1]
            carta.hint(value=value, color=color)
            self.deck.append(carta)
