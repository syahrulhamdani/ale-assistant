"""Base repository layer for BigQuery."""
from dataclasses import dataclass

from google.cloud import bigquery
from pandas import DataFrame

from ale.core.config import config as c


@dataclass
class BigQueryBase:
    """Base repostitory for BigQuery."""
    project_id: str
    dataset: str

    @property
    def client(self):
        """Property to lazily initialize and retrieve the BigQuery client.

        Returns:
            bigquery.Client: The BigQuery client instance.
        """
        if not hasattr(self, "_client"):
            setattr(self, "_client", bigquery.Client(
                project=self.project_id,
                location=c.BQ_LOCATION
            ))
        return getattr(self, "_client")

    def _query(
        self, query: str, query_params: list = None, dry_run: bool = False
    ) -> DataFrame:
        """Runs query with the given parameters.

        Args:
            query (str): query to run.
            query_params (List): list of query parameters.

        Returns:
            pd.DataFrame
        """
        if not query_params:
            query_params = []

        job_config = bigquery.QueryJobConfig(dry_run=dry_run)
        job_config.query_parameters = query_params
        query_job = self.client.query(query, job_config=job_config)
        return DataFrame([dict(row) for row in query_job])
