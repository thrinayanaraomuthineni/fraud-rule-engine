import { useState } from "react";
import Console from "./pages/Console";

export default function App() {
  const [showNew, setShowNew] = useState(false);
  return (
    <>
      <header className="top">
        <div className="brand">Tripwire <small>Transaction review console</small></div>
        <button className="btn light" onClick={() => setShowNew(true)}>New transaction</button>
      </header>
      <Console showNew={showNew} onCloseNew={() => setShowNew(false)} />
    </>
  );
}
