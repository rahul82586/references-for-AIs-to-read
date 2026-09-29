"""M5 patch: RedisEventBus URL support + ping for health checks."""
import io

PATH = "infrastructure/messaging/redis_event_bus.py"
with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old_init = (
    "        self._local_handlers: dict = {}\r\n"
    "        self._pending_redis_channels: set = set()\r\n"
    "        self._host = host\r\n"
)
new_init = (
    "        self._local_handlers: dict = {}\r\n"
    "        self._pending_redis_channels: set = set()\r\n"
    "        # M5: every production caller passes a URL (REDIS_URL, e.g. rediss://\r\n"
    "        # for TLS providers like Upstash) as the first positional argument,\r\n"
    "        # but connect() used it as a bare hostname - DNS could never resolve\r\n"
    "        # it, so the REDIS_URL path had never actually been exercised. A URL\r\n"
    "        # is now detected and routed through from_url(); host/port stay for\r\n"
    "        # direct construction.\r\n"
    "        self._url: Optional[str] = (\r\n"
    "            host\r\n"
    "            if isinstance(host, str)\r\n"
    "            and host.startswith((\"redis://\", \"rediss://\", \"unix://\"))\r\n"
    "            else None\r\n"
    "        )\r\n"
    "        self._host = host\r\n"
)
assert src.count(old_init) == 1, "init anchor not found"
src = src.replace(old_init, new_init)

old_connect = (
    "    async def connect(self) -> None:\r\n"
    "        \"\"\"Establishes connection to Redis.\"\"\"\r\n"
    "        self._redis_client = redis.Redis(\r\n"
    "            host=self._host,\r\n"
    "            port=self._port,\r\n"
    "            db=self._db,\r\n"
    "            decode_responses=False\r\n"
    "        )\r\n"
    "        logger.info(f\"Connected to Redis at {self._host}:{self._port}\")\r\n"
)
new_connect = (
    "    async def connect(self) -> None:\r\n"
    "        \"\"\"Establishes connection to Redis (URL or host/port).\"\"\"\r\n"
    "        if self._url is not None:\r\n"
    "            self._redis_client = redis.Redis.from_url(\r\n"
    "                self._url, decode_responses=False\r\n"
    "            )\r\n"
    "            where = _mask_url(self._url)\r\n"
    "        else:\r\n"
    "            self._redis_client = redis.Redis(\r\n"
    "                host=self._host,\r\n"
    "                port=self._port,\r\n"
    "                db=self._db,\r\n"
    "                decode_responses=False\r\n"
    "            )\r\n"
    "            where = f\"{self._host}:{self._port}\"\r\n"
    "        # Fail at startup, not at first publish: a URL that cannot be reached\r\n"
    "        # must stop the boot rather than silently degrade the bus.\r\n"
    "        await self._redis_client.ping()\r\n"
    "        logger.info(f\"Connected to Redis at {where}\")\r\n"
    "\r\n"
    "    async def ping(self) -> bool:\r\n"
    "        \"\"\"Liveness probe for /health. False when not connected.\"\"\"\r\n"
    "        if self._redis_client is None:\r\n"
    "            return False\r\n"
    "        return bool(await self._redis_client.ping())\r\n"
)
assert src.count(old_connect) == 1, "connect anchor not found"
src = src.replace(old_connect, new_connect)

# add the masking helper next to the logger definition
old_logger = "logger = logging.getLogger(__name__)\r\n"
new_logger = (
    "logger = logging.getLogger(__name__)\r\n"
    "\r\n"
    "\r\n"
    "def _mask_url(url: str) -> str:\r\n"
    "    \"\"\"Strip credentials so a Redis URL is safe to log.\"\"\"\r\n"
    "    try:\r\n"
    "        from urllib.parse import urlsplit\r\n"
    "\r\n"
    "        parts = urlsplit(url)\r\n"
    "        host = parts.hostname or \"\"\r\n"
    "        if parts.port:\r\n"
    "            host = f\"{host}:{parts.port}\"\r\n"
    "        return f\"{parts.scheme}://{host}\"\r\n"
    "    except ValueError:\r\n"
    "        return \"<unparseable url>\"\r\n"
)
assert src.count(old_logger) == 1, "logger anchor not found"
src = src.replace(old_logger, new_logger)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("redis_event_bus.py patched: URL support + startup ping + health ping + masked logging")
