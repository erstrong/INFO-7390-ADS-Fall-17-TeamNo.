#!venv/bin/python
from flask import Flask, request, make_response
from flask_restful import Resource, Api
import MySQLdb as sql
from json import dumps
from flask import jsonify
import configparser

app = Flask(__name__)
api = Api(app)



config=configparser.RawConfigParser()
configFilePath=r'config.py'
config.read(configFilePath)
MYSQL_DATABASE_HOST=config.get('app','MYSQL_DATABASE_HOST');
MYSQL_DATABASE_USER=config.get('app','MYSQL_DATABASE_USER');
MYSQL_DATABASE_PASSWORD=config.get('app','MYSQL_DATABASE_PASSWORD');

#app.config.from_pyfile('config.py')
#con = sql.connect(host = "127.0.0.1", user = "root", passwd = "", db = "properties")
con = sql.connect(host = MYSQL_DATABASE_HOST, user = MYSQL_DATABASE_USER, passwd = MYSQL_DATABASE_PASSWORD, db = "adsesrk")
# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = ''
#app.config['MYSQL_DATABASE_DB'] = 'properties'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)


@app.route('/api/neighbors', methods=['GET'])
def get_neighbors():
    latitude= request.args.get('latitude')
    longitude= request.args.get('longitude')
    query ="select @orig_lat := " + str(latitude) + ", @orig_lon := " + str(longitude) +";"
    cur = con.cursor()
    with con:
        cur.execute(query)
        cur.execute("select *,3956*2*asin(sqrt(power(sin((@orig_lat - abs(dest.latitude)) * pi()/180/2),2) + cos(@orig_lat * pi()/180) * cos(abs(dest.latitude) * pi()/180) * power(sin((@orig_lon - dest.longitude) * pi()/180/2),2))) as distance from adsesrk.properties dest order by distance limit 10;")
    return jsonify(data=cur.fetchall())


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)


