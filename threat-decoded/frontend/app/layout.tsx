import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Threat Decoded | TD Bank Fraud Verification",
  description: "Got a suspicious message claiming to be from TD? Don't wonder — ask TD.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-white text-td-dark min-h-screen">
        {children}
      </body>
    </html>
  );
}
