from flask import Flask,json,jsonify,request
import requests
import threading

app = Flask(__name__)

@app.route('/game_info', methods=['POST'])
def game_info():
    try:
        ingame_id = request.json["ingame_id"]
        secret_id = request.json["secret_id"]
        starting_stack = request.json["starting_stack"]
    except Exception(e):
        return jsonify(status='ERROR',message=str(e))

def server_thread():
    app.run()

if __name__ == "__main__":
    # Start web server thread
    threading.Thread(target=server_thread).start()
    
    