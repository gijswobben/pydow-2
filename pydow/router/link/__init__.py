from pydow.core.component import Component


class Link(Component):
    """ A link is a special object that (when clicked) sends a notification
        to the Router component to change its content.
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialization of the link component.
        """

        # Initialize the component
        super(Link, self).__init__(template_location=__file__, *args, **kwargs)

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
        self.dispatcher.addEventListener(f"ON_CLICK_{self.identifier}", self.onClick)

    def onClick(self: object, event: dict) -> None:
        """ Default onClick handler.
        """

        self.dispatcher.dispatchEvent(
            {"type": "NAVIGATION_EVENT", "target": self.target, "search": self.search, "session_id": event.get("session_id")}
        )
