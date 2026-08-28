"use client";

import { useEffect, useRef } from "react";
import { CandlestickSeries, ColorType, createChart, type CandlestickData, type Time } from "lightweight-charts";
import type { Market } from "@/lib/market-data";

export function MarketChart({ market }: { market: Market }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      autoSize: true,
      height: 390,
      layout: {
        // lightweight-charts parses these values itself and does not support
        // OKLCH yet. Keep its canvas palette in sRGB while the surrounding UI
        // continues to use the OKLCH design-token system.
        background: { type: ColorType.Solid, color: "#171b23" },
        textColor: "#a7afbd",
        attributionLogo: false,
      },
      grid: {
        vertLines: { color: "rgba(70, 78, 93, 0.34)" },
        horzLines: { color: "rgba(70, 78, 93, 0.34)" },
      },
      rightPriceScale: { borderColor: "#464e5d" },
      timeScale: {
        borderColor: "#464e5d",
        timeVisible: true,
        rightOffset: 2,
        barSpacing: 19,
      },
      crosshair: {
        vertLine: { color: "rgba(56, 189, 248, 0.5)", labelBackgroundColor: "#0879a8" },
        horzLine: { color: "rgba(56, 189, 248, 0.5)", labelBackgroundColor: "#0879a8" },
      },
      handleScroll: true,
      handleScale: true,
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#42d39d",
      downColor: "#f05a67",
      wickUpColor: "#42d39d",
      wickDownColor: "#f05a67",
      borderVisible: false,
      priceLineColor: "#38bdf8",
    });

    series.setData(market.candles.map((item) => ({ ...item, time: item.time as Time })) as CandlestickData<Time>[]);
    chart.timeScale().fitContent();

    return () => chart.remove();
  }, [market]);

  return <div ref={containerRef} className="market-chart" aria-label={`${market.symbol} candlestick chart`} />;
}
