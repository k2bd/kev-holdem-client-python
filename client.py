#!/usr/bin/env python3
#coding: utf8

from flask import Flask,jsonify,request
import requests
import threading
import json
import sys

app = Flask(__name__)

class Card:
    def __init__(self,card_str):
        self.value = card_str[:-1]
        in_suit  = card_str[-1]

        if in_suit == "h":
            self.suit = "♥"
        elif in_suit == "d":
            self.suit = "♦"
        elif in_suit == "c":
            self.suit = "♣"
        elif in_suit == "s":
            self.suit = "♠"

class DumbGame:
    def __init__(self,stack,player_id,secret_id):
        self.starting_stack = stack
        self.stack = stack
        self.player_id = player_id
        self.secret_id = secret_id
        self.hole_cards = []
        self.board_cards = []
        self.id_player_map = {}

    def deal_hand(self,cards):
        self.hole_cards = []
        for card_str in cards:
            self.hole_cards.append(Card(card_str))
    
    def deal_street(self,street,street_cards):
        if street == "PreFlop":
            self.board_cards = []
        elif street == "Flop":
            for card_str in street_cards:
                self.board_cards.append(Card(card_str))
        else:
            for card_str in street_cards:
                self.board_cards.append(Card(card_str))
    
    def id_to_name(self,id):
        return self.id_player_map[id]

# This is obviously bad practice but it reduces non-demonstrative code. Organize your code better.
dumb_game = DumbGame(0,None,None)

@app.route('/player', methods=['POST'])
def game_info():
    global dumb_game

    try:
        #print(request.json)

        if request.json["info"] == "PlayerPrivateInfo":
            dumb_game.secret_id = request.json["secret_id"]
            dumb_game.player_id = request.json["ingame_id"]

        elif request.json["info"] == "GameTableInfo":
            dumb_game.starting_stack = int(request.json["starting_stack"])
            dumb_game.stack = dumb_game.starting_stack
            for entry in request.json["display_names"]:
                player_id = entry[0]
                player_name = entry[1]
                dumb_game.id_player_map[player_id] = player_name

            print("Game Info:")
            print(" Starting Stack: {}".format(dumb_game.starting_stack))
            print(" Seat order: {}".format(" ".join([dumb_game.id_to_name(pl_id) for pl_id in request.json["seat_order"]])))
            print(" Button position: {}".format(dumb_game.id_to_name(request.json["button_player"])))

        elif request.json["info"] == "HoleCardInfo":
            dumb_game.hole_cards = [Card(card_str) for card_str in request.json["hole_cards"]]
            print("New hand! Here are your cards:")
            print_cards(dumb_game.hole_cards)

        elif request.json["info"] == "MoveInfo":
            moved_player = dumb_game.id_to_name(request.json["player_id"])
            move_type = request.json["move_type"].lower()
            if move_type == "bet":
                print("{} bet {}".format(moved_player,request.json["value"]))
            elif move_type == "blind":
                print("{} posts blind {}".format(moved_player,request.json["value"]))
            else:
                print("{} {}s".format(moved_player,move_type))

        elif request.json["info"] == "ToMoveInfo":
            if request.json["player_id"] == dumb_game.player_id:
                print("It's your turn!")
                print("Your hand:")
                print_cards(dumb_game.hole_cards)
                print("Current board:")
                print_cards(dumb_game.board_cards)

        elif request.json["info"] == "StreetInfo":
            street = request.json["street"]
            street_cards = request.json["board_cards_revealed"]
            dumb_game.deal_street(street,street_cards)
            button_player = dumb_game.id_to_name(request.json["button_player"])
            if street == "PreFlop":
                print("Button is on {}".format(button_player))
            else:
                print("Dealing {}:".format(street.lower()))
                print_cards(dumb_game.board_cards)
                
        elif request.json["info"] == "PayoutInfo":
            # TODO: Evaluate what player had what
            dumb_game.board_cards = []

            reason = request.json["reason"]
            payouts = request.json["payouts"]
            hole_cards = request.json["hole_cards"]
            revealed_players = [info[0] for info in hole_cards]
            
            print("Hand over: {}")
            print("Payouts:")
            for payout in payouts:
                print("-----")
                player_id = payout[0]
                player = dumb_game.id_to_name(player_id)
                print("{}: {}".format(player,payout[1]))
                if player_id in revealed_players:
                    for info in hole_cards:
                        if info[0] == player_id:
                            print_cards([Card(card) for card in info[1]])
            print("=====")

        elif request.json["info"] == "PlayerEliminatedInfo":
            print("{} eliminated!".format(dumb_game.id_to_name(request.json["eliminated_player"])))

        elif request.json["info"] == "GameOverInfo":
            print("Game Over!!")
            print("Winner: {}".format(dumb_game.id_to_name(request.json["winning_player"])))

        return jsonify(status="OK")
    except Exception(e):
        print(e)
        return jsonify(status='ERROR',message=str(e))

def post(addr, data):
    header = {'Content-Type' : 'application/json'}
    response = requests.post(addr, headers=header, json=data)
    return response

def configure_game(address, message, value):
    data = {}
    data['config'] = message
    data['value']  = value

    print("Configuring game...")
    res = post(address+'/config',data)
    #print(res)

def join_game(address, display_name, return_addr):
    data = {}
    data['name'] = display_name
    data['address'] = return_addr

    print("Registering...")
    res = post(address+'/reg', data)
    #print(res)

def make_move(address, secret_id, action, value=0):
    data = {}
    data['secret_id'] = secret_id
    data['action'] = action
    data['value'] = value

    print("Posting move...")
    res = post(address+'/game', data)
    #print(res)

def print_cards(cards):
    card_top = "┌─────┐"
    card_bot = "└─────┘"
    cards_lines = [[],[],[],[],[]]
    for card in cards:
        value = card.value

        if len(value) == 1:
            value_top = value + " "
            value_bot = " " + value

        cards_lines[0].append(card_top)
        cards_lines[1].append("|{}   |".format(value_top))
        cards_lines[2].append("|  {}  |".format(card.suit))
        cards_lines[3].append("|   {}|".format(value_bot))
        cards_lines[4].append(card_bot)

    for line in cards_lines:
        print(" ".join(line))


def server_thread(port):
    app.run(port=port)

if __name__ == "__main__":
    # Start web server thread
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    threading.Thread(target=server_thread, args=(port,)).start()

    # Defaults are based on my local testing - k2bd
    server_addr = "http://localhost:8000"
    my_addr = "http://localhost:"+str(port)

    print("")
    print("")

    while True:
        action = input("kevpoker> ").lower().split()
        if len(action) > 0:
            if "bet" == action[0]:
                make_move(server_addr, dumb_game.secret_id, action[0], int(action[1]))
            elif action[0] in ["check", "fold"]:
                make_move(server_addr, dumb_game.secret_id, action[0])
            elif "join" == action[0]:
                join_game(server_addr, action[1], my_addr)
            elif "config" == action[0]:
                if action[1] in ["start"]:
                    configure_game(server_addr, action[1], 0)
                else:
                    configure_game(server_addr, action[1], int(action[2]))
            elif "server" == action[0]:
                server_addr = action[1]
            elif "secret" == action[0]:
                secret_id = action[1]
            elif "return" == action[0]:
                my_addr = action[1]
            else:
                print("Invalid action")