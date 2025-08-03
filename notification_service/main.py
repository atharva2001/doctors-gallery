from fastapi import FastAPI
import uvicorn
from kafka import KafkaProducer
from contextlib import asynccontextmanager
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import asyncio
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

import json


producer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")

    for _ in range(10):
        try:
            await producer.start()
            app.state.kafka_producer = producer
            break
        except KafkaConnectionError:
            print("Kafka not ready, retrying...")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("Kafka not reachable after retries")

    yield

    await producer.stop()



app = FastAPI(
    title="Notification Service",
    description="A service to handle notifications using RabbitMQ",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Notification Service"}



@app.post("/create_message")
async def send(topic: str, message: str):
    try:
        value_json = json.dumps({"message": message}).encode("utf-8")
        await producer.send_and_wait(topic=topic, value=value_json)
        return {"status": "Message sent", "topic": topic}
    except Exception as e:
        return {"error": str(e)}

@app.post("/create-topic")
async def create_topic(topic_name: str):
    admin_client = KafkaAdminClient(
            bootstrap_servers="kafka:9092",
            client_id="admin"
        )
    # topic_name = f"topic_name_{doc_id}_{patient_id}"
    try:
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"Topic '{topic_name}' created.")
    except Exception as e:
        print(f"Topic creation failed: {e}")
    



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
    )
