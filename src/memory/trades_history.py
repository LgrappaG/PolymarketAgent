"""Trade history management - Persistent storage of all trades"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TradeHistory:
    """Manage trade history with persistence"""

    def __init__(self, history_file: str = "memory/trades_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        self.trades: List[Dict[str, Any]] = self._load_history()
        logger.info(f"TradeHistory initialized with {len(self.trades)} trades")

    def log_trade(
        self,
        market: str,
        decision: str,  # BUY/SELL
        confidence: float,
        position_size: float,
        entry_price: float,
        exit_price: Optional[float] = None,
        pnl: Optional[float] = None,
        status: str = "OPEN",  # OPEN/CLOSED
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Log a trade to history

        Returns:
            Trade record
        """

        trade = {
            "id": len(self.trades) + 1,
            "timestamp": datetime.now().isoformat(),
            "market": market,
            "decision": decision,
            "confidence": confidence,
            "position_size": position_size,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl": pnl,
            "pnl_percent": (pnl / (position_size * entry_price) * 100) if pnl else None,
            "status": status,
            "notes": notes,
        }

        self.trades.append(trade)
        self._save_history()

        logger.info(
            f"Trade logged: {market} {decision} @ {confidence:.0%} "
            f"(size: ${position_size:.2f})"
        )

        return trade

    def close_trade(
        self, trade_id: int, exit_price: float, notes: str = ""
    ) -> Optional[Dict]:
        """Close an open trade"""

        for trade in self.trades:
            if trade["id"] == trade_id and trade["status"] == "OPEN":
                pnl = (exit_price - trade["entry_price"]) * trade["position_size"]
                if trade["decision"] == "SELL":
                    pnl = -pnl  # Invert for sells

                trade["exit_price"] = exit_price
                trade["pnl"] = pnl
                trade["pnl_percent"] = (pnl / (trade["position_size"] * trade["entry_price"])) * 100
                trade["status"] = "CLOSED"
                trade["closed_at"] = datetime.now().isoformat()
                trade["notes"] = notes

                self._save_history()

                logger.info(f"Trade closed: {trade['market']} PnL=${pnl:.2f}")
                return trade

        return None

    def get_trades_by_market(self, market: str) -> List[Dict]:
        """Get all trades for a market"""
        return [t for t in self.trades if t["market"] == market]

    def get_open_trades(self) -> List[Dict]:
        """Get all currently open trades"""
        return [t for t in self.trades if t["status"] == "OPEN"]

    def get_closed_trades(self) -> List[Dict]:
        """Get all closed trades (for analysis)"""
        return [t for t in self.trades if t["status"] == "CLOSED"]

    def get_trades_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict]:
        """Get trades within date range (ISO format)"""
        return [
            t
            for t in self.trades
            if start_date <= t["timestamp"] <= end_date
        ]

    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading trade history: {e}")
        return []

    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")

    def export_csv(self, filepath: str = "trades_export.csv"):
        """Export trades to CSV for analysis"""
        try:
            import csv

            with open(filepath, "w", newline="") as f:
                if not self.trades:
                    logger.warning("No trades to export")
                    return

                writer = csv.DictWriter(f, fieldnames=self.trades[0].keys())
                writer.writeheader()
                writer.writerows(self.trades)

                logger.info(f"Trades exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting trades: {e}")
