from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/number/', methods=['GET'])
def get_number():
    # GET /number/?param=5
    param = request.args.get('param', type=float)
    if param is None:
        return jsonify(error="param is required"), 400
    rand = random.random()
    return jsonify(result=rand * param)