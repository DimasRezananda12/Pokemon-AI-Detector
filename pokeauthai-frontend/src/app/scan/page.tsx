'use client';

import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { scanCard } from '@/lib/api';

export default function ScanPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG, WebP).');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size must be under 10 MB.');
      return;
    }
    setError(null);
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, [handleFile]);

  const handleAnalyse = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const result = await scanCard(file);
      router.push(`/scan/${result.session_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-dark-bg">
      <Header />

      <main className="flex-grow w-full max-w-7xl mx-auto px-6 py-12 flex flex-col">
        <div className="mb-10">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">Upload Card Photo</h1>
          <p className="text-neutral-400 text-sm">
            Ensure high quality images for accurate professional verification.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8 items-start flex-grow">
          {/* Left: Dropzone & Actions */}
          <div className="w-full lg:w-2/3 flex flex-col gap-5">
            {/* Dropzone */}
            <div
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              className={`border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-12 text-center cursor-pointer transition-all min-h-[400px] ${
                dragActive
                  ? 'border-primary bg-primary/5'
                  : preview
                    ? 'border-success/50 bg-success/5'
                    : 'border-dark-border bg-dark-surface hover:border-neutral-400 hover:bg-dark-border/30'
              }`}
            >
              {preview ? (
                <div className="flex flex-col items-center gap-4">
                  <img
                    src={preview}
                    alt="Card preview"
                    className="max-h-64 rounded-lg shadow-2xl border-2 border-dark-border"
                  />
                  <p className="text-sm text-success font-semibold">{file?.name}</p>
                  <p className="text-xs text-neutral-400">Click to change photo</p>
                </div>
              ) : (
                <>
                  <span
                    className="material-symbols-outlined text-5xl text-neutral-400 mb-4"
                    style={{ fontVariationSettings: "'FILL' 0" }}
                  >
                    photo_camera
                  </span>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Click to upload or drag photo here
                  </h3>
                  <p className="text-neutral-400 text-sm max-w-sm mx-auto mb-4">
                    Upload a clear, well-lit photo of the card front. Professional verification requires high detail.
                  </p>
                  <div className="flex gap-2 items-center text-xs">
                    <span className="bg-dark-border text-neutral-200 px-2 py-1 rounded">PNG, JPG</span>
                    <span className="bg-dark-border text-neutral-200 px-2 py-1 rounded">Max 10MB</span>
                  </div>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFile(e.target.files[0]);
                }}
              />
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-4 rounded-lg">
                {error}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end gap-4 mt-2">
              <button
                onClick={() => { setFile(null); setPreview(null); setError(null); }}
                className="px-6 py-2.5 rounded-md font-semibold text-sm border border-dark-border text-neutral-200 hover:bg-dark-border/50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAnalyse}
                disabled={!file || loading}
                className={`px-6 py-2.5 rounded-md font-semibold text-sm flex items-center gap-2 transition-all ${
                  !file || loading
                    ? 'bg-neutral-600 text-neutral-400 cursor-not-allowed'
                    : 'bg-primary hover:bg-primary-dark text-white shadow-lg shadow-primary/20'
                }`}
              >
                {loading ? (
                  <>
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Analysing...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>
                      analytics
                    </span>
                    Analyse Photo
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right: Tips Sidebar */}
          <div className="w-full lg:w-1/3 bg-dark-surface border border-dark-border rounded-lg shadow-sm p-6 sticky top-24">
            <h3 className="font-semibold text-white mb-4 border-b border-dark-border pb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                fact_check
              </span>
              Photo Coverage
            </h3>
            <p className="text-neutral-400 text-sm mb-5">
              For the best analysis results, provide a clear photo. Green check indicates detected coverage.
            </p>

            <ul className="flex flex-col gap-3">
              {[
                { icon: 'crop_portrait', label: 'Front Face', done: !!file },
                { icon: 'flip_to_back', label: 'Back Face', done: false },
                { icon: '3d_rotation', label: 'Angled (Texture)', done: false },
                { icon: 'brightness_high', label: 'Hologram Focus', done: false },
              ].map((item, idx) => (
                <li key={idx} className="flex items-center justify-between p-3 rounded-lg border border-dark-border bg-dark-bg">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-neutral-400" style={{ fontVariationSettings: "'FILL' 0" }}>
                      {item.icon}
                    </span>
                    <span className="text-sm text-neutral-200 font-medium">{item.label}</span>
                  </div>
                  {item.done ? (
                    <span className="material-symbols-outlined text-success" style={{ fontVariationSettings: "'FILL' 1" }}>
                      check_circle
                    </span>
                  ) : (
                    <span className="material-symbols-outlined text-neutral-600" style={{ fontVariationSettings: "'FILL' 0" }}>
                      radio_button_unchecked
                    </span>
                  )}
                </li>
              ))}
            </ul>

            <div className="mt-6 pt-4 border-t border-dark-border">
              <h4 className="text-sm font-semibold text-white mb-2">Pro Tips</h4>
              <ul className="text-neutral-400 text-sm space-y-1.5">
                <li>• Avoid harsh reflections.</li>
                <li>• Place card on a dark, solid background.</li>
                <li>• Ensure edges are fully visible.</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
