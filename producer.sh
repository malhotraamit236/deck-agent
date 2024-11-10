#!/bin/sh

# Redis connection details (adjust if needed)
REDIS_HOST="redis"  # Redis server hostname or IP
REDIS_PORT="6379"   # Redis server port (default is 6379)
REDIS_LIST="task_queue"  # Name of the Redis list to push data to
redis-cli -h $REDIS_HOST -p $REDIS_PORT FLUSHALL
# Loop forever to produce test data repeatedly
# while true; do
  # Produce data for IDs 1 to 20
  for id in $(seq 1 20); do

    
    # Push the JSON data to the Redis list using LPUSH
    echo "Pushing task data (post_id=$id) to Redis list $REDIS_LIST"
    redis-cli -h $REDIS_HOST -p $REDIS_PORT LPUSH $REDIS_LIST "$id"
    
    # Optional: sleep for a short time to avoid hammering the Redis server
    sleep 0.1  # Adjust the sleep time as needed
  done
  
  sleep 3  
exit 0
# done
