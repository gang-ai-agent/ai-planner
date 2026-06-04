import { ShieldCheck, Sparkles } from "lucide-react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { AppShell } from "@/components/layout/AppShell";

export default function Home() {
  return (
    <AppShell>
      <section className="grid min-h-screen grid-cols-1 gap-8 px-6 py-8 lg:grid-cols-[360px_1fr]">
        <aside className="flex flex-col justify-between border-r border-stone-300 pr-0 lg:pr-8">
          <div>
            <div className="mb-6 flex items-center gap-2 text-coast">
              <Sparkles size={22} />
              <span className="text-sm font-semibold uppercase tracking-wider">AI Vacation Planner</span>
            </div>
            <h1 className="text-4xl font-semibold leading-tight text-ink">Plan a trip with memory, evidence, and guardrails.</h1>
            <p className="mt-5 text-base leading-7 text-slate-700">
              Build itineraries from preferences, trusted travel retrieval, validation checks, and secure agent workflow state.
            </p>
          </div>
          <div className="mt-10 flex items-center gap-3 rounded border border-stone-300 bg-white p-4 text-sm text-slate-700">
            <ShieldCheck className="shrink-0 text-coast" size={20} />
            Input safety, Qdrant retrieval sanitization, output validation, and memory audit are part of the flow.
          </div>
        </aside>
        <ChatPanel />
      </section>
    </AppShell>
  );
}
