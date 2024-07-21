from flask import Flask, request, jsonify
from database import db
from models.user import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = "SUA_SECRET_KEY_PESSOAL"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


# view login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        # login
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print(current_user)
            return jsonify({
                "message": f"Usuário {username} autenticado com sucesso"
            }), 200

    return jsonify({
        "message": "Credenciais inválidas"
    }), 400


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({
                "message": "Já existe um usuário com esse username"
            }), 400
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "message": "Usuário cadastrado com sucesso"
        })

    return jsonify({
        "message": "Credenciais inválidas"
    }), 400


@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)
    if user:
        return jsonify({
            "username": user.username
        })

    return jsonify({
        "message": "Usuário não localizado"
    }), 404


@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
    user = User.query.get(id_user)
    data = request.json
    password = data.get('password')
    if user and password:
        user.password = password
        db.session.commit()

        return jsonify({
            "message": f"Usuário {user.username} atualizado com sucesso"
        })

    return jsonify({
        "message": "Usuário não localizado"
    }), 404


@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)
    if id_user == current_user.id:
        return jsonify({
            "message": "Não permitido"
        }), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "message": f"Usuário {user.username} deletado com sucesso"
        })

    return jsonify({
        "message": "Usuário não localizado"
    }), 404


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({
        "message": "Logout realizado com sucesso"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
