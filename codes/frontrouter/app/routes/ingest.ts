import { backpyFetch } from "~/lib/backpy.server";

import type { Route } from "./+types/ingest";

// Public entry for `curbcut publish`. backpy checks the token; this route only forwards.
export async function action({ request }: Route.ActionArgs) {
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  try {
    const response = await backpyFetch("/api/reports/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: request.headers.get("Authorization") ?? "" },
      body: await request.text(),
    });
    return new Response(await response.text(), {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json({ detail: "Report storage is unreachable." }, { status: 503 });
  }
}

export function loader() {
  return new Response("Method not allowed", { status: 405 });
}
