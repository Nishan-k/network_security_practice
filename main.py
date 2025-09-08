from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import (DataIngestionConfig, TrainingPipelineConfig,
                                                  DataValidationConfig)
from networksecurity.logging.logger import logging, log_separator

from networksecurity.components.data_validation import DataValidation





if __name__ == "__main__":
    training_pipeline_config = TrainingPipelineConfig()

    # Data Ingestion:
    data_ingestion_config = DataIngestionConfig(training_pipeline_config)
    data_ingestion = DataIngestion(data_ingestion_config)
    log_separator("Data Ingestion")
    logging.info("Initiate the Data Ingestion.")
    data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
    logging.info(f"Data Ingestion Artifacts: \n{data_ingestion_artifact}")
    logging.info("Data Ingestion Completed.")
    print(data_ingestion_artifact)


    # Data Validation:
    data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
    data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    log_separator("Data Validation")
    logging.info("Initiate Data Validation")
    data_validation_artifact = data_validation.initiate_data_validation()
    logging.info(f"Data Validation Artifacts: \n{data_validation_artifact}")
    logging.info("Data Validation Completed.")
    print(data_validation_artifact)







