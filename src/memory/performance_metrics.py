"""Performance metrics calculation - ROI, win rate, Sharpe ratio, etc."""

import logging
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Calculate trading performance metrics"""

    def __init__(self):
        logger.info("PerformanceMetrics initialized")

    def calculate_all_metrics(
        self, trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate all performance metrics from trade list"""

        closed_trades = [t for t in trades if t.get("status") == "CLOSED"]

        if not closed_trades:
            logger.warning("No closed trades for metrics calculation")
            return self._empty_metrics()

        return {
            "summary": self._calculate_summary(closed_trades),
            "win_metrics": self._calculate_win_metrics(closed_trades),
            "risk_metrics": self._calculate_risk_metrics(closed_trades),
            "time_metrics": self._calculate_time_metrics(closed_trades),
        }

    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            "summary": {
                "total_trades": 0,
                "gross_profit": 0,
                "gross_loss": 0,
                "net_profit": 0,
                "roi_percent": 0,
            },
            "win_metrics": {
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "win_loss_ratio": 0,
            },
            "risk_metrics": {
                "max_drawdown": 0,
                "max_drawdown_percent": 0,
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
            },
            "time_metrics": {
                "avg_trade_duration": 0,
                "first_trade": None,
                "last_trade": None,
            },
        }

    def _calculate_summary(self, trades: List[Dict]) -> Dict:
        """Calculate trade summary"""

        pnls = [t.get("pnl", 0) for t in trades if t.get("pnl") is not None]

        if not pnls:
            return {
                "total_trades": len(trades),
                "gross_profit": 0,
                "gross_loss": 0,
                "net_profit": 0,
                "roi_percent": 0,
            }

        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = sum(p for p in pnls if p < 0)
        net_profit = sum(pnls)

        # Calculate ROI (assume $1000 initial balance)
        roi_percent = (net_profit / 1000) * 100

        return {
            "total_trades": len(trades),
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "net_profit": net_profit,
            "roi_percent": roi_percent,
        }

    def _calculate_win_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate win rate and related metrics"""

        pnls = [t.get("pnl", 0) for t in trades if t.get("pnl") is not None]

        if not pnls:
            return {
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "win_loss_ratio": 0,
            }

        winning = [p for p in pnls if p > 0]
        losing = [p for p in pnls if p < 0]

        win_rate = len(winning) / len(pnls) if pnls else 0
        avg_win = statistics.mean(winning) if winning else 0
        avg_loss = statistics.mean(losing) if losing else 0
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        return {
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "win_loss_ratio": win_loss_ratio,
        }

    def _calculate_risk_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate max drawdown, Sharpe ratio, etc."""

        pnls = [t.get("pnl", 0) for t in trades if t.get("pnl") is not None]

        if not pnls:
            return {
                "max_drawdown": 0,
                "max_drawdown_percent": 0,
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
            }

        # Max drawdown
        cumulative = 0
        running_max = 0
        max_dd = 0

        for pnl in pnls:
            cumulative += pnl
            running_max = max(running_max, cumulative)
            drawdown = running_max - cumulative
            max_dd = max(max_dd, drawdown)

        max_dd_percent = (max_dd / 1000) * 100  # Assume $1000 balance

        # Sharpe ratio (simplified: daily returns)
        try:
            std_dev = statistics.stdev(pnls)
            sharpe = (statistics.mean(pnls) / std_dev * (252**0.5)) if std_dev else 0
        except:
            sharpe = 0

        # Sortino ratio (only downside volatility)
        downside_returns = [p for p in pnls if p < 0]
        try:
            downside_std = statistics.stdev(downside_returns) if downside_returns else 0
            sortino = (
                (statistics.mean(pnls) / downside_std * (252**0.5))
                if downside_std
                else 0
            )
        except:
            sortino = 0

        return {
            "max_drawdown": max_dd,
            "max_drawdown_percent": max_dd_percent,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
        }

    def _calculate_time_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate time-based metrics"""

        if not trades:
            return {
                "avg_trade_duration": 0,
                "first_trade": None,
                "last_trade": None,
            }

        timestamps = [t.get("timestamp") for t in trades if t.get("timestamp")]

        if not timestamps:
            return {
                "avg_trade_duration": 0,
                "first_trade": None,
                "last_trade": None,
            }

        first = min(timestamps)
        last = max(timestamps)

        # Average duration (in hours)
        durations = []
        for t in trades:
            if t.get("timestamp") and t.get("closed_at"):
                start = datetime.fromisoformat(t["timestamp"])
                end = datetime.fromisoformat(t["closed_at"])
                duration = (end - start).total_seconds() / 3600
                durations.append(duration)

        avg_duration = statistics.mean(durations) if durations else 0

        return {
            "avg_trade_duration_hours": avg_duration,
            "first_trade": first,
            "last_trade": last,
            "trading_period_days": (
                (datetime.fromisoformat(last) - datetime.fromisoformat(first)).days
            ),
        }

    def get_summary_report(self, trades: List[Dict]) -> str:
        """Generate text summary report"""

        metrics = self.calculate_all_metrics(trades)

        report = f"""
╔════════════════════════════════════════════════╗
║         TRADING PERFORMANCE REPORT             ║
╚════════════════════════════════════════════════╝

SUMMARY:
  Total Trades: {metrics['summary']['total_trades']}
  Net Profit: ${metrics['summary']['net_profit']:.2f}
  ROI: {metrics['summary']['roi_percent']:.1f}%
  Gross Profit: ${metrics['summary']['gross_profit']:.2f}
  Gross Loss: ${metrics['summary']['gross_loss']:.2f}

WIN RATE:
  Winning Trades: {metrics['win_metrics']['winning_trades']}
  Losing Trades: {metrics['win_metrics']['losing_trades']}
  Win Rate: {metrics['win_metrics']['win_rate']:.1%}
  Avg Win: ${metrics['win_metrics']['avg_win']:.2f}
  Avg Loss: ${metrics['win_metrics']['avg_loss']:.2f}
  Win/Loss Ratio: {metrics['win_metrics']['win_loss_ratio']:.2f}

RISK:
  Max Drawdown: ${metrics['risk_metrics']['max_drawdown']:.2f}
  Max Drawdown %: {metrics['risk_metrics']['max_drawdown_percent']:.1f}%
  Sharpe Ratio: {metrics['risk_metrics']['sharpe_ratio']:.2f}
  Sortino Ratio: {metrics['risk_metrics']['sortino_ratio']:.2f}

TIME:
  Avg Trade Duration: {metrics['time_metrics']['avg_trade_duration_hours']:.1f} hours
  Trading Period: {metrics['time_metrics']['trading_period_days']} days
"""

        return report
