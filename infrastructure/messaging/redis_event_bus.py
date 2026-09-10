"""
Redis Event Bus - High-Performance Pub/Sub Implementation

This adapter implements the IEventBus interface using redis.asyncio.
It provides a scalable, distributed event routing mechanism for the platform.
"""
import json
import logging
from typing import Callable, Any, Optional

import redis.asyncio as redis

from core.events.domain_events import DomainEvent
from core.ports.interfaces import IEventBus

logger = logging.getLogger(__name__)


class RedisEventBus(IEventBus):
    """
    Redis-based implementation of the Event Bus.

    Architectural Purpose:
    Provides a high-performance, pub/sub mechanism for distributing domain events.
    Uses Redis Pub/Sub to fan-out messages to multiple subscribers
    (Analytics, AI, Notifications) in real-time.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._host = host
        self._port = port
        self._db = db
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """Establishes connection to Redis."""
        self._redis_client = redis.Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            decode_responses=False
        )
        logger.info(f"Connected to Redis at {self._host}:{self._port}")

    async def publish(self, event: DomainEvent) -> None:
        """
        Serializes the event to JSON and publishes it to a channel named after its type.

        Example Channel: "order.created"

        This is non-blocking and fire-and-forget, ensuring high throughput
        even under heavy load.
        """
        if not self._redis_client:
            await self.connect()

        channel = event.event_type.value
        message = json.dumps(event.to_dict()).encode('utf-8')

        try:
            await self._redis_client.publish(channel, message)
            logger.debug(f"Event published to {channel}: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            raise

    async def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        """
        Subscribes to a channel and processes incoming messages.

        When a message arrives, it deserializes the JSON payload
        and passes it to the provided callback function.

        Note: This method should be called within an asyncio task
        as it runs an infinite listening loop.
        """
        if not self._redis_client:
            await self.connect()

        if self._pubsub is None:
            self._pubsub = self._redis_client.pubsub()

        await self._pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")

        async def _listen_loop():
            """Internal loop that listens for messages and invokes callback."""
            try:
                async for message in self._pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'].decode('utf-8'))
                            await callback(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode message from {channel}: {e}")
                        except Exception as e:
                            logger.error(f"Error processing message from {channel}: {e}")
            except asyncio.CancelledError:
                logger.info(f"Subscription to {channel} cancelled")
            except Exception as e:
                logger.error(f"Error in listen loop for {channel}: {e}")
                raise

        # Start the listener as a background task
        import asyncio
        asyncio.create_task(_listen_loop())

    async def disconnect(self) -> None:
        """Closes the Redis connection and cleans up resources."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None

        logger.info("Redis Event Bus disconnected")
