#!/usr/bin/env python3
"""launch-pricing: per-user economics for a subscription or per-unit product.

Stdlib only (Python 3.8+). Every number comes from an input you can check.

    python3 cost_model.py --price 20 --fixed 100 --variable 3 \
        --fee-pct 2.9 --fee-fixed 0.30 [--users 200] [--churn 5] [--sweep 10,15,20,30] [--json]

  --price      price per user per period (e.g. per month)
  --fixed      fixed costs per period (hosting floor, tools, your time if you count it)
  --variable   cost to serve ONE user per period (AI/API calls, storage, email, support)
  --fee-pct    payment processor percentage fee (default 2.9)
  --fee-fixed  payment processor fixed fee per charge (default 0.30)
  --users      show profit at this many paying users
  --churn      monthly churn % (adds average lifetime in periods and lifetime value)
  --sweep      comma list of prices to compare side by side
"""
import argparse
import json
import math
import sys


def model(price, fixed, variable, fee_pct, fee_fixed, users=None, churn=None):
    fee = price * fee_pct / 100.0 + fee_fixed
    contrib = price - variable - fee
    out = {
        "price": price, "variable_cost": variable, "processor_fee": round(fee, 4),
        "contribution_per_user": round(contrib, 4),
        "gross_margin_pct": round(100.0 * contrib / price, 1) if price else None,
    }
    if contrib > 0:
        out["break_even_users"] = int(math.ceil(fixed / contrib)) if fixed > 0 else 0
    else:
        out["break_even_users"] = None
        out["warning"] = "Each user loses money at this price. Raise the price or cut cost-to-serve."
    if users is not None:
        out["users"] = users
        out["profit_at_users"] = round(users * contrib - fixed, 2)
    if churn:
        life = 100.0 / churn
        out["avg_lifetime_periods"] = round(life, 1)
        out["lifetime_value"] = round(contrib * life, 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", type=float)
    ap.add_argument("--fixed", type=float, default=0.0)
    ap.add_argument("--variable", type=float, default=0.0)
    ap.add_argument("--fee-pct", type=float, default=2.9)
    ap.add_argument("--fee-fixed", type=float, default=0.30)
    ap.add_argument("--users", type=int)
    ap.add_argument("--churn", type=float)
    ap.add_argument("--sweep")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    prices = [float(p) for p in a.sweep.split(",")] if a.sweep else []
    if a.price is not None:
        prices = [a.price] + [p for p in prices if p != a.price]
    if not prices:
        sys.exit("give --price or --sweep")
    rows = [model(p, a.fixed, a.variable, a.fee_pct, a.fee_fixed, a.users, a.churn) for p in prices]
    if a.json:
        print(json.dumps(rows[0] if len(rows) == 1 or a.sweep is None else rows, indent=2))
        return 0
    print("price  fee    contribution  margin  break-even users" + ("  profit@%d" % a.users if a.users else ""))
    for r in rows:
        print("%-6g %-6.2f %-13.2f %-7s %-16s%s" % (
            r["price"], r["processor_fee"], r["contribution_per_user"],
            "%s%%" % r["gross_margin_pct"], r["break_even_users"] if r["break_even_users"] is not None else "never",
            ("  %.2f" % r["profit_at_users"]) if a.users else ""))
        if "warning" in r:
            print("       ! " + r["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
