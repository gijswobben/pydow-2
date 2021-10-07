from pydow.core import Component

from blinker import signal


class Input(Component):
    """ Component that renders an input field on the page and adds onClick
        and onChange behaviour to the field.
    """

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        """ Initialization of the input field
        """

        # Initialize like any other component and point to the template location (this folder)
        super(Input, self).__init__(template_location=__file__, *args, **kwargs)

        # Specific signals for this button
        self.signal_on_click = signal(f"ON_CLICK_{self.identifier}")
        self.signal_on_change = signal(f"ON_CHANGE_{self.identifier}")

        # Add things that can be rendered
        self.bindings = {"value": self.store.getState(f"INPUT_{self.identifier}", "")}

        # Create the onClick behaviour
        if hasattr(self, "onClick"):
            on_click_method = self.onClick
            if on_click_method is not None:
                self.signal_on_click.connect(on_click_method, weak=False)

        # Store the content of the field
        self.signal_on_change.connect(self.onChange, weak=False)

    def onChange(self: object, event: dict) -> None:
        """ Default onChange method. Stores the current state of the input
            field (the value) to the store.
        """
        session_id = event.get("session_id")
        self.setValue(session_id=session_id, new_value=event.get("value", ""))

    def setValue(self: object, session_id: str, new_value: str) -> None:
        """ Helper method that sets the state for this component in the store.
        """
        self.store.setState(
            f"INPUT_{self.identifier}", new_value, session_id=session_id
        )

    def getValue(self: object, session_id: str, default=""):
        """ Helper method that gets the state from the store.
        """
        return self.store.getState(
            f"INPUT_{self.identifier}", default, session_id=session_id
        )

    def update(self: object, session_id: str, *args, **kwargs) -> None:
        """ Method that is called at each render. Updates the current value
            property with the state.
        """
        self.bindings["value"] = self.store.getState(
            f"INPUT_{self.identifier}", "", session_id=session_id
        )
