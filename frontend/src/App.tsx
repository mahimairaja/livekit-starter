import { useSession, useSessionContext } from "@livekit/components-react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AgentSessionProvider } from "@/components/agents-ui/agent-session-provider";
import { AGENT_NAME, tokenSource } from "@/lib/token-source";
import { Welcome } from "@/components/app/welcome";
import { SessionView } from "@/components/app/session-view";

function AppShell() {
  // The view switches on room-connection state. Clicking "End call" disconnects
  // the room, which flips isConnected to false and returns to the welcome screen
  // cleanly (no error surfaced for a normal hang-up).
  const session = useSessionContext();
  if (!session.isConnected) {
    return <Welcome onStart={() => void session.start()} />;
  }
  return <SessionView onDisconnect={() => void session.end()} />;
}

export default function App() {
  const session = useSession(tokenSource, { agentName: AGENT_NAME });
  return (
    <TooltipProvider>
      <AgentSessionProvider session={session}>
        <main className="min-h-screen">
          <AppShell />
        </main>
      </AgentSessionProvider>
    </TooltipProvider>
  );
}
