import asyncio
import contextlib
import inspect
import logging
import typing as t
import uuid
from asyncio import Task
from datetime import datetime
from functools import partial
from typing import Optional
from uuid import uuid4

from discord.ext.commands.errors import BadArgument

log = logging.getLogger(__name__)


class Scheduler:

    def __init__(self) -> None:
        self._scheduled_tasks: t.Dict[t.Hashable, asyncio.Task] = {}

    def schedule_at(self, callback: t.Awaitable, *, time: datetime) -> uuid.UUID:
        """Schedules a callback for execution at a given datetime object

        Args:

            callback (t.Awaitable): The callback to be execute when time has expired

            time (datetime): The datetime object that specifies the date to execute the given
            callback

        Raises:

            BadArgument:

        Returns:

            uuid: Unique Identifier for the scheduled task 
        """

        delay_time = (time - datetime.utcnow()).total_seconds()
        if delay_time < 0:
            raise BadArgument('Scheduled task contained invalid negative time')

        if callback is None:
            raise BadArgument('Scheduled callback was none')

        return self._schedule(delay_time, callback)

    def schedule_in(self, callback: t.Awaitable, *, time: t.Union[int, float]) -> uuid.UUID:
        """Schedules a callback for exection in a given number of seconds

        Args:

            callback (t.Awaitable): The callback to be execute when time has expired

            time (t.Union[int, float]): Time in seconds to wait before executing
            the given callback

        Raises:

            BadArgument:

        Returns:

            uuid: Unique Identifier for the scheduled task 
        """

        if callback is None:
            raise BadArgument('Scheduled callback was none')

        if time < 0:
            raise BadArgument('Scheduled task contained invalid negative time')

        return self._schedule(time, callback)

    def get_task(self, task_id: int) -> Optional[Task]:
        if task_id in self._scheduled_tasks.keys():
            return self._scheduled_tasks[task_id]
        return None

    def __contains__(self, task_id: t.Hashable) -> bool:
        """Return True if a task with the given `task_id` is currently scheduled."""
        return task_id in self._scheduled_tasks

    def cancel(self, task_id):
        try:
            self._scheduled_tasks[task_id].cancel()
        except KeyError:
            log.error('Tried to cancel non existent task - Id: {task_id}', task_id=str(task_id))
            raise

        del self._scheduled_tasks[task_id]

    def _schedule(self, time, coro: t.Awaitable):

        task_id = uuid.uuid4()

        log.info('Scheduling coroutine - Id: {task_id} for execution in {time} seconds', task_id=str(task_id), time=time)

        del_coro = self._delayed_coro(time, coro, task_id)
        # creates a non-blocking task that elides the await
        task = asyncio.create_task(del_coro)

        # add the callback so the task can be closed and removed from the internal list
        task.add_done_callback(partial(self._end_scheduled_task, task_id))

        self._scheduled_tasks[task_id] = task
        return task_id

    async def _delayed_coro(self, delay: t.Union[float, int], coro: t.Awaitable, task_id: uuid.UUID):
        try:
            # await the timed delay
            log.info('Waiting {delay} seconds before executing coroutine with Id: {task_id}', delay=delay, task_id=str(task_id))
            await asyncio.sleep(delay)

            # time is up, execute the callback
            log.info('Delay complete for coroutine {task_id}; executing coroutine', task_id=str(task_id))
            await asyncio.shield(coro)
        # use a finally so that the coro is closed even if it throws
        finally:
            if inspect.getcoroutinestate(coro) == 'CORO_CREATED':
                log.info('Explicitly closing the coroutine for #{task_id}.', task_id=str(task_id))
                coro.close()
            else:
                log.info('Finally block reached for #{task_id}', task_id=str(task_id))

    def _end_scheduled_task(self, task_id, coro):
        finished_task = self._scheduled_tasks.get(task_id)
        if finished_task:
            del self._scheduled_tasks[task_id]

        with contextlib.suppress(asyncio.CancelledError):
            exception = coro.exception()
            # Log the exception if one exists.
            if exception:
                raise exception
