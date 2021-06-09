from discord.ext.commands.errors import BadArgument
import pytest
import asyncio
from datetime import datetime

from bot.utils.scheduler import Scheduler

class TestScheduler:

    def test_schedule_at_invalid_time_throws_bad_arg(self):
        s = Scheduler()
        with pytest.raises(BadArgument):
            s.schedule_at(None, time= datetime(1, 1, 1, 0, 0))

    def test_schedule_at_null_callback_throws_bad_arg(self):
        s = Scheduler()
        with pytest.raises(BadArgument):
            s.schedule_at(None, time= datetime(1, 1, 1, 0, 0))

    def test_schedule_at_valid_time_adds_to_tasks(self):
        async def foo():
            pass

        async def valid_time_test():
            s = Scheduler()
            s.schedule_at(foo, time= datetime(year=2100, month= 1, day=1))

            assert len(s._scheduled_tasks) == 1
        asyncio.get_event_loop().run_until_complete(valid_time_test())

    def test_schedule_in_invalid_time_throws_bad_arg(self):
        async def foo():
            pass

        s = Scheduler()
        with pytest.raises(BadArgument):
            s.schedule_in(foo, time= -1)

    def test_schedule_in_null_callback_throws_bad_arg(self):
        s = Scheduler()
        with pytest.raises(BadArgument):
            s.schedule_in(None, time= datetime(1, 1, 1, 0, 0))

    def test_schedule_in_valid_time_adds_to_tasks(self):
        async def foo():
            pass

        async def valid_time_test():
            s = Scheduler()
            s.schedule_in(foo, time= 1)

            assert len(s._scheduled_tasks) == 1
        asyncio.get_event_loop().run_until_complete(valid_time_test())

    def test_get_task_invalid_task_returns_none(self):
        s = Scheduler()
        assert s.get_task(1) is None

    def test_get_task_schedule_in_returns_valid_task(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            t_id = s.schedule_in(foo, time= 1)

            assert s.get_task(t_id) is not None

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())

    def test_get_task_schedule_at_returns_valid_task(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            t_id = s.schedule_at(foo, time= datetime(year=2100, month= 1, day=1))

            assert s.get_task(t_id) is not None

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())

    def test_cancel_task_schedule_at_removes_task(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            t_id = s.schedule_at(foo, time= datetime(year=2100, month= 1, day=1))

            s.cancel(t_id)

            assert len(s._scheduled_tasks) == 0

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())

    def test_cancel_task_schedule_at_invalid_id_throws_key_error(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            t_id = s.schedule_at(foo, time= datetime(year=2100, month= 1, day=1))

            with pytest.raises(KeyError):
                s.cancel(1)

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())
    
    def test_cancel_task_schedule_in_removes_task(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            t_id = s.schedule_in(foo, time= 1)

            s.cancel(t_id)

            assert len(s._scheduled_tasks) == 0

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())

    def test_cancel_task_schedule_in_invalid_id_throws_key_error(self):
        async def foo():
            pass

        async def get_task_valid_task():
            s = Scheduler()
            s.schedule_in(foo, time= 1)

            with pytest.raises(KeyError):
                s.cancel(1)

        asyncio.get_event_loop().run_until_complete(get_task_valid_task())

