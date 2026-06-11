import React, { useState, useRef } from "react";
import { uploadFile } from "../lib/api";
import { DocumentInfo } from "../lib/types";

interface FileUploadProps {
  onUpload: (doc: DocumentInfo) => void;
}

export default function FileUpload({ onUpload }: FileUploadProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!allowedTypes.includes(file.type)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await uploadFile(file);
      onUpload(data);
    } catch (err: any) {
      setError(err.message || "Failed to upload file.");
    } finally {
      setLoading(false);
    }
  };

  const onDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="mb-6">
      <div
        onDragEnter={onDrag}
        onDragOver={onDrag}
        onDragLeave={onDrag}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          dragActive
            ? "border-indigo-500 bg-indigo-500/5"
            : "border-zinc-800 bg-zinc-900/30 hover:border-zinc-700"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          disabled={loading}
        />
        {loading ? (
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-zinc-400">Processing and embedding document...</p>
          </div>
        ) : (
          <div>
            <p className="text-sm font-medium text-zinc-200">
              Drag & drop your file here, or <span className="text-indigo-400">browse</span>
            </p>
            <p className="text-xs text-zinc-500 mt-1">Supports PDF and DOCX</p>
          </div>
        )}
      </div>
      {error && <p className="text-xs text-rose-400 mt-1">{error}</p>}
    </div>
  );
}