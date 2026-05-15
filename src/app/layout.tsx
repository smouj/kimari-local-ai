import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Kimari Local AI — Run useful local AI on older NVIDIA GPUs",
  description: "Open-source framework for running local language models on consumer NVIDIA GPUs. GTX 1060, GTX 1080 and more. Local-first, open-source, GGUF runtime.",
  keywords: ["Kimari", "local AI", "GGUF", "llama.cpp", "CUDA", "NVIDIA", "GTX 1060", "GTX 1080", "OpenAI-compatible", "local LLM"],
  authors: [{ name: "Smouj" }],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "Kimari Local AI",
    description: "Run useful local AI on older NVIDIA GPUs. Local-first, open-source, GGUF runtime.",
    url: "https://github.com/smouj/kimari-local-ai",
    siteName: "Kimari",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Kimari Local AI",
    description: "Run useful local AI on older NVIDIA GPUs",
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
        {children}
        <Toaster />
      </body>
    </html>
  );
}
