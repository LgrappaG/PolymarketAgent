"""Claude Calibration Tracker - Measure Claude's confidence vs actual accuracy"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class CalibrationTracker:
    """Track Claude's prediction accuracy vs confidence"""

    def __init__(self, calibration_file: str = "memory/claude_calibration.json"):
        self.calibration_file = Path(calibration_file)
        self.calibration_file.parent.mkdir(parents=True, exist_ok=True)

        self.records: List[Dict[str, Any]] = self._load_calibration()
        logger.info(
            f"CalibrationTracker initialized with {len(self.records)} records"
        )

    def log_prediction(
        self,
        market: str,
        claude_confidence: float,
        predicted_direction: str,  # BUY/SELL
        actual_outcome: str,  # CORRECT/INCORRECT
    ) -> Dict:
        """
        Log a Claude prediction for calibration analysis

        Args:
            market: Market name
            claude_confidence: 0-1, Claude's confidence
            predicted_direction: BUY or SELL
            actual_outcome: Did it turn out correct?

        Returns:
            Calibration record
        """

        record = {
            "id": len(self.records) + 1,
            "timestamp": datetime.now().isoformat(),
            "market": market,
            "claude_confidence": claude_confidence,
            "predicted_direction": predicted_direction,
            "actual_outcome": actual_outcome,
            "correct": actual_outcome == "CORRECT",
        }

        self.records.append(record)
        self._save_calibration()

        logger.debug(
            f"Calibration logged: {predicted_direction} "
            f"@ {claude_confidence:.0%} → {actual_outcome}"
        )

        return record

    def get_accuracy_by_confidence_bin(
        self, bin_size: float = 0.1
    ) -> Dict[str, Any]:
        """
        Get accuracy for each confidence level

        Args:
            bin_size: Bin size for grouping (0.1 = 10% bins)

        Returns:
            {
                "0.0-0.1": {"avg_confidence": 0.05, "accuracy": 0.45, "count": 20},
                ...
            }
        """

        bins = {}

        # Create bins
        for i in range(0, 11):
            bin_start = i * bin_size
            bin_end = (i + 1) * bin_size
            bin_name = f"{bin_start:.1f}-{bin_end:.1f}"
            bins[bin_name] = {
                "start": bin_start,
                "end": bin_end,
                "confidences": [],
                "correct": 0,
                "total": 0,
            }

        # Populate bins
        for record in self.records:
            conf = record["claude_confidence"]

            for bin_info in bins.values():
                if bin_info["start"] <= conf < bin_info["end"]:
                    bin_info["confidences"].append(conf)
                    bin_info["total"] += 1
                    if record["correct"]:
                        bin_info["correct"] += 1
                    break

        # Calculate metrics
        result = {}
        for bin_name, bin_info in bins.items():
            if bin_info["total"] > 0:
                accuracy = bin_info["correct"] / bin_info["total"]
                avg_conf = (
                    statistics.mean(bin_info["confidences"])
                    if bin_info["confidences"]
                    else bin_info["start"]
                )

                result[bin_name] = {
                    "avg_confidence": avg_conf,
                    "accuracy": accuracy,
                    "count": bin_info["total"],
                }

        return result

    def get_overall_calibration(self) -> Dict[str, Any]:
        """Get overall calibration metrics"""

        if not self.records:
            return {
                "total_predictions": 0,
                "overall_accuracy": 0,
                "avg_confidence": 0,
                "calibration_error": 0,
            }

        correct = sum(1 for r in self.records if r["correct"])
        confidences = [r["claude_confidence"] for r in self.records]

        overall_accuracy = correct / len(self.records)
        avg_confidence = statistics.mean(confidences)

        # Calibration error = |predicted_confidence - actual_accuracy|
        calibration_error = abs(avg_confidence - overall_accuracy)

        return {
            "total_predictions": len(self.records),
            "overall_accuracy": overall_accuracy,
            "avg_confidence": avg_confidence,
            "calibration_error": calibration_error,
            "confidence_interval": f"{min(confidences):.1%} - {max(confidences):.1%}",
        }

    def get_accuracy_by_market(self) -> Dict[str, Dict]:
        """Get accuracy breakdown by market"""

        markets = {}

        for record in self.records:
            market = record["market"]

            if market not in markets:
                markets[market] = {"correct": 0, "total": 0, "confidences": []}

            markets[market]["total"] += 1
            if record["correct"]:
                markets[market]["correct"] += 1
            markets[market]["confidences"].append(record["claude_confidence"])

        # Calculate metrics per market
        result = {}
        for market, data in markets.items():
            result[market] = {
                "accuracy": data["correct"] / data["total"],
                "prediction_count": data["total"],
                "avg_confidence": statistics.mean(data["confidences"]),
            }

        return result

    def get_calibration_report(self) -> str:
        """Generate calibration report"""

        overall = self.get_overall_calibration()
        by_market = self.get_accuracy_by_market()
        by_confidence = self.get_accuracy_by_confidence_bin()

        report = f"""
╔════════════════════════════════════════════════╗
║     CLAUDE CALIBRATION ANALYSIS REPORT         ║
╚════════════════════════════════════════════════╝

OVERALL PERFORMANCE:
  Total Predictions: {overall['total_predictions']}
  Overall Accuracy: {overall['overall_accuracy']:.1%}
  Avg Confidence: {overall['avg_confidence']:.1%}
  Calibration Error: {overall['calibration_error']:.1%}

  → Interpretation:
    - If calibration_error < 5%: WELL-CALIBRATED ✓
    - If calibration_error 5-15%: ACCEPTABLE
    - If calibration_error > 15%: NEEDS ADJUSTMENT

ACCURACY BY MARKET:
"""

        for market, metrics in sorted(
            by_market.items(), key=lambda x: x[1]["accuracy"], reverse=True
        ):
            report += (
                f"  {market:<30} "
                f"{metrics['accuracy']:>6.1%} "
                f"({metrics['prediction_count']} predictions)\n"
            )

        report += f"""
ACCURACY BY CONFIDENCE LEVEL:
"""

        for conf_bin, metrics in sorted(by_confidence.items()):
            report += (
                f"  {conf_bin:<12} "
                f"Accuracy: {metrics['accuracy']:>5.1%} "
                f"(n={metrics['count']})\n"
            )

        return report

    def _load_calibration(self) -> List[Dict]:
        """Load calibration records"""
        if self.calibration_file.exists():
            try:
                with open(self.calibration_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading calibration: {e}")
        return []

    def _save_calibration(self):
        """Save calibration records"""
        try:
            with open(self.calibration_file, "w") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")
