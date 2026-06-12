import type {
  CompareResponse,
  DocumentInfo,
  QueryResponse,
} from "./types";

const BASE = (
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;

  try {
    res = await fetch(`${BASE}${path}`, init);
  } catch {
    throw new Error(`Cannot reach the backend API at ${BASE}`);
  }

  if (!res.ok) {
    const body = await res.text();
    let message = body;

    try {
      const parsed = JSON.parse(body) as { detail?: unknown };
      if (typeof parsed.detail === "string") {
        message = parsed.detail;
      }
    } catch {
      // Keep the raw response body when it is not JSON.
    }

    throw new Error(message || `Request failed: ${res.status}`);
  }

  return res.json();
}

export async function uploadFile(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  return fetchJson("/documents/upload", { method: "POST", body: form });
}

export async function uploadURL(url: string): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("url", url);
  return fetchJson("/documents/upload-url", { method: "POST", body: form });
}

export async function getDocuments(): Promise<DocumentInfo[]> {
  return fetchJson("/documents/");
}

export async function deleteDocument(doc_id: string) {
  return fetchJson(`/documents/${doc_id}`, { method: "DELETE" });
}

export async function queryDocuments(
  question: string,
  doc_ids?: string[],
  top_k = 5
): Promise<QueryResponse> {
  return fetchJson("/query/", {
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
  return fetchJson("/query/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, doc_id_1, doc_id_2 }),
  });
}
