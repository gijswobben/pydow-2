import os
import uuid

import xml.etree.ElementTree as ET

from urllib.parse import parse_qs

from jinja2 import Template
from typing import TypeVar
from typing import Union
from typing import Optional

from xml.etree.ElementTree import ParseError


VirtualDOM_type = TypeVar("VirtualDOM")
Component_type = TypeVar("Component")
Router_type = TypeVar("Router")


class Component(object):
    """ Base component that can be used to create custom components.
    """

    def __init__(
        self: object,
        parent: Union[VirtualDOM_type, Component_type] = None,
        tag: Optional[str] = None,
        identifier: Optional[str] = None,
        attributes: Optional[dict] = None,
        router: Optional[Router_type] = None,
        template_location: str = "./templates",
        template_file: str = "./template.html",
        *args: list,
        **kwargs: dict
    ) -> None:
        """ Initialization of a component.
        """

        if attributes is None:
            attributes = {}

        # Store other attributes
        for key, value in kwargs.items():

            # Add attributes as object properties
            setattr(self, key, value)

            # Make string values also accessible as attributes
            if (
                isinstance(key, str)
                and isinstance(value, str)
                and key not in ["content"]
            ):
                attributes[key] = value

        # If no HTML tag is provided, use the class name
        if tag is None:
            tag = self.__class__.__name__

        # Create an identifier if none is provided in arguments and attributes
        if identifier is None and "identifier" not in attributes:
            identifier = str(uuid.uuid4())
        elif "identifier" in attributes:
            identifier = attributes.get("identifier")

        self.dispatcher = parent.dispatcher
        self.store = parent.store

        # Store the input parameters
        self.tag = tag
        self.identifier = identifier
        self.attributes = attributes
        self.router = router
        if hasattr(parent, "router"):
            self.router = parent.router
        self.template_location = template_location
        self.template_file = template_file
        self.context = parent.context

    def getURLSearchParameters(self: object, session_id: str) -> dict:
        """ Method that retrieves and parses URL search parameters.
        """

        # Get the current route from the router
        current_route = self.store.getState(f"ROUTER_CURRENT_ROUTE_{session_id}", {})
        search_parameters = current_route.get("search", None)

        # Return an empty dict if no parameters were found
        if search_parameters is None:
            return {}

        # Parse and return
        else:
            return(parse_qs(search_parameters.strip("?")))

    def render(self: object, *args: list, **kwargs: dict) -> str:
        """ Render the component into valid HTML
        """

        # Make sure everything is up-to-date before rendering
        self.update(*args, **kwargs)

        # Construct the absolute path to the template file
        filename = os.path.abspath(
            os.path.join(os.path.dirname(self.template_location), self.template_file)
        )

        # Open the template file and put the content into a Jinja template
        with open(filename) as file_:
            template_content = file_.read()
            template = Template(template_content)

        # Use the regular render method to render the component into HTML
        try:
            rendered = template.render(self.bindings, *args, **kwargs)
        except ParseError as e:
            print(e)
            print("Bindings:", self.bindings)
            print("Template:", template_content)
            raise

        # Parse the new HTML
        root = ET.fromstring(rendered)

        # Add the object identifier to the element
        root.set("identifier", self.identifier)

        # Get the current attributes of the element (from the template)
        attributes = root.attrib

        # Loop over the attributes and add the other attributes to the root component
        for key, value in self.attributes.items():

            # Make sure we're not overwriting existing attributes
            if key in attributes:
                root.set(key, value + " " + attributes.get(key))
            else:
                root.set(key, value)

        # Return the new HTML as string
        return ET.tostring(root).decode("utf-8")

    def update(self: object, *args: list, **kwargs: dict) -> None:
        """ Default update method does nothing. Components may
            over write this method.
        """
        pass

    def __call__(self: object, *args: list, **kwargs: dict):
        return self.render(*args, **kwargs)

    def __str__(self: object):
        return self.render()
