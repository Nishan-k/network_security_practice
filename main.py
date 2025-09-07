from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
from networksecurity.logging.logger import logging, log_separator






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





