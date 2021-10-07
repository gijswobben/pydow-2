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

    def getState(self: object, key: str, default=None, session_id: str = None, identifier: str = None):
        """ Helper method the retrieve a state.
        """

        # If a session key is provided, use it to postfix the key
        if session_id is not None:
            key = f"{key}_{session_id}"

        if identifier is not None:
            key = f"{key}_{identifier}"

        # Return the value
        return self._data.get(key, default)

    def setState(self: object, key: str, value, session_id: str = None, identifier: str = None):
        """ Helper method to store a state.
        """

        # If a session key is provided, use it to postfix the key
        if session_id is not None:
            key = f"{key}_{session_id}"

        if identifier is not None:
            key = f"{key}_{identifier}"

        # Set the value in the state
        self._data[key] = value
