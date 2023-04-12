import pika, sys, os, time
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


def main():

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        response = {
                    "cpu": 14,
                    "memory": 88
                } 
        ch.basic_publish(exchange='',
                     routing_key=str(properties.reply_to),
                     properties=pika.BasicProperties(correlation_id = \
                                                         properties.correlation_id),
                     body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        #для справки - когда поступит сообщение из mq - произойдет вызов функции callback
        queue=os.environ.get("INFO_QUEUE"), on_message_callback=callback
    )

    print(" [x] Awaiting RPC requests")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try: 
            sys.exit(0)
        except SystemExit:
            os._exit(0)