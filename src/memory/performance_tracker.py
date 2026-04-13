"""Performance tracking system - Complete memory management"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.memory.trades_history import TradeHistory
from src.memory.performance_metrics import PerformanceMetrics
from src.memory.calibration_tracker import CalibrationTracker

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Central performance tracking - aggregates all memory systems"""

    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-systems
        self.trades = TradeHistory(f"{memory_dir}/trades_history.json")
        self.metrics = PerformanceMetrics()
        self.calibration = CalibrationTracker(f"{memory_dir}/claude_calibration.json")

        logger.info(f"PerformanceTracker initialized (memory_dir={memory_dir})")

    # ========== TRADE MANAGEMENT ==========

    def log_trade(
        self,
        market: str,
        decision: str,
        confidence: float,
        position_size: float,
        entry_price: float,
        exit_price: Optional[float] = None,
        pnl: Optional[float] = None,
        notes: str = "",
    ) -> Dict:
        """Log a trade"""
        return self.trades.log_trade(
            market=market,
            decision=decision,
            confidence=confidence,
            position_size=position_size,
            entry_price=entry_price,
            exit_price=exit_price,
            pnl=pnl,
            status="OPEN" if exit_price is None else "CLOSED",
            notes=notes,
        )

    def close_trade(self, trade_id: int, exit_price: float, notes: str = "") -> bool:
        """Close a trade"""
        result = self.trades.close_trade(trade_id, exit_price, notes)
        return result is not None

    def get_open_trades(self) -> List[Dict]:
        """Get all open positions"""
        return self.trades.get_open_trades()

    def get_closed_trades(self) -> List[Dict]:
        """Get all closed trades (for analysis)"""
        return self.trades.get_closed_trades()

    def get_trades_by_market(self, market: str) -> List[Dict]:
        """Get trades for a specific market"""
        return self.trades.get_trades_by_market(market)

    # ========== CLAUDE CALIBRATION ==========

    def log_prediction(
        self,
        market: str,
        claude_confidence: float,
        predicted_direction: str,
        actual_outcome: str,
    ) -> Dict:
        """Log Claude prediction for calibration"""
        return self.calibration.log_prediction(
            market=market,
            claude_confidence=claude_confidence,
            predicted_direction=predicted_direction,
            actual_outcome=actual_outcome,
        )

    def get_claude_calibration(self) -> Dict:
        """Get Claude's calibration metrics"""
        return self.calibration.get_overall_calibration()

    def get_accuracy_by_market(self) -> Dict:
        """Get Claude's accuracy per market"""
        return self.calibration.get_accuracy_by_market()

    # ========== PERFORMANCE METRICS ==========

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate all performance metrics"""
        closed_trades = self.trades.get_closed_trades()
        return self.metrics.calculate_all_metrics(closed_trades)

    # ========== REPORTING ==========

    def print_summary(self):
        """Print complete performance summary"""

        print("\n" + "=" * 60)
        print("PERFORMANCE & CALIBRATION SUMMARY")
        print("=" * 60)

        # Trade summary
        all_trades = self.trades.trades
        open_trades = self.get_open_trades()
        closed_trades = self.get_closed_trades()

        print(f"\nTRADES:")
        print(f"  Total: {len(all_trades)}")
        print(f"  Open: {len(open_trades)}")
        print(f"  Closed: {len(closed_trades)}")

        if closed_trades:
            metrics = self.get_performance_metrics()
            print(f"\nPERFORMANCE:")
            print(f"  Net P&L: ${metrics['summary']['net_profit']:.2f}")
            print(f"  ROI: {metrics['summary']['roi_percent']:.1f}%")
            print(f"  Win Rate: {metrics['win_metrics']['win_rate']:.1%}")
            print(f"  Max Drawdown: {metrics['risk_metrics']['max_drawdown_percent']:.1f}%")

        # Claude calibration
        calibration = self.get_claude_calibration()
        if calibration["total_predictions"] > 0:
            print(f"\nCLAUDE CALIBRATION:")
            print(
                f"  Accuracy: {calibration['overall_accuracy']:.1%} "
                f"(from {calibration['total_predictions']} predictions)"
            )
            print(
                f"  Avg Confidence: {calibration['avg_confidence']:.1%}"
            )
            print(
                f"  Calibration Error: {calibration['calibration_error']:.1%}"
            )

        print("=" * 60 + "\n")

    def export_full_report(self, filepath: str = "performance_report.txt"):
        """Export complete report to file"""

        try:
            with open(filepath, "w") as f:
                # Trade history
                f.write("=" * 60 + "\n")
                f.write("TRADE HISTORY\n")
                f.write("=" * 60 + "\n\n")
                f.write(json.dumps(self.trades.trades, indent=2))

                # Metrics
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("PERFORMANCE METRICS\n")
                f.write("=" * 60 + "\n\n")
                f.write(self.metrics.get_summary_report(self.get_closed_trades()))

                # Calibration
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("CLAUDE CALIBRATION\n")
                f.write("=" * 60 + "\n\n")
                f.write(self.calibration.get_calibration_report())

            logger.info(f"Full report exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def save(self, verbose: bool = False):
        """Save all memory systems"""
        self.trades._save_history()
        self.calibration._save_calibration()

        if verbose:
            logger.info("All memory systems saved")

