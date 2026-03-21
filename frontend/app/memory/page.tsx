"use client";

import { Card } from "@/components/ui/card";

export default function MemoryPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Memory</h1>
        <p className="text-sm text-muted-foreground mt-2">AI-powered insights and historical analysis</p>
      </div>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Ask Your AI Coach</h2>
          <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Ask about your patterns, habits, or insights..." 
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
              Ask
            </button>
          </div>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-4">Memory Bank</h2>
          <div className="space-y-3">
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Your insights and memories will appear here.</p>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground mb-2">How It Works</h2>
          <p className="text-sm text-muted-foreground">Your local LLM (Llama 3.1) analyzes your life data to find patterns, provide insights, and answer questions about your habits and productivity.</p>
        </div>
      </Card>
    </div>
  );
}
