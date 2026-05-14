import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { QueryClientProviderWrapper } from "@/components/providers/query-provider";
import { ThemeProvider } from "next-themes";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Kimari — Local AI Gateway",
  description: "Kimari Local AI Gateway Dashboard. Manage and monitor your local LLM inference server with GPU profiles, models, benchmarks, and integrations.",
  keywords: ["Kimari", "Local AI", "LLM", "Gateway", "llama.cpp", "Consumer GPU", "OpenAI-compatible"],
  authors: [{ name: "Kimari AI" }],
  icons: {
    icon: "/kimari-logo.png",
    apple: "/kimari-logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <QueryClientProviderWrapper>
            {children}
          </QueryClientProviderWrapper>
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  );
}
