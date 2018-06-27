class BasePlugin(object):
    """ Class that can be used to build new plugins.
    """

    def __init__(self: object, app, vdom, *args: list, **kwargs: dict) -> None:
        """ Initialization of the plugin. Adds some attributes to the plugin (like
            the app context and vdom) and runs the registration method of the plugin.
        """

        # Add attributes to the plugin
        self.app = app
        self.vdom = vdom

        # Register the plugin
        self.registerPlugin()

    def registerPlugin(self: object) -> None:
        """ Default registration method for any plugin. Raises an exception if not
            over-written by the plugin itself.
        """

        raise NotImplementedError("This plugin has no registerPlugin method!")
