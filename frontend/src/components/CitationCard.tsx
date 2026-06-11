import React from "react";
import { CitedChunk } from "../lib/types";

interface CitationCardProps {
  chunk: CitedChunk;
  index: number;
}

export default function CitationCard({ chunk, index }: CitationCardProps) {
  const percentage = Math.round(chunk.similarity_score * 100);

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-all rounded-lg p-4 mb-3">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex items-center gap-2 overflow-hidden">
          <span className="flex-shrink-0 flex items-center justify-center bg-zinc-800 text-zinc-400 text-xs font-bold h-5 w-5 rounded">
            [{index + 1}]
          </span>
          <span className="text-sm font-semibold text-zinc-200 truncate" title={chunk.source}>
            {chunk.source}
          </span>
          {chunk.page && (
            <span className="flex-shrink-0 text-xs bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded">
              Page {chunk.page}
            </span>
          )}
        </div>
        <span className="flex-shrink-0 text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full">
          {percentage}% Match
        </span>
      </div>
      <p className="text-sm text-zinc-400 leading-relaxed whitespace-pre-wrap pl-7">
        "{chunk.content}"
      </p>
    </div>
  );
}
