import weakref as wr
from inspect import ismethod
from typing import Callable, Union

"""This is the global message bus that handles all application level events"""

events = {}

WeakObjOrMethod = Union[wr.WeakMethod, wr.ref]

DeadRefObserver = Callable[[WeakObjOrMethod], None]

async def publish(event: str, *args) -> None:
    """publishes an event onto the global message queue with accompanying arguements"""
    if event in events.keys():
        for sub in events[event]:
            await sub()(*args)

def subscribe(event: str, callback: callable) -> None:
    """Subscribes a method as a callback listener to a given event """
    weak_ref = getWeakRef(callback)
    if event in events.keys():
        events[event].append(weak_ref)
    else:
        events[event] = [weak_ref]


def getWeakRef(obj, notifyDead: DeadRefObserver = None):
    """
    Get a weak reference to obj. If obj is a bound method, a WeakMethod
    object, that behaves like a WeakRef, is returned; if it is
    anything else a WeakRef is returned.
    """
    if ismethod(obj):
        createRef = wr.WeakMethod
    else:
        createRef = wr.ref
    return createRef(obj)
