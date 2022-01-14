#!/usr/bin/env python3
import time
from copy import copy
from sys import argv, stdout
from threading import Thread

from numpy.distutils.fcompiler import none

import GameData
import socket
from constants import *
import os
from boad_analisys import Board

RED = 0
YELLOW = 1
GREEN = 2
BLUE = 3
WHITE = 4

if len(argv) < 4:
    print("You need the player name to start the game.")
    #exit(-1)
    playerName = "Alice" # For debug
    ip = HOST
    port = PORT
else:
    playerName = argv[3]
    ip = argv[1]
    port = int(argv[2])


run = True
ai= False# set to false to visualize the "show" command
statuses = ["Lobby", "Game", "GameHint"]

status = statuses[0]

hintState = ("", "")
board = Board()
board.my_name = playerName
board_setup = False
was_hint = True

def manageInput():
    global run
    global status
    while run:
        command = input()
        # Choose data to send
        if command == "print":
            board.print_board()
        if command == "exit":
            run = False
            os._exit(0)
        elif command == "ready" and status == statuses[0]:
            s.send(GameData.ClientPlayerStartRequest(playerName).serialize())
        elif command == "show" and status == statuses[1]:
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        elif command.split(" ")[0] == "discard" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerDiscardCardRequest(playerName, cardOrder).serialize())
            except:
                print("Maybe you wanted to type 'discard <num>'?")
                continue
        elif command.split(" ")[0] == "play" and status == statuses[1]:
            try:
                cardStr = command.split(" ")
                cardOrder = int(cardStr[1])
                s.send(GameData.ClientPlayerPlayCardRequest(playerName, cardOrder).serialize())
            except:
                print("Maybe you wanted to type 'play <num>'?")
                continue
        elif command.split(" ")[0] == "hint" and status == statuses[1]:
            try:
                destination = command.split(" ")[2]
                t = command.split(" ")[1].lower()
                if t != "colour" and t != "color" and t != "value":
                    print("Error: type can be 'color' or 'value'")
                    continue
                value = command.split(" ")[3].lower()
                if t == "value":
                    value = int(value)
                    if int(value) > 5 or int(value) < 1:
                        print("Error: card values can range from 1 to 5")
                        continue
                else:
                    if value not in ["green", "red", "blue", "yellow", "white"]:
                        print("Error: card color can only be green, red, blue, yellow or white")
                        continue
                s.send(GameData.ClientHintData(playerName, destination, t, value).serialize())
            except:
                print("Maybe you wanted to type 'hint <type> <destinatary> <value>'?")
                continue
        elif command == "":
            print("[" + playerName + " - " + status + "]: ", end="")
        else:
            print("Unknown command: " + command)
            continue
        stdout.flush()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    request = GameData.ClientPlayerAddData(playerName)
    s.connect((HOST, PORT))
    s.send(request.serialize())
    data = s.recv(DATASIZE)
    data = GameData.GameData.deserialize(data)
    if type(data) is GameData.ServerPlayerConnectionOk:
        print("Connection accepted by the server. Welcome " + playerName)
    print("[" + playerName + " - " + status + "]: ", end="")
    Thread(target=manageInput).start()
    while run:
        dataOk = False
        data = s.recv(DATASIZE)
        if not data:
            continue
        data = GameData.GameData.deserialize(data)
        data2 = copy(data)
        if type(data) is GameData.ServerPlayerMoveOk:
            dataOk = True
            board.handleMove(data2)
            was_hint = False
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
            print("Nice move!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerStartRequestAccepted:
            dataOk = True
            print("Ready: " + str(data.acceptedStartRequests) + "/"  + str(data.connectedPlayers) + " players")
            data = s.recv(DATASIZE)
            data = GameData.GameData.deserialize(data)
        if type(data) is GameData.ServerStartGameData:
            dataOk = True
            print("Game start!")
            s.send(GameData.ClientPlayerReadyData(playerName).serialize())
            status = statuses[1]
            time.sleep(1)
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        if type(data) is GameData.ServerGameStateData:
            dataOk = True
            if not ai:
                print("Current player: " + data.currentPlayer)


            if not ai:
                print("Player hands: ")
            for p in data.players:
                if not board_setup:
                    board.add_player(p.name)
                    for card in p.hand:
                        if card.color == "green":
                            color = GREEN
                        if card.color == "red":
                            color = RED
                        if card.color == "blue":
                            color = BLUE
                        if card.color == "yellow":
                            color = YELLOW
                        if card.color == "white":
                            color = WHITE
                        board.give_card_to_player(p.name,card.value, color)
                else:
                    if p.name == board.current_player_name and board.current_player_name != playerName and not was_hint:
                        card = p.hand[-1]
                        if card.color == "green":
                            color = GREEN
                        if card.color == "red":
                            color = RED
                        if card.color == "blue":
                            color = BLUE
                        if card.color == "yellow":
                            color = YELLOW
                        if card.color == "white":
                            color = WHITE
                        board.give_card_to_player(p.name,card.value, color)
                if not ai:
                    print(p)
                    print(p.toClientString())
            if not ai:
                print("Table cards: ")
            for pos in data.tableCards:
                if not ai:
                    print(pos + ": [ ")
                for c in data.tableCards[pos]:
                    if not ai:
                        print(c.toClientString() + " ")
                if not ai:
                    print("]")
            if not ai:
                print("Discard pile: ")
            for c in data.discardPile:
                if not ai:
                    print("\t" + c.toClientString())
            if not ai:
                print("Note tokens used: " + str(data.usedNoteTokens) + "/8")
                print("Storm tokens used: " + str(data.usedStormTokens) + "/3")

            board_setup = True
            board.current_player_name = data.currentPlayer
            if playerName == data2.currentPlayer:
                time.sleep(0.1)
                action,val,playerToSend, typeToSend = board.makeMove()
                if action == "discard":
                    s.send(GameData.ClientPlayerDiscardCardRequest(playerName, val).serialize())
                if action == "play":
                    s.send(GameData.ClientPlayerPlayCardRequest(playerName, val).serialize())
                if action == "hint":
                    if typeToSend =="color":
                        if val == RED:
                            val ="red"
                        if val == BLUE:
                            val ="blue"
                        if val == YELLOW:
                            val ="yellow"
                        if val == GREEN:
                            val ="green"
                        if val == WHITE:
                            val ="white"
                    s.send(GameData.ClientHintData(playerName, playerToSend,typeToSend, val).serialize())
            stdout.flush()
        if type(data2) is GameData.ServerActionInvalid:
            dataOk = True
            print("Invalid action performed. Reason:")
            print(data.message)
        if type(data) is GameData.ServerActionValid:
            dataOk = True
            board.handleMove(data)
            was_hint = False
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
            print("Action valid!")
            print("Current player: " + data.player)
        if type(data) is GameData.ServerPlayerThunderStrike:
            dataOk = True
            board.handleMove(data)
            was_hint = False
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
            print("OH NO! The Gods are unhappy with you!")
        if type(data) is GameData.ServerHintData:
            dataOk = True
            board.handleMove(data)
            print("Hint type: " + data.type)
            print("Player " + data.destination + " cards with value " + str(data.value) + " are:")
            for i in data.positions:
                print("\t" + str(i))
            was_hint = True
            s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        if type(data) is GameData.ServerInvalidDataReceived:
            dataOk = True
            print(data.data)
        if type(data) is GameData.ServerGameOver:
            dataOk = True
            print(data.message)
            print(data.score)
            print(data.scoreMessage)
            stdout.flush()
            print("Ready for a new game!")
            board = None
            board = Board()
            #s.send(GameData.ClientGetGameStateRequest(playerName).serialize())
        if not dataOk:
            print("Unknown or unimplemented data type: " +  str(type(data)))
        print("[" + playerName + " - " + status + "]: ", end="")
        stdout.flush()
        data = none



#s.send(GameData.ClientPlayerStartRequest(playerName).serialize())