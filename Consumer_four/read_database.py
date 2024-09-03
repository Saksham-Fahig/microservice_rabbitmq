import pika
import pymongo
import json

# RabbitMQ setup
credentials = pika.PlainCredentials(username='guest', password='guest')
parameters = pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# Connect to MongoDB
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client["database"]
collection = db["ccdb"]

# Declare the "read_database" queue
channel.queue_declare(
    queue='read_database',
    durable=True
)

channel.queue_declare(queue='send_database', durable=True)
channel.queue_bind(exchange='microservices', queue='send_database', routing_key='send_database')

# Define the callback function to process incoming messages
def callback(ch, method, properties, body):
    # Retrieve all records from the database
    # records = collection.find()
    
    # # Send each record to the producer through RabbitMQ
    # for i in records:
    #     dict
    records = list(collection.find({}))

    records_json = json.dumps(records, default=str)  # `default=str` to handle ObjectId

    channel.basic_publish(exchange='microservices', routing_key='send_database', body=records_json)
    # channel.basic_publish(exchange='microservices', routing_key='send_database', body="TEST")

    # Acknowledge that the message has been processed
    channel.basic_ack(delivery_tag=method.delivery_tag)
    for i in records:
        print(i)

# Consume messages from the "read_database" queue
channel.basic_consume(queue='read_database', on_message_callback=callback)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()
