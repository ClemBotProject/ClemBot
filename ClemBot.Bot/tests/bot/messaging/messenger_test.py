import asyncio

import pytest
from unittest import mock

from bot.messaging.messenger import Messenger

class TestMessenger:

    @pytest.mark.asyncio
    async def test_adds_event_on_subscribe(self):
        async def foo():
            pass
        messenger = Messenger()
        messenger.subscribe('bar', foo)
        assert 'bar' in messenger._events.keys()

    @pytest.mark.asyncio
    async def test_subscribe_with_none_raises_typeerror(self):
        messenger = Messenger()
        with pytest.raises(TypeError):
            messenger.subscribe('bar', None)

    @pytest.mark.asyncio
    async def test_subscribe_with_sync_method_raises_typeerror(self):
        def foo():
            pass
        messenger = Messenger()
        with pytest.raises(TypeError):
            messenger.subscribe('bar', foo)
        
    @pytest.mark.asyncio
    async def test_adds_two_listeners(self):
        async def foo():
            pass

        async def bar():
            pass

        messenger = Messenger()
        messenger.subscribe('baz', foo)
        messenger.subscribe('baz', bar)

        assert len(messenger._events['baz']) == 2

    @pytest.mark.asyncio
    async def test_adds_three_listeners(self):
        async def foo():
            pass

        async def bar():
            pass

        async def ham():
            pass

        messenger = Messenger()
        messenger.subscribe('baz', foo)
        messenger.subscribe('baz', bar)
        messenger.subscribe('baz', ham)

        assert len(messenger._events['baz']) == 3

    @pytest.mark.asyncio
    async def test_publish_non_existent_event_does_nothing(self):
        await Messenger().publish('foo')
        assert True

    @pytest.mark.asyncio
    async def test_publish_event_invokes_listener(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.mock = mock.Mock()

            async def async_mock(self, *args, **kwargs):
                self.mock(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_mock)
        await messenger.publish('bar')

        foo.mock.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_publish_event_invokes_two_listeners(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('bar', foo.async_2)
        await messenger.publish('bar')

        foo.async_mock1.assert_called_once_with()
        foo.async_mock2.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_publish_event_invokes_listener_twice(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        await messenger.publish('bar')
        await messenger.publish('bar')

        assert foo.async_mock1.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_different_event_invokes_same_listener_twice(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_1)
        await messenger.publish('bar')
        await messenger.publish('baz')

        assert foo.async_mock1.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_dead_ref(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        del foo
        await messenger.publish('bar')

        assert len(messenger._events['bar']) == 0

    @pytest.mark.asyncio
    async def test_publish_queue_event_creates_one_queue_one_publish(self):
        messenger = Messenger()

        await messenger.publish_to_queue('bar', 1)

        assert len(messenger._guild_event_queue) == 1

        await messenger.close()

    @pytest.mark.asyncio
    async def test_publish_queue_event_creates_two_queue_two_publish(self):
        messenger = Messenger()

        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('bar', 2)

        assert len(messenger._guild_event_queue) == 2

        await messenger.close()

    @pytest.mark.asyncio
    async def test_publish_queue_event_creates_one_queue_one_publish(self):
        messenger = Messenger()

        await messenger.publish_to_queue('bar', 1)

        assert len(messenger._guild_event_queue) == 1

        await messenger.close()

    @pytest.mark.asyncio
    async def test_publish_queue_event_creates_one_queue_two_publish(self):
        messenger = Messenger()

        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        assert len(messenger._guild_event_queue) == 1

        await messenger.close()

    @pytest.mark.asyncio
    async def test_publish_queue_event_creates_three_queue_three_publish(self):
        messenger = Messenger()

        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('bar', 2)
        await messenger.publish_to_queue('bar', 3)

        assert len(messenger._guild_event_queue) == 3

        await messenger.close()

    @pytest.mark.asyncio
    async def test_publish_queue_event_invokes_listener_once(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.mock = mock.Mock()

            async def async_mock(self, *args, **kwargs):
                self.mock(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_mock)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        foo.mock.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_publish_queue_event_invokes_same_listener_twice(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.mock = mock.Mock()

            async def async_mock(self, *args, **kwargs):
                self.mock(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_mock)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert foo.mock.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_event_queue_one_event_invokes_two_listeners(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('bar', foo.async_2)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        foo.async_mock1.assert_called_once_with()
        foo.async_mock2.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_publish_event_queue_two_event_invokes_one_listeners(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        await messenger.close()

        foo.async_mock1.assert_called_once_with()
        foo.async_mock2.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_two_listeners_in_order(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state.append(1)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                self.call_state.append(2)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        await messenger.close()

        assert foo.call_state == [1, 2]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_two_guild_invokes_two_listeners_in_order(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = {
                    1: [],
                    2: []
                }

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state[args[0]].append(1)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                self.call_state[args[0]].append(2)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1, 1)
        await messenger.publish_to_queue('baz', 1, 1)

        await messenger.publish_to_queue('baz', 2, 2)
        await messenger.publish_to_queue('bar', 2, 2)

        await messenger.close()

        assert foo.call_state[1] == [1, 2]
        assert foo.call_state[2] == [2, 1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_two_event_one_guild_invokes_four_listeners_in_order(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state.append(1)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                self.call_state.append(2)

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)
        await messenger.publish_to_queue('baz', 1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert foo.call_state == [1, 2, 2, 1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_two_event_one_guild_invokes_two_listeners_in_order_doesnt_fail_on_exception(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state.append(1)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        await messenger.close()

        assert foo.call_state == [1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_two_listeners_in_order_doesnt_fail_on_exception(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert foo.call_state == []

    @pytest.mark.asyncio
    async def test_publish_event_queue_two_event_one_guild_invokes_two_listeners_in_order_invokes_error_callback_on_error(self):
        messenger = Messenger()

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state.append(1)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        await messenger.close()

        assert foo.call_state == [1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_one_listeners_in_order_invokes_error_callback_on_error(self):
        messenger = Messenger()
        error_call_state = []

        async def error_callback(e, *, traceback: str):
            error_call_state.append(1)

        messenger.error_callback = error_callback


        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert error_call_state == [1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_two_listeners_in_order_invokes_twice_error_callback_on_error(self):
        messenger = Messenger()
        error_call_state = []

        async def error_callback(e, *, traceback: str):
            error_call_state.append(1)

        messenger.error_callback = error_callback

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                raise Exception()

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert error_call_state == [1, 1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_two_listeners_in_order_invokes_twice_error_callback_on_error_twice(self):
        messenger = Messenger()
        error_call_state = []

        async def error_callback(e, *, traceback: str):
            error_call_state.append(1)

        messenger.error_callback = error_callback

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                raise Exception()

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)

        await messenger.close()

        assert error_call_state == [1, 1]

    @pytest.mark.asyncio
    async def test_publish_event_queue_event_one_guild_invokes_two_listeners_in_order_invokes_once_error_callback_on_error(self):
        messenger = Messenger()
        error_call_state = []

        async def error_callback(e, *, traceback: str):
            error_call_state.append(1)

        messenger.error_callback = error_callback

        class Foo:
            def __init__(self):
                self.async_mock1 = mock.Mock()
                self.async_mock2 = mock.Mock()

                self.call_state = []

            async def async_1(self, *args, **kwargs):
                self.async_mock1(*args, **kwargs)
                self.call_state.append(2)

            async def async_2(self, *args, **kwargs):
                self.async_mock2(*args, **kwargs)
                raise Exception()

        foo = Foo()
        messenger.subscribe('bar', foo.async_1)
        messenger.subscribe('baz', foo.async_2)
        await messenger.publish_to_queue('bar', 1)
        await messenger.publish_to_queue('baz', 1)
        await messenger.publish_to_queue('bar', 1)

        await messenger.close()

        assert error_call_state == [1] and foo.call_state == [2, 2]
