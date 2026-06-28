import type {
  CompareResponse,
  DocumentInfo,
  QueryResponse,
} from "./types";
import { createClient } from "@supabase/supabase-js";

// Initialize temporary fallback client purely to read tokens locally if initialization sequence requires it
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const supabase = createClient(supabaseUrl, supabaseAnonKey);

const BASE = (
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
)
  .trim()
  .replace(/\/$/, "");

/**
 * 🛑 INTERNAL HELPER: Synchronously returns or provisions a Guest Session ID 
 * from sessionStorage so it automatically clears when the user closes their browser tab.
 */
function getOrInitializeGuestId(): string {
  if (typeof window === "undefined") return "";
  let guestId = sessionStorage.getItem("guest_session_id");
  if (!guestId) {
    // Generate a quick random tracking identifier string for the guest workspace
    guestId = `guest_${Math.random().toString(36).substring(2, 11)}_${Date.now().toString(36)}`;
    sessionStorage.setItem("guest_session_id", guestId);
  }
  return guestId;
}

/**
 * 🛑 INTERNAL HELPER: Assembles multi-tenant authorization injection headers
 * by verifying the Supabase JWT profile first, then falling back to X-Session-ID.
 */
async function buildHeaders(customHeaders: Record<string, string> = {}): Promise<Record<string, string>> {
  const headers: Record<string, string> = { ...customHeaders };
  
  try {
    // 1. Attempt to fetch current active logged-in Google Member session token
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session?.access_token) {
      headers["Authorization"] = `Bearer ${session.access_token}`;
    } else {
      // 2. Fall back to temporary browser-scoped session validation
      headers["X-Session-ID"] = getOrInitializeGuestId();
    }
  } catch (err) {
    console.error("Identity matching interceptor caught error:", err);
    headers["X-Session-ID"] = getOrInitializeGuestId();
  }
  
  return headers;
}

// Upgraded wrapper: intercept non-JSON responses to prevent UI crashes
async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;

  // Intercept the request to dynamically append modern multi-tenant validation headers
  const dynamicHeaders = await buildHeaders(
    init?.headers ? (init.headers as Record<string, string>) : {}
  );
  
  const updatedInit: RequestInit = {
    ...init,
    headers: dynamicHeaders
  };

  try {
    res = await fetch(`${BASE}${path}`, updatedInit);
  } catch {
    throw new Error(`Cannot reach the backend API at ${BASE}`);
  }

  // 1. Verify the response is actually JSON
  const contentType = res.headers.get("content-type");
  const isJson = contentType && contentType.includes("application/json");

  // 2. Handle HTTP Errors (400s, 500s)
  if (!res.ok) {
    let message = `Request failed: ${res.status}`;
    
    if (isJson) {
      try {
        const parsed = await res.json() as { detail?: unknown };
        if (typeof parsed.detail === "string") {
          message = parsed.detail;
        } else if (parsed.detail) {
          message = JSON.stringify(parsed.detail); // Catch complex FastAPI errors
        }
      } catch {
        // Parsing failed, keep default message
      }
    } else {
      // It's likely a Vercel/Railway HTML error page
      const text = await res.text();
      console.error(`API returned non-JSON error (${res.status}):`, text.substring(0, 150));
      message = `Server error (${res.status}). Please try again later.`;
    }

    throw new Error(message);
  }

  // 3. Handle success but non-JSON (e.g., a proxy intercepts and returns 200 OK HTML)
  if (!isJson) {
    const text = await res.text();
    console.error("API returned non-JSON success response:", text.substring(0, 150));
    throw new Error("Invalid API response format (expected JSON)");
  }

  // 4. Safe to parse
  return res.json();
}


// --- API Endpoints ---

export async function uploadFile(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  // Headers are handled automatically inside fetchJson
  return fetchJson<DocumentInfo>("/documents/upload", { method: "POST", body: form });
}

export async function uploadURL(url: string): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("url", url);
  return fetchJson<DocumentInfo>("/documents/upload-url", { method: "POST", body: form });
}

export async function getDocuments(): Promise<DocumentInfo[]> {
  try {
    return await fetchJson<DocumentInfo[]>("/documents/");
  } catch (err) {
    console.error("Failed to fetch documents:", err);
    return []; // Fail silently so the UI shows an empty list instead of crashing
  }
}

export async function deleteDocument(doc_id: string): Promise<{ message: string }> {
  return fetchJson<{ message: string }>(`/documents/${doc_id}`, { method: "DELETE" });
}

export async function queryDocuments(
  question: string,
  doc_ids?: string[],
  top_k = 5
): Promise<QueryResponse> {
  return fetchJson<QueryResponse>("/query/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, doc_ids, top_k }),
  });
}

export async function compareDocuments(
  question: string,
  doc_id_1: string,
  doc_id_2: string
): Promise<CompareResponse> {
  return fetchJson<CompareResponse>("/query/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, doc_id_1, doc_id_2 }),
  });
}