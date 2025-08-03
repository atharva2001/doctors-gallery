from aiokafka import AIOKafkaConsumer
import asyncio
import json

async def consume():
    consumer = AIOKafkaConsumer(
        "new_doc_notifier",
        bootstrap_servers="kafka:9092",
        group_id="test-group",
        auto_offset_reset="earliest"  # important for catching older messages
    )
    await consumer.start()
    print("AIOKafkaConsumer started. Listening for messages...", flush=True)
    try:
        async for msg in consumer:
            dict_msg = json.loads(msg.value.decode("utf-8"))["message"]
            print(dict_msg, flush=True)
            print(f'Consumer msg: {msg.value.decode("utf-8")}', flush=True)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())  