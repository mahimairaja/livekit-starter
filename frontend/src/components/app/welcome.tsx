import { Button } from "@/components/ui/button";

export function Welcome({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6 text-center">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">Voice assistant</h1>
        <p className="text-muted-foreground">
          Click start, allow your microphone, and talk to the agent.
        </p>
      </div>
      <Button size="lg" onClick={onStart}>
        Start conversation
      </Button>
    </div>
  );
}
