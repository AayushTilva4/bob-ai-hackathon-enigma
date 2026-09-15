import type { Metadata } from "next";
import "../styles/globals.css";
import AppShell from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "HarborAI — Intelligent Port Operations Optimizer",
  description: "Intelligent Port Operations Optimizer for container congestion prediction and berth allocation. IBM BoB AI Innovation Hackathon 2026.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
