from mcp.server.fastmcp import FastMCP
from . import store

mcp = FastMCP("NexusCart", streamable_http_path="/")


@mcp.tool()
def list_inventory() -> list[dict]:
    """List every product with its base price (INR, before GST) and remaining stock."""
    return store.snapshot()["inventory"]


@mcp.tool()
def process_checkout(item: str, quantity: int = 1) -> dict:
    """Buy `quantity` units of `item` (e.g. 'laptop'). Deducts stock, adds 18% GST,
    updates the running balance and the peak-sale record, and returns the final bill."""
    return store.checkout(item, quantity)


@mcp.tool()
def get_peak_sale() -> dict:
    """Return the highest single transaction so far (King-of-the-Hill) and which item set it."""
    s = store.snapshot()
    return {"peak": s["peak"], "item": s["peak_item"]}


@mcp.tool()
def get_running_balance() -> dict:
    """Return total revenue collected so far including GST, and the GST portion alone."""
    s = store.snapshot()
    return {"running_balance": s["running_balance"], "gst_collected": s["gst_collected"]}