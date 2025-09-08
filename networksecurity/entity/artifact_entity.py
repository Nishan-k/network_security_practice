from dataclasses import dataclass



# 1. Data Ingestion Artifacts:
@dataclass
class DataIngestionArtifact:
    trained_file_path: str
    test_file_path: str


# 2. Data Validation Artifacts:
@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

    

