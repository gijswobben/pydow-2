from tinydb import TinyDB, Query


class Store(object):

    def __init__(self: object, *args: list, **kwargs: dict) -> None:
        self._db = TinyDB("database.json")

    def getState(self: object, key: str, default=None, session_id: str = None, identifier: str = None):
        """
        """
        pass

    def setState(self: object, key: str, value, session_id: str = None, identifier: str = None) -> None:
        """
        """

        if session_id is not None:
            key = f"{session_id}_{key}"

        if identifier is not None:
            key = f"{identifier}_{key}"

        self._db.insert({key: value})


if __name__ == '__main__':
    store = Store()
    print(store._db)
