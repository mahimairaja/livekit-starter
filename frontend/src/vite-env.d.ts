/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TOKEN_ENDPOINT?: string;
  readonly VITE_AGENT_NAME?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
