"use client";

import { Send } from "lucide-react";
import { FormEvent, useState } from "react";

import { sendChat } from "@/lib/api";
import type { ChatResponse, TravelRequirements } from "@/lib/types";

export function ChatPanel() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [threadId, setThreadId] = useState<string | undefined>();
  const [travelRequirements, setTravelRequirements] = useState<TravelRequirements>({});
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed) return;

    setIsSending(true);
    setError(null);
    const nextRequirements = mergeRequirements(
      travelRequirements,
      inferRequirementsFromMessage(trimmed, response?.follow_up_questions ?? [])
    );
    try {
      const result = await sendChat(trimmed, "local-user", threadId, nextRequirements);
      setResponse(result);
      setThreadId(result.thread_id);
      setTravelRequirements(nextRequirements);
      setMessage("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Chat request failed.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <section className="flex min-h-[calc(100vh-4rem)] flex-col rounded border border-stone-300 bg-white">
      <div className="border-b border-stone-200 px-5 py-4">
        <h2 className="text-lg font-semibold">Planning Session</h2>
        <p className="text-sm text-slate-600">Start with destination, dates, interests, and constraints.</p>
      </div>
      <div className="flex-1 p-5">
        <div className="max-w-xl rounded border border-stone-200 bg-mist p-4 text-sm leading-6 text-slate-700">
          Try: Plan a 5 day food and history trip to Lisbon for two people.
        </div>
        {error ? (
          <div className="mt-4 max-w-xl rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
        ) : null}
        {response ? (
          <div className="mt-4 max-w-3xl rounded border border-stone-200 p-4">
            {response.itinerary ? (
              <>
                <h3 className="text-xl font-semibold">{response.itinerary.destination ?? "Trip plan"}</h3>
                {response.itinerary.main_route.length ? (
                  <section className="mt-5">
                    <h4 className="font-semibold">Selected cities</h4>
                    <div className="mt-3 grid gap-3">
                      {response.itinerary.main_route.map((stop) => (
                        <div className="rounded border border-stone-200 p-3 text-sm leading-6 text-slate-700" key={stop.name}>
                          <div className="font-medium text-ink">{stop.name}</div>
                          {stop.background ? <p className="mt-1 line-clamp-3">{stop.background}</p> : null}
                          {stop.major_attractions.length ? (
                            <p className="mt-2">
                              <span className="font-medium text-ink">Highlights: </span>
                              {stop.major_attractions.slice(0, 4).join(", ")}
                            </p>
                          ) : null}
                          {stop.local_food.length ? (
                            <p>
                              <span className="font-medium text-ink">Food: </span>
                              {stop.local_food.slice(0, 3).join(", ")}
                            </p>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}
                {response.itinerary.days.length ? (
                  <section className="mt-5 border-t border-stone-200 pt-4">
                    <h4 className="font-semibold">Daily plan</h4>
                    <div className="mt-3 space-y-3">
                      {response.itinerary.days.map((day) => (
                        <div className="rounded border border-stone-200 p-3" key={day.day_number}>
                          <h5 className="font-medium text-ink">{day.title}</h5>
                          <ul className="mt-2 space-y-1 text-sm text-slate-700">
                            {day.activities.map((activity) => (
                              <li key={`${day.day_number}-${activity.title}`}>
                                {activity.time ? `${activity.time}: ` : ""}
                                {activity.title}
                                {activity.duration ? ` (${activity.duration})` : ""}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </section>
                ) : null}
              </>
            ) : (
              <div>
                <div className="mb-2 text-sm font-semibold uppercase tracking-wider text-coast">{response.status}</div>
                <p className="text-sm leading-6 text-slate-700">{response.message}</p>
                {response.follow_up_questions.length > 0 ? (
                  <ul className="mt-4 list-disc pl-5 text-sm text-slate-700">
                    {response.follow_up_questions.map((question) => (
                      <li key={question}>{question}</li>
                    ))}
                  </ul>
                ) : null}
              </div>
            )}
          </div>
        ) : null}
      </div>
      <form className="flex gap-3 border-t border-stone-200 p-4" onSubmit={handleSubmit}>
        <input
          className="min-w-0 flex-1 rounded border border-stone-300 px-3 py-2 outline-none focus:border-coast"
          placeholder="Describe your trip..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded bg-coast text-white disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          aria-label="Send"
          disabled={isSending}
        >
          {isSending ? <span className="text-xs font-semibold">...</span> : <Send size={18} />}
        </button>
      </form>
    </section>
  );
}

function mergeRequirements(current: TravelRequirements, next: TravelRequirements): TravelRequirements {
  return {
    ...current,
    ...next,
    interests: mergeStringLists(current.interests, next.interests),
    transportation_preferences: mergeStringLists(
      current.transportation_preferences,
      next.transportation_preferences
    ),
    accommodation_preferences: mergeStringLists(
      current.accommodation_preferences,
      next.accommodation_preferences
    ),
    special_constraints: mergeStringLists(current.special_constraints, next.special_constraints)
  };
}

function mergeStringLists(first: string[] = [], second: string[] = []): string[] | undefined {
  const values = Array.from(new Set([...first, ...second]));
  return values.length ? values : undefined;
}

function inferRequirementsFromMessage(message: string, questions: string[]): TravelRequirements {
  const text = message.trim();
  const lower = text.toLowerCase();
  const questionText = questions.join(" ").toLowerCase();
  const inferred: TravelRequirements = {};

  const destinationMatch = text.match(/\b(?:to|in)\s+([A-Z][A-Za-z\s-]{2,40})(?:\s+under|\s+for|\s+with|,|\.|$)/);
  if (destinationMatch) {
    inferred.destination = destinationMatch[1].trim();
  } else if (questionText.includes("destination")) {
    const firstAnswer = text.split(/[,;\n]/)[0]?.trim();
    if (firstAnswer && !/\d/.test(firstAnswer)) {
      inferred.destination = firstAnswer;
    }
  }

  const durationMatch = text.match(/\b(\d{1,2})\s*(?:day|days|天|日)\b/i);
  if (durationMatch) {
    inferred.duration_days = Number(durationMatch[1]);
  } else if (questionText.includes("duration")) {
    const numberMatch = text.match(/\b(\d{1,2})\b/);
    if (numberMatch) inferred.duration_days = Number(numberMatch[1]);
  }

  const budgetMatch = text.match(/(?:under|below|budget|预算|不超过)?\s*[$¥￥]?\s*(\d{2,6}(?:,\d{3})*(?:\.\d+)?)/i);
  if (budgetMatch && (questionText.includes("budget") || /[$¥￥]|budget|under|below|预算|不超过/i.test(text))) {
    inferred.budget_max = Number(budgetMatch[1].replace(",", ""));
  }

  const travelersMatch = text.match(/\b(\d{1,2})\s*(?:people|person|travelers|travellers|adults|kids)\b/i);
  if (travelersMatch) inferred.travelers = Number(travelersMatch[1]);

  const interestAliases: Record<string, string[]> = {
    history: ["history", "historical"],
    art: ["art", "museum", "gallery"],
    food: ["food", "dining", "restaurant"],
    shopping: ["shopping"],
    leisure: ["leisure", "relax"]
  };
  const interests = Object.entries(interestAliases)
    .filter(([, aliases]) => aliases.some((alias) => lower.includes(alias)))
    .map(([interest]) => interest);
  if (interests.length) inferred.interests = interests;

  return inferred;
}
