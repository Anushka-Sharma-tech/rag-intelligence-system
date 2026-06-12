"use client";

import React, { useState, useEffect } from "react";
import FileUpload from "../components/FileUpload";
import URLInput from "../components/URLInput";
import DocumentList from "../components/DocumentList";
import ChatInterface from "../components/ChatInterface";
import { getDocuments, deleteDocument } from "../lib/api";
import { DocumentInfo } from "../lib/types";

export default function Home() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [inventoryError, setInventoryError] = useState<string | null>(null);

  const fetchInventory = async () => {
    try {
      setInventoryError(null);
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setInventoryError(
        err instanceof Error ? err.message : "Failed to sync backend document inventory."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const handleNewUpload = (newDoc: DocumentInfo) => {
    setDocuments((prev) => [newDoc, ...prev]);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.doc_id !== id));
      setSelectedDocIds((prev) => prev.filter((docId) => docId !== id));
    } catch (err) {
      alert("Failed to delete document from backend store.");
    }
  };

  const handleToggleSelect = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((docId) => docId !== id) : [...prev, id]
    );
  };

  return (
    <main className="min-h-screen bg-black text-zinc-100 p-6 md:p-12 selection:bg-indigo-500/30">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="border-b border-zinc-800 pb-6 flex justify-between items-end">
          <div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
              RAG Intelligence Deck
            </h1>
            <p className="text-sm text-zinc-500 mt-1">
              Multi-document contextual engine with localized semantic chunking and verifiable citations.
            </p>
          </div>
          <div className="text-xs text-zinc-600 font-mono">v1.0.0</div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Panel: Ingestion & Inventory */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-zinc-950 border border-zinc-900 rounded-xl p-5 shadow-2xl">
              <h2 className="text-sm font-semibold text-zinc-300 mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-500" /> Data Source Ingestion
              </h2>
              <FileUpload onUpload={handleNewUpload} />
              <URLInput onUpload={handleNewUpload} />
            </div>

            <div className="bg-zinc-950 border border-zinc-900 rounded-xl p-5 shadow-2xl">
              <h2 className="text-sm font-semibold text-zinc-300 mb-2 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500" /> Knowledge Inventory
              </h2>
              <p className="text-xs text-zinc-500 mb-4">
                Select specific sources to isolate searches, or uncheck all to scan the complete system context.
              </p>
              {loading ? (
                <div className="text-center p-6 text-sm text-zinc-500">Syncing vector state...</div>
              ) : inventoryError ? (
                <div className="rounded-lg border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-200">
                  {inventoryError}
                </div>
              ) : (
                <DocumentList
                  documents={documents}
                  onDelete={handleDelete}
                  selectedIds={selectedDocIds}
                  onToggleSelect={handleToggleSelect}
                />
              )}
            </div>
          </div>

          {/* Right Panel: Interactive Query Shell */}
          <div className="lg:col-span-7 bg-zinc-950 border border-zinc-900 rounded-xl p-6 shadow-2xl h-fit">
            <h2 className="text-sm font-semibold text-zinc-300 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500" /> Contextual Query Shell
            </h2>
            <ChatInterface selectedDocIds={selectedDocIds} />
          </div>

        </div>
      </div>
    </main>
  );
}
