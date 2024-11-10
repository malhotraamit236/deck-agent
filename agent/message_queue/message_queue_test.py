import pytest
from unittest import mock
import time
import random
from .message_queue import Publisher, Channel, FakeRabbitMQQueue  

@pytest.fixture(autouse=True)
def mock_sleep_and_random():
    with mock.patch('time.sleep', return_value=None), mock.patch('random.uniform', return_value=0.2):
        yield

def test_publisher_initialization():
    channel = Channel()

    publisher = Publisher(channel, "test_queue")

    assert publisher.channel.queue.name == "test_queue"
    assert isinstance(publisher.channel.queue, FakeRabbitMQQueue)


def test_publish_string_message():
    
    channel = Channel()
    publisher = Publisher(channel, "test_queue")

    publisher.publish("Test message")

    messages = publisher.get_published_messages()
    assert len(messages) == 1
    assert messages[0] == "Test message"


def test_publish_non_string_message():
    
    channel = Channel()
    publisher = Publisher(channel, "test_queue")
 
    publisher.publish(123)

    messages = publisher.get_published_messages()
    assert len(messages) == 1
    assert messages[0] == "123"


def test_publish_without_declaring_queue():
    
    channel = Channel()

    publisher = Publisher(channel, "test_queue")
    publisher.channel.queue = None  

    with pytest.raises(Exception, match="Queue not declared."):
        publisher.publish("Test message")


def test_get_published_messages():
    
    channel = Channel()
    publisher = Publisher(channel, "test_queue")

    publisher.publish("First message")
    publisher.publish("Second message")
    
    messages = publisher.get_published_messages()
    assert len(messages) == 2
    assert messages[0] == "First message"
    assert messages[1] == "Second message"
