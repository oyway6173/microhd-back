import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from infostorage import info_rpc_client
from sender import to_user_mnt_srv
from bson.objectid import ObjectId

server = Flask(__name__)

config = {
  'ORIGINS': [
    'http://localhost:3000', 
    'http://localhost:8081',  # React
    'http://127.0.0.1:3000',  # React
  ],

  'SECRET_KEY': '...'
}

CORS(server, resources={ r'/*': {'origins': config['ORIGINS']}}, supports_credentials=True)


mongo_video = PyMongo(
        server,
        uri="mongodb://host.minikube.internal:27017/videos"
    )

mongo_mp3 = PyMongo(
        server,
        uri="mongodb://host.minikube.internal:27017/mp3s"
    )

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else: 
        return err
    
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err
        
        return "success!", 200
    else:
        return "not authorized", 401
    
@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required"
        
        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401

@server.route("/dash", methods=["POST"])
def dash():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)

    if access["admin"]:
        
        noterr = info_rpc_client.InfoRpcClient()
        err = noterr.call(request.path, access)
        if err:
            return err
        
        # return "success!", 200
    else:
        return "not authorized", 401
    
@server.route("/tickets", methods=["POST"])
def tickets():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin' | 'user' | 'worker':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401

@server.route("/faq", methods=["POST"])
def faq():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case _:
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err

@server.route("/rating", methods=["POST"])
def rating():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin' | 'worker':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case 'user':
            return "not authorized", 401
        
@server.route("/profile", methods=["POST"])
def profile():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin' | 'user' | 'worker':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401
        
@server.route("/users", methods=["POST"])
def users():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401
    
@server.route("/roles", methods=["POST"])
def roles():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401

@server.route("/deps", methods=["POST"])
def deps():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401
        
@server.route("/statuses", methods=["POST"])
def statuses():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401
        
@server.route("/priorities", methods=["POST"])
def priorities():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)
    
    match access["role"]:
        case 'admin':
            noterr = info_rpc_client.InfoRpcClient()
            err = noterr.call(request.path, access)
            if err:
                return err
        case _:
            return "not authorized", 401

@server.route("/users/mnt", methods=["POST", "DELETE", "UPDATE"])
def users_mnt():
    access, err = validate.token(request)

    if err: 
        return err

    access = json.loads(access)

    match access["role"]:
        case 'admin':
            if request.method == "POST":
                err = to_user_mnt_srv.send("create", access, request.form, channel)
                if err:
                    return err
                return "success!", 200
            else: 
                return "method not allowed", 405
        case _:
            return "not authorized", 401



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
