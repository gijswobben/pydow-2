from pydow.core import Component


class Select(Component):
    """ Component that renders an input field on the page and adds onClick
        and onChange behaviour to the field.
    """

    def __init__(self: object, template_location=__file__, *args: list, **kwargs: dict) -> None:
        """ Initialization of the input field
        """

        # Initialize like any other component and point to the template location (this folder)
        super(Select, self).__init__(template_location=template_location, *args, **kwargs)

        default_value = ""
        if hasattr(self, "default"):
            default_value = self.default

        label_value = None
        if hasattr(self, "label"):
            print(self.label)
            label_value = self.label

        if not hasattr(self, "getOptions"):
            raise Exception("Unable to get options for dropdown.")

        # Add things that can be rendered
        self.bindings = {
            "value": self.store.getState(f"INPUT_{self.identifier}", default_value),
            "getOptions": self.getOptions,
            "default": default_value,
            "label": label_value,
            "identifier": self.identifier
        }

        # Create the onClick behaviour
        if hasattr(self, "onClick"):
            on_click_method = self.onClick
            if on_click_method is not None:
                self.dispatcher.addEventListener(f"ON_CLICK_{self.identifier}", on_click_method)

        # Store the content of the field
        self.dispatcher.addEventListener(f"ON_CHANGE_{self.identifier}", self.onChange)

    def onChange(self: object, event: dict) -> None:
        """ Default onChange method. Stores the current state of the input
            field (the value) to the store.
        """
        session_id = event.get("session_id")
        self.setValue(session_id=session_id, new_value=event.get("value", ""))

    def setValue(self: object, session_id: str, new_value: str) -> None:
        """ Helper method that sets the state for this component in the store.
        """
        self.store.setState(f"INPUT_{self.identifier}_{session_id}", new_value)

    def getValue(self: object, session_id: str, default=""):
        """ Helper method that gets the state from the store.
        """
        return self.store.getState(f"INPUT_{self.identifier}_{session_id}", default)

    def update(self: object, session_id: str, *args, **kwargs) -> None:
        """ Method that is called at each render. Updates the current value
            property with the state.
        """
        self.bindings["value"] = self.store.getState(f"INPUT_{self.identifier}_{session_id}", "")
