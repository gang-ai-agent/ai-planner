export type Itinerary = {
  destination?: string;
  summary: string;
  estimated_total_cost?: number;
  citations: string[];
  main_route: Array<{
    name: string;
    stop_type: string;
    arrival_time_required?: string;
    transportation?: string;
    estimated_transport_cost?: number;
    estimated_total_cost?: number;
    background: string;
    major_attractions: string[];
    activities: string[];
    local_food: string[];
    shopping: string[];
  }>;
  detail_plans: Array<{
    stop_name: string;
    highlights: Array<Activity>;
    optional_adjustments: string[];
    brief_background: string;
  }>;
  alternative_options: Array<{
    title: string;
    reason: string;
    estimated_time?: string;
    estimated_cost?: number;
  }>;
  days: Array<{
    day_number: number;
    title: string;
    activities: Activity[];
  }>;
};

export type Activity = {
  time?: string;
  title: string;
  location?: string;
  notes?: string;
  importance?: string;
  duration?: string;
  transport?: string;
  ticket?: string;
  reservation_required?: boolean;
  local_specialty?: boolean;
  estimated_cost?: number;
};

export type MemoryRecord = {
  id: string;
  type: string;
  content: string;
  confidence: number;
};

export type TravelRequirements = {
  destination?: string;
  budget_min?: number;
  budget_max?: number;
  start_date?: string;
  end_date?: string;
  duration_days?: number;
  travelers?: number;
  travel_style?: "luxury" | "mid_range" | "budget" | "backpacking";
  interests?: string[];
  transportation_preferences?: string[];
  accommodation_preferences?: string[];
  special_constraints?: string[];
};

export type ChatResponse = {
  thread_id: string;
  run_id: string;
  status: string;
  message: string;
  follow_up_questions: string[];
  itinerary?: Itinerary;
};
