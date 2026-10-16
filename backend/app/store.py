from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from threading import Lock

GST_RATE = Decimal("0.18")
PAISE = Decimal("0.01")
_lock = Lock()

inventory = {
    "laptop": {"name":"Laptop", "price": Decimal("84700.00"), "stock": 5},
    "phone": {"name": "Phone", "price": Decimal("29999.00"), "stock": 10},
    "headphones": {"name": "Headphones", "price": Decimal("2499.00"), "stock": 3},
    "keyboard": {"name": "Keyboard", "price": Decimal("1999.00"), "stock": 0},
}

state = {
    "peak": Decimal("0.00"),
    "peak_item": None,
    "running_balance": Decimal("0.00"),
    "gst_collected": Decimal("0.00"),
    "last_update": None,
}

logs: list[str] = ["[SYSTEM] : Awaiting incoming agent execution requests.."]

def _log(tag: str, msg: str) -> None:
    logs.append(f"[{tag}] : {msg}")
    del logs[:-100]

def _money(x: Decimal) -> Decimal:
    return x.quantize(PAISE, rounding=ROUND_HALF_UP)


def checkout(item: str, quantity: int) -> dict:
    key = item.strip().lower()
    with _lock:
        _log("MCP_HOST", f'Invoking process_checkout(item="{key}", quantity={quantity})')
        if quantity < 1:
            _log("ERROR", "Quantity must be at least 1.")
            return {"ok": False, "error": "Quantity must be at least 1."}
        if key not in inventory:
            _log("ERROR", f"Unknown item '{key}'.")
            return {"ok": False, "error": f"Unknown item '{key}'."}
        entry = inventory[key]
        if entry["stock"] < quantity:
            _log("ERROR", f"Insufficient stock for {key}: {entry['stock']} left.")
            return {"ok": False, "error": f"Only {entry['stock']} unit(s) of {key} left."}

        base = _money(entry["price"] * quantity)
        gst = _money(base * GST_RATE)
        total = base + gst

        entry["stock"] -= quantity
        state["running_balance"] += total
        state["gst_collected"] += gst
        new_peak = total > state["peak"]
        if new_peak:
            state["peak"], state["peak_item"] = total, entry["name"]
        state["last_update"] = datetime.now().isoformat(timespec="seconds")

        _log("SUCCESS", f"Deducted stock. Applied 18% GST. Final bill ₹{total:,.2f} committed.")
        if new_peak:
            _log("PEAK", f"New King-of-the-Hill record: ₹{total:,.2f}")
        _log("SYSTEM", "React state refreshing...")
        return {"ok": True, "item": entry["name"], "quantity": quantity,
                "base": str(base), "gst": str(gst), "total": str(total), "new_peak": new_peak}


def snapshot() -> dict:
    with _lock:
        return {
            "peak": str(state["peak"]),
            "peak_item": state["peak_item"],
            "running_balance": str(state["running_balance"]),
            "gst_collected": str(state["gst_collected"]),
            "last_update": state["last_update"],
            "inventory": [
                {"id": k, "name": v["name"], "price": str(v["price"]), "stock": v["stock"]}
                for k, v in inventory.items()
            ],
            "logs": list(logs),
        }


def reset() -> None:
    with _lock:
        for k, stock in {"laptop": 5, "phone": 10, "headphones": 3, "keyboard": 0}.items():
            inventory[k]["stock"] = stock
        state.update(peak=Decimal("0.00"), peak_item=None,
                     running_balance=Decimal("0.00"), gst_collected=Decimal("0.00"),
                     last_update=None)
        logs[:] = ["[SYSTEM]: State reset. Awaiting incoming agent execution requests..."]