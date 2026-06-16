import { useAgent, useSessionMessages } from "@livekit/components-react";
import { AgentAudioVisualizerBar } from "@/components/agents-ui/agent-audio-visualizer-bar";
import { AgentChatTranscript } from "@/components/agents-ui/agent-chat-transcript";
import { AgentControlBar } from "@/components/agents-ui/agent-control-bar";

export function SessionView({
  isConnected,
  onDisconnect,
}: {
  isConnected: boolean;
  onDisconnect: () => void;
}) {
  const { state, microphoneTrack } = useAgent();
  const { messages } = useSessionMessages();

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col gap-4 p-4">
      <div className="flex flex-col items-center gap-2 pt-6">
        <AgentAudioVisualizerBar
          state={state}
          audioTrack={microphoneTrack}
          barCount={5}
          size="lg"
        />
        <p className="text-muted-foreground text-sm">{state}</p>
      </div>

      <AgentChatTranscript
        messages={messages}
        agentState={state}
        className="flex-1 overflow-y-auto rounded-lg border p-3"
      />

      {/* AgentControlBar bundles the mic toggle, an expandable text chat input
          (controls.chat), and the leave button. */}
      <AgentControlBar
        isConnected={isConnected}
        onDisconnect={onDisconnect}
        controls={{
          microphone: true,
          chat: true,
          leave: true,
          camera: false,
          screenShare: false,
        }}
      />
    </div>
  );
}
