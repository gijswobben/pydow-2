from pydow.core.component import Component
from pydow.signals import signal_navigation_event


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
        # self.dispatcher.addEventListener("NAVIGATION_EVENT", self.changeRoute)
        signal_navigation_event.connect(self.changeRoute)

    def getContent(self, session_id):
        current_route = self.store.getState("ROUTER_CURRENT_ROUTE", {"link_target": "/"}, session_id=session_id)
        return self.routes.get(current_route["link_target"])(session_id=session_id)

    def changeRoute(self: object, event: dict) -> None:
        """ Method that handles updates to the url.
        """

        session_id = event.get("session_id")

        link_target = event.get("link_target")
        link_search = event.get("link_search", "")
        link_anchor = event.get("link_anchor", "")

        route = {
            "link_target": link_target,
            "link_search": link_search,
            "link_anchor": link_anchor
        }

        self.store.setState(f"ROUTER_CURRENT_ROUTE", route, session_id=session_id)
