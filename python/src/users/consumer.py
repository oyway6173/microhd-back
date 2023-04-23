import pika, sys, os, time, json
from flask import Flask, request, jsonify
from action import actions
from flaskext.mysql import MySQL

server = Flask(__name__)
mysql = MySQL()
mysql.init_app(server)

server.config["MYSQL_DATABASE_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_DATABASE_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_DATABASE_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DATABASE_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_DATABASE_PORT"] = int(os.environ.get("MYSQL_PORT"))


def main():

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        pass
        err = actions.create(body, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("USERS_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

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