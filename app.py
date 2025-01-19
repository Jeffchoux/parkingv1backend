from flask import Flask, request, jsonify

app = Flask(__name__)

# Liste simulée pour stocker les utilisateurs (base de données simulée)
users = []

@app.route('/register', methods=['POST'])
def register_user():
    # Récupération des données envoyées dans la requête
    data = request.json

    # Debug : Afficher dans les logs les données reçues
    print("Data received:", data)

    # Vérifier que toutes les données nécessaires sont présentes
    if not data.get('email') or not data.get('password') or not data.get('plate_number'):
        return jsonify({"message": "Missing data"}), 400

    # Créer un utilisateur avec les données reçues
    user = {
        "id": len(users) + 1,  # Générer un ID unique
        "email": data['email'],
        "password": data['password'],  # ⚠️ Ne jamais stocker de mot de passe en clair dans une vraie application
        "plate_number": data['plate_number']
    }

    # Ajouter l'utilisateur à la liste simulée
    users.append(user)

    # Retourner une réponse de succès
    return jsonify({
        "message": "User registered successfully!",
        "user": user
    }), 201


# Point d'entrée pour exécuter le serveur Flask
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
