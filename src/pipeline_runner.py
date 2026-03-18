import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class PipelineStep:
    def __init__(self, name, func, *args, **kwargs):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.duration = None
        self.status = "pending"

    def execute(self, input_data=None):
        start = time.time()
        self.status = "running"
        try:
            if input_data is not None:
                self.result = self.func(input_data, *self.args, **self.kwargs)
            else:
                self.result = self.func(*self.args, **self.kwargs)
            self.status = "success"
        except Exception as e:
            self.status = "failed"
            logger.error(f"Step '{self.name}' failed: {e}")
            raise
        finally:
            self.duration = round(time.time() - start, 3)
        return self.result


class Pipeline:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.results = {}
        self.start_time = None
        self.end_time = None

    def add_step(self, name, func, *args, **kwargs):
        step = PipelineStep(name, func, *args, **kwargs)
        self.steps.append(step)
        return self

    def run(self, initial_data=None):
        self.start_time = datetime.now()
        logger.info(f"Pipeline '{self.name}' started at {self.start_time}")
        current_data = initial_data
        for i, step in enumerate(self.steps):
            logger.info(f"  [{i+1}/{len(self.steps)}] Running '{step.name}'...")
            current_data = step.execute(current_data)
            self.results[step.name] = {
                "status": step.status,
                "duration": step.duration
            }
        self.end_time = datetime.now()
        total = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Pipeline '{self.name}' completed in {total:.1f}s")
        return current_data

    def get_report(self):
        return {
            "pipeline": self.name,
            "start": self.start_time.isoformat() if self.start_time else None,
            "end": self.end_time.isoformat() if self.end_time else None,
            "steps": self.results,
            "total_steps": len(self.steps),
            "passed": sum(1 for s in self.steps if s.status == "success"),
            "failed": sum(1 for s in self.steps if s.status == "failed")
        }

    def reset(self):
        for step in self.steps:
            step.result = None
            step.duration = None
            step.status = "pending"
        self.results = {}
        self.start_time = None
        self.end_time = None
