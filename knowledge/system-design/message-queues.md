---
difficulty: medium
last_sent: 2026-07-15 11:56:41.236829+00:00
review_count: 1
tags:
- message-queue
- async
- kafka
- rabbitmq
- decoupling
topic: system-design
---

# Message queues

Message Queues enable asynchronous communication between services by temporarily storing messages until they're processed. Think of it as a post office mailbox where senders drop letters without waiting for recipients to read them.

## How it works

1. **Producer** — Service that sends messages to the queue without waiting for processing completion. It fires and forgets.
2. **Queue** — Persistent storage that holds messages in order until consumers are ready. Survives service restarts.
3. **Consumer** — Service that pulls messages and processes them at its own pace. Multiple consumers can read from the same queue.
4. **Acknowledgment** — Consumer confirms successful processing. On failure, message returns to queue for retry. Prevents message loss.

## Patterns

- **Point-to-point**: One message → one consumer (task processing). Like a to-do list — only one person does each task.
- **Pub/Sub**: One message → multiple consumers (event broadcasting). Like a newsletter — everyone subscribed gets it.
- **Priority queue**: High-priority messages processed first. Payment processing before analytics.
- **Dead letter queue**: Failed messages routed to a separate queue for inspection. Don't block the main queue with poison messages.

## Why use it

- **Decoupling** — Producers don't wait for slow consumers, preventing cascading failures. If the email service is slow, orders still process.
- **Spike absorption** — Buffers requests during peak loads (Black Friday) instead of overwhelming downstream services
- **Retry logic** — Failed operations automatically retry without custom code. Built-in resilience.
- **Delivery guarantees** — Messages persist even if consumers are temporarily down. Process when you're ready.

## Delivery semantics

- **At-most-once** — Fast, but messages can be lost. Fire and forget. Good for metrics, logs.
- **At-least-once** — Messages may be duplicated; consumers must be idempotent. Most common choice.
- **Exactly-once** — Hardest to achieve, usually requires consumer-side dedup. Use when duplication is unacceptable (payments).

## Choosing a tool

- **RabbitMQ**: Traditional message queue. Good for task queues, RPC. Supports complex routing.
- **Apache Kafka**: Event streaming platform. High throughput, durable, replayable. Good for event sourcing.
- **AWS SQS**: Fully managed. Simple. Good for decoupling AWS services.
- **Redis Pub/Sub**: Lightweight, fast. Good for real-time notifications, not for durability.

## Real impact

Uber uses queues for ride matching. When you request a ride, the request goes to a queue. Driver matching happens asynchronously without blocking your app. During surge, queues buffer millions of requests instead of dropping them.

## Popular tools

RabbitMQ (traditional queue), Apache Kafka (event streaming), AWS SQS (managed), Redis Pub/Sub (lightweight), NATS (cloud-native)