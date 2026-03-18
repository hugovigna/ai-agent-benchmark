"""Pipeline orchestrator: ties ingestion, transform, and export together."""

import logging
from typing import List, Optional
from datetime import datetime

from src.ingestion import IngestionPipeline
from src.transform import TransformChain, clean_dataframe, normalize_columns
from src.export import ReportGenerator, write_csv
from src.models import PipelineState
from config.settings import PIPELINE

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Main orchestrator that runs the full ETL pipeline."""

    def __init__(self, sources: List[str], output_dir: Optional[str] = None):
        self.sources = sources
        self.output_dir = output_dir or PIPELINE["output_dir"]
        self.state = PipelineState(
            pipeline_name="main_etl",
            total_steps=3
        )
        self._ingestion = IngestionPipeline(sources)
        self._transforms = TransformChain()
        self._reporter = ReportGenerator(self.output_dir)

    def configure_transforms(self, transforms: TransformChain):
        """Replace the default transform chain."""
        self._transforms = transforms

    def run(self) -> dict:
        """Execute the full pipeline: ingest -> transform -> export."""
        self.state.status = "running"
        self.state.started_at = datetime.now()

        # Step 1: Ingest
        logger.info("Step 1/3: Ingestion")
        raw_df = self._ingestion.run()
        self.state.advance("ingestion", {"rows": len(raw_df)})

        # Step 2: Transform
        logger.info("Step 2/3: Transform")
        self._transforms.add("clean", clean_dataframe)
        self._transforms.add("normalize", normalize_columns)
        transformed_df = self._transforms.execute(raw_df)
        self.state.advance("transform", {"rows": len(transformed_df)})

        # Step 3: Export
        logger.info("Step 3/3: Export")
        output_path = f"{self.output_dir}/output.csv"
        write_csv(transformed_df, output_path)
        summary = self._reporter.create_summary(transformed_df, "main_output")
        self._reporter.save_report(summary, "summary.json")
        self.state.advance("export", {"path": output_path})

        self.state.status = "completed"
        self.state.finished_at = datetime.now()

        return self.get_status()

    def get_status(self) -> dict:
        return {
            "pipeline": self.state.pipeline_name,
            "status": self.state.status,
            "step": f"{self.state.current_step}/{self.state.total_steps}",
            "results": self.state.step_results
        }


def run_pipeline(sources: List[str], output_dir: str = None) -> dict:
    """Convenience function to run the full pipeline."""
    orch = PipelineOrchestrator(sources, output_dir)
    return orch.run()
