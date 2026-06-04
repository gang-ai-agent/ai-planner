import type { MemoryRecord } from "@/lib/types";

export function MemoryList({ memories }: { memories: MemoryRecord[] }) {
  return (
    <ul>
      {memories.map((memory) => (
        <li key={memory.id}>{memory.content}</li>
      ))}
    </ul>
  );
}
