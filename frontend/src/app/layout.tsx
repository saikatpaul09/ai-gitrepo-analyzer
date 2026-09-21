import type { Metadata } from "next";

import Providers from "./providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Engineering Analyzer",
  description:
    "AI-powered GitHub repository architecture and engineering analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}