import asyncio
import inspect
import logging
import typing as t
import weakref as wr

log = logging.getLogger(__name__)


class Messenger:
    """This is the global message bus that handles all application level events"""

    def __init__(self, name=None) -> None:
        log.info(f'New messenger created with name: {name}')
        self.name = name
        self._events: t.Dict[str, t.Awaitable] = {}

    async def publish(self, event: str, *args, **kwargs) -> None:
        """
        Publishes an event with given args onto the global message bus

        Args:
            event (str): The event invoke the listeners on
        """
        log.info(f'Recieved published event: {event}')
        event = event
        print(event)
        if event in self._events.keys():
            listeners = self._events[event]
            for i, sub in enumerate(listeners):
                if sub._alive:
                    log.info(f'Invoking listener: {sub} on event {event} in Messenger: {self.name}')
                    await sub()(*args, **kwargs)
                else:
                    log.info(f'Deleting dead reference in Event: {event} function: {sub}')
                    del listeners[i]

    def subscribe(self, event: str, callback: t.Awaitable) -> None:
        """Subscribes a method as a callback listener to a given event """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError('A given messenger callback must be awaitable')

        weak_ref = self._getWeakRef(callback)
        if event in self._events.keys():
            self._events[event].append(weak_ref)
        else:
            log.info(f'Registering new event: {event} to Messenger: {self.name}')
            self._events[event] = [weak_ref]

        log.info(f'Registering listener {callback} to event: {event} in Messenger: {self.name}')

    def _getWeakRef(self, obj):
        """
        Get a weak reference to obj. If obj is a bound method, a WeakMethod
        object, that behaves like a WeakRef, is returned; if it is
        anything else a WeakRef is returned.
        """
        if inspect.ismethod(obj):
            createRef = wr.WeakMethod
        else:
            createRef = wr.ref
        return createRef(obj)
