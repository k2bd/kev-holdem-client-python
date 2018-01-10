#!/usr/bin/env python3

from flask import Flask,jsonify,request
import requests
import threading
import json

app = Flask(__name__)

@app.route('/player', methods=['POST'])
def game_info():
    try:
        print(request.json)
        return jsonify(status="OK")
    except Exception(e):
        print(e)
        return jsonify(status='ERROR',message=str(e))

def server_thread():
    app.run()

def post(addr, data):
    header = {'Content-Type' : 'application/json'}
    response = requests.post(addr, headers=header, json=data)
    #req = urllib2.Request(addr)
    #req.add_header('Content-Type', 'application/json')
    #response = urllib2.urlopen(req, json.dumps(data))
    return response

def configure_game(address, message, value):
    data = {}
    data['config'] = message
    data['value']  = value

    res = post(address+'/config',data)
    print(res)

def join_game(address, display_name, return_addr):
    data = {}
    data['name'] = display_name
    data['address'] = return_addr

    res = post(address+'/reg', data)
    print(res)

def make_move(address, secret_id, action, value=0):
    data = {}
    data['player_id'] = secret_id
    data['action'] = action
    data['value'] = value

    res = post(address+'/game', data)
    print(res)

if __name__ == "__main__":
    # Start web server thread
    threading.Thread(target=server_thread).start()

    server_addr = ""
    secret_id = ""
    my_addr = ""

    print("")
    print("")

    while True:
        action = input("kevpoker> ").lower().split()
        if "bet" == action[0]:
            make_move(server_addr, secret_id, action[0], action[1])
        elif action[0] in ["check", "fold"]:
            make_move(server_addr, secret_id, action[0])
        elif "join" == action[0]:
            join_game(server_addr, action[1], my_addr)
        elif "config" == action[0]:
            configure_game(server_addr, action[1], action[2])
        elif "server" == action[0]:
            server_addr = action[1]
        elif "secret" == action[0]:
            secret_id = action[1]
        elif "return" == action[0]:
            my_addr = action[1]
        else:
            print("Invalid action")