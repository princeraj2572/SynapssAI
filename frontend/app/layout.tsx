import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import ThemeToggle from "@/components/layout/ThemeToggle";
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";

const inter = Inter({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  title: "SynapseAI - Life Analytics",
  description: "Your private, AI-powered personal life analytics dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={cn("font-sans", inter.variable)}>
      <head>
        <script dangerouslySetInnerHTML={{
          __html: `try{if(localStorage.theme==='dark'||(!localStorage.theme&&window.matchMedia('(prefers-color-scheme:dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}`
        }} />
      </head>
      <body className="bg-background text-foreground">
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <header className="h-14 border-b border-border flex items-center justify-end px-6">
              <ThemeToggle />
            </header>
            <main className="flex-1 overflow-auto">
              <div className="p-6 md:p-8 max-w-7xl mx-auto">
                {children}
              </div>
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
