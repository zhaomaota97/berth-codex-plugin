import { createOpenAICompatible } from "@ai-sdk/openai-compatible";
import { defineAgent } from "eve";

const agentourURL = process.env.AGENTOUR_URL?.replace(/\/$/, "");
const runtimeToken = process.env.AGENTOUR_RUNTIME_TOKEN || "";

const provider = createOpenAICompatible({
  name: "agentour",
  baseURL: `${agentourURL || "http://127.0.0.1:8600"}/v1/llm`,
  apiKey: runtimeToken,
});

export default defineAgent({
  model: provider("MODEL_ID"),
  modelContextWindowTokens: 1_000_000,
});
