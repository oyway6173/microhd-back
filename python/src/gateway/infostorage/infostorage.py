import pika, json
import uuid

def send(channel, access, route):
    
    match route:
        case "dash":
            message = {
                "route": route,
                "username": access["username"],
            }
    callback_queue = "info"    

    try:
        channel.basic_publish(
            exchange="",
            routing_key="info",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                # delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                reply_to = callback_queue,
            ),
        )
    except Exception as err:
        print(err)
        return f"/{err} internal server error2", 500

