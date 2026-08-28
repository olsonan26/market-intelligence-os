export type SymbolKey = "EURUSD" | "BTCUSD" | "XAUUSD" | "SPX";

export type Candle = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
};

export type Market = {
  key: SymbolKey;
  symbol: string;
  name: string;
  market: string;
  price: string;
  change: number;
  spread: string;
  bias: "bullish" | "bearish" | "neutral";
  confidence: number;
  decision: string;
  summary: string;
  candles: Candle[];
};

const candle = (time: string, open: number, high: number, low: number, close: number): Candle => ({
  time,
  open,
  high,
  low,
  close,
});

export const markets: Record<SymbolKey, Market> = {
  EURUSD: {
    key: "EURUSD",
    symbol: "EUR/USD",
    name: "Euro / U.S. Dollar",
    market: "Forex",
    price: "1.16942",
    change: 0.31,
    spread: "0.7 pip",
    bias: "bullish",
    confidence: 68,
    decision: "WAIT FOR CONFIRMATION",
    summary: "Buyers have the advantage, but the expected reward does not yet justify the risk.",
    candles: [
      candle("2026-08-05", 1.1532, 1.1584, 1.1501, 1.1568),
      candle("2026-08-06", 1.1568, 1.1602, 1.1539, 1.1587),
      candle("2026-08-07", 1.1587, 1.1611, 1.1543, 1.1558),
      candle("2026-08-08", 1.1558, 1.1597, 1.1528, 1.1589),
      candle("2026-08-11", 1.1589, 1.1642, 1.1575, 1.1628),
      candle("2026-08-12", 1.1628, 1.1654, 1.1594, 1.1607),
      candle("2026-08-13", 1.1607, 1.1668, 1.1591, 1.1652),
      candle("2026-08-14", 1.1652, 1.1681, 1.1622, 1.1669),
      candle("2026-08-15", 1.1669, 1.1704, 1.1644, 1.1688),
      candle("2026-08-18", 1.1688, 1.1726, 1.1667, 1.1715),
      candle("2026-08-19", 1.1715, 1.1731, 1.1679, 1.1691),
      candle("2026-08-20", 1.1691, 1.1718, 1.1657, 1.1672),
      candle("2026-08-21", 1.1672, 1.1709, 1.1654, 1.1698),
      candle("2026-08-22", 1.1698, 1.1742, 1.1684, 1.1729),
      candle("2026-08-25", 1.1729, 1.1761, 1.1693, 1.1704),
      candle("2026-08-26", 1.1704, 1.1736, 1.1678, 1.1681),
      candle("2026-08-27", 1.1681, 1.1712, 1.1665, 1.16942),
    ],
  },
  BTCUSD: {
    key: "BTCUSD",
    symbol: "BTC/USD",
    name: "Bitcoin / U.S. Dollar",
    market: "Crypto",
    price: "112,842.30",
    change: -1.24,
    spread: "$6.20",
    bias: "neutral",
    confidence: 54,
    decision: "NO TRADE",
    summary: "Price is volatile and the evidence conflicts. Preserving capital is the strongest decision.",
    candles: [
      candle("2026-08-05", 113200, 116400, 111800, 115300),
      candle("2026-08-06", 115300, 117800, 113900, 116200),
      candle("2026-08-07", 116200, 116900, 111100, 112400),
      candle("2026-08-08", 112400, 115700, 110800, 114900),
      candle("2026-08-11", 114900, 118600, 114200, 117900),
      candle("2026-08-12", 117900, 119100, 115300, 116100),
      candle("2026-08-13", 116100, 117200, 112900, 114400),
      candle("2026-08-14", 114400, 116600, 111700, 115900),
      candle("2026-08-15", 115900, 118000, 114800, 117300),
      candle("2026-08-18", 117300, 118200, 113800, 114500),
      candle("2026-08-19", 114500, 116300, 111900, 112700),
      candle("2026-08-20", 112700, 114800, 110600, 113900),
      candle("2026-08-21", 113900, 115100, 111400, 112600),
      candle("2026-08-22", 112600, 114900, 111800, 114100),
      candle("2026-08-25", 114100, 115700, 112500, 113200),
      candle("2026-08-26", 113200, 114000, 111300, 112100),
      candle("2026-08-27", 112100, 114200, 111600, 112842.3),
    ],
  },
  XAUUSD: {
    key: "XAUUSD",
    symbol: "XAU/USD",
    name: "Gold / U.S. Dollar",
    market: "Metals",
    price: "3,419.72",
    change: 0.67,
    spread: "$0.28",
    bias: "bullish",
    confidence: 73,
    decision: "WATCH BUY ZONE",
    summary: "Gold is trending higher with supportive macro evidence, but entry price still matters.",
    candles: [
      candle("2026-08-05", 3338, 3354, 3321, 3348), candle("2026-08-06", 3348, 3370, 3341, 3364),
      candle("2026-08-07", 3364, 3377, 3346, 3351), candle("2026-08-08", 3351, 3379, 3348, 3372),
      candle("2026-08-11", 3372, 3391, 3364, 3387), candle("2026-08-12", 3387, 3396, 3371, 3378),
      candle("2026-08-13", 3378, 3402, 3374, 3398), candle("2026-08-14", 3398, 3410, 3389, 3406),
      candle("2026-08-15", 3406, 3418, 3394, 3401), candle("2026-08-18", 3401, 3427, 3397, 3422),
      candle("2026-08-19", 3422, 3431, 3406, 3412), candle("2026-08-20", 3412, 3425, 3398, 3404),
      candle("2026-08-21", 3404, 3421, 3399, 3417), candle("2026-08-22", 3417, 3438, 3411, 3432),
      candle("2026-08-25", 3432, 3441, 3414, 3420), candle("2026-08-26", 3420, 3428, 3401, 3408),
      candle("2026-08-27", 3408, 3424, 3405, 3419.72),
    ],
  },
  SPX: {
    key: "SPX",
    symbol: "S&P 500",
    name: "U.S. Large-Cap Index",
    market: "Index",
    price: "6,512.84",
    change: 0.18,
    spread: "0.4 pt",
    bias: "neutral",
    confidence: 61,
    decision: "HOLD / OBSERVE",
    summary: "The broader trend is positive, but crowded positioning and event risk reduce the edge.",
    candles: [
      candle("2026-08-05", 6378, 6402, 6359, 6394), candle("2026-08-06", 6394, 6427, 6388, 6418),
      candle("2026-08-07", 6418, 6432, 6384, 6398), candle("2026-08-08", 6398, 6441, 6392, 6436),
      candle("2026-08-11", 6436, 6462, 6429, 6454), candle("2026-08-12", 6454, 6470, 6438, 6447),
      candle("2026-08-13", 6447, 6488, 6441, 6480), candle("2026-08-14", 6480, 6502, 6471, 6494),
      candle("2026-08-15", 6494, 6510, 6479, 6487), candle("2026-08-18", 6487, 6522, 6483, 6516),
      candle("2026-08-19", 6516, 6531, 6498, 6504), candle("2026-08-20", 6504, 6518, 6477, 6489),
      candle("2026-08-21", 6489, 6514, 6480, 6507), candle("2026-08-22", 6507, 6539, 6501, 6531),
      candle("2026-08-25", 6531, 6542, 6508, 6517), candle("2026-08-26", 6517, 6526, 6496, 6503),
      candle("2026-08-27", 6503, 6521, 6498, 6512.84),
    ],
  },
};

export const evidence = [
  { source: "Price structure", signal: "Bullish", detail: "Higher lows remain intact", weight: 82 },
  { source: "Macro regime", signal: "Supportive", detail: "Rate expectations favor EUR", weight: 66 },
  { source: "Positioning", signal: "Caution", detail: "Long exposure is becoming crowded", weight: 48 },
  { source: "News context", signal: "Mixed", detail: "One source is delayed", weight: 41 },
];

export const opportunities = [
  { symbol: "XAU/USD", setup: "Trend continuation", probability: "73%", netEv: "+0.42R", risk: "Moderate", action: "Watch" },
  { symbol: "EUR/USD", setup: "Pullback reversal", probability: "68%", netEv: "+0.18R", risk: "Low", action: "Wait" },
  { symbol: "S&P 500", setup: "Breakout retest", probability: "61%", netEv: "+0.06R", risk: "Elevated", action: "Observe" },
  { symbol: "BTC/USD", setup: "Range breakout", probability: "54%", netEv: "-0.11R", risk: "High", action: "No trade" },
];

export const news = [
  { time: "12:18", source: "Federal Reserve", headline: "Policy speakers reinforce a data-dependent path", impact: "USD", state: "verified" },
  { time: "11:46", source: "ECB", headline: "Inflation expectations remain anchored near target", impact: "EUR", state: "verified" },
  { time: "10:32", source: "Benzinga", headline: "Markets reassess the timing of the next rate move", impact: "Macro", state: "updated" },
  { time: "09:15", source: "CFTC", headline: "Speculative EUR longs expand for a third week", impact: "Positioning", state: "verified" },
];
