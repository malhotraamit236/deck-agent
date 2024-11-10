import asyncio
import redis
import json
from api_client import ApiClient
from message_queue import Channel, Publisher
from config import load_config

def get_redis_client():
    config = load_config()
    redis_config = config['redis']
    return redis.StrictRedis(
        host=redis_config['host'],
        port=redis_config['port'],
        db=redis_config['db'],
        password=redis_config['password'],
        socket_timeout=redis_config['timeout']
    )

def get_message_queue_client():
    config = load_config()
    message_queue_config = config['message_queue']
    channel = Channel()
    publisher = Publisher(channel, message_queue_config['queue_name'])
    return publisher

redis_client = get_redis_client()
message_queue_client = get_message_queue_client()

MAX_RETRY_COUNT = 3
RETRY_HASHMAP = 'task_retries'

# TODO: this is a very crude implementation of process_task
# For production use we'd need to decouple various function/system boundary errors for more reslience.
# There are many other improvements such as - we can seek more than one task at a time in a single process
# and use co-routies to work on them concurrently.
async def process_task(task_id: int, processing_queue: str):
    try:
        retry_count = int(redis_client.hget(RETRY_HASHMAP, task_id) or 0)
        print(f"Processing task {task_id}, retries={retry_count}")
        
        async with ApiClient() as client:
            post = await client.get(f"/posts/{task_id}", dict)

            # Non-retryable error: post is None or title is missing
            if post is None or post.get('title') is None:
                print(f"Non-retryable error for task {task_id}: Post or title is missing.")
                redis_client.lrem(processing_queue, 0, task_id)
                redis_client.hdel(RETRY_HASHMAP, task_id)
                return 

            letter_count = len(post['title'])
            message = f"{post['id']}:{letter_count}"

            # TODO: handle this error separately
            message_queue_client.publish(message)

            redis_client.lrem(processing_queue, 0, task_id)
            redis_client.hdel(RETRY_HASHMAP, task_id)
        

    except Exception as e:
        # Retryable error handling
        retry_count = int(redis_client.hget(RETRY_HASHMAP, task_id) or 0)
        if retry_count < MAX_RETRY_COUNT - 1:
            print(f"Retrying task {task_id} due to error: {str(e)}")
            redis_client.rpoplpush(processing_queue, "task_queue")
            redis_client.hincrby(RETRY_HASHMAP, task_id, 1)
        else:
            # Non-retryable error after max retries
            redis_client.lrem(processing_queue, 0, task_id)
            print(f"Removing task {task_id} from processing_queue after reaching max retries.")
            redis_client.hdel(RETRY_HASHMAP, task_id)




async def run():
    task_queue = 'task_queue'
    processing_queue = 'processing_queue'
   
    while True:
        task_id = redis_client.brpoplpush(task_queue, processing_queue, 5)
        
        if task_id is None:
            print(f"await new tasks...")
            await asyncio.sleep(1)
            continue
        
        await process_task(int(task_id), processing_queue)
        await asyncio.sleep(1)


# TODO: implement a watcher co-routine to watch for tasks that have been retried max or have been there long
# and handle them