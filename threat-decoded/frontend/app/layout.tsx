import type { Metadata, Viewport } from "next";
import "./globals.css";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#008A4C",
};

export const metadata: Metadata = {
  title: "Threat Decoded | TD Bank Fraud Verification",
  description:
    "Got a suspicious message claiming to be from TD? Don't wonder — ask TD. Verify suspicious texts, emails, and links instantly.",
  keywords: ["fraud detection", "TD Bank", "phishing", "verification", "cybersecurity"],
  icons: {
    icon: "/td-logo.svg",
    apple: "/td-logo.svg",
  },
  openGraph: {
    title: "Threat Decoded",
    description: "Your bank shouldn't guess. It should know.",
    siteName: "Threat Decoded",
    type: "website",
  },
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
