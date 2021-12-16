from enum import Enum

from numpy.distutils.fcompiler import none


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
        # removes color and values from cards that did not recieve a certain hint
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

    def remove_card(self, position):
        del self.hand[position]

    def give_card_last(self, card):
        self.hand.append(card)


class Board(object):
    def __init__(self):
        players = []
        fireworks = [-1, -1, -1, -1, -1]
        discard_pile = []
        hand = []
        for _ in range(1,5):
            hand.add(Card)

    def set_firework(self, color, value):
        match color:
            case "red":
                self.fireworks[0] = value
            case "yellow":
                self.fireworks[1] = value
            case "green":
                self.fireworks[2] = value
            case "blue":
                self.fireworks[3] = value
            case "white":
                self.fireworks[4] = value

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

    def player_palys_card(self, name, id):
        for player in self.players:
            if player.name == name:
                break
        player.remove_card(id)

    def print_board(self):
        for player in self.players:
            print(player.name)
            i = 0
            for card in player.hand:
                print(i)
                print(card.p_color)
                print(card.p_value)
            i += 1
    def give_hint(self, ids, value = -1 , color = -1):
        for i in range(self.hand.size()):
            if ids.contains(i):
                self.hand[id].hint(value,color)
            else:
                self.hand[id].negative_hint(value, color)

    def give_hint_to_player(self, name, value = -1, color  = -1):
        for player in self.players:
            if player.name == name:
                break
        for i in range(player.hand.size()):
            if player.hand[i].value == value or player.hand[i].value == value:
                player.personal_hand[i].hint(value,color)
            else:
                player.personal_hand[i].hint(value, color)

def state_deserializer(state):
    lines = state.split("\n")
    board = Board()
    players = []
    current_player = lines[0].split(":")[1]
    status = ""
    for line in lines[2:]:
        if line.split(" ") == "Player":
            player = Player(line[1])
            players.push(player)
        if line.split(" ") == "Card":
            card = Card()
            for info in line.split(" "):
                if info.split(": ")[0] == "value":
                    card.hint(value=int(info.split(": ")[1].toInt))
                if info.split(": ")[0] == "color":
                    card.hint(color=int(info.split(": ")[1].toInt))
            if status == "":
                players[0].give_card_last(card)
            else:
                if status != "Discard pile":
                    board.set_firework(card.p_color[0], card.p_value[0])
        else:
            if line.split(":")[0] == ("red" or "yellow" or "green" or "blue" or "white" or "Discard pile"):
                status = line.split(":")[0]
    # implemented up to detection of discard pile, still waiting for correct api on show

# exaple of show function
# Current player: Test
# Player hands:
# Player Test2 {
#	cards: [
#		Card 35; value: 4; color: red
#		Card 5; value: 1; color: red
#		Card 30; value: 3; color: red
#		Card 26; value: 3; color: yellow
#		Card 31; value: 3; color: yellow
#	 ];
#	score: 0
# }
# Player Test3 {
#	cards: [
#		Card 44; value: 4; color: white
#		Card 25; value: 3; color: red
#		Card 41; value: 4; color: yellow
#		Card 39; value: 4; color: white
#		Card 29; value: 3; color: white
#	 ];
#	score: 0
# }
# Table cards:
# red: [
# ]
# yellow: [
# ]
# green: [
# ]
# blue: [
# ]
# white: [
# ]
# Discard pile:
# Note tokens used: 0/8
# Storm tokens used: 0/3
