// Server-only client for backpy. In production backpy has no public domain.
import type { Report, ReportListItem } from "./types";

const TIMEOUT_MS = 5000;

export class BackpyError extends Error {
  status?: number;
}

function baseUrl(): string {
  const url = process.env.BACKPY_INTERNAL_URL;
  if (!url) throw new BackpyError("BACKPY_INTERNAL_URL is not set");
  return url.replace(/\/+$/, "");
}

export async function backpyFetch(path: string, init?: RequestInit): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl()}${path}`, { ...init, signal: AbortSignal.timeout(TIMEOUT_MS) });
  } catch (cause) {
    console.error(`[backpy] request failed: ${path}`, cause);
    throw new BackpyError(`backpy unreachable at ${path}`, { cause });
  }
  return response;
}

async function json<T>(path: string): Promise<T> {
  const response = await backpyFetch(path);
  if (!response.ok) {
    const error = new BackpyError(`backpy ${path} returned ${response.status}`);
    error.status = response.status;
    console.error(error.message);
    throw error;
  }
  return (await response.json()) as T;
}

export const listReports = () => json<ReportListItem[]>("/api/reports");
export const getReport = (id: string) => json<Report>(`/api/reports/${encodeURIComponent(id)}`);
export const getBackpyHealth = () => json<{ git_sha: string; database: boolean; ingest: boolean }>("/api/health");
