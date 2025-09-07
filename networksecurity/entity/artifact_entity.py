from dataclasses import dataclass



# 1. Data Ingestion Artifacts:
@dataclass
class DataIngestionArtifact:
    trained_file_path: str
    test_file_path: str