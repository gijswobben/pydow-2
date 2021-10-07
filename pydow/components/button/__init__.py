from pydow.core import Component

from blinker import signal


class Button(Component):
    """ Component that renders a button on the page and adds onClick behaviour
        to the button.
    """

    def __init__(self: object, *args, **kwargs) -> None:
        """ Initialization of the button
        """

        # Initialize like any other component and point to the template location (this folder)
        super(Button, self).__init__(template_location=__file__, *args, **kwargs)

        # Specific signals for this button
        self.signal_on_click = signal(f"ON_CLICK_{self.identifier}")

        # Add things that can be rendered
        self.bindings = {
            "content": self.content if hasattr(self, "content") else "Button"
        }

        # Create the onClick behaviour
        if hasattr(self, "onClick"):
            on_click_method = self.onClick
            if on_click_method is not None:
                self.signal_on_click.connect(on_click_method)
