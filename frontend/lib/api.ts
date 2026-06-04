import type { ChatResponse, TravelRequirements } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function sendChat(
  message: string,
  userId = "local-user",
  threadId?: string,
  travelRequirements?: TravelRequirements
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message,
      thread_id: threadId,
      travel_requirements: travelRequirements
    })
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  return response.json();
}
