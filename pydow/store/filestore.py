class Store(dict):
    """ Default store class that handles the state in memory.
    """

    def __init__(self: object, *args, **kwargs) -> None:
        """ Simple store that takes care of the state of the application.
        """

        # Initialize the object as usual
        super(Store, self).__init__(*args, **kwargs)

        # Create the object that will hold the state (in memory) for the entire application
        self._data = {}

    def getState(self: object, key: str, default=None):
        """ Helper method the retrieve a state.
        """
        return self._data.get(key, default)

    def setState(self: object, key: str, value):
        """ Helper method to store a state.
        """
        self._data[key] = value
