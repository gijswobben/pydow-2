import xml.etree.ElementTree as ET

from pydow.store.filestore import Store
from pydow.router.router import Router
from pydow.events.dispatcher import EventDispatcher
from pydow.core.helpers import h

from typing import TypeVar
from typing import Generic
from typing import Callable


Component_type = TypeVar("Component")


class VirtualDOM(object):
    """ Class that handles the generation and manipulation of the virtual DOM.
    """

    def __init__(
        self: object, root_class: Generic[Component_type], routes: dict
    ) -> None:
        """ Initialization of the virtual DOM
        """

        # Store the input parameters
        self.dispatcher = EventDispatcher()
        self.store = Store()

        # Create the router
        self.router = Router(
            parent=self,
            routes={key: value(parent=self) for key, value in routes.items()},
        )

        # Create the root object
        self.root_class = root_class(parent=self, router=self.router)

        # Use the refresh method to build the HTML and actual VDOM
        # self.refresh()

    def toDict(self: object, session_id: str) -> dict:
        """ Helper method that returns the full virtual DOM as a dict.
        """

        # Refresh the VDOM
        self.refresh(session_id=session_id)

        # The VDOM is a dict, so return it
        return self.vdom

    def refresh(self: object, session_id: str) -> None:
        """ Refresh the virtual DOM.
        """

        self.vdom = self._createVDOM(session_id=session_id)

    def _createVDOM(self: object, session_id: str) -> dict:
        """ Parse the HTML into a VDOM.
        """

        def _createVDOMElement(element) -> Callable:

            # Extract information from the elements
            element_type = element.tag
            element_props = element.attrib

            # Check for nested elements
            if len(element) > 0:
                element_children = [
                    _createVDOMElement(element=child)
                    for child in element
                    if child is not None
                ]
            else:
                if element.text is not None:
                    element_children = [element.text]
                else:
                    element_children = []

            # Return the virtual DOM element
            return h(element_type, element_props, *element_children)

        # Start by converting the root object into HTML
        html = self.root_class.render(session_id=session_id)

        # Parse the HTML to an element tree
        root = ET.fromstring(html)

        # Use the helper method to run through the tree and create virtual DOM elements
        return _createVDOMElement(root)
