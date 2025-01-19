from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock databases
users = []  # Liste des utilisateurs enregistrés
parking_slots = []  # Liste des emplacements de parking
reservations = []  # Liste des réservations
transactions = []  # Liste des transactions financières

# Route : Enregistrer un utilisateur
@app.route('/register', methods=['POST'])
def register_user():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.json
    if not data.get('email') or not data.get('password') or not data.get('plate_number'):
        return jsonify({"message": "Missing data: email, password, or plate_number"}), 400

    user = {
        "id": len(users) + 1,
        "email": data['email'],
        "password": data['password'],  # Hacher les mots de passe en production !
        "plate_number": data['plate_number'],
        "balance": 10.0  # Solde initial pour permettre les premiers tests
    }
    users.append(user)
    return jsonify({"message": "User registered successfully!", "user": user}), 201

# Route : Ajouter une place de parking
@app.route('/add_parking_slot', methods=['POST'])
def add_parking_slot():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.json
    if not data.get('latitude') or not data.get('longitude') or not data.get('description') or not data.get('owner_id'):
        return jsonify({"message": "Missing data: latitude, longitude, description, or owner_id"}), 400

    owner = next((u for u in users if u['id'] == data['owner_id']), None)
    if not owner:
        return jsonify({"message": "Owner not found"}), 404

    slot = {
        "id": len(parking_slots) + 1,
        "latitude": data['latitude'],
        "longitude": data['longitude'],
        "description": data['description'],
        "status": "available",
        "owner_id": owner['id']
    }
    parking_slots.append(slot)
    return jsonify({"message": "Parking slot added successfully!", "slot": slot}), 201

# Route : Lister les places de parking
@app.route('/list_parking_slots', methods=['GET'])
def list_parking_slots():
    return jsonify({"parking_slots": parking_slots}), 200

# Route : Réserver une place de parking (avec paiement)
@app.route('/reserve', methods=['POST'])
def reserve_parking_slot():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.json
    if not data.get('user_id') or not data.get('slot_id'):
        return jsonify({"message": "Missing data: user_id or slot_id"}), 400

    user = next((u for u in users if u['id'] == data['user_id']), None)
    slot = next((s for s in parking_slots if s['id'] == data['slot_id']), None)

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not slot:
        return jsonify({"message": "Parking slot not found"}), 404
    if slot['status'] == "reserved":
        return jsonify({"message": "Parking slot already reserved"}), 400

    if user['balance'] < 2.0:
        return jsonify({"message": "Insufficient balance"}), 400

    # Paiement
    user['balance'] -= 2.0  # Débiter l'utilisateur
    slot_owner = next((u for u in users if u['id'] == slot.get('owner_id')), None)
    if slot_owner:
        slot_owner['balance'] += 1.0  # Créditer le propriétaire de la place

    # Enregistrer la transaction
    transaction = {
        "id": len(transactions) + 1,
        "user_id": user['id'],
        "slot_id": slot['id'],
        "amount": 2.0,
        "application_fee": 1.0,
        "owner_credit": 1.0
    }
    transactions.append(transaction)

    # Marquer la place comme réservée
    slot['status'] = "reserved"
    reservation = {
        "id": len(reservations) + 1,
        "user_id": user['id'],
        "slot_id": slot['id']
    }
    reservations.append(reservation)

    return jsonify({"message": "Slot reserved successfully!", "reservation": reservation, "transaction": transaction}), 201

# Route : Annuler une réservation
@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 400

    data = request.json
    if not data.get('reservation_id'):
        return jsonify({"message": "Missing data: reservation_id"}), 400

    reservation = next((r for r in reservations if r['id'] == data['reservation_id']), None)
    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    slot = next((s for s in parking_slots if s['id'] == reservation['slot_id']), None)
    if slot:
        slot['status'] = "available"

    reservations.remove(reservation)
    return jsonify({"message": "Reservation cancelled successfully!"}), 200

# Route : Vérifier le solde d’un utilisateur
@app.route('/balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"balance": user['balance']}), 200

# Route : Consulter les transactions
@app.route('/transactions', methods=['GET'])
def list_transactions():
    return jsonify({"transactions": transactions}), 200

# Route : Accueil
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Parking API"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
