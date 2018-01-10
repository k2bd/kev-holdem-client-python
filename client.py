#!/usr/bin/env python3

from flask import Flask,jsonify,request
import requests
import threading
import json
import sys

app = Flask(__name__)

@app.route('/player', methods=['POST'])
def game_info():
    try:
        print(request.json)
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
    data['secret_id'] = secret_id
    data['action'] = action
    data['value'] = value

    res = post(address+'/game', data)
    print(res)

def server_thread(port):
    app.run(port=port)

if __name__ == "__main__":
    # Start web server thread
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    threading.Thread(target=server_thread, args=(port,)).start()

    server_addr = ""
    secret_id = ""
    my_addr = ""

    print("")
    print("")

    while True:
        action = input("kevpoker> ").lower().split()
        if len(action) > 0:
            if "bet" == action[0]:
                make_move(server_addr, secret_id, action[0], int(action[1]))
            elif action[0] in ["check", "fold"]:
                make_move(server_addr, secret_id, action[0])
            elif "join" == action[0]:
                join_game(server_addr, action[1], my_addr)
            elif "config" == action[0]:
                configure_game(server_addr, action[1], int(action[2]))
            elif "server" == action[0]:
                server_addr = action[1]
            elif "secret" == action[0]:
                secret_id = action[1]
            elif "return" == action[0]:
                my_addr = action[1]
            else:
                print("Invalid action")