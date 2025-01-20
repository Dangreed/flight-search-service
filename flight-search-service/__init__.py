from flask import Flask, request, jsonify
from neo4j import GraphDatabase

def create_app():
    app = Flask(__name__)
    uri = "neo4j://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
    driver.verify_connectivity()

    def get_session():
        return driver.session()

    # Register a new city
    @app.route('/cities', methods=['PUT'])
    def register_city():
        data = request.get_json()
        name = data.get("name")
        country = data.get("country")
        
        if not name or not country:
            return jsonify({"error": "Missing data"}), 400

        with get_session() as session:
            result = session.run("MERGE (c:City {name: $name, country: $country}) "
                                 "RETURN c", name=name, country=country)
            city = result.single()
            
            if city:
                return jsonify({"message": "City registered successfully"}), 201
            return jsonify({"error": "City already exists"}), 400

    # Get cities
    @app.route('/cities', methods=['GET'])
    def get_cities():
        country = request.args.get('country', type=str)
        with get_session() as session:
            if country:
                result = session.run("MATCH (c:City {country: $country})"
                    "RETURN c.name AS name, c.country AS country", country=country)
            else:
                result = session.run("MATCH (c:City) RETURN c.name AS name, c.country AS country")
            cities = [{"name": record["name"], "country": record["country"]} for record in result]
        return jsonify(cities), 200

    # Get city
    @app.route('/cities/<name>', methods=['GET'])
    def get_city(name):
        with get_session() as session:
            result = session.run("MATCH (c:City {name: $name}) RETURN c.name AS name, c.country AS country", name=name)
            record = result.single()
            if record:
                return jsonify({"name": record["name"], "country": record["country"]}), 200
        return jsonify({"error": "City not found"}), 404

    # Register an Airport
    @app.route('/cities/<name>/airports', methods=['PUT'])
    def register_airport(name):
        with get_session() as session:
            city_result = session.run("MATCH (c:City {name: $name}) RETURN c", name=name)
            if not city_result.single():
                return jsonify({"error": "City not found"}), 400

            data = request.get_json()
            code = data.get("code")
            airport_name = data.get("name")
            numberOfTerminals = data.get("numberOfTerminals")
            address = data.get("address")
            if not code or not airport_name or not numberOfTerminals or not address:
                return jsonify({"error": "Missing data"}), 400

            result = session.run("MERGE (a:Airport {code: $code, name: $name, numberOfTerminals: $numberOfTerminals, address: $address}) "
                                 "WITH a "
                                 "MATCH (c:City {name: $city_name}) "
                                 "MERGE (a)-[:LOCATED_IN]->(c) "
                                 "RETURN a",
                                 code=code, name=airport_name, numberOfTerminals=numberOfTerminals,
                                 address=address, city_name=name)
            airport = result.single()
            
            if airport:
                return jsonify({"message": "Airport created"}), 201
            return jsonify({"error": "Airport already exists"}), 400

    # Get airports in a city
    @app.route('/cities/<name>/airports', methods=['GET'])
    def get_airports(name):
        with get_session() as session:
            result = session.run("MATCH (c:City {name: $name})<-[:LOCATED_IN]-(a:Airport) "
                                 "RETURN a.code AS code, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address", name=name)
            airports = [{"code": record["code"], "name": record["name"], "numberOfTerminals": record["numberOfTerminals"], "address": record["address"]} for record in result]
            if airports:
                return jsonify(airports), 200
        return jsonify({"error": "City not found"}), 404

    # Get airport
    @app.route('/airports/<code>', methods=['GET'])
    def get_airport(code):
        with get_session() as session:
            result = session.run("MATCH (a:Airport {code: $code})-[:LOCATED_IN]->(c:City) "
                                 "RETURN a.code AS code, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address, c.name AS city", code=code)
            record = result.single()
            if record:
                return jsonify({
                    "code": record["code"],
                    "name": record["name"],
                    "numberOfTerminals": record["numberOfTerminals"],
                    "address": record["address"],
                    "city": record["city"]
                }), 200
        return jsonify({"error": "Airport not found"}), 404

    # Register a new flight
    @app.route('/flights', methods=['PUT'])
    def register_flight():
        data = request.get_json()
        number = data.get("number")
        from_airport_code = data.get("fromAirport")
        to_airport_code = data.get("toAirport")
        price = data.get("price")
        flight_time = data.get("flightTimeInMinutes")
        operator = data.get("operator")

        if not all([number, from_airport_code, to_airport_code, price, flight_time, operator]):
            return jsonify({"error": "Missing data"}), 400

        with get_session() as session:
            # Check if both airports exist
            from_airport = session.run("MATCH (a:Airport {code: $code}) RETURN a", code=from_airport_code).single()
            to_airport = session.run("MATCH (a:Airport {code: $code}) RETURN a", code=to_airport_code).single()
            
            if not from_airport or not to_airport:
                return jsonify({"error": "One or both airports not found"}), 400

            # Create or update the FLIGHT relationship with properties
            result = session.run("""
                MATCH (from:Airport {code: $from_code}), (to:Airport {code: $to_code})
                MERGE (from)-[f:FLIGHT {number: $number}]->(to)
                SET f.price = $price, f.flightTimeInMinutes = $flightTimeInMinutes, f.operator = $operator
                RETURN f
                """,
                from_code=from_airport_code, to_code=to_airport_code,
                number=number, price=price, flightTimeInMinutes=flight_time, operator=operator)

            flight = result.single()
            
            if flight:
                return jsonify({"message": "Flight created as relationship"}), 201
            return jsonify({"error": "Could not create flight"}), 400

    # Get full flight information
    @app.route('/flights/<code>', methods=['GET'])
    def get_flight_info(code):
        with get_session() as session:
            result = session.run("""
                MATCH (from:Airport)-[f:FLIGHT {number: $code}]->(to:Airport)
                MATCH (from)-[:LOCATED_IN]->(from_city:City)
                MATCH (to)-[:LOCATED_IN]->(to_city:City)
                RETURN f.number AS number, 
                       from.code AS fromAirport, from_city.name AS fromCity, 
                       to.code AS toAirport, to_city.name AS toCity, 
                       f.price AS price, f.flightTimeInMinutes AS flightTimeInMinutes, f.operator AS operator
            """, code=code)
            
            record = result.single()
            if record:
                return jsonify({
                    "number": record["number"],
                    "fromAirport": record["fromAirport"],
                    "fromCity": record["fromCity"],
                    "toAirport": record["toAirport"],
                    "toCity": record["toCity"],
                    "price": record["price"],
                    "flightTimeInMinutes": record["flightTimeInMinutes"],
                    "operator": record["operator"]
                }), 200
        return jsonify({"error": "Flight not found"}), 404


    # Find flights to and from city
    @app.route('/search/flights/<fromCity>/<toCity>', methods=['GET'])
    def find_flights_between_cities_with_stops(fromCity, toCity):
        with get_session() as session:
            result = session.run("""
                MATCH (from_city:City {name: $fromCity})<-[:LOCATED_IN]-(from_airport:Airport),
                      (to_city:City {name: $toCity})<-[:LOCATED_IN]-(to_airport:Airport),
                      path = (from_airport)-[:FLIGHT*..3]->(to_airport)
                WITH path, 
                     reduce(totalPrice = 0, r IN relationships(path) | totalPrice + r.price) AS price,
                     reduce(totalTime = 0, r IN relationships(path) | totalTime + r.flightTimeInMinutes) AS timeInMinutes
                RETURN [a IN nodes(path) | a.code] AS airports,  // list of airport codes in the path
                       [r IN relationships(path) | r.number] AS flights,  // list of flight numbers in the path
                       price,
                       timeInMinutes
                ORDER BY timeInMinutes ASC
            """, fromCity=fromCity, toCity=toCity)
            
            records = result.data()
            if records:
                flights_info = []
                for record in records:
                    airports = record["airports"]
                    flights_info.append({
                        "fromAirport": airports[0],
                        "toAirport": airports[-1],
                        "flights": record["flights"],
                        "price": record["price"],
                        "flightTimeInMinutes": record["timeInMinutes"]
                    })
                    
                return jsonify(flights_info), 200

        return jsonify({"error": "No flights found between the specified cities with up to 3 stops"}), 404



    # Cleanup
    @app.route('/cleanup', methods=['POST'])
    def cleanup():
        with get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        return jsonify({"message": "Cleanup successful"}), 200
    return app