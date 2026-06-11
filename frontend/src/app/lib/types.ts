export interface DocumentInfo {
  doc_id: string;
  filename: string;
  chunks: number;
  created_at: string;
  file_type: string;
}

export interface CitedChunk {
  content: string;
  source: string;
  page: number | null;
  similarity_score: number;
}

export interface QueryResponse {
  answer: string;
  cited_chunks: CitedChunk[];
  confidence_score: number;
  confidence_label: "High" | "Medium" | "Low";
}

export interface CompareResponse {
  doc1_answer: string;
  doc2_answer: string;
  synthesis: string;
  doc1_name: string;
  doc2_name: string;
}