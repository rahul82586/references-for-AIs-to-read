"""M5 patch: move `disconnect` out of _Subscription (where it was misfiled) into RedisEventBus.

Before this patch RedisEventBus inherited IEventBus.disconnect as an unimplemented
abstract method - the class could not be instantiated at all, so every REDIS_URL
startup died with TypeError. The real body existed but was indented into the
_Subscription helper (which has __slots__ = () and none of the referenced attrs).
"""
import io

PATH = "infrastructure/messaging/redis_event_bus.py"
with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    src = f.read()

misfiled = (
    "\r\n"
    "    async def disconnect(self) -> None:\r\n"
    "        \"\"\"Closes the Redis connection and cleans up resources.\"\"\"\r\n"
    "        if self._pubsub:\r\n"
    "            await self._pubsub.unsubscribe()\r\n"
    "            await self._pubsub.close()\r\n"
    "            self._pubsub = None\r\n"
    "\r\n"
    "        if self._redis_client:\r\n"
    "            await self._redis_client.close()\r\n"
    "            self._redis_client = None\r\n"
    "\r\n"
    "        logger.info(\"Redis Event Bus disconnected\")\r\n"
)
assert src.count(misfiled) == 1, "misfiled disconnect block not found"
src = src.replace(misfiled, "")  # remove from _Subscription (it is the class tail)

# add the real disconnect to RedisEventBus, right after ping()
ping_anchor = (
    "    async def ping(self) -> bool:\r\n"
    "        \"\"\"Liveness probe for /health. False when not connected.\"\"\"\r\n"
    "        if self._redis_client is None:\r\n"
    "            return False\r\n"
    "        return bool(await self._redis_client.ping())\r\n"
)
real_disconnect = ping_anchor + (
    "\r\n"
    "    async def disconnect(self) -> None:\r\n"
    "        \"\"\"Closes the Redis connection and cleans up resources.\"\"\"\r\n"
    "        if self._pubsub:\r\n"
    "            try:\r\n"
    "                await self._pubsub.unsubscribe()\r\n"
    "                await self._pubsub.close()\r\n"
    "            finally:\r\n"
    "                self._pubsub = None\r\n"
    "\r\n"
    "        if self._redis_client:\r\n"
    "            try:\r\n"
    "                await self._redis_client.close()\r\n"
    "            finally:\r\n"
    "                self._redis_client = None\r\n"
    "\r\n"
    "        logger.info(\"Redis Event Bus disconnected\")\r\n"
)
assert src.count(ping_anchor) == 1, "ping anchor not found"
src = src.replace(ping_anchor, real_disconnect)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("disconnect moved into RedisEventBus")
