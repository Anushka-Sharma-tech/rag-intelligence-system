"use client";

import React, { useState, useEffect } from "react";
import FileUpload from "../components/FileUpload";
import URLInput from "../components/URLInput";
import DocumentList from "../components/DocumentList";
import ChatInterface from "../components/ChatInterface";
import { getDocuments, deleteDocument } from "../lib/api";
import { DocumentInfo } from "../lib/types";
import { createClient } from "@supabase/supabase-js";

// Initialize Supabase Client to track current user profiles locally
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default function Home() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [inventoryError, setInventoryError] = useState<string | null>(null);
  
  // Auth states
  const [user, setUser] = useState<any>(null);
  const [isGuest, setIsGuest] = useState(false);

  // Sync inventory documents from backend
  const fetchInventory = async () => {
    try {
      setInventoryError(null);
      setLoading(true);
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

  // Monitor Supabase Authentication cycles
  useEffect(() => {
    // 1. Check current logged session state
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
        setIsGuest(false);
      } else {
        setUser(null);
        setIsGuest(true);
      }
    });

    // 2. Listen for auth changes (Login/Logout triggers)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(session.user);
        setIsGuest(false);
      } else {
        setUser(null);
        setIsGuest(true);
        // Clear any leftover selected keys if switching contexts
        setSelectedDocIds([]);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Whenever user context alters (Login/Logout/Guest initialization), reload inventory partition
  useEffect(() => {
    fetchInventory();
  }, [user, isGuest]);

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

  // Action: Trigger Google OAuth flow via Supabase
  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin,
      },
    });
  };

  // Action: Sign out current active member session
  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setIsGuest(true);
  };

  return (
    <main className="min-h-screen bg-black text-zinc-100 p-6 md:p-12 selection:bg-indigo-500/30">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="border-b border-zinc-800 pb-6 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
              RAG Intelligence Deck
            </h1>
            <p className="text-sm text-zinc-500 mt-1">
              Multi-document contextual engine with localized semantic chunking and verifiable citations.
            </p>
          </div>

          {/* Authentication System Quick State Toggle Wrapper */}
          <div className="flex items-center gap-3 self-stretch sm:self-auto justify-between sm:justify-end">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs text-zinc-400 font-medium">{user.email}</div>
                  <div className="text-[10px] text-emerald-400 font-mono tracking-wider uppercase">Google Member</div>
                </div>
                <button
                  onClick={handleSignOut}
                  className="px-3 py-1.5 text-xs bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 rounded-md transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs text-zinc-500">Temporary Session</div>
                  <div className="text-[10px] text-amber-500 font-mono tracking-wider uppercase">Guest Mode</div>
                </div>
                <button
                  onClick={handleGoogleLogin}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-zinc-100 text-zinc-900 hover:bg-zinc-200 rounded-md transition-colors shadow-sm"
                >
                  {/* Simple explicit Google icon representation */}
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Sign in with Google
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Guest Warning Message Indicator Banner */}
        {isGuest && (
          <div className="bg-amber-950/20 border border-amber-900/40 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-inner">
            <div className="space-y-0.5">
              <h4 className="text-sm font-medium text-amber-300">You are browsing in Guest Mode</h4>
              <p className="text-xs text-zinc-400">
                Uploaded documents are temporary, isolated to this device, and are deleted automatically from our servers when you close this window.
              </p>
            </div>
            <button 
              onClick={handleGoogleLogin} 
              className="text-xs font-semibold text-amber-400 hover:text-amber-300 underline underline-offset-4 shrink-0"
            >
              Save data to an account →
            </button>
          </div>
        )}

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
                <div className="text-center p-6 text-sm text-zinc-500 font-mono animate-pulse">Syncing vector state...</div>
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