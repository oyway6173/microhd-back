import pika, json

def send(action, access, data, channel):
    
    message = {
        "action": action, 
        "uid": access["uid"],
        "role": access["role"],
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "work_place": data["work_place"],
        "role": data["role"],
        "dep": data["dep"],
        "status": data["status"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="users",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(err)
        return f"/{err} internal server error2", 500