from flask import Flask, request, jsonify
import random, operator

app = Flask(__name__)
ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.floordiv}

@app.route('/number/', methods=['GET'])
def get_number():
    p = int(request.args.get('param', 1))
    r = random.randint(1, 100)
    return jsonify(result=r * p, operation='*')

@app.route('/number/', methods=['POST'])
def post_number():
    p = int(request.json.get('jsonParam', 1))
    r = random.randint(1, 100)
    op = random.choice(list(ops))
    return jsonify(result=ops[op](r, p), operation=op)

@app.route('/number/', methods=['DELETE'])
def delete_number():
    r = random.randint(1, 100)
    op = random.choice(list(ops))
    return jsonify(result=ops[op](r, r), operation=op)

if __name__ == '__main__':
    app.run(debug=True)
