import React, { useState } from "react";
import { queryDocuments } from "../lib/api";
import { DocumentInfo, QueryResponse } from "../lib/types";
import ConfidenceMeter from "./ConfidenceMeter";
import CitationCard from "./CitationCard";

interface ChatInterfaceProps {
  selectedDocIds: string[];
}

export default function ChatInterface({ selectedDocIds }: ChatInterfaceProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    try {
      // Pass targeted filter array if checkboxes are ticked, otherwise let backend search everything
      const data = await queryDocuments(
        question.trim(), 
        selectedDocIds.length > 0 ? selectedDocIds : undefined
      );
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "Query failed to process.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleQuery} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={
            selectedDocIds.length > 0
              ? `Querying ${selectedDocIds.length} selected document(s)...`
              : "Ask a context-aware question across all intelligence sources..."
          }
          disabled={loading}
          className="flex-1 bg-zinc-900 border border-zinc-800 focus:border-zinc-700 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-zinc-200 placeholder-zinc-600"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-5 py-2.5 rounded-lg disabled:opacity-40 transition-colors flex items-center justify-center min-w-[90px]"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            "Analyze"
          )}
        </button>
      </form>

      {error && (
        <div className="p-3 bg-rose-500/5 border border-rose-500/20 rounded-lg text-xs text-rose-400">
          {error}
        </div>
      )}

      {response && (
        <div className="space-y-4 animate-fadeIn">
          <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-5">
            <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">Synthesized Answer</h3>
            <p className="text-sm text-zinc-200 leading-relaxed whitespace-pre-wrap">
              {response.answer}
            </p>
          </div>

          <ConfidenceMeter score={response.confidence_score} label={response.confidence_label} />

          {response.cited_chunks && response.cited_chunks.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-1">Verifiable Source Citations</h3>
              <div className="space-y-2">
                {response.cited_chunks.map((chunk, index) => (
                  <CitationCard key={index} chunk={chunk} index={index} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}