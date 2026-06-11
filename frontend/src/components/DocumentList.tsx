import React from "react";
import { DocumentInfo } from "../lib/types";

interface DocumentListProps {
  documents: DocumentInfo[];
  onDelete: (id: string) => void;
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
}

export default function DocumentList({
  documents,
  onDelete,
  selectedIds,
  onToggleSelect,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="text-center p-8 bg-zinc-900/20 border border-zinc-800 rounded-xl">
        <p className="text-sm text-zinc-500">No documents ingested yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
      {documents.map((doc) => {
        const isSelected = selectedIds.includes(doc.doc_id);
        return (
          <div
            key={doc.doc_id}
            className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
              isSelected
                ? "bg-indigo-500/5 border-indigo-500/30"
                : "bg-zinc-900/40 border-zinc-800/80 hover:border-zinc-700"
            }`}
          >
            <div className="flex items-center gap-3 overflow-hidden min-w-0">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggleSelect(doc.doc_id)}
                className="h-4 w-4 rounded border-zinc-800 bg-zinc-900 text-indigo-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
              />
              <div className="min-w-0">
                <p className="text-sm font-medium text-zinc-200 truncate" title={doc.filename}>
                  {doc.filename}
                </p>
                <div className="flex items-center gap-2 mt-0.5 text-xs text-zinc-500">
                  <span className="uppercase font-semibold tracking-wider text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50">
                    {doc.file_type || "link"}
                  </span>
                  <span>•</span>
                  <span>{doc.chunks} vectors</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => onDelete(doc.doc_id)}
              className="text-zinc-500 hover:text-rose-400 p-1.5 rounded-md hover:bg-rose-500/5 transition-all ml-2 flex-shrink-0"
              title="Remove document"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-4v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        );
      })}
    </div>
  );
}