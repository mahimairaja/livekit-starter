import { useState } from "react";
import { useAgent, useSession } from "@livekit/components-react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AgentSessionProvider } from "@/components/agents-ui/agent-session-provider";
import { AGENT_NAME, tokenSource } from "@/lib/token-source";
import { Welcome } from "@/components/app/welcome";
import { SessionView } from "@/components/app/session-view";

function AppShell({ session }: { session: ReturnType<typeof useSession> }) {
  const agent = useAgent();
  const [hasStarted, setHasStarted] = useState(false);

  const start = async () => {
    setHasStarted(true);
    await session.start();
  };

  const disconnect = () => {
    void session.end();
    setHasStarted(false);
  };

  // Welcome screen before starting and after a clean or failed end.
  if (!hasStarted || agent.isFinished) {
    return <Welcome onStart={start} failureReasons={agent.failureReasons ?? undefined} />;
  }
  return <SessionView isConnected={agent.isConnected} onDisconnect={disconnect} />;
}

export default function App() {
  const session = useSession(tokenSource, { agentName: AGENT_NAME });
  return (
    <TooltipProvider>
      <AgentSessionProvider session={session}>
        <main className="min-h-screen">
          <AppShell session={session} />
        </main>
      </AgentSessionProvider>
    </TooltipProvider>
  );
}
