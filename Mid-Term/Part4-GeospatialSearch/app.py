#!venv/bin/python
from flask import Flask, request, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify


app = Flask(__name__)
api = Api(app)

app.config['']

@app.route('/neighbors', methods=['GET'])
def get_neighbors():
    return jsonify({'tasks': tasks})

def neighborscalc():


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


