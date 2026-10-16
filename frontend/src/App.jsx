import { useEffect, useRef, useState } from "react";

const POLL_MS = 1500;
const inr = (v) =>
  "₹" + Number(v).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function App() {
  const [data, setData] = useState(null);
  const [online, setOnline] = useState(false);
  const [flash, setFlash] = useState(false);
  const prevPeak = useRef("0.00");
  const consoleRef = useRef(null);

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const res = await fetch("/api/state");
        const json = await res.json();
        if (!alive) return;
        setOnline(true);
        if (Number(json.peak) > Number(prevPeak.current)) {
          setFlash(true);
          setTimeout(() => setFlash(false), 1200);
        }
        prevPeak.current = json.peak;
        setData(json);
      } catch {
        if (alive) setOnline(false);
      }
    };
    poll();
    const id = setInterval(poll, POLL_MS);
    return () => { alive = false; clearInterval(id); };
  }, []);

  useEffect(() => {
    if (consoleRef.current) consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
  }, [data?.logs.length]);

  const reset = () => fetch("/api/reset", { method: "POST" });

  return (
    <div className="app">
      <header className="header">
        <h1>NEXUSCART AI // CORE HUB</h1>
        <div className="status">
          <span className={`dot ${online ? "on" : "off"}`} />
          {online ? "MCP BACKEND LINK ACTIVE" : "BACKEND OFFLINE"}
          <span className="counter">{data ? data.inventory.length : 0} ITEM TYPES TRACKED</span>
        </div>
      </header>

      <section className="grid">
        <div className={`card peak ${flash ? "flash" : ""}`}>
          <h2>🏆 MAX TRANSACTION PEAK (KING-OF-THE-HILL ANALYSIS)</h2>
          <div className="big">{inr(data?.peak ?? 0)}</div>
          <p className="sub">{data?.peak_item ? `Set by: ${data.peak_item}` : "No sales yet"}</p>
          <p className="sub">
            Running balance: <b>{inr(data?.running_balance ?? 0)}</b> · GST collected:{" "}
            <b>{inr(data?.gst_collected ?? 0)}</b>
          </p>
        </div>

        <div className="card">
          <h2>📦 INVENTORY LEDGER</h2>
          <table>
            <thead>
              <tr><th>Item Name</th><th>Base Price</th><th>Units Left</th></tr>
            </thead>
            <tbody>
              {data?.inventory.map((i) => (
                <tr key={i.id} className={i.stock === 0 ? "out" : ""}>
                  <td>{i.name}</td>
                  <td>{inr(i.price)}</td>
                  <td>{i.stock === 0 ? <span className="badge">OUT OF STOCK</span> : i.stock}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h2>🤖 LIVE MCP AGENT CONSOLE <button className="reset" onClick={reset}>reset demo</button></h2>
        <pre className="terminal" ref={consoleRef}>
          {(data?.logs ?? ["[SYSTEM]: Connecting to backend..."]).map((l, i) => (
            <div key={i} className={l.startsWith("[ERROR]") ? "err" : ""}>{l}</div>
          ))}
        </pre>
      </section>
    </div>
  );
}