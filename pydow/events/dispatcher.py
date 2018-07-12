from typing import Callable


class EventDispatcher(object):
    """ Generic event dispatcher which listen and dispatch events
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialize the event dispatcher.
        """

        super(EventDispatcher, self).__init__(*args, **kwargs)

        # Create an empty set of events
        self._events = dict()

    def __del__(self: object) -> None:
        """ Remove all listener references at destruction time.
        """

        # Reset the events
        self._events = None

    def hasEventListener(self: object, event_type: str, listener: Callable) -> bool:
        """ Return true if listener is register to event_type.
        """

        # Check for event type and for the listener
        if event_type in self._events.keys():
            return listener in self._events[event_type]
        else:
            return False

    def dispatchEvent(self: object, event: dict):
        """ Dispatch an instance of Event class.
        """

        print(f"DEBUG: Dispatching event: {event}")

        # Make sure the required fields are present
        if "type" not in event:
            raise Exception(f"Unknown event type for event: {event}")

        # Extract the event type
        event_type = event.get("type")

        if event_type not in self._events.keys():
            event_type = "DEFAULT"

        # Dispatch the event to all the associated listeners
        if event_type in self._events.keys():
            listeners = self._events[event_type]

            for listener in listeners:
                listener(event)

    def addEventListener(self: object, event_type: str, listener: Callable, ensure_single: bool = False) -> None:
        """ Add an event listener for an event type.
        """

        # Add listener to the event type
        if not self.hasEventListener(event_type, listener):

            # Make sure there is only a single listener for this event type
            if ensure_single:
                if event_type in self._events.keys():
                    return False

            # Get the current listeners
            listeners = self._events.get(event_type, [])

            # Append the new listener
            listeners.append(listener)

            # Set the listeners to for the event type
            self._events[event_type] = listeners

    def removeEventListener(self: object, event_type: str, listener: Callable) -> None:
        """ Remove event listener.
        """

        # Remove the listener from the event type
        if self.hasEventListener(event_type, listener):
            listeners = self._events[event_type]

            # Only this listener remains so remove the key
            if len(listeners) == 1:
                del self._events[event_type]

            # Update listeners chain
            else:
                listeners.remove(listener)
                self._events[event_type] = listeners
