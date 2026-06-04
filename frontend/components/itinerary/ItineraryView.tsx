import type { Itinerary } from "@/lib/types";

export function ItineraryView({ itinerary }: { itinerary: Itinerary }) {
  return (
    <article>
      <h2>{itinerary.destination ?? "Trip"} itinerary</h2>
      <p>{itinerary.summary}</p>
    </article>
  );
}
