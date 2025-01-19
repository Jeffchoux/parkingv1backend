from flask import Flask, request, jsonify
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Mock databases
users = []
parking_slots = []
reservations = []

# Fonction pour calculer la distance entre deux points géographiques
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en kilomètres
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Route : Enregistrer un utilisateur
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('plate_number'):
        return jsonify({"message": "Missing data"}), 400

    user = {
        "id": len(users) + 1,
        "email": data['email'],
        "password": data['password'],  # ⚠️ À hacher en production
        "plate_number": data['plate_number']
    }
    users.append(user)
    return jsonify({"message": "User registered successfully!", "user": user}), 201

# Route : Ajouter un emplacement de parking
@app.route('/add_parking_slot', methods=['POST'])
def add_parking_slot():
    data = request.json
    if not data.get('latitude') or not data.get('longitude'):
        return jsonify({"message": "Missing data: latitude and longitude are required"}), 400

    slot = {
        "id": len(parking_slots) + 1,
        "latitude": data['latitude'],
        "longitude": data['longitude'],
        "description": data.get('description', ""),  # Optionnel : Description ou adresse
        "status": "available"  # Par défaut, l'emplacement est disponible
    }
    parking_slots.append(slot)
    return jsonify({"message": "Parking slot added successfully!", "slot": slot}), 201

# Route : Lister les emplacements proches
@app.route('/list_parking_slots', methods=['GET'])
def list_parking_slots():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)

    if not latitude or not longitude:
        return jsonify({"message": "Missing data: latitude and longitude are required"}), 400

    # Filtrer les emplacements proches (moins de 5 km)
    nearby_slots = [
        slot for slot in parking_slots
        if calculate_distance(latitude, longitude, slot['latitude'], slot['longitude']) <= 5
    ]
    return jsonify({"parking_slots": nearby_slots}), 200

# Route : Réserver une place
@app.route('/reserve', methods=['POST'])
def reserve_parking_slot():
    data = request.json
    slot_id = data.get('slot_id')
    user_id = data.get('user_id')

    if not slot_id or not user_id:
        return jsonify({"message": "Missing data: slot_id and user_id are required"}), 400

    # Vérifier si la place existe et est disponible
    slot = next((s for s in parking_slots if s['id'] == slot_id and s['status'] == "available"), None)
    if not slot:
        return jsonify({"message": "Slot not available or does not exist!"}), 400

    # Réserver la place
    slot['status'] = "reserved"
    reservation = {
        "id": len(reservations) + 1,
        "user_id": user_id,
        "slot_id": slot_id
    }
    reservations.append(reservation)
    return jsonify({"message": "Slot reserved successfully!", "reservation": reservation}), 201

# Route : Annuler une réservation
@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    data = request.json
    reservation_id = data.get('reservation_id')

    if not reservation_id:
        return jsonify({"message": "Missing data: reservation_id is required"}), 400

    # Trouver la réservation
    reservation = next((r for r in reservations if r['id'] == reservation_id), None)
    if not reservation:
        return jsonify({"message": "Reservation not found!"}), 404

    # Annuler la réservation et libérer la place
    slot = next((s for s in parking_slots if s['id'] == reservation['slot_id']), None)
    if slot:
        slot['status'] = "available"
    reservations.remove(reservation)

    return jsonify({"message": "Reservation cancelled successfully!"}), 200

# Route : Vérifier les places disponibles proches
@app.route('/check_availability', methods=['GET'])
def check_availability():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)

    if not latitude or not longitude:
        return jsonify({"message": "Missing data: latitude and longitude are required"}), 400

    # Filtrer les places disponibles proches (moins de 5 km)
    available_slots = [
        slot for slot in parking_slots
        if slot['status'] == "available" and calculate_distance(latitude, longitude, slot['latitude'], slot['longitude']) <= 5
    ]
    return jsonify({"available_slots": available_slots}), 200

# Route : Accueil
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Parking API"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
