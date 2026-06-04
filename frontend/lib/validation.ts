import { z } from "zod";

export const chatInputSchema = z.object({
  message: z.string().min(3).max(12000)
});
