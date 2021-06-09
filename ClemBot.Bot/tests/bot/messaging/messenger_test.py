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
    