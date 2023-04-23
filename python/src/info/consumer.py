import pika, sys, os, time, json
from flask import Flask, request, jsonify
# from flask_mysqldb import MySQL
from dash import info_to_dash
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
        
        message = json.loads(body)

        response = {}

        match message['route']:
            case '/dash':
                response = info_to_dash.dash(message["uid"])
            case "/tickets":
                response = info_to_dash.tickets(message["uid"], message["role"])
            case "/faq":
                response = info_to_dash.faq()
            case '/rating':
                response = info_to_dash.rating(message["uid"])
            case '/profile':
                response = info_to_dash.profile(message["uid"])
            case '/users':
                response = info_to_dash.users()
            case '/roles':
                response = info_to_dash.roles()
            case '/deps':
                response = info_to_dash.deps()
            case '/statuses':
                response = info_to_dash.statuses()
            case '/priorities':
                response = info_to_dash.priorities()


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