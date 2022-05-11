import asyncio
import dataclasses
import inspect
import logging
import traceback
import typing as t
import weakref as wr

log = logging.getLogger(__name__)


@dataclasses.dataclass
class QueuedEvent:
    name: str
    args: tuple
    kwargs: dict


@dataclasses.dataclass
class DispatchQueue:
    task: asyncio.Task
    cancelled: bool = False


class Messenger:
    """The global message bus that handles all application level events"""

    def __init__(self, name=None) -> None:
        log.info('New messenger created with name: {name}', name=name)
        self.name = name
        self._events: t.Dict[str, t.List[t.Awaitable]] = {}

        # Error callback to report exceptions in queued events back to
        self.error_callback: t.Callable = None

        # pylint: disable=E1136
        self._guild_event_queue: t.Dict[int, asyncio.Queue[QueuedEvent]] = {}

        self._queue_dispatch_tasks: t.Dict[int, DispatchQueue] = {}

    def subscribe(self, event: str, callback: t.Awaitable) -> None:
        """Subscribes a method as a callback listener to a given event """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError('A given messenger callback must be awaitable')

        weak_ref = self.__get_weak_ref(callback)
        if event in self._events.keys():
            self._events[event].append(weak_ref)
        else:
            log.info('Registering new event: {event} to Messenger: {name}', event=str(event), name=self.name)
            self._events[event] = [weak_ref]

        log.info('Registering listener {callback} to event: {event} in Messenger: {name}',
                 callback=str(weak_ref.__callback__),
                 event=str(event),
                 name=self.name)

    async def publish(self, event: str, *args, **kwargs) -> None:
        """
        Immediately publishes an event to listeners with given args onto the global message bus
        Bypasses the messenger guild event queue

        Args:
            event (str): The event invoke the listeners on
        """
        log.info('Received published event: {event}', event=str(event))
        await self.__publish(event, *args, **kwargs)

    async def publish_to_queue(self, event: str, guild_id: int, *args, **kwargs) -> None:
        """
        Publishes an event to listeners with given args onto the guild message queue

        Args:
            event (str): The event invoke the listeners on
        """
        log.info('Received published to queue event: {event}', event=str(event))
        await self.__add_to_queue(event, guild_id, *args, **kwargs)

    async def close(self):
        """
        Sets all dispatch tasks to a cancellation state and clears the task dictionary
        """
        log.info('Gracefully closing all dispatch tasks with ids: {tasks}', tasks=list(self._queue_dispatch_tasks.keys()))

        for guild_id, dispatch_task in self._queue_dispatch_tasks.items():

            # Check if the event queue contains events to send, if it does not we can cancel the task
            if self._guild_event_queue[guild_id].qsize() == 0:
                dispatch_task.task.cancel()
                continue

            # Set the task to exit as soon as all events have cleared the queue
            dispatch_task.cancelled = True

        # Wait for all dispatch tasks to exit gracefully
        await asyncio.gather(*[task.task for _, task in self._queue_dispatch_tasks.items()])

        self._queue_dispatch_tasks.clear()

        log.info('All messenger tasks cancelled successfully')

    async def __publish(self, event: str, *args, **kwargs) -> None:
        if event in self._events.keys():
            listeners = self._events[event]
            for i, sub in enumerate(listeners):
                if sub._alive:
                    log.info('Invoking listener: {sub} on event {event} in Messenger: {name}',
                             sub=str(sub),
                             event=str(event),
                             name=self.name)
                    await sub()(*args, **kwargs)
                else:
                    log.info('Deleting dead reference in Event: {event} function: {sub}', event=str(event), sub=str(sub))
                    del listeners[i]

    async def __add_to_queue(self, event: str, guild_id: int, *args, **kwargs):

        # Check if the guild_id is the in the queue dict, if it's not we need to create the queue first
        if guild_id not in self._guild_event_queue:
            log.info('Creating guild event queue for guild {guild}', guild=guild_id)
            self._guild_event_queue[guild_id] = asyncio.Queue()

            # Create the polling task to dispatch events
            task = asyncio.create_task(self.__send_guild_queue(guild_id))

            # Add the task to the dispatch task list, so we can stop it later
            self._queue_dispatch_tasks[guild_id] = DispatchQueue(task=task)

        size = self._guild_event_queue[guild_id].qsize()
        log.info('Added event {event} to queue {queue} with new size {size}',
                 event=event,
                 queue=guild_id,
                 size=size + 1)

        complete_event = QueuedEvent(event, args, kwargs)

        await self._guild_event_queue[guild_id].put(complete_event)

    async def __send_guild_queue(self, guild_id: int):

        # Loop infinitely to dispatch events
        while True:
            event = await self._guild_event_queue[guild_id].get()
            size = self._guild_event_queue[guild_id].qsize()

            log.info('Dispatching queued event: {event} on queue: {queue} new queue size: {size}',
                     event=event.name,
                     queue=guild_id,
                     size=size)
            try:
                await self.__publish(event.name, *event.args, **event.kwargs)
            except Exception as e:
                # Check if we have an error callback to report the error too
                if self.error_callback:
                    # Notify the error callback of the exception and continue attempting to dispatch events
                    # We don't want to raise the exception further than this because
                    # That will exit our loop and cause no more events to be dispatched
                    tb = traceback.format_exc()
                    # pylint: disable=E1102
                    await self.error_callback(e, traceback=tb)
                else:
                    log.exception('No error callback set in messenger {messenger} for error {error}',
                                  messenger=self.name,
                                  error=e)

            # Check if the task has been cancelled AFTER we have attempted to dispatch all events
            # This is important for the tests to be deterministic
            if self._queue_dispatch_tasks[guild_id].cancelled and self._guild_event_queue[guild_id].qsize() == 0:
                return

    def __get_weak_ref(self, obj):
        """
        Get a weak reference to obj. If obj is a bound method, a WeakMethod
        object, that behaves like a WeakRef, is returned; if it is
        anything else a WeakRef is returned.
        """
        if inspect.ismethod(obj):
            create_ref = wr.WeakMethod
        else:
            create_ref = wr.ref
        return create_ref(obj)
