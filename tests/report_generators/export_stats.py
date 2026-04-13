"""Export performance statistics"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()

# Get latest data
trades = tracker.trades.trades if tracker.trades else []
metrics = tracker.metrics.calculate_all_metrics(trades) if trades else {}

# Create export
export = {
    "timestamp": datetime.now().isoformat(),
    "session_type": "paper_trading",
    "total_trades": len(trades),
    "metrics": metrics,
    "recent_trades": [
        {
            "market": t.get("market"),
            "decision": t.get("decision"),
            "confidence": t.get("confidence"),
            "entry_price": t.get("entry_price"),
            "position_size": t.get("position_size"),
        }
        for t in trades[-20:]
    ]
}

# Save to file
export_dir = Path("memory/exports")
export_dir.mkdir(parents=True, exist_ok=True)

filename = export_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, "w") as f:
    json.dump(export, f, indent=2)

print(f"\n[+] Statistics exported to: {filename}")
print(f"[+] Total trades recorded: {len(trades)}")

if metrics:
    print(f"\nSummary Metrics:")
    if "summary" in metrics:
        for key, value in metrics["summary"].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
