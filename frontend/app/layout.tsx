import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Vacation Planner",
  description: "Agentic vacation planning with memory, guardrails, and trusted travel retrieval."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
