'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import VerdictBadge from '@/components/VerdictBadge';
import EvidenceCard from '@/components/EvidenceCard';
import PriceTable from '@/components/PriceTable';
import { getResult, getMarketPrices } from '@/lib/api';
import type { ScanResponse, PriceData } from '@/lib/api';

function buildDescription(data: ScanResponse): string {
  if (data.verdict === 'LIKELY_REAL') {
    return `Based on comprehensive analysis including text validation, attribute matching, and database cross-referencing, this card exhibits all expected hallmarks of an authentic specimen. ${data.anomalies.length === 0 ? 'No significant anomalies detected.' : ''}`;
  } else if (data.verdict === 'UNCERTAIN') {
    return `Analysis produced mixed results. Some attributes match the expected profile, but ${data.anomalies.length} anomal${data.anomalies.length === 1 ? 'y was' : 'ies were'} flagged for manual review. Consider professional grading for definitive assessment.`;
  } else if (data.verdict === 'SUSPICIOUS') {
    return `Multiple discrepancies detected between the submitted card and our authenticated database. ${data.anomalies.join('. ')}. This card warrants careful manual inspection before any transaction.`;
  }
  return 'Insufficient data to render a definitive verdict. Please upload a clearer image.';
}

function buildEvidence(data: ScanResponse) {
  const items = [];

  // OCR Confidence
  items.push({
    name: 'Text Recognition (OCR)',
    status: data.scores.ocr_confidence >= 0.8 ? 'pass' as const : data.scores.ocr_confidence >= 0.5 ? 'caution' as const : 'fail' as const,
    confidence: data.scores.ocr_confidence,
    description: data.ocr_data.card_name
      ? `Detected card name: "${data.ocr_data.card_name}"${data.ocr_data.hp ? `, HP: ${data.ocr_data.hp}` : ''}. Types: ${data.ocr_data.types.length > 0 ? data.ocr_data.types.join(', ') : 'N/A'}.`
      : 'Could not extract readable text from the card image.',
  });

  // Rule Match
  items.push({
    name: 'Database Cross-Reference',
    status: data.scores.rule_match >= 0.9 ? 'pass' as const : data.scores.rule_match >= 0.5 ? 'caution' as const : 'fail' as const,
    confidence: data.scores.rule_match,
    description: data.matched_card.name
      ? `Matched to "${data.matched_card.name}" from ${data.matched_card.set_name || 'unknown set'}.${data.anomalies.length > 0 ? ` Issues: ${data.anomalies.join('; ')}` : ' All attributes verified.'}`
      : 'No matching card found in the TCG database.',
  });

  // Visual Quality
  items.push({
    name: 'Visual Quality Assessment',
    status: data.scores.visual_quality >= 0.8 ? 'pass' as const : data.scores.visual_quality >= 0.5 ? 'caution' as const : 'fail' as const,
    confidence: data.scores.visual_quality,
    description: data.scores.visual_quality >= 0.8
      ? 'Image quality meets recommended standards. Good lighting and focus detected.'
      : 'Image quality is below optimal threshold. Consider re-uploading a clearer photo for better accuracy.',
  });

  return items;
}

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [data, setData] = useState<ScanResponse | null>(null);
  const [prices, setPrices] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getResult(sessionId);
        setData(result);

        // Fetch market prices if we have a matched card
        if (result.matched_card?.id) {
          try {
            const market = await getMarketPrices(result.matched_card.id);
            setPrices(market.pricing || []);
          } catch {
            // Market prices are optional
          }
        }
      } catch {
        setError('Result not found. The session may have expired.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-bg">
        <Header />
        <main className="flex-grow flex items-center justify-center">
          <div className="flex flex-col items-center gap-4 animate-fade-in-up">
            <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
            <p className="text-neutral-400 text-sm">Loading analysis results...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-bg">
        <Header />
        <main className="flex-grow flex items-center justify-center">
          <div className="bg-dark-surface border border-dark-border rounded-xl p-10 text-center max-w-md animate-fade-in-up">
            <span className="material-symbols-outlined text-5xl text-red-400 mb-4 block">error</span>
            <h2 className="text-xl font-bold text-white mb-2">Result Not Found</h2>
            <p className="text-neutral-400 text-sm mb-6">{error}</p>
            <Link
              href="/scan"
              className="bg-primary hover:bg-primary-dark text-white font-semibold px-6 py-3 rounded-lg transition-colors no-underline inline-block"
            >
              Scan Another Card
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const description = buildDescription(data);
  const evidence = buildEvidence(data);

  return (
    <div className="min-h-screen flex flex-col bg-dark-bg">
      <Header />

      <main className="flex-grow w-full max-w-7xl mx-auto px-6 py-10 flex flex-col gap-8">
        {/* Hero Result Section */}
        <section className="bg-dark-surface rounded-xl border border-dark-border overflow-hidden flex flex-col lg:flex-row relative shadow-lg animate-fade-in-up">
          {/* Left: Card Display */}
          <div className="lg:w-1/3 p-8 flex flex-col justify-center items-center border-b lg:border-b-0 lg:border-r border-dark-border bg-gradient-to-b from-dark-surface to-dark-bg/50 relative overflow-hidden">
            {/* Glow background */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.05),transparent)] pointer-events-none" />

            {data.matched_card.image_url ? (
              <div className="perspective-1000 z-10">
                <div className="preserve-3d animate-float transition-transform duration-500 hover:animate-none hover:scale-105 cursor-pointer">
                  <img
                    src={data.matched_card.image_url}
                    alt={data.matched_card.name || 'Card'}
                    className="w-56 rounded-xl shadow-2xl border-2 border-dark-border/50 animate-pulse-glow"
                  />
                  {/* Holographic overlay */}
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-tr from-transparent via-white/10 to-transparent mix-blend-overlay pointer-events-none" />
                </div>
              </div>
            ) : (
              <div className="w-56 h-80 bg-dark-border rounded-xl flex items-center justify-center">
                <span className="material-symbols-outlined text-6xl text-neutral-600">image_not_supported</span>
              </div>
            )}

            <p className="text-xs text-neutral-400 mt-4 uppercase tracking-widest font-semibold z-10">
              Analysis Complete
            </p>
          </div>

          {/* Right: Summary */}
          <div className="lg:w-2/3 p-8 flex flex-col justify-between relative z-10">
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">
                {data.matched_card.name || data.ocr_data.card_name || 'Unknown Card'}
              </h2>
              {data.matched_card.set_name && (
                <p className="text-sm text-neutral-400 mb-4">
                  {data.matched_card.set_name}
                  {data.matched_card.hp ? ` • HP ${data.matched_card.hp}` : ''}
                  {data.matched_card.types.length > 0 ? ` • ${data.matched_card.types.join('/')}` : ''}
                </p>
              )}
            </div>

            <div className="mt-4">
              <VerdictBadge
                verdict={data.verdict}
                confidence={data.scores.final_score}
                description={description}
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mt-6">
              <button className="flex-1 bg-primary hover:bg-primary-dark text-white font-semibold text-sm py-3 px-6 rounded-md flex items-center justify-center gap-2 transition-colors shadow-lg shadow-primary/20">
                <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>save</span>
                Save Result
              </button>
              <Link
                href="/scan"
                className="flex-1 border border-dark-border bg-dark-surface hover:bg-dark-border/50 text-white font-semibold text-sm py-3 px-6 rounded-md flex items-center justify-center gap-2 transition-colors no-underline"
              >
                <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>add_a_photo</span>
                Analyse Another
              </Link>
            </div>
          </div>
        </section>

        {/* Two Column Details */}
        <div className="flex flex-col xl:flex-row gap-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          {/* Left: Evidence */}
          <div className="w-full xl:w-3/5">
            <EvidenceCard evidence={evidence} />
          </div>

          {/* Right: Market + Recommendations */}
          <div className="w-full xl:w-2/5 flex flex-col gap-8">
            <PriceTable prices={prices} />

            {/* Recommendations */}
            <div className="bg-dark-surface rounded-lg border border-dark-border p-6">
              <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary" style={{ fontSize: '24px' }}>lightbulb</span>
                Recommendations
              </h4>
              <ul className="text-neutral-400 space-y-3 text-sm">
                {data.verdict === 'LIKELY_REAL' && (
                  <>
                    <li>• Consider professional grading (PSA/BGS) given high authenticity score.</li>
                    <li>• Store in a UV-protected, rigid sleeve immediately.</li>
                    <li>• Monitor market trends; compare prices across sources.</li>
                  </>
                )}
                {data.verdict === 'UNCERTAIN' && (
                  <>
                    <li>• Upload additional photos (back, angled) for improved analysis.</li>
                    <li>• Compare with known authentic examples before purchasing.</li>
                    <li>• Seek a second opinion from a professional grader.</li>
                  </>
                )}
                {data.verdict === 'SUSPICIOUS' && (
                  <>
                    <li>• Do NOT purchase this card without professional verification.</li>
                    <li>• Compare closely with authenticated examples side-by-side.</li>
                    <li>• Report suspected counterfeits to the marketplace platform.</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-info/10 border-l-4 border-info rounded-md p-4 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          <p className="text-sm text-blue-300">
            ⓘ This tool provides evidence-based guidance, not official grading. Always consult a professional grader for high-value cards.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
