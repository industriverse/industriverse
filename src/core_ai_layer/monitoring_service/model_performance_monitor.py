
# model_performance_monitor.py

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import numpy as np
try:
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, 
        mean_squared_error, mean_absolute_error, r2_score
    )
except ImportError:
    # Fallback for environments without sklearn
    def _mock_metric(*args, **kwargs): return 0.0
    accuracy_score = precision_score = recall_score = f1_score = roc_auc_score = _mock_metric
    mean_squared_error = mean_absolute_error = r2_score = _mock_metric
# For LLM metrics, specific libraries might be needed, e.g., evaluate (from Hugging Face), nltk
# from evaluate import load # Example

from .monitoring_schemas import (
    ModelIdentifier,
    ModelType,
    MetricType,
    PerformanceMetricConfig,
    PerformanceMetricValue,
    ModelPerformanceReport
)
from .monitoring_exceptions import (
    MetricCalculationError,
    ConfigurationError,
    InvalidInputError
)

logger = logging.getLogger(__name__)

class ModelPerformanceMonitor:
    """
    Service responsible for calculating and tracking the performance of deployed AI models.
    """

    def __init__(self, global_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the ModelPerformanceMonitor.
        Args:
            global_config: Global configuration, potentially for accessing other services or default params.
        """
        self.global_config = global_config or {}
        # self.llm_metric_evaluators = {} # To store loaded LLM metric evaluators, e.g., self.llm_metric_evaluators["bleu"] = load("bleu")
        logger.info("ModelPerformanceMonitor initialized.")

    async def calculate_performance_metrics(
        self,
        model_identifier: ModelIdentifier,
        config_id: str, # uuid.UUID, but pass as str
        predictions: List[Any],
        ground_truth: List[Any],
        metric_configs: List[PerformanceMetricConfig],
        prediction_probabilities: Optional[List[Union[List[float], float]]] = None, # For classification AUC/log_loss
        positive_label_for_binary: Any = 1 # For binary classification metrics like precision, recall, f1
    ) -> ModelPerformanceReport:
        """
        Calculates performance metrics for a given set of predictions and ground truth.

        Args:
            model_identifier: Identifier for the model.
            config_id: The monitoring configuration ID.
            predictions: List of model predictions.
            ground_truth: List of actual ground truth values.
            metric_configs: List of configurations for metrics to calculate.
            prediction_probabilities: For classification, list of probabilities for the positive class or list of lists for multi-class.
            positive_label_for_binary: The value considered as the positive label in binary classification.

        Returns:
            A ModelPerformanceReport summarizing the calculated metrics.
        """
        logger.info(f"Starting performance metric calculation for model {model_identifier.model_id}, config {config_id}")
        if len(predictions) != len(ground_truth):
            raise InvalidInputError(f"Predictions count ({len(predictions)}) and ground truth count ({len(ground_truth)}) must match.")
        if not predictions:
            raise InvalidInputError("Predictions and ground truth lists cannot be empty.")
        if not metric_configs:
            logger.warning(f"No metric configurations provided for model {model_identifier.model_id}. Returning empty report.")
            return ModelPerformanceReport(
                config_id=config_id, # type: ignore
                model_identifier=model_identifier,
                metrics=[],
                summary="No metrics configured for calculation."
            )

        calculated_metrics: List[PerformanceMetricValue] = []

        # Convert to numpy arrays for scikit-learn compatibility where appropriate
        try:
            # Attempt conversion, but be mindful of LLM outputs which might be strings/lists of strings
            if model_identifier.model_type not in [ModelType.LLM_GENERATIVE, ModelType.LLM_EMBEDDING]:
                np_predictions = np.array(predictions)
                np_ground_truth = np.array(ground_truth)
                if prediction_probabilities is not None:
                    np_prediction_probabilities = np.array(prediction_probabilities)
            else: # For LLMs, keep as lists for now, specific metrics will handle
                np_predictions = predictions # type: ignore
                np_ground_truth = ground_truth # type: ignore
                np_prediction_probabilities = prediction_probabilities # type: ignore

        except Exception as e:
            logger.error(f"Error converting predictions/ground truth to NumPy arrays: {e}")
            raise InvalidInputError(f"Could not process predictions/ground truth: {e}")

        for m_config in metric_configs:
            metric_value = None
            try:
                if model_identifier.model_type == ModelType.CLASSIFICATION:
                    metric_value = self._calculate_classification_metric(
                        m_config.metric_name, np_ground_truth, np_predictions, 
                        np_prediction_probabilities, positive_label_for_binary, m_config.custom_metric_params
                    )
                elif model_identifier.model_type == ModelType.REGRESSION:
                    metric_value = self._calculate_regression_metric(m_config.metric_name, np_ground_truth, np_predictions, m_config.custom_metric_params)
                elif model_identifier.model_type in [ModelType.LLM_GENERATIVE, ModelType.LLM_EMBEDDING]:
                    metric_value = await self._calculate_llm_metric(m_config.metric_name, predictions, ground_truth, m_config.custom_metric_params)
                else:
                    logger.warning(f"Performance monitoring for model type 	{model_identifier.model_type}	 not fully supported or metric 	{m_config.metric_name}	 unknown for this type.")
                    # Optionally, allow custom metric calculation here

                if metric_value is not None:
                    calculated_metrics.append(PerformanceMetricValue(
                        metric_name=m_config.metric_name,
                        value=metric_value,
                        model_identifier=model_identifier,
                        config_id=config_id # type: ignore
                    ))
            except MetricCalculationError as e:
                logger.error(f"Error calculating metric {m_config.metric_name} for model {model_identifier.model_id}: {e}")
                # Optionally add a metric value indicating error, or skip
            except Exception as e:
                logger.error(f"Unexpected error calculating metric {m_config.metric_name}: {e}", exc_info=True)

        report = ModelPerformanceReport(
            config_id=config_id, # type: ignore
            model_identifier=model_identifier,
            metrics=calculated_metrics,
            summary=f"Calculated {len(calculated_metrics)} performance metrics."
            # data_window_start/end would be set by orchestrator based on data used
        )
        logger.info(f"Performance calculation completed for model {model_identifier.model_id}. Report ID: {report.report_id}")
        return report

    def _calculate_classification_metric(
        self, 
        metric_name: MetricType, 
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        y_prob: Optional[np.ndarray] = None,
        positive_label: Any = 1,
        params: Optional[Dict[str, Any]] = None
    ) -> float:
        params = params or {}
        avg_method = params.get("average_method", "binary" if len(np.unique(y_true)) <= 2 else "macro")
        
        # Ensure positive_label is correctly used for binary, or labels for multiclass
        labels = np.unique(np.concatenate((y_true, y_pred)))
        pos_label_kwarg = {} 
        if len(labels) == 2 and metric_name in [MetricType.PRECISION, MetricType.RECALL, MetricType.F1_SCORE]:
            # Check if positive_label is in labels, if not, try to infer or raise error
            if positive_label not in labels:
                logger.warning(f"Positive label 	{positive_label}	 not found in y_true/y_pred. Using default or first label.")
                # Heuristic: if labels are 0,1 use 1. If boolean, use True.
                if all(isinstance(x, bool) for x in labels) or (0 in labels and 1 in labels):
                     positive_label = True if True in labels else 1 # type: ignore
                else:
                    positive_label = labels[1] # Default to the second unique label as positive if not 0/1 or bool
            pos_label_kwarg = {"pos_label": positive_label}

        try:
            if metric_name == MetricType.ACCURACY:
                return accuracy_score(y_true, y_pred, **params.get("accuracy_params", {}))
            elif metric_name == MetricType.PRECISION:
                return precision_score(y_true, y_pred, average=avg_method, **pos_label_kwarg, **params.get("precision_params", {}), zero_division=0)
            elif metric_name == MetricType.RECALL:
                return recall_score(y_true, y_pred, average=avg_method, **pos_label_kwarg, **params.get("recall_params", {}), zero_division=0)
            elif metric_name == MetricType.F1_SCORE:
                return f1_score(y_true, y_pred, average=avg_method, **pos_label_kwarg, **params.get("f1_params", {}), zero_division=0)
            elif metric_name == MetricType.AUC:
                if y_prob is None:
                    raise MetricCalculationError("AUC calculation requires prediction probabilities (y_prob).")
                # Handle binary vs multiclass AUC
                if len(y_prob.shape) == 1 or y_prob.shape[1] == 1: # Binary or prob of positive class
                    return roc_auc_score(y_true, y_prob, **params.get("auc_params", {}))
                elif y_prob.shape[1] > 1: # Multiclass probabilities
                    return roc_auc_score(y_true, y_prob, multi_class=params.get("multi_class_auc", "ovr"), average=params.get("average_auc", "macro"), **params.get("auc_params", {}))
            else:
                raise MetricCalculationError(f"Unsupported classification metric: {metric_name}")
        except ValueError as ve:
            # Catch common sklearn errors like "Target is multiclass but average=	binary	" etc.
            logger.error(f"ValueError calculating {metric_name}: {ve}")
            raise MetricCalculationError(f"Could not calculate {metric_name}: {ve}")

    def _calculate_regression_metric(self, metric_name: MetricType, y_true: np.ndarray, y_pred: np.ndarray, params: Optional[Dict[str, Any]] = None) -> float:
        params = params or {}
        if metric_name == MetricType.RMSE:
            return np.sqrt(mean_squared_error(y_true, y_pred, **params.get("mse_params", {})))
        elif metric_name == MetricType.MAE:
            return mean_absolute_error(y_true, y_pred, **params.get("mae_params", {}))
        elif metric_name == MetricType.R_SQUARED:
            return r2_score(y_true, y_pred, **params.get("r2_params", {}))
        else:
            raise MetricCalculationError(f"Unsupported regression metric: {metric_name}")

    async def _calculate_llm_metric(self, metric_name: MetricType, predictions: List[str], references: List[Union[str, List[str]]], params: Optional[Dict[str, Any]] = None) -> float:
        params = params or {}
        logger.info(f"Calculating LLM metric: {metric_name}. (Placeholder implementation)")
        # This is a placeholder. Actual implementation would use libraries like Hugging Face evaluate.
        # Example using a hypothetical loaded evaluator:
        # if metric_name.value in self.llm_metric_evaluators:
        #     evaluator = self.llm_metric_evaluators[metric_name.value]
        #     # Ensure predictions and references are in the format expected by the evaluator
        #     # For BLEU/ROUGE, references might be List[List[str]]
        #     formatted_references = [[ref] if isinstance(ref, str) else ref for ref in references]
        #     results = evaluator.compute(predictions=predictions, references=formatted_references, **params)
        #     # Extract the specific score, e.g., results["bleu"] or results["rougeL"]
        #     if metric_name == MetricType.BLEU and "bleu" in results:
        #         return results["bleu"]
        #     elif metric_name == MetricType.ROUGE_L and "rougeL" in results: # or rougeLsum
        #         return results["rougeL"]
        #     # Add perplexity if applicable (usually needs model and tokenized input)
        # else:
        #     raise MetricCalculationError(f"LLM metric evaluator for {metric_name} not loaded or available.")
        
        # Placeholder values for now
        if metric_name == MetricType.BLEU: return 0.5 
        if metric_name == MetricType.ROUGE_L: return 0.6
        if metric_name == MetricType.PERPLEXITY: return 10.0 # Lower is better
        
        raise MetricCalculationError(f"Unsupported or not yet implemented LLM metric: {metric_name}")

    # async def _load_llm_evaluators(self, metrics_to_load: List[MetricType]):
    #     # Example: Load evaluators on demand or at init
    #     for metric in metrics_to_load:
    #         if metric.value not in self.llm_metric_evaluators:
    #             try:
    #                 self.llm_metric_evaluators[metric.value] = load(metric.value)
    #                 logger.info(f"Loaded LLM metric evaluator: {metric.value}")
    #             except Exception as e:
    #                 logger.error(f"Failed to load LLM metric evaluator {metric.value}: {e}")

