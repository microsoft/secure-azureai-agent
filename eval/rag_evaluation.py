"""
RAGAS-based RAG Evaluation System.
Implements comprehensive RAG system evaluation using RAGAS metrics.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import pandas as pd
from datetime import datetime
import os

# RAGAS imports
try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy, 
        context_precision,
        context_recall,
        context_relevancy
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"RAGAS not available: {e}. Please install ragas: pip install ragas")
    RAGAS_AVAILABLE = False

# Local imports
from config import AzureConfig, EvaluationConfig
from azure_rag import AzureSearchRAGSystem, RAGResponse

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """Results of RAG system evaluation."""
    query: str
    answer: str
    contexts: List[str]
    ground_truth: Optional[str] = None
    faithfulness_score: Optional[float] = None
    answer_relevancy_score: Optional[float] = None
    context_precision_score: Optional[float] = None
    context_recall_score: Optional[float] = None
    context_relevancy_score: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)

@dataclass
class EvaluationSummary:
    """Summary statistics for evaluation results."""
    total_queries: int
    avg_faithfulness: Optional[float] = None
    avg_answer_relevancy: Optional[float] = None
    avg_context_precision: Optional[float] = None
    avg_context_recall: Optional[float] = None
    avg_context_relevancy: Optional[float] = None
    evaluation_timestamp: str = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.evaluation_timestamp is None:
            self.evaluation_timestamp = datetime.utcnow().isoformat()

class RAGEvaluationSystem:
    """
    Comprehensive RAG evaluation system using RAGAS metrics.
    """
    
    def __init__(
        self, 
        rag_system: AzureSearchRAGSystem,
        eval_config: EvaluationConfig
    ):
        """
        Initialize the evaluation system.
        
        Args:
            rag_system: RAG system to evaluate
            eval_config: Evaluation configuration
        """
        if not RAGAS_AVAILABLE:
            raise ImportError(
                "RAGAS is required for evaluation. Install with: pip install ragas"
            )
        
        self.rag_system = rag_system
        self.eval_config = eval_config
        
        # Configure RAGAS metrics based on config
        self.metrics = []
        if eval_config.enable_faithfulness:
            self.metrics.append(faithfulness)
        if eval_config.enable_answer_relevancy:
            self.metrics.append(answer_relevancy)
        if eval_config.enable_context_precision:
            self.metrics.append(context_precision)
        if eval_config.enable_context_recall:
            self.metrics.append(context_recall)
        if eval_config.enable_context_relevancy:
            self.metrics.append(context_relevancy)
        
        logger.info(f"RAG Evaluation System initialized with {len(self.metrics)} metrics")
    
    def prepare_evaluation_dataset(
        self,
        queries: List[str],
        ground_truths: Optional[List[str]] = None,
        rag_responses: Optional[List[RAGResponse]] = None
    ) -> Dataset:
        """
        Prepare dataset for RAGAS evaluation.
        
        Args:
            queries: List of evaluation queries
            ground_truths: Optional list of ground truth answers
            rag_responses: Optional pre-computed RAG responses
            
        Returns:
            Dataset formatted for RAGAS evaluation
        """
        if rag_responses is None:
            raise ValueError("RAG responses must be provided")
        
        if len(queries) != len(rag_responses):
            raise ValueError("Number of queries must match number of RAG responses")
        
        if ground_truths and len(ground_truths) != len(queries):
            raise ValueError("Number of ground truths must match number of queries")
        
        # Prepare data in RAGAS format
        data = {
            "question": queries,
            "answer": [resp.answer for resp in rag_responses],
            "contexts": [resp.contexts for resp in rag_responses]
        }
        
        # Add ground truths if available
        if ground_truths:
            data["ground_truth"] = ground_truths
        
        # Create dataset
        dataset = Dataset.from_dict(data)
        
        logger.info(f"Prepared evaluation dataset with {len(queries)} samples")
        return dataset
    
    async def generate_rag_responses(
        self,
        queries: List[str],
        **rag_kwargs
    ) -> List[RAGResponse]:
        """
        Generate RAG responses for evaluation queries.
        
        Args:
            queries: List of queries to process
            **rag_kwargs: Additional arguments for RAG processing
            
        Returns:
            List of RAG responses
        """
        logger.info(f"Generating RAG responses for {len(queries)} queries")
        
        # Use batch processing for efficiency
        responses = await self.rag_system.batch_process_queries(
            queries=queries,
            batch_size=self.eval_config.batch_size,
            **rag_kwargs
        )
        
        logger.info(f"Generated {len(responses)} RAG responses")
        return responses
    
    def evaluate_with_ragas(
        self,
        dataset: Dataset,
        custom_metrics: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Perform RAGAS evaluation on the dataset.
        
        Args:
            dataset: Dataset formatted for RAGAS
            custom_metrics: Optional custom metrics to use
            
        Returns:
            Evaluation results from RAGAS
        """
        metrics_to_use = custom_metrics if custom_metrics else self.metrics
        
        if not metrics_to_use:
            raise ValueError("No metrics specified for evaluation")
        
        logger.info(f"Starting RAGAS evaluation with {len(metrics_to_use)} metrics")
        
        try:
            # Run RAGAS evaluation
            results = evaluate(
                dataset=dataset,
                metrics=metrics_to_use,
                # llm=self._get_evaluation_llm(),
                # embeddings=self._get_evaluation_embeddings()
            )
            
            logger.info("RAGAS evaluation completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"RAGAS evaluation failed: {e}")
            raise
    
    def process_ragas_results(
        self,
        ragas_results: Dict[str, Any],
        queries: List[str],
        rag_responses: List[RAGResponse],
        ground_truths: Optional[List[str]] = None
    ) -> List[EvaluationResult]:
        """
        Process RAGAS results into structured format.
        
        Args:
            ragas_results: Results from RAGAS evaluation
            queries: Original queries
            rag_responses: RAG responses
            ground_truths: Optional ground truth answers
            
        Returns:
            List of structured evaluation results
        """
        evaluation_results = []
        
        # Extract metrics from RAGAS results
        metrics_data = {}
        for metric_name, values in ragas_results.items():
            if isinstance(values, list):
                metrics_data[metric_name] = values
        
        # Create evaluation results
        for i, (query, response) in enumerate(zip(queries, rag_responses)):
            result = EvaluationResult(
                query=query,
                answer=response.answer,
                contexts=response.contexts,
                ground_truth=ground_truths[i] if ground_truths else None,
                metadata={
                    "rag_metadata": response.metadata,
                    "evaluation_config": asdict(self.eval_config)
                }
            )
            
            # Add metric scores
            if "faithfulness" in metrics_data:
                result.faithfulness_score = metrics_data["faithfulness"][i]
            if "answer_relevancy" in metrics_data:
                result.answer_relevancy_score = metrics_data["answer_relevancy"][i]
            if "context_precision" in metrics_data:
                result.context_precision_score = metrics_data["context_precision"][i]
            if "context_recall" in metrics_data:
                result.context_recall_score = metrics_data["context_recall"][i]
            if "context_relevancy" in metrics_data:
                result.context_relevancy_score = metrics_data["context_relevancy"][i]
            
            evaluation_results.append(result)
        
        return evaluation_results
    
    def calculate_summary_statistics(
        self,
        evaluation_results: List[EvaluationResult]
    ) -> EvaluationSummary:
        """
        Calculate summary statistics from evaluation results.
        
        Args:
            evaluation_results: List of evaluation results
            
        Returns:
            Summary statistics
        """
        def safe_mean(values):
            """Calculate mean of values, ignoring None values."""
            valid_values = [v for v in values if v is not None]
            return sum(valid_values) / len(valid_values) if valid_values else None
        
        # Extract scores
        faithfulness_scores = [r.faithfulness_score for r in evaluation_results]
        answer_relevancy_scores = [r.answer_relevancy_score for r in evaluation_results]
        context_precision_scores = [r.context_precision_score for r in evaluation_results]
        context_recall_scores = [r.context_recall_score for r in evaluation_results]
        context_relevancy_scores = [r.context_relevancy_score for r in evaluation_results]
        
        # Calculate averages
        summary = EvaluationSummary(
            total_queries=len(evaluation_results),
            avg_faithfulness=safe_mean(faithfulness_scores),
            avg_answer_relevancy=safe_mean(answer_relevancy_scores),
            avg_context_precision=safe_mean(context_precision_scores),
            avg_context_recall=safe_mean(context_recall_scores),
            avg_context_relevancy=safe_mean(context_relevancy_scores),
            config=asdict(self.eval_config)
        )
        
        return summary
    
    async def full_evaluation(
        self,
        queries: List[str],
        ground_truths: Optional[List[str]] = None,
        output_file: Optional[str] = None,
        **rag_kwargs
    ) -> Tuple[List[EvaluationResult], EvaluationSummary]:
        """
        Perform complete RAG evaluation pipeline.
        
        Args:
            queries: List of evaluation queries
            ground_truths: Optional ground truth answers
            output_file: Optional file to save results
            **rag_kwargs: Additional arguments for RAG processing
            
        Returns:
            Tuple of (evaluation_results, summary_statistics)
        """
        logger.info(f"Starting full evaluation for {len(queries)} queries")
        
        try:
            # Step 1: Generate RAG responses
            rag_responses = await self.generate_rag_responses(queries, **rag_kwargs)
            
            # Step 2: Prepare evaluation dataset
            dataset = self.prepare_evaluation_dataset(
                queries=queries,
                ground_truths=ground_truths,
                rag_responses=rag_responses
            )
            
            # Step 3: Run RAGAS evaluation
            ragas_results = self.evaluate_with_ragas(dataset)
            
            # Step 4: Process results
            evaluation_results = self.process_ragas_results(
                ragas_results=ragas_results,
                queries=queries,
                rag_responses=rag_responses,
                ground_truths=ground_truths
            )
            
            # Step 5: Calculate summary
            summary = self.calculate_summary_statistics(evaluation_results)
            
            # Step 6: Save results if requested
            if output_file:
                self.save_results(evaluation_results, summary, output_file)
            
            logger.info("Full evaluation completed successfully")
            return evaluation_results, summary
            
        except Exception as e:
            logger.error(f"Full evaluation failed: {e}")
            raise
    
    def save_results(
        self,
        evaluation_results: List[EvaluationResult],
        summary: EvaluationSummary,
        output_file: str
    ):
        """
        Save evaluation results to file.
        
        Args:
            evaluation_results: List of evaluation results
            summary: Summary statistics
            output_file: Output file path
        """
        try:
            # Prepare data for saving
            results_data = {
                "summary": asdict(summary),
                "detailed_results": [result.to_dict() for result in evaluation_results]
            }
            
            # Save as JSON
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            # Also save as CSV for easy analysis
            csv_file = output_file.replace('.json', '.csv')
            df = pd.DataFrame([result.to_dict() for result in evaluation_results])
            df.to_csv(csv_file, index=False)
            
            logger.info(f"Results saved to {output_file} and {csv_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def compare_evaluations(
        self,
        baseline_file: str,
        current_results: List[EvaluationResult],
        current_summary: EvaluationSummary
    ) -> Dict[str, Any]:
        """
        Compare current evaluation with baseline results.
        
        Args:
            baseline_file: Path to baseline results file
            current_results: Current evaluation results
            current_summary: Current summary statistics
            
        Returns:
            Comparison results
        """
        try:
            # Load baseline results
            with open(baseline_file, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            baseline_summary = baseline_data["summary"]
            
            # Compare summaries
            comparison = {
                "baseline_summary": baseline_summary,
                "current_summary": asdict(current_summary),
                "improvements": {},
                "degradations": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Compare each metric
            metrics = [
                "avg_faithfulness", 
                "avg_answer_relevancy",
                "avg_context_precision", 
                "avg_context_recall",
                "avg_context_relevancy"
            ]
            
            for metric in metrics:
                baseline_val = baseline_summary.get(metric)
                current_val = getattr(current_summary, metric)
                
                if baseline_val is not None and current_val is not None:
                    diff = current_val - baseline_val
                    if diff > 0:
                        comparison["improvements"][metric] = {
                            "baseline": baseline_val,
                            "current": current_val,
                            "improvement": diff
                        }
                    elif diff < 0:
                        comparison["degradations"][metric] = {
                            "baseline": baseline_val,
                            "current": current_val,
                            "degradation": abs(diff)
                        }
            
            logger.info("Evaluation comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            raise