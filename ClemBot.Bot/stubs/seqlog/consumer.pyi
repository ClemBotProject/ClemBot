from _typeshed import Incomplete
from typing import Any

class QueueConsumer:
    is_running: bool
    state_lock: Incomplete
    consumer_thread: Incomplete
    flush_timer: Incomplete
    current_batch: Incomplete
    name: Incomplete
    queue: Incomplete
    callback: Incomplete
    batch_size: Incomplete
    auto_flush_timeout: Incomplete
    def __init__(self, name: Any, queue: Any, callback: Any, batch_size: Any, auto_flush_timeout: Incomplete | None = ...) -> None: ...
    @property
    def current_batch_size(self) -> Any: ...
    def flush(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
