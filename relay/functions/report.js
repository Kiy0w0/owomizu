const RATE_WINDOW_MS = 60_000;
const RATE_MAX = 30;
const ipHits = new Map();

function rateLimited(ip) {
  const now = Date.now();
  const hits = (ipHits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  if (hits.length >= RATE_MAX) {
    ipHits.set(ip, hits);
    return true;
  }
  hits.push(now);
  ipHits.set(ip, hits);
  return false;
}

function clip(value, max) {
  if (typeof value !== "string") return "";
  return value.length > max ? value.slice(0, max) : value;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  const secret = request.headers.get("X-Mizu-Secret") || "";
  if (!env.MIZU_SECRET || secret !== env.MIZU_SECRET) {
    return new Response("forbidden", { status: 403 });
  }

  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  if (rateLimited(ip)) {
    return new Response("rate limited", { status: 429 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  if (!body || typeof body !== "object") {
    return new Response("bad request", { status: 400 });
  }

  const errorType = clip(body.error_type || "Unknown", 200);
  const message = clip(body.message || "", 1000);
  const tb = clip(body.traceback || "", 1500);
  const account = clip(body.account || "unknown", 100);
  const version = clip(body.version || "", 50);

  const webhookUrl = env.DISCORD_WEBHOOK_URL;
  if (!webhookUrl) {
    return new Response("relay not configured", { status: 500 });
  }

  const embed = {
    title: `❌ ${errorType}`,
    color: 0xff5555,
    description: message || "(no message)",
    fields: [
      { name: "Account", value: account, inline: true },
      { name: "Version", value: version || "unknown", inline: true },
    ],
    timestamp: new Date().toISOString(),
    footer: { text: "owomizu error relay" },
  };

  if (tb) {
    embed.fields.push({ name: "Traceback", value: "```\n" + tb + "\n```" });
  }

  const forward = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: "owomizu relay", embeds: [embed] }),
  });

  if (!forward.ok) {
    return new Response("upstream failed", { status: 502 });
  }

  return new Response("ok", { status: 200 });
}

export async function onRequest(context) {
  if (context.request.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }
  return onRequestPost(context);
}
