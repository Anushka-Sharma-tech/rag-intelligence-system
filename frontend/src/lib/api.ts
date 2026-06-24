import type {
  CompareResponse,
  DocumentInfo,
  QueryResponse,
} from "./types";

const BASE = (
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
)
  .trim()
  .replace(/\/$/, "");

// Upgraded wrapper: intercept non-JSON responses to prevent UI crashes
async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;

  try {
    res = await fetch(`${BASE}${path}`, init);
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

export async function deleteDocument(doc_id: string) {
  return fetchJson(`/documents/${doc_id}`, { method: "DELETE" });
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