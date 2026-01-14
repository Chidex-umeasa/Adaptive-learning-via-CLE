import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Adaptive Load Tutor",
  description: "Adaptive learning via cognitive load estimation"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
