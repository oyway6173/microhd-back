import jwt, datetime, os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))
# server.config["MYSQL_HOST"] = "host.minikube.internal"
# server.config["MYSQL_USER"] = "auth_user"
# server.config["MYSQL_PASSWORD"] = "Auth123"
# server.config["MYSQL_DB"] = "auth"
# server.config["MYSQL_PORT"] = 3306

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401 
    
    #check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password, role FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        role = user_row[2]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        elif role == 'admin':
            return jsonify(access_token=createJWT(auth.username, os.environ.get("JWT_SECRET"), True, "admin"))
        elif role == 'user':
            return jsonify(access_token=createJWT(auth.username, os.environ.get("JWT_SECRET"), False, 'user'))
        else:
            return jsonify(access_token=createJWT(auth.username, os.environ.get("JWT_SECRET"), True, 'worker'))
    else: 
        return "invalid credentials", 401
    
@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try: 
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403
    
    return decoded, 200
    
def createJWT(username, secret, authz, role):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(hours=2),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
            "role": role
        },
        secret,
        algorithm="HS256",
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
