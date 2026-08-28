import type { Metadata } from "next";
import "../web/styles/mios.css";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "FOX TRADING",
    template: "%s | FOX TRADING",
  },
  description: "FOX TRADING is a point-in-time market intelligence, evidence, and risk-control platform.",
  applicationName: "FOX TRADING",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-theme="dark">
      <body>{children}</body>
    </html>
  );
}
