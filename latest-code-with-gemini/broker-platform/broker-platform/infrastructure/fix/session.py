"""
FIX session transports (M10).

IFixSession is the narrow port the liquidity gateway talks to: connect, send a
FixMessage, await the next FixMessage, close. Sequence numbers, logon and
heartbeat framing are the TRANSPORT's responsibility - that is exactly the part
quickfixn already does correctly, so the gateway never re-implements it.

Two implementations live here:

  * QuickFixSession - skeleton adapter over the quickfixn C++ engine
    (pip: quickfix). NOT exercised in CI: quickfixn needs a native build and
    there is no LP endpoint in the test environment. It is written against the
    documented quickfix API and fails loudly at construction when the module
    is absent.

  * SimulatedFixSession - an honest in-process LP simulator (separate module,
    simulated_session.py) used by tests and the m10 proof. It parses what the
    gateway sends and answers like a real counterparty would (ExecutionReports,
    MarketDataSnapshots). It moves no money and says so.
"""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

from infrastructure.fix.messages import FixMessage, FixParseError

logger = logging.getLogger(__name__)


class FixSessionClosed(RuntimeError):
    """Raised by recv() when the session is closed or dropped."""


class IFixSession(ABC):
    """Transport port: an ordered, reliable FIX message pipe."""

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def send(self, msg: FixMessage) -> None: ...

    @abstractmethod
    async def recv(self) -> FixMessage:
        """Await the next inbound message; raises FixSessionClosed at EOF."""

    @abstractmethod
    async def close(self) -> None: ...


class QuickFixSession(IFixSession):
    """
    quickfixn ThreadedSocketInitiator session (SKELETON - untestable in CI).

    quickfixn callbacks arrive on engine threads; inbound messages are marshalled
    onto the asyncio loop through a Queue via run_coroutine_threadsafe. Outbound
    messages are handed to Session.sendToTarget after logon.
    """

    def __init__(
        self,
        host: str,
        port: int,
        sender_comp_id: str,
        target_comp_id: str,
        *,
        begin_string: str = "FIX.4.4",
        heartbeat_interval: int = 30,
        reconnect_interval: int = 5,
    ) -> None:
        try:
            import quickfix  # noqa: F401
        except ImportError as e:  # pragma: no cover - env dependent
            raise RuntimeError(
                "quickfixn is not installed (pip: quickfix). The FIX gateway needs "
                "it for real LP connectivity; for local testing set "
                "BROKER_FIX_SIMULATOR=1 to use the in-process simulated LP."
            ) from e
        self.host = host
        self.port = int(port)
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.begin_string = begin_string
        self.heartbeat_interval = heartbeat_interval
        self.reconnect_interval = reconnect_interval
        self._initiator = None
        self._session_id = None
        self._queue: "asyncio.Queue[Optional[FixMessage]]" = asyncio.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._logged_on = asyncio.Event()
        self._connected = False

    # --- quickfix Application callbacks (engine thread) --------------------

    def _put(self, msg: Optional[FixMessage]) -> None:
        if self._loop is None or self._loop.is_closed():  # pragma: no cover
            return
        asyncio.run_coroutine_threadsafe(self._queue.put(msg), self._loop)

    def onCreate(self, session_id):  # noqa: N802 - quickfix API
        self._session_id = session_id

    def onLogon(self, session_id):  # noqa: N802 - quickfix API
        self._session_id = session_id
        self._connected = True
        if self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._logged_on.set(), self._loop)

    def onLogout(self, session_id):  # noqa: N802 - quickfix API
        self._connected = False
        self._put(None)  # EOF sentinel -> recv() raises FixSessionClosed

    def toAdmin(self, message, session_id):  # noqa: N802 - quickfix API
        pass  # quickfix owns header/seqnum/logon framing

    def fromAdmin(self, message, session_id):  # noqa: N802 - quickfix API
        self._forward(message)

    def toApp(self, message, session_id):  # noqa: N802 - quickfix API
        pass

    def fromApp(self, message, session_id):  # noqa: N802 - quickfix API
        self._forward(message)

    def _forward(self, qf_message) -> None:
        try:
            self._put(FixMessage.parse(str(qf_message), verify=False))
        except FixParseError as e:  # pragma: no cover - defensive
            logger.error("dropping unparseable inbound FIX message: %s", e)

    # --- IFixSession --------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        import quickfix

        self._loop = asyncio.get_running_loop()
        settings = quickfix.SessionSettings(
            f"""
[DEFAULT]
FileStorePath=/tmp/fixstore-{self.sender_comp_id}
FileLogPath=/tmp/fixlog-{self.sender_comp_id}
ConnectionType=initiator
ReconnectInterval={self.reconnect_interval}
StartTime=00:00:00
EndTime=00:00:00
HeartBtInt={self.heartbeat_interval}
UseDataDictionary=N

[SESSION]
BeginString={self.begin_string}
SenderCompID={self.sender_comp_id}
TargetCompID={self.target_comp_id}
SocketConnectHost={self.host}
SocketConnectPort={self.port}
"""
        )
        self._initiator = quickfix.ThreadedSocketInitiator(self, settings)
        self._initiator.start()
        try:
            await asyncio.wait_for(self._logged_on.wait(), timeout=15)
        except asyncio.TimeoutError as e:  # pragma: no cover - env dependent
            self._initiator.stop()
            raise RuntimeError(
                f"FIX logon to {self.host}:{self.port} timed out "
                f"(sender={self.sender_comp_id} target={self.target_comp_id})"
            ) from e

    async def send(self, msg: FixMessage) -> None:
        import quickfix

        if self._session_id is None or not self._connected:
            raise FixSessionClosed("FIX session is not logged on")
        qf_msg = quickfix.Message(msg.encode())
        await asyncio.get_running_loop().run_in_executor(
            None, quickfix.Session.sendToTarget, qf_msg, self._session_id
        )

    async def recv(self) -> FixMessage:
        item = await self._queue.get()
        if item is None:
            raise FixSessionClosed("FIX session logged out or dropped")
        return item

    async def close(self) -> None:
        self._connected = False
        if self._initiator is not None:  # pragma: no cover - env dependent
            self._initiator.stop()
            self._initiator = None


__all__ = ["IFixSession", "FixSessionClosed", "QuickFixSession"]
