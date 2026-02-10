import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers":
    "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

interface RequestBody {
  messages: ChatMessage[];
  model?: string;
  provider?: string;
  apiKey?: string;
  baseUrl?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

const SYSTEM_PROMPT =
  "You are Dive AI, a powerful and intelligent coding assistant. " +
  "You help users with software development, debugging, architecture, code review, and technical problem-solving. " +
  "You write clean, production-ready code with clear explanations. " +
  "Use markdown formatting with code blocks when showing code. " +
  "Be concise but thorough.";

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const body: RequestBody = await req.json();
    const {
      messages = [],
      model = "gpt-4o-mini",
      provider = "openai",
      apiKey,
      baseUrl,
      temperature = 0.7,
      maxTokens = 4096,
      stream = false,
    } = body;

    const key =
      apiKey ||
      Deno.env.get("OPENAI_API_KEY") ||
      Deno.env.get("LLM_API_KEY") ||
      "";

    const url =
      baseUrl || resolveBaseUrl(provider);

    const fullMessages: ChatMessage[] = [
      { role: "system", content: SYSTEM_PROMPT },
      ...messages.slice(-30),
    ];

    if (!key) {
      const reply = fallbackResponse(
        messages[messages.length - 1]?.content || ""
      );
      return new Response(JSON.stringify({ reply, model: "fallback" }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    if (stream) {
      const upstream = await fetch(`${url}/chat/completions`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${key}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model,
          messages: fullMessages,
          temperature,
          max_tokens: maxTokens,
          stream: true,
        }),
      });

      if (!upstream.ok) {
        const errText = await upstream.text();
        return new Response(
          JSON.stringify({
            error: `Provider returned ${upstream.status}`,
            details: errText,
            reply: "The AI provider returned an error. Check your API key and model settings.",
          }),
          {
            status: 502,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      }

      return new Response(upstream.body, {
        headers: {
          ...corsHeaders,
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      });
    }

    const upstream = await fetch(`${url}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: fullMessages,
        temperature,
        max_tokens: maxTokens,
      }),
    });

    if (!upstream.ok) {
      const errText = await upstream.text();
      return new Response(
        JSON.stringify({
          error: `Provider returned ${upstream.status}`,
          details: errText,
          reply: "The AI provider returned an error. Check your API key and model settings.",
        }),
        {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const data = await upstream.json();
    const reply =
      data.choices?.[0]?.message?.content || "No response from model.";
    const usage = data.usage || {};

    return new Response(
      JSON.stringify({ reply, model: data.model || model, usage }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Unknown error";
    return new Response(
      JSON.stringify({
        error: msg,
        reply: "I encountered an error processing your request. Please try again.",
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

function resolveBaseUrl(provider: string): string {
  switch (provider) {
    case "openai":
      return "https://api.openai.com/v1";
    case "groq":
      return "https://api.groq.com/openai/v1";
    case "together":
      return "https://api.together.xyz/v1";
    case "openrouter":
      return "https://openrouter.ai/api/v1";
    case "deepseek":
      return "https://api.deepseek.com/v1";
    default:
      return "https://api.openai.com/v1";
  }
}

function fallbackResponse(userMessage: string): string {
  const lower = userMessage.toLowerCase();

  if (
    lower.includes("hello") ||
    lower.includes("hi") ||
    lower.includes("hey")
  ) {
    return "Hello! I'm Dive AI. I'm currently running in **demo mode** without an LLM API key configured.\n\nTo enable full AI responses, add your API key in Settings or configure the `OPENAI_API_KEY` environment variable.\n\nI can still help you explore the interface!";
  }

  if (lower.includes("code") || lower.includes("function")) {
    return '**Demo Mode** - Here\'s an example of what I can do with a real LLM connection:\n\n```typescript\nfunction fibonacci(n: number): number {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}\n\nconsole.log(fibonacci(10)); // 55\n```\n\nConfigure your API key to get real coding assistance!';
  }

  if (lower.includes("help") || lower.includes("what can")) {
    return "I'm Dive AI, your coding assistant. In **full mode** I can:\n\n- Write and debug code in any language\n- Explain complex concepts\n- Review architecture decisions\n- Generate tests and documentation\n- Analyze errors and suggest fixes\n\n**Setup:** Add your OpenAI/Groq/DeepSeek API key in Settings to activate the LLM connection.";
  }

  return `**Demo Mode** - I received your message but no LLM API key is configured.\n\nTo get real AI responses:\n1. Go to **Settings**\n2. Enter your API key (OpenAI, Groq, DeepSeek, etc.)\n3. Select your preferred model\n\nYour message: "${userMessage.slice(0, 100)}${userMessage.length > 100 ? "..." : ""}"`;
}
