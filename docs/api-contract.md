# API Contract

Primary endpoint: `POST /api/chat`.

Request:

```json
{
  "user_id": "user-123",
  "message": "Plan a 5 day trip to Lisbon",
  "thread_id": "optional-thread-id"
}
```

Response includes `thread_id`, `run_id`, `status`, `message`, optional `itinerary`, and `guardrail_events`.
