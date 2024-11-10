import time
import random
from typing import Any

class FakeRabbitMQQueue:
    def __init__(self, name: str):
        self.name = name
        self.messages = []

    def add_message(self, message: str):

        self.messages.append(message)

    def get_messages(self):

        return self.messages

class Channel:
    def __init__(self):
        self.queue = None
    
    def declare_queue(self, queue_name: str):

        self.queue = FakeRabbitMQQueue(queue_name)
        print(f"Queue '{queue_name}' declared.")
    
    def basic_publish(self, message: str):

        if not self.queue:
            raise Exception("Queue not declared.")
        
        print(f"Publishing message: {message}")
        self.queue.add_message(message)
        print(f"Message published to queue '{self.queue.name}'.")

class Publisher:
    def __init__(self, channel: Channel, queue_name: str):
        self.channel = channel
        self.queue_name = queue_name
        self.channel.declare_queue(queue_name)
    
    def publish(self, message: Any):

        if isinstance(message, str):
            message_body = message
        else:
            message_body = str(message)

        # Simulate network delay or processing delay
        time.sleep(random.uniform(0.1, 0.5))  # random delay to simulate real-time processing
        
        self.channel.basic_publish(message_body)
        print(f"Message '{message_body}' published to RabbitMQ (simulated).")

    def get_published_messages(self):

        return self.channel.queue.get_messages()
