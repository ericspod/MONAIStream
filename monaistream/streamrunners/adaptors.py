from ignite.engine import Engine, Events
# from monai.engines.workflow import Workflow



class IgniteEngineAdaptor:

    def __init__(self, engine, data_loader):
        self.running = False
        self.engine = engine
        self.engine.add_event_handler(Events.ITERATION_COMPLETED, self._interrupt)
        self.data_loader = data_loader

    def _interrupt(self):
        self.engine.interrupt()

    def _stop(self):
        self.running = False

    def __call__(self, src):
        # provide data sample 'src' to workflow dataset
        self.data_loader.payload(src)
        self.engine.run(self.data_loader)
        return self.engine.state
