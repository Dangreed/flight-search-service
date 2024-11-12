from neo4j import GraphDatabase
from flask import (Flask, request, jsonify)

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    #[NOTE] Connect to database
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    URI = "<URI for Neo4j database>"
    AUTH = ("<Username>", "<Password>")
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    session = driver.session(database="...")

    @app.route('/cities', methods=['PUT'])
    def register_city():
        pass

    @app.route('/cities', methods=['GET'])
    def get_cities():
        pass

    @app.route('/cities/<name>', methods=['GET'])
    def get_city():
        pass

    @app.route('/cities/<name>/airports', methods=['PUT'])
    def register_airport():
        pass

    @app.route('/cities/<name>/airports', methods=['GET'])
    def get_airports_in_city():
        pass

    @app.route('/airports/<code>', methods=['GET'])
    def get_airport():
        pass

    @app.route('/flights', methods=['PUT'])
    def register_flight():
        pass

    @app.route('/flights/<code>', methods=['GET'])
    def get_flight_info():
        pass

    @app.route('/search/flights/<fromCity>/<toCity>', methods=['GET'])
    def find_flights():
        pass

    @app.route('/cleanup', methods=['POST'])
    def cleanup():
        pass

    return app