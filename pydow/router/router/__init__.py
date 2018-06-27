from pydow.core.component import Component


class Router(Component):
    """ The Router component is responsible for listening to navigation change
        events and responds by changing the component it displays to match a
        set of routing rules.
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialization of the router.
        """

        # Provide a default route
        self.current_route = "/"

        # Initialize the component
        super(Router, self).__init__(template_location=__file__, *args, **kwargs)

        self.components = {"content": self.routes.get(self.current_route, "/")}

        # Register for all navigation events
        self.dispatcher.addEventListener("NAVIGATION_EVENT", self.changeRoute)

    def changeRoute(self: object, event: dict) -> None:
        """ Method that handles updates to the url.
        """

        # Get the current location from the navigation event
        self.current_route = event.get("target", "/")

        # Set the content to the new route
        self.components["content"] = self.routes.get(self.current_route, "/")

    def update(self: object, *args: list, **kwargs: dict) -> None:
        self.components["content"] = self.routes.get(self.current_route, "/")
