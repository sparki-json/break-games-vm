from app import application
import multiprocessing
import gunicorn.app.base

class RunByGunicorn(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    options = {
            'bind': '%s:%s' % ('0.0.0.0', '8000'),
            'workers': 1,
    }
    RunByGunicorn(application, options).run()
        
