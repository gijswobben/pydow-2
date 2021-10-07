class BaseMiddleWare(object):

    def __init__(self, app, vdom, config, *args, **kwargs):

        self.app = app
        self.vdom = vdom
        self.config = config
        self.store = vdom.store
        self.dispatcher = vdom.dispatcher

    def run(self, *args, **kwargs):
        pass
