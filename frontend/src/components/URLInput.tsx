import React, { useState } from "react";
import { uploadURL } from "../lib/api";
import { DocumentInfo } from "../lib/types";

interface URLInputProps {
  onUpload: (doc: DocumentInfo) => void;
}

export default function URLInput({ onUpload }: URLInputProps) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await uploadURL(url.trim());
      onUpload(data);
      setUrl("");
    } catch (err: any) {
      setError(err.message || "Failed to process URL.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste documentation or article URL..."
          disabled={loading}
          className="flex-1 bg-zinc-900 border border-zinc-800 focus:border-zinc-700 focus:outline-none rounded-lg px-4 py-2 text-sm text-zinc-200 placeholder-zinc-600 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 disabled:opacity-40 font-medium text-sm px-4 py-2 rounded-lg transition-colors flex items-center justify-center min-w-[80px]"
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            "Ingest"
          )}
        </button>
      </div>
      {error && <p className="text-xs text-rose-400 mt-2">{error}</p>}
    </form>
  );
}