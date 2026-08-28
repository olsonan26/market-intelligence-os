"use client";

import { useEffect, useMemo, useRef, useState, type ComponentType } from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Bell,
  BookOpenCheck,
  BrainCircuit,
  ChevronRight,
  CircleCheck,
  CircleHelp,
  Clock3,
  Database,
  Eye,
  FileSearch,
  FlaskConical,
  Gauge,
  GitBranch,
  GraduationCap,
  Landmark,
  Layers3,
  LockKeyhole,
  Menu,
  Network,
  Newspaper,
  RotateCcw,
  Search,
  ServerCog,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  TriangleAlert,
  UserRound,
  WalletCards,
  X,
  Zap,
} from "lucide-react";
import { evidence, markets, news, opportunities, type Market, type SymbolKey } from "@/lib/market-data";

const MarketChart = dynamic(
  () => import("@/components/market-chart").then((module) => module.MarketChart),
  {
    ssr: false,
    loading: () => <div className="market-chart market-chart--loading" aria-label="Loading market chart" />,
  },
);

type ViewKey = "pulse" | "markets" | "time" | "research" | "decisions" | "risk" | "memory" | "system";

type NavItem = {
  key: ViewKey;
  label: string;
  description: string;
  icon: ComponentType<{ size?: number; strokeWidth?: number }>;
};

const nav: NavItem[] = [
  { key: "pulse", label: "Market Pulse", description: "Start here", icon: Gauge },
  { key: "markets", label: "Markets", description: "Prices and setups", icon: BarChart3 },
  { key: "time", label: "Time Machine", description: "What was knowable", icon: Clock3 },
  { key: "research", label: "Research Lab", description: "Models and evidence", icon: FlaskConical },
  { key: "decisions", label: "Decision Center", description: "Trade or wait", icon: Target },
  { key: "risk", label: "Risk & Execution", description: "Protect capital", icon: ShieldCheck },
  { key: "memory", label: "System Memory", description: "Lessons retained", icon: BrainCircuit },
  { key: "system", label: "System Health", description: "Sources and gates", icon: ServerCog },
];

const viewTitles: Record<ViewKey, { eyebrow: string; title: string; subtitle: string }> = {
  pulse: { eyebrow: "Command overview", title: "Market Pulse", subtitle: "The clearest answer first—then the evidence behind it." },
  markets: { eyebrow: "Multi-market radar", title: "Markets", subtitle: "Compare price, direction, risk, and opportunity without changing screens." },
  time: { eyebrow: "Point-in-time replay", title: "Time Machine", subtitle: "See only what the system could genuinely know at the selected moment." },
  research: { eyebrow: "Model arena", title: "Research Lab", subtitle: "Separate useful evidence from confident-looking noise." },
  decisions: { eyebrow: "Decision intelligence", title: "Decision Center", subtitle: "Understand why the safest action may be to wait." },
  risk: { eyebrow: "Capital protection", title: "Risk & Execution", subtitle: "Every proposed action must survive deterministic risk controls." },
  memory: { eyebrow: "Learning ledger", title: "System Memory", subtitle: "What worked, what failed, and what the system is forbidden to forget." },
  system: { eyebrow: "Operational truth", title: "System Health", subtitle: "Freshness, provider gaps, build gates, and authority boundaries." },
};

const timeEvents = [
  { at: "09:30", label: "U.S. session opens", detail: "Price and spread observations begin", state: "verified" },
  { at: "10:08", label: "Macro release received", detail: "Provider first-seen timestamp verified", state: "verified" },
  { at: "10:42", label: "News article updated", detail: "Version 2 supersedes—not erases—version 1", state: "updated" },
  { at: "11:16", label: "Sequence gap detected", detail: "Affected features degraded until reconciliation", state: "caution" },
  { at: "12:04", label: "Gap reconciled", detail: "Canonical state restored and hashed", state: "verified" },
];

function Info({ label }: { label: string }) {
  return (
    <span className="info-tip" tabIndex={0} aria-label={label} data-tip={label}>
      <CircleHelp size={14} aria-hidden="true" />
    </span>
  );
}

function Lineage({ id, onOpen }: { id: string; onOpen: () => void }) {
  return (
    <footer className="lineage">
      <GitBranch size={13} aria-hidden="true" />
      <span>Evidence attached</span>
      <button className="lineage__link" type="button" onClick={onOpen}>{id}</button>
    </footer>
  );
}

function MetricCard({
  label,
  value,
  delta,
  direction,
  meaning,
  lineage,
  onOpen,
}: {
  label: string;
  value: string;
  delta: string;
  direction: "up" | "down" | "flat";
  meaning: string;
  lineage: string;
  onOpen: () => void;
}) {
  return (
    <article className="card metric insight-card">
      <div className="metric-label-row">
        <span className="card__title">{label}</span>
        <Info label={meaning} />
      </div>
      <strong className="metric__value">{value}</strong>
      <span className="metric__delta" data-dir={direction}>{delta}</span>
      <p className="plain-meaning"><BookOpenCheck size={14} aria-hidden="true" />{meaning}</p>
      <Lineage id={lineage} onOpen={onOpen} />
    </article>
  );
}

function EvidenceDrawer({ market, onClose }: { market: Market; onClose: () => void }) {
  return (
    <div className="drawer-backdrop" onMouseDown={onClose}>
      <aside className="evidence-drawer" role="dialog" aria-modal="true" aria-labelledby="evidence-title" onMouseDown={(event) => event.stopPropagation()}>
        <div className="drawer-head">
          <div>
            <span className="eyebrow">Decision lineage</span>
            <h2 id="evidence-title">Why the system says “{market.decision}”</h2>
          </div>
          <button className="icon-btn" type="button" onClick={onClose} aria-label="Close evidence panel"><X size={18} /></button>
        </div>
        <div className="explain-box">
          <Sparkles size={18} aria-hidden="true" />
          <div><strong>Plain-English answer</strong><p>{market.summary}</p></div>
        </div>
        <ol className="evidence-list">
          {evidence.map((item, index) => (
            <li key={item.source}>
              <span className="evidence-index">{index + 1}</span>
              <div className="evidence-copy"><strong>{item.source}</strong><span>{item.detail}</span></div>
              <div className="evidence-score"><span>{item.signal}</span><b className="num">{item.weight}</b></div>
            </li>
          ))}
        </ol>
        <div className="decision-math">
          <div><span>Raw probability</span><strong className="num">74%</strong></div>
          <ChevronRight size={16} aria-hidden="true" />
          <div><span>After calibration</span><strong className="num">{market.confidence}%</strong></div>
          <ChevronRight size={16} aria-hidden="true" />
          <div><span>After costs + risk</span><strong className="num">+0.18R</strong></div>
        </div>
        <div className="provenance-block">
          <span className="caps">Independent evidence roots</span>
          <div className="trail">
            <span className="trail__node"><Database size={12} /><b>Price feed</b> v1842</span>
            <span className="trail__arrow">→</span>
            <span className="trail__node"><Network size={12} /><b>Feature set</b> f93d</span>
            <span className="trail__arrow">→</span>
            <span className="trail__node"><ShieldCheck size={12} /><b>Risk policy</b> r7.4</span>
          </div>
        </div>
        <div className="drawer-foot">
          <span className="mode" data-mode="fixture">Fixture evidence</span>
          <span className="hash hash--verified">8a29b2c6…dc6050e</span>
        </div>
      </aside>
    </div>
  );
}

function MarketSelector({ selected, onSelect }: { selected: SymbolKey; onSelect: (key: SymbolKey) => void }) {
  return (
    <div className="symbol-strip" aria-label="Market selector">
      {(Object.keys(markets) as SymbolKey[]).map((key) => {
        const item = markets[key];
        return (
          <button key={key} type="button" className="symbol-tab" data-active={selected === key} onClick={() => onSelect(key)} aria-pressed={selected === key}>
            <span><b>{item.symbol}</b><small>{item.market}</small></span>
            <span className="symbol-price"><b className="num">{item.price}</b><small data-dir={item.change >= 0 ? "up" : "down"}>{item.change >= 0 ? "+" : ""}{item.change}%</small></span>
          </button>
        );
      })}
    </div>
  );
}

function ChartWorkspace({ market, timeframe, setTimeframe, onEvidence }: { market: Market; timeframe: string; setTimeframe: (value: string) => void; onEvidence: () => void }) {
  return (
    <section className="card chart-card">
      <div className="chart-head">
        <div className="instrument-title">
          <span className="instrument-icon"><TrendingUp size={20} /></span>
          <div><span className="eyebrow">{market.market} · Fixture feed</span><h2>{market.symbol} <small>{market.name}</small></h2></div>
        </div>
        <div className="quote-block"><strong className="num">{market.price}</strong><span data-dir={market.change >= 0 ? "up" : "down"}>{market.change >= 0 ? "+" : ""}{market.change}% today</span></div>
      </div>
      <div className="chart-toolbar">
        <div className="segmented" aria-label="Chart timeframe">
          {["1H", "4H", "1D", "1W"].map((value) => <button type="button" key={value} aria-pressed={timeframe === value} onClick={() => setTimeframe(value)}>{value}</button>)}
        </div>
        <div className="chart-legend"><span><i data-candle="up" /> Price rose</span><span><i data-candle="down" /> Price fell</span><Info label="Each candle shows the opening, highest, lowest, and closing price for the selected period." /></div>
      </div>
      <MarketChart market={market} />
      <div className="chart-summary">
        <Sparkles size={17} aria-hidden="true" />
        <div><strong>What the chart is saying</strong><p>{market.summary}</p></div>
        <button type="button" className="btn btn--ghost" onClick={onEvidence}>Show evidence <ChevronRight size={15} /></button>
      </div>
    </section>
  );
}

function Overview({ market, selected, onSelect, timeframe, setTimeframe, onEvidence, guided }: {
  market: Market; selected: SymbolKey; onSelect: (key: SymbolKey) => void; timeframe: string; setTimeframe: (value: string) => void; onEvidence: () => void; guided: boolean;
}) {
  return (
    <div className="page-stack">
      <div className="safety-banner">
        <span className="safety-icon"><LockKeyhole size={16} /></span>
        <div><strong>Safe learning environment</strong><span>All values are clearly labeled fixture data. No real orders can be placed.</span></div>
        <span className="mode" data-mode="fixture">Fixture</span>
      </div>
      {guided && (
        <div className="guided-callout">
          <GraduationCap size={21} aria-hidden="true" />
          <div><strong>New here? Read the dashboard in this order.</strong><p>1. Start with the decision → 2. Check confidence → 3. Confirm reward versus risk → 4. Open the evidence.</p></div>
        </div>
      )}
      <MarketSelector selected={selected} onSelect={onSelect} />
      <div className="overview-grid">
        <ChartWorkspace market={market} timeframe={timeframe} setTimeframe={setTimeframe} onEvidence={onEvidence} />
        <aside className="decision-card card">
          <div className="decision-top"><span className="caps">System decision</span><span className="pill" data-state="pending">Wait</span></div>
          <div className="decision-orb" data-bias={market.bias}><span>Calibrated chance</span><strong className="num">{market.confidence}%</strong><small>{market.bias} scenario</small></div>
          <div className="decision-answer"><span>Safest action now</span><strong>{market.decision}</strong><p>{market.summary}</p></div>
          <div className="risk-reward">
            <div><span>Potential reward</span><strong className="num">+0.18R</strong><small>after estimated costs</small></div>
            <div><span>Risk if wrong</span><strong className="num">−1.00R</strong><small>before size reduction</small></div>
          </div>
          <button type="button" className="btn btn--primary decision-cta" onClick={onEvidence}>Explain this decision <FileSearch size={16} /></button>
          <p className="decision-note"><ShieldCheck size={14} /> The system can recommend “do nothing.” Capital preservation is a valid result.</p>
        </aside>
      </div>
      <section>
        <div className="section-head"><h2>Decision at a glance</h2><span className="muted">Every number opens to its evidence</span></div>
        <div className="grid metric-grid">
          <MetricCard label="Calibrated probability" value={`${market.confidence}%`} delta="+6% vs. random baseline" direction="up" meaning="How often similar forecasts were correct after correcting model overconfidence." lineage="CAL-2026-0827" onOpen={onEvidence} />
          <MetricCard label="Net expected value" value="+0.18R" delta="Positive, but below entry threshold" direction="flat" meaning="The average expected reward after spread, fees, slippage, and failure risk." lineage="EV-02841" onOpen={onEvidence} />
          <MetricCard label="Evidence quality" value="82/100" delta="3 independent evidence roots" direction="up" meaning="How complete, current, and independent the evidence is—not how confident the AI sounds." lineage="PRV-3ROOT" onOpen={onEvidence} />
          <MetricCard label="Data freshness" value="1.8s" delta="News source is delayed" direction="down" meaning="How long ago the slowest required source was received. Stale data can block a trade." lineage="FRESH-118" onOpen={onEvidence} />
        </div>
      </section>
      <div className="lower-grid">
        <section className="card opportunity-card">
          <div className="card-head"><div><span className="eyebrow">Ranked by risk-adjusted edge</span><h2>Opportunity radar</h2></div><button className="text-action" type="button">View all markets <ArrowUpRight size={14} /></button></div>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Market</th><th>Setup</th><th className="num">Probability</th><th className="num">Net EV</th><th>Risk</th><th>Action</th></tr></thead>
              <tbody>{opportunities.map((item) => <tr key={item.symbol}><td><strong>{item.symbol}</strong></td><td>{item.setup}</td><td className="num">{item.probability}</td><td className="num" data-positive={item.netEv.startsWith("+")}>{item.netEv}</td><td>{item.risk}</td><td><span className="pill" data-state={item.action === "No trade" ? "blocked" : item.action === "Watch" ? "pass" : "pending"}>{item.action}</span></td></tr>)}</tbody>
            </table>
          </div>
        </section>
        <section className="card news-card">
          <div className="card-head"><div><span className="eyebrow">Point-in-time news</span><h2>What changed</h2></div><span className="staleness">Updated 18s ago</span></div>
          <div className="news-list">{news.map((item) => <article key={`${item.time}-${item.source}`}><time>{item.time}</time><div><span>{item.source} · {item.impact}</span><strong>{item.headline}</strong></div><span className="pill" data-state={item.state === "verified" ? "pass" : "pending"}>{item.state}</span></article>)}</div>
        </section>
      </div>
    </div>
  );
}

function MarketsView({ market, selected, onSelect, timeframe, setTimeframe, onEvidence }: { market: Market; selected: SymbolKey; onSelect: (key: SymbolKey) => void; timeframe: string; setTimeframe: (v: string) => void; onEvidence: () => void }) {
  return <div className="page-stack"><MarketSelector selected={selected} onSelect={onSelect} /><ChartWorkspace market={market} timeframe={timeframe} setTimeframe={setTimeframe} onEvidence={onEvidence} /><div className="grid">{(Object.keys(markets) as SymbolKey[]).map((key) => { const item = markets[key]; return <article className="card market-snapshot" key={key}><div className="row-between"><span className="pill" data-state={item.bias === "bullish" ? "pass" : item.bias === "bearish" ? "fail" : "pending"}>{item.bias}</span><span className="muted">{item.market}</span></div><h3>{item.symbol}</h3><strong className="num">{item.price}</strong><p>{item.summary}</p><button className="text-action" type="button" onClick={() => onSelect(key)}>Open workspace <ChevronRight size={14} /></button></article>; })}</div></div>;
}

function TimeMachineView({ timeIndex, setTimeIndex }: { timeIndex: number; setTimeIndex: (value: number) => void }) {
  const visible = timeEvents.slice(0, timeIndex + 1);
  return <div className="page-stack"><div className="banner" data-kind="caution"><Clock3 size={18} /><div><strong>Historical truth is locked to the cutoff.</strong> Later article edits, macro revisions, prices, and fills are invisible until the clock reaches them.</div></div><section className="card time-console"><div className="row-between"><div><span className="eyebrow">Simulation clock</span><h2 className="time-readout">2026-08-27 · {timeEvents[timeIndex].at}:00 ET</h2></div><button type="button" className="btn btn--ghost" onClick={() => setTimeIndex(0)}><RotateCcw size={14} /> Reset</button></div><label className="time-slider-label" htmlFor="time-slider"><span>Move through the day</span><b>{Math.round((timeIndex / (timeEvents.length - 1)) * 100)}%</b></label><input id="time-slider" className="time-slider" type="range" min="0" max={timeEvents.length - 1} value={timeIndex} onChange={(event) => setTimeIndex(Number(event.target.value))} /><div className="timeline-labels"><span>Market open</span><span>Current cutoff</span><span>Session now</span></div></section><div className="time-grid"><section className="card"><div className="card-head"><div><span className="eyebrow">Visible now</span><h2>Evidence timeline</h2></div><span className="pill" data-state="pass">{visible.length} event{visible.length === 1 ? "" : "s"} allowed</span></div><ol className="event-timeline">{visible.map((event) => <li key={event.at}><time>{event.at}</time><span className="timeline-dot" data-state={event.state} /><div><strong>{event.label}</strong><p>{event.detail}</p></div><span className="hash">evt-{event.at.replace(":", "")}</span></li>)}</ol></section><section className="card blocked-future"><Eye size={24} /><span className="caps">Future-blind by design</span><strong>{timeEvents.length - visible.length} later event{timeEvents.length - visible.length === 1 ? "" : "s"} hidden</strong><p>This prevents the backtest from “knowing” a correction, data revision, or price that had not arrived yet.</p><div className="divider" /><span className="muted">Visibility policy</span><b className="mono">STRICT_INGESTED_AT</b></section></div></div>;
}

function ResearchView() {
  const agents = [{ name: "Price structure", vote: "Bullish", score: 76 }, { name: "Macro regime", vote: "Bullish", score: 67 }, { name: "News events", vote: "Neutral", score: 52 }, { name: "Positioning", vote: "Caution", score: 44 }];
  return <div className="page-stack"><div className="research-grid"><section className="card"><div className="card-head"><div><span className="eyebrow">Independent reasoning paths</span><h2>Agent evidence map</h2></div><span className="pill" data-state="observe">4 active</span></div><div className="agent-list">{agents.map((agent) => <article key={agent.name}><span className="agent-icon"><BrainCircuit size={16} /></span><div><strong>{agent.name}</strong><span>{agent.vote}</span></div><b className="num">{agent.score}</b><span className="score-track"><i style={{ width: `${agent.score}%` }} /></span></article>)}</div><div className="explain-box"><Network size={18} /><div><strong>Four votes do not always mean four sources.</strong><p>Correlated evidence is traced to its root so repeated reporting cannot fake consensus.</p></div></div></section><section className="card champion-card"><span className="eyebrow">Champion / challenger</span><h2>Model arena</h2><div className="model-match"><div><span className="pill" data-state="pass">Champion</span><strong>Gradient Baseline v4.8</strong><p>Stable calibration across 1,248 walk-forward windows.</p><b className="num">Brier 0.184</b></div><span className="versus">VS</span><div><span className="pill" data-state="blocked">Rejected</span><strong>Deep Sequence v2.1</strong><p>Higher returns, but failed the leakage sentinel.</p><b className="num">LEAK-003</b></div></div><p className="decision-note"><ShieldCheck size={14} /> A more exciting model never replaces a safer one without passing every promotion gate.</p></section></div><section className="card"><div className="card-head"><div><span className="eyebrow">Reproducible inputs</span><h2>Feature lineage</h2></div><span className="hash hash--verified">f93d81…a2c4</span></div><div className="lineage-flow"><span><Database size={17} /><b>Raw events</b><small>184 records</small></span><ChevronRight /><span><Clock3 size={17} /><b>Time cutoff</b><small>12:04 ET</small></span><ChevronRight /><span><Layers3 size={17} /><b>Feature set</b><small>37 features</small></span><ChevronRight /><span><BrainCircuit size={17} /><b>Champion</b><small>v4.8</small></span><ChevronRight /><span><ShieldCheck size={17} /><b>Risk gate</b><small>WAIT</small></span></div></section></div>;
}

function DecisionsView({ market, onEvidence }: { market: Market; onEvidence: () => void }) {
  const steps = [{ icon: Database, title: "Evidence", result: "Complete", note: "3 independent roots" }, { icon: BrainCircuit, title: "Probability", result: `${market.confidence}%`, note: "Calibrated, not raw" }, { icon: WalletCards, title: "Net reward", result: "+0.18R", note: "Below +0.25R threshold" }, { icon: ShieldCheck, title: "Final action", result: "WAIT", note: "Risk policy R7.4" }];
  return <div className="page-stack"><section className="decision-hero card"><div><span className="eyebrow">Current decision · {market.symbol}</span><h2>{market.decision}</h2><p>{market.summary}</p><button className="btn btn--primary" type="button" onClick={onEvidence}>Open complete evidence <FileSearch size={16} /></button></div><div className="decision-gauge"><span>Threshold to act</span><div className="gauge-track"><i style={{ width: `${market.confidence}%` }} /><b style={{ left: "72%" }} /></div><div className="row-between"><strong className="num">Current {market.confidence}%</strong><strong className="num">Required 72%</strong></div><p>The evidence is close, but “close” is not permission to risk capital.</p></div></section><div className="decision-steps">{steps.map((step, index) => { const StepIcon = step.icon; return <article className="card" key={step.title}><span className="step-number">{index + 1}</span><StepIcon size={20} /><span>{step.title}</span><strong>{step.result}</strong><small>{step.note}</small></article>; })}</div></div>;
}

function RiskView() {
  return <div className="page-stack"><div className="banner" data-kind="verified"><ShieldCheck size={18} /><div><strong>All protection systems are active.</strong> This environment can model paper decisions but has no live-capital authority.</div></div><div className="risk-grid"><section className="card risk-score"><span className="eyebrow">Portfolio risk used</span><strong className="num">18%</strong><div className="risk-meter"><i style={{ width: "18%" }} /></div><p>Low utilization leaves room for future opportunities without concentrating exposure.</p></section><section className="card"><div className="card-head"><div><span className="eyebrow">Deterministic limits</span><h2>Guardrails</h2></div><span className="pill" data-state="pass">Enforced</span></div><div className="guardrail-list">{[["Risk per decision", "0.50%", "≤ 1.00%"], ["Daily loss ceiling", "0.80%", "≤ 2.00%"], ["Correlated exposure", "22%", "≤ 35%"], ["Stale-source tolerance", "1.8s", "≤ 3.0s"]].map(([name, current, limit]) => <div key={name}><span>{name}</span><strong className="num">{current}</strong><small>{limit}</small><CircleCheck size={15} /></div>)}</div></section><section className="killswitch"><TriangleAlert size={22} /><div><strong className="killswitch__title">Emergency stop</strong><p className="killswitch__note">Available only to a risk officer. This demo shows the control but cannot submit or cancel real orders.</p></div><div className="gated" data-role-ok="false" data-required-role="risk officer"><button type="button" className="btn btn--danger" disabled>Activate kill switch</button></div></section></div><section className="card"><div className="card-head"><div><span className="eyebrow">Paper-only lifecycle</span><h2>Execution ledger</h2></div><span className="mode" data-mode="paper">Paper</span></div><div className="execution-flow"><span data-state="pass"><CircleCheck />Intent created<small>12:03:10.081</small></span><ChevronRight /><span data-state="pass"><CircleCheck />Risk accepted<small>12:03:10.094</small></span><ChevronRight /><span data-state="pass"><CircleCheck />Partial fill<small>12:03:10.322</small></span><ChevronRight /><span data-state="pass"><CircleCheck />Reconciled<small>12:03:11.008</small></span></div></section></div>;
}

function MemoryView() {
  return <div className="page-stack"><div className="grid">{[{ title: "Failure memory", value: "127", note: "Known failure patterns retained", icon: TriangleAlert, state: "caution" }, { title: "Regime memory", value: "18", note: "Distinct market environments", icon: Activity, state: "pass" }, { title: "Source reputation", value: "42", note: "Providers with scored reliability", icon: Database, state: "observe" }, { title: "Calibration memory", value: "1,248", note: "Walk-forward evaluation windows", icon: Target, state: "pass" }].map((item) => <article className="card memory-card" key={item.title}><span className="memory-icon"><item.icon size={20} /></span><span className="pill" data-state={item.state}>{item.title}</span><strong className="num">{item.value}</strong><p>{item.note}</p></article>)}</div><section className="card"><div className="card-head"><div><span className="eyebrow">Lessons retained</span><h2>Recent system learning</h2></div><span className="muted">Append-only</span></div><div className="lesson-list">{[["EUR/USD false breakout", "A news revision arrived 42 seconds after the first signal. Future versions require a longer confirmation window.", "Failure"], ["Gold trend continuation", "Macro and price evidence remained independently supportive across three regimes.", "Validated"], ["BTC weekend liquidity", "Predicted fill quality diverged from simulated fills during thin liquidity.", "Caution"]].map(([title, body, state]) => <article key={title}><span className="lesson-state" data-state={state.toLowerCase()}>{state}</span><div><strong>{title}</strong><p>{body}</p></div><span className="hash">mem-{title.slice(0, 3).toLowerCase()}24</span></article>)}</div></section></div>;
}

function SystemView() {
  const phases = ["Foundation", "Market data", "Time Machine", "Simulation", "Research", "News + macro", "Memory", "Risk", "Paper execution", "Shadow mode", "Operator console", "Hardening"];
  return <div className="page-stack"><div className="health-grid"><section className="card"><div className="card-head"><div><span className="eyebrow">Provider freshness</span><h2>Source health</h2></div><span className="staleness">System observed</span></div><div className="source-health">{[["Market data", "1.2s", "Healthy"], ["Macro releases", "18s", "Healthy"], ["News stream", "46s", "Degraded"], ["Filings", "2m", "Healthy"]].map(([source, age, state]) => <div key={source}><span className="source-dot" data-state={state.toLowerCase()} /><strong>{source}</strong><span className="num">{age}</span><span className="pill" data-state={state === "Healthy" ? "pass" : "pending"}>{state}</span></div>)}</div></section><section className="card authority-card"><LockKeyhole size={25} /><span className="eyebrow">Authority boundary</span><h2>Live trading is structurally disabled</h2><p>No setting, environment variable, or frontend action can enable a live-capital route.</p><span className="hash hash--verified">LIVE-000 PASS</span></section></div><section className="card"><div className="card-head"><div><span className="eyebrow">Build truth</span><h2>Phase ladder</h2></div><span className="pill" data-state="pending">Fixture verified</span></div><div className="phase-grid ladder">{phases.map((phase, index) => <article className="phase" data-gate={index === 10 ? "pending" : "pass"} key={phase}><span className="phase__idx" /><span className="phase__name">{phase}<small>{index === 10 ? "Console repaired · production verification in progress" : "Acceptance evidence stored"}</small></span><span className="pill" data-state={index === 10 ? "pending" : "pass"}>{index === 10 ? "Testing" : "Pass"}</span></article>)}</div></section></div>;
}

export function OperatorConsole() {
  const [view, setView] = useState<ViewKey>("pulse");
  const [selected, setSelected] = useState<SymbolKey>("EURUSD");
  const [timeframe, setTimeframe] = useState("1D");
  const [guided, setGuided] = useState(true);
  const [mobileNav, setMobileNav] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [timeIndex, setTimeIndex] = useState(3);
  const [search, setSearch] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const market = markets[selected];
  const header = viewTitles[view];
  const normalizedSearch = search.trim().toLowerCase();
  const marketMatches = useMemo(() => normalizedSearch ? (Object.keys(markets) as SymbolKey[]).filter((key) => `${markets[key].symbol} ${markets[key].name} ${markets[key].market}`.toLowerCase().includes(normalizedSearch)) : [], [normalizedSearch]);
  const featureMatches = useMemo(() => normalizedSearch ? nav.filter((item) => `${item.label} ${item.description} ${viewTitles[item.key].subtitle}`.toLowerCase().includes(normalizedSearch)) : [], [normalizedSearch]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
      }
      if (event.key === "Escape") { setDrawerOpen(false); setMobileNav(false); setSearch(""); }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const chooseView = (key: ViewKey) => { setView(key); setMobileNav(false); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const chooseMarket = (key: SymbolKey) => { setSelected(key); setSearch(""); };
  const onEvidence = () => setDrawerOpen(true);

  return (
    <div className="console-shell">
      <aside className="console-rail" data-open={mobileNav}>
        <div className="rail-brand">
          <span className="brand__mark brand__mark--fox" aria-hidden="true">
            <Image src="/brand/fox-trading-mark.png" alt="" width={48} height={48} priority sizes="48px" />
          </span>
          <div className="brand__lockup">
            <strong><span>FOX</span> TRADING</strong>
            <small>Market Intelligence</small>
          </div>
          <button type="button" className="mobile-close" onClick={() => setMobileNav(false)} aria-label="Close navigation"><X size={18} /></button>
        </div>
        <div className="mode-panel"><div><span className="mode" data-mode="fixture">Fixture</span><strong>Learning-safe mode</strong></div><p>Real money cannot be traded from this build.</p></div>
        <nav className="console-nav" aria-label="Main navigation">
          <span className="nav__label">Intelligence workspace</span>
          {nav.map((item) => <button key={item.key} type="button" className="console-nav__item" aria-current={view === item.key ? "page" : undefined} onClick={() => chooseView(item.key)}><item.icon size={17} strokeWidth={1.8} /><span><strong>{item.label}</strong><small>{item.description}</small></span>{view === item.key && <ChevronRight size={14} className="nav-chevron" />}</button>)}
        </nav>
        <div className="rail-status mt-auto"><div className="row-between"><span className="staleness">System healthy</span><span className="num">99.98%</span></div><div className="status-bars" aria-label="System health 99.98 percent"><i /><i /><i /><i /><i data-warn /></div><span>1 source delayed · safety gate active</span></div>
        <div className="operator-card"><span className="operator-avatar"><UserRound size={17} /></span><div><strong>Alex Olson</strong><span>Operator · Viewer access</span></div><button className="icon-btn" type="button" aria-label="Open account menu"><ChevronRight size={15} /></button></div>
      </aside>
      {mobileNav && <button className="mobile-scrim" type="button" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
      <main className="console-main">
        <header className="console-topbar">
          <button type="button" className="mobile-menu" onClick={() => setMobileNav(true)} aria-label="Open navigation"><Menu size={20} /></button>
          <div className="global-search">
            <Search size={16} aria-hidden="true" />
            <input ref={searchInputRef} value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search a market or feature…" aria-label="Search markets and features" autoComplete="off" />
            <kbd>⌘ K</kbd>
            {normalizedSearch && <div className="search-results" role="listbox" aria-label="Search results">
              {marketMatches.map((key) => <button type="button" key={key} role="option" aria-selected="false" onClick={() => { chooseMarket(key); chooseView("markets"); }}><span><strong>{markets[key].symbol}</strong><small>{markets[key].name} · {markets[key].market}</small></span><ChevronRight size={14} /></button>)}
              {featureMatches.map((item) => <button type="button" key={item.key} role="option" aria-selected="false" onClick={() => { setSearch(""); chooseView(item.key); }}><span><strong>{item.label}</strong><small>{item.description}</small></span><ChevronRight size={14} /></button>)}
              {marketMatches.length === 0 && featureMatches.length === 0 && <p className="search-empty">No matching market or feature</p>}
            </div>}
          </div>
          <label className="guided-toggle"><GraduationCap size={16} /><span>Guided mode</span><input type="checkbox" checked={guided} onChange={(event) => setGuided(event.target.checked)} /><i /></label>
          <button type="button" className="icon-btn notification" aria-label="Notifications"><Bell size={18} /><span /></button>
        </header>
        <div className="console-content">
          <div className="page-header">
            <div><span className="eyebrow">{header.eyebrow}</span><h1>{header.title}</h1><p>{header.subtitle}</p></div>
            <div className="as-of"><span>As of</span><strong className="num">Aug 27, 2026 · 12:24 UTC</strong><span className="pill" data-state="pass">Point-in-time clean</span></div>
          </div>
          {view === "pulse" && <Overview market={market} selected={selected} onSelect={chooseMarket} timeframe={timeframe} setTimeframe={setTimeframe} onEvidence={onEvidence} guided={guided} />}
          {view === "markets" && <MarketsView market={market} selected={selected} onSelect={chooseMarket} timeframe={timeframe} setTimeframe={setTimeframe} onEvidence={onEvidence} />}
          {view === "time" && <TimeMachineView timeIndex={timeIndex} setTimeIndex={setTimeIndex} />}
          {view === "research" && <ResearchView />}
          {view === "decisions" && <DecisionsView market={market} onEvidence={onEvidence} />}
          {view === "risk" && <RiskView />}
          {view === "memory" && <MemoryView />}
          {view === "system" && <SystemView />}
        </div>
      </main>
      {drawerOpen && <EvidenceDrawer market={market} onClose={() => setDrawerOpen(false)} />}
    </div>
  );
}
