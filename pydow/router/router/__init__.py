from pydow.core.component import Component


class Router(Component):
    """ The Router component is responsible for listening to navigation change
        events and responds by changing the component it displays to match a
        set of routing rules.
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialization of the router.
        """

        # Initialize the component
        super(Router, self).__init__(template_location=__file__, *args, **kwargs)

        self.bindings = {
            "getContent": self.getContent
        }

        # Register for all navigation events
        self.dispatcher.addEventListener("NAVIGATION_EVENT", self.changeRoute)

    def getContent(self, session_id):
        current_route = self.store.getState(f"ROUTER_CURRENT_ROUTE_{session_id}", "/")
        return self.routes.get(current_route["target"])(session_id=session_id)

    def changeRoute(self: object, event: dict) -> None:
        """ Method that handles updates to the url.
        """

        session_id = event.get("session_id")

        target = event.get("target")
        search = event.get("search")
        anchor = event.get("anchor")

        route = {
            "target": target,
            "search": search,
            "anchor": anchor
        }

        self.store.setState(f"ROUTER_CURRENT_ROUTE_{session_id}", route)
