import { createDeepSeek } from "@ai-sdk/deepseek";
import { defineAgent } from "eve";

// Runtime injects both values. Build Gate injects AGENTOUR_URL only, so runtime
// secrets must not be validated at module-import time.
const agentourURL = process.env.AGENTOUR_URL?.replace(/\/$/, "") || "http://agentour-build.invalid";
const runtimeKey = process.env.AGENTOUR_RUNTIME_KEY || "build-only-placeholder";

const provider = createDeepSeek({
  baseURL: `${agentourURL}/v1/llm`,
  apiKey: runtimeKey,
});

export default defineAgent({
  model: provider("MODEL_ID"),
  modelContextWindowTokens: 1_000_000,
  system: `ROLE_AND_INSTRUCTIONS`,
});
