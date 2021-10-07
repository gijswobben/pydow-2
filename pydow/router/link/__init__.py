from pydow.core.component import Component
from pydow.signals import signal_navigation_event

from blinker import signal


class Link(Component):
    """ A link is a special object that (when clicked) sends a notification
        to the Router component to change its content.
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialization of the link component.
        """

        # Initialize the component
        super(Link, self).__init__(template_location=__file__, tag="pydow_link", *args, **kwargs)

        # Specify specific signals
        self.signal_on_click = signal(f"ON_CLICK_{self.identifier}")

        # Create elements that can be rendered by the template
        self.bindings = {"content": self.content if hasattr(self, "content") else ""}

        # Make sure that required arguments are set
        if not hasattr(self, "target"):
            raise Exception("Link elements need a target!")

        # Split the target and the query parameters
        parts = self.target.split("?")
        if len(parts) == 1:
            self.target = parts[0]
            self.search = ""
        if len(parts) == 2:
            self.target = parts[0]
            self.search = parts[1]

        # Create the onClick behaviour
        # self.dispatcher.addEventListener(f"ON_CLICK_{self.identifier}", self.onClick)
        self.signal_on_click.connect(self.onClick, weak=False)

    def onClick(self: object, event: dict) -> None:
        """ Default onClick handler.
        """

        signal_navigation_event.send({"link_target": self.target, "link_search": self.search, "session_id": event.get("session_id")})
