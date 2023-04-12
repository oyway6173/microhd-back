import pika, json, os

def start(message, fs_videos, fs_mp3s, channel):
    message = {
        "cpu": 1.2,
        "memory": 0.3
    } 

    try: 
        channel.basic_publish(
            exchange="", 
            routing_key=os.environ.get("INFO_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message"