const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function uploadFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/documents/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadURL(url: string) {
  const form = new FormData();
  form.append("url", url);
  const res = await fetch(`${BASE}/documents/upload-url`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDocuments(): Promise<import("./types").DocumentInfo[]> {
  const res = await fetch(`${BASE}/documents/`);
  if (!res.ok) throw new Error("Failed to load documents");
  return res.json();
}

export async function deleteDocument(doc_id: string) {
  const res = await fetch(`${BASE}/documents/${doc_id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
  return res.json();
}

export async function queryDocuments(
  question: string,
  doc_ids?: string[],
  top_k = 5
): Promise<import("./types").QueryResponse> {
  const res = await fetch(`${BASE}/query/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, doc_ids, top_k }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function compareDocuments(
  question: string,
  doc_id_1: string,
  doc_id_2: string
): Promise<import("./types").CompareResponse> {
  const res = await fetch(`${BASE}/query/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, doc_id_1, doc_id_2 }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}