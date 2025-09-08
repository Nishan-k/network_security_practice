import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp, chi2_contingency
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file, read_data


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # -------------------------
    # Schema & basic checks
    # -------------------------
    def validate_columns_and_types(self, df: pd.DataFrame) -> (bool, list):
        errors = []
        # Column names
        expected_columns = list(self._schema_config["columns"].keys())
        if list(df.columns) != expected_columns:
            errors.append(f"Columns mismatch. Expected {expected_columns}, found {list(df.columns)}")

        # Data types
        for col, dtype in self._schema_config["columns"].items():
            if col in df.columns:
                if not np.issubdtype(df[col].dtype, np.dtype(dtype).type):
                    errors.append(f"Column '{col}' expected type {dtype}, found {df[col].dtype}")
        return len(errors) == 0, errors

    def validate_missing_values(self, df: pd.DataFrame, threshold: float = 0.05) -> (bool, list):
        errors = []
        for col in df.columns:
            missing_pct = df[col].isna().mean()
            if missing_pct > threshold:
                errors.append(f"Column '{col}' has {missing_pct*100:.2f}% missing values > allowed {threshold*100}%")
        return len(errors) == 0, errors

    def validate_numeric_ranges(self, df: pd.DataFrame) -> (bool, list):
        errors = []
        for col, limits in self._schema_config.get("numeric_limits", {}).items():
            if col in df.columns:
                if df[col].min() < limits[0] or df[col].max() > limits[1]:
                    errors.append(f"Column '{col}' out of range {limits}")
        return len(errors) == 0, errors

    def validate_categorical_values(self, df: pd.DataFrame) -> (bool, list):
        errors = []
        for col, allowed in self._schema_config.get("categorical_values", {}).items():
            if col in df.columns:
                invalid_vals = set(df[col].dropna()) - set(allowed)
                if invalid_vals:
                    errors.append(f"Column '{col}' has invalid values: {invalid_vals}")
        return len(errors) == 0, errors

    def validate_duplicates(self, df: pd.DataFrame) -> (bool, list):
        if df.duplicated().any():
            return False, ["Data has duplicate rows"]
        return True, []

    # -------------------------
    # Data Drift
    # -------------------------
    def detect_data_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        drift_report = {}

        # We assume data is valid and no drift exists until proven otherwise:
        status = True
        for col in base_df.columns:
            if pd.api.types.is_numeric_dtype(base_df[col]):
                pvalue = ks_2samp(base_df[col].dropna(), current_df[col].dropna()).pvalue
            else:
                # categorical drift with chi-square
                base_counts = base_df[col].value_counts()
                current_counts = current_df[col].value_counts()
                all_idx = base_counts.index.union(current_counts.index)
                base_freq = base_counts.reindex(all_idx, fill_value=0)
                current_freq = current_counts.reindex(all_idx, fill_value=0)
                pvalue = chi2_contingency([base_freq, current_freq])[1]
            drift_report[col] = {
                "p_value": float(pvalue),
                "drift_status": pvalue < threshold
            }
            #If p-value is small (reject H₀), it means drift is detected for that column → we mark status = False:
            if pvalue < threshold:
                status = False
        # Save drift report
        os.makedirs(os.path.dirname(self.data_validation_config.drift_report_file_path), exist_ok=True)
        write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=drift_report)
        return status

    # -------------------------
    # Full validation for a dataset
    # -------------------------
    def validate_dataframe(self, df: pd.DataFrame, data_name: str) -> (bool, list):
        is_valid, errors = self.validate_columns_and_types(df)
        if not is_valid: 
            errors = [f"[{data_name}] {err}" for err in errors]
            return False, errors

        for check in [self.validate_missing_values,
                      self.validate_numeric_ranges,
                      self.validate_categorical_values,
                      self.validate_duplicates]:
            valid, errs = check(df)
            if not valid:
                errors.extend([f"[{data_name}] {err}" for err in errors])
        return len(errors) == 0, errors

    # -------------------------
    # Main initiation
    # -------------------------
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_df = read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = read_data(self.data_ingestion_artifact.test_file_path)

            # Validate datasets
            train_valid, train_errors = self.validate_dataframe(train_df, "training_data")
            test_valid, test_errors = self.validate_dataframe(test_df, "testing_data")

            # Save valid or invalid datasets
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.data_validation_config.invalid_train_file_path), exist_ok=True)

            if train_valid:
                gold_train_path = self.data_validation_config.valid_train_file_path
                train_df.to_csv(gold_train_path, index=False)
            else:
                gold_train_path = None
                train_df.to_csv(self.data_validation_config.invalid_train_file_path, index=False)
                logging.warning(f"Training data invalid: {train_errors}")

            if test_valid:
                gold_test_path = self.data_validation_config.valid_test_file_path
                test_df.to_csv(gold_test_path, index=False)
            else:
                gold_test_path = None
                test_df.to_csv(self.data_validation_config.invalid_test_file_path, index=False)
                logging.warning(f"Test data invalid: {test_errors}")

            # Run data drift only if both train & test are valid
            drift_status = False
            if train_valid and test_valid:
                drift_status = self.detect_data_drift(base_df=train_df, current_df=test_df)

            return DataValidationArtifact(
                validation_status=train_valid and test_valid,
                valid_train_file_path=gold_train_path,
                valid_test_file_path=gold_test_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)
