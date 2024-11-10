# Deck Agent
A sample demonstrationg how to design a data gathering and publishing system that is scalable.

## How to run?
```
docker compose up --build
```
You'll should start seeing logs from the three agent instances (hardcoded 3 replicas in `docker-compose.yml`)

The `producer` service that enqueues work will shutdown after enqueueing 20 tasks. To keep repeating it change the restart property for producer in the `docker-compose.yml` to "always"

## Architecture
Agent contains:
- `api_client` module to fetch data from a mock service `jsonplaceholder.typicode.com`
- `business_logic` Business logic module that uses `api_client` module to gather dummy `posts` data by `id`` and then does a simple transformation (count of the characters in title) and then publishes to a simulated rabbitmq channel
- `message_queue` module simulates RabbitMQ

### Work distribution - horizontal scalability
- Redis is used in this project for simplicity for distributing the work among various instances of `agent` service
- using `BRPOPLPUSH` a reliable queue system is created
- work is queued in a `task_queue` and each `agent` instance pops the task from the queue puts atomically into a `processing_queue` and also processes the poped task.
- `process_task` is where the actual work and restries are handled

## What needs to be done to make it cloud/production ready?
- As it currently stands, the work distribution is handled via Redis which is not durable - Using a proper a more reliable Cloud native service like AWS SQS we can make this agent more reliable
- This is a very crude implementation of `process_task`. For production use we'd need to decouple various function/system boundary errors for more reslience. 
- We can seek more than one task at a time in a single process and use co-routies to work on them concurrently. this will let us scale more optimally (diagonally)
- Needs structured logging
- needs unit tests for business_logic - separation of concerns can still be improved a lot
- this demo doesn't show any best practices regarding security - for example, secrets shouldn't be put in evironment vars if there were secrets for systems used in this demo, like for Redis authn, API authn etc.
- graceful shutdown remains to be implemented
- better retry with backoff remains to be implemented
- we also need to have better telementry using open standards like OTEL or cloud-native services like AWS Cloudwatch
