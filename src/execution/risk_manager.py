"""Risk Management - Position sizing, drawdown limits, etc."""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """Risk management configuration"""

    initial_balance: float = 1000.0
    max_position_size: float = 0.05  # 5% of balance per trade
    max_portfolio_draw_down: float = 0.20  # 20% max drawdown
    risk_per_trade: float = 0.02  # 2% per trade
    profit_target: float = 0.30  # 30% profit target
    min_confidence: float = 0.70  # Minimum confidence to trade (UPDATED)
    kelly_criterion_fraction: float = 0.25  # Fractional Kelly


class RiskManager:
    """Manage position sizing and risk limits"""

    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.current_balance = self.config.initial_balance
        self.peak_balance = self.config.initial_balance
        self.locked_capital = 0.0

        logger.info(
            f"RiskManager initialized (balance=${self.current_balance:.2f}, "
            f"max_pos={self.config.max_position_size:.1%})"
        )

    def set_balance(self, balance: float):
        """Update current balance"""
        self.current_balance = balance
        self.peak_balance = max(self.peak_balance, balance)

    def can_trade(
        self,
        confidence: float,
        implied_edge: float | None = None,
    ) -> tuple[bool, str]:
        """
        Check if we can place a trade

        Args:
            confidence: Claude's confidence (0-1)
            implied_edge: Expected edge if available

        Returns:
            (can_trade, reason)
        """

        # Check minimum confidence
        if confidence < self.config.min_confidence:
            return False, f"Confidence {confidence:.0%} < minimum {self.config.min_confidence:.0%}"

        # Check drawdown limit
        current_dd = 1 - (self.current_balance / self.peak_balance)
        if current_dd > self.config.max_portfolio_draw_down:
            return (
                False,
                f"Drawdown {current_dd:.1%} > limit {self.config.max_portfolio_draw_down:.1%}",
            )

        # Check available balance
        available = self.current_balance - self.locked_capital
        min_position = 10  # Minimum $10

        if available < min_position:
            return False, f"Insufficient balance (${available:.2f} < ${min_position})"

        return True, "OK"

    def calculate_position_size(
        self,
        confidence: float,
        entry_price: float,
        stop_loss_percent: float = 0.10,
    ) -> float:
        """
        Calculate position size using Kelly Criterion

        Args:
            confidence: Win probability (0-1)
            entry_price: Entry price
            stop_loss_percent: Stop loss distance (%)

        Returns:
            Position size in dollars
        """

        # Win/loss ratio based on risk/reward
        win_size = 1.0  # $1 per contract
        loss_size = stop_loss_percent

        # Kelly Criterion: f = (bp - q) / b
        # where b=win_size, p=confidence, q=1-confidence
        if loss_size == 0:
            return 0

        kelly_fraction = (
            (loss_size * confidence - (1 - confidence)) / loss_size
        )

        # Apply Kelly fraction safety factor
        kelly_fraction = kelly_fraction * self.config.kelly_criterion_fraction

        # Cap at 0
        kelly_fraction = max(0, kelly_fraction)

        # Calculate position size
        risk_amount = self.current_balance * self.config.risk_per_trade
        max_size = self.current_balance * self.config.max_position_size

        position_size = min(
            risk_amount / (entry_price * stop_loss_percent) if entry_price > 0 else 0,
            max_size,
        )

        logger.debug(
            f"Position size: Kelly={kelly_fraction:.2%}, "
            f"Risk=${risk_amount:.2f}, Size={position_size:.2f}@${entry_price:.3f}"
        )

        return max(1.0, position_size)  # Minimum 1 share

    def get_dynamic_stop_loss(
        self, entry_price: float, volatility: float = 0.05
    ) -> float:
        """
        Calculate dynamic stop loss based on volatility

        Args:
            entry_price: Entry price
            volatility: Estimated volatility (e.g., 0.05 = 5%)

        Returns:
            Stop loss price
        """

        # ATR-based stop loss
        atr_multiple = 2.0  # 2x volatility
        stop_loss_distance = entry_price * volatility * atr_multiple
        stop_loss_price = entry_price - stop_loss_distance

        return max(0, stop_loss_price)

    def get_take_profit(self, entry_price: float, confidence: float) -> float:
        """
        Calculate take profit level

        Args:
            entry_price: Entry price
            confidence: Confidence level

        Returns:
            Take profit price
        """

        # Higher confidence = higher target
        target_pnl_percent = 0.05 + (confidence - 0.5) * 0.1  # 5-10%

        return entry_price * (1 + target_pnl_percent)

    def update_after_trade(self, pnl: float):
        """Update balance after trade execution"""
        self.current_balance += pnl
        self.peak_balance = max(self.peak_balance, self.current_balance)

        logger.info(
            f"Balance updated: ${self.current_balance:.2f} "
            f"(PnL: ${pnl:+.2f}, Drawdown: {self.get_current_drawdown():.1%})"
        )

    def get_current_drawdown(self) -> float:
        """Get current drawdown %"""
        if self.peak_balance == 0:
            return 0
        return 1 - (self.current_balance / self.peak_balance)

    def get_status(self) -> Dict[str, Any]:
        """Get risk manager status"""
        return {
            "current_balance": self.current_balance,
            "peak_balance": self.peak_balance,
            "drawdown": self.get_current_drawdown(),
            "locked_capital": self.locked_capital,
            "available": self.current_balance - self.locked_capital,
            "max_position_size": self.config.max_position_size,
            "risk_per_trade": self.config.risk_per_trade,
        }
