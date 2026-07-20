import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-dark-bg">
      <Header />

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24 max-w-4xl mx-auto gap-6">
        <h1 className="text-3xl md:text-4xl font-bold text-white leading-tight tracking-tight">
          Card Analysis &amp; Market Intelligence
        </h1>
        <p className="text-neutral-400 max-w-2xl text-base leading-relaxed">
          Leverage advanced optical recognition and real-time market data for evidence-based card evaluation and pricing guidance.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 mt-8">
          <Link
            href="/scan"
            className="bg-primary hover:bg-primary-dark text-white font-semibold px-6 py-3 rounded-lg transition-colors shadow-lg shadow-primary/20 flex items-center gap-2 no-underline"
          >
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>
              document_scanner
            </span>
            Scan Your Card
          </Link>
          <Link
            href="/results"
            className="bg-dark-surface hover:bg-dark-border text-white font-semibold px-6 py-3 rounded-lg transition-colors border border-dark-border flex items-center gap-2 no-underline"
          >
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>
              analytics
            </span>
            View My Results
          </Link>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 bg-info/10 border-l-4 border-info rounded-md p-4 max-w-xl text-left">
          <p className="text-sm text-blue-300">
            ⓘ This tool provides evidence-based guidance, not official grading. Always consult a professional grader for high-value cards.
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6 bg-dark-surface">
        <div className="max-w-7xl mx-auto flex flex-col gap-12">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-white">Systematic Evaluation Process</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connecting line (desktop) */}
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-px bg-dark-border -z-10 -translate-y-12" />

            {/* Step 1 */}
            <div className="bg-dark-bg border border-dark-border rounded-lg p-6 flex flex-col items-center text-center gap-4 shadow-sm relative">
              <div className="w-12 h-12 rounded-full bg-dark-border text-neutral-400 flex items-center justify-center font-bold text-lg border-4 border-dark-bg shadow-sm">
                1
              </div>
              <span className="material-symbols-outlined text-4xl text-secondary" style={{ fontVariationSettings: "'FILL' 0" }}>
                upload
              </span>
              <h3 className="font-semibold text-white">High-Res Upload</h3>
              <p className="text-neutral-400 text-sm">
                Submit clear, well-lit images of the front for optimal optical recognition.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-dark-bg border border-dark-border rounded-lg p-6 flex flex-col items-center text-center gap-4 shadow-sm relative">
              <div className="w-12 h-12 rounded-full bg-dark-border text-neutral-400 flex items-center justify-center font-bold text-lg border-4 border-dark-bg shadow-sm">
                2
              </div>
              <span className="material-symbols-outlined text-4xl text-secondary" style={{ fontVariationSettings: "'FILL' 0" }}>
                psychology
              </span>
              <h3 className="font-semibold text-white">Algorithmic Analysis</h3>
              <p className="text-neutral-400 text-sm">
                Our models evaluate text, attributes, and patterns against a vast database.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-dark-bg border border-dark-border rounded-lg p-6 flex flex-col items-center text-center gap-4 shadow-sm relative">
              <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-lg border-4 border-dark-bg shadow-sm">
                3
              </div>
              <span className="material-symbols-outlined text-4xl text-primary" style={{ fontVariationSettings: "'FILL' 0" }}>
                data_thresholding
              </span>
              <h3 className="font-semibold text-white">Intelligence Report</h3>
              <p className="text-neutral-400 text-sm">
                Receive a detailed breakdown of condition metrics and aggregated market pricing data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Use PokeAuthAI */}
      <section className="py-20 px-6 bg-dark-bg">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-16 items-center">
          <div className="w-full md:w-1/2 flex flex-col gap-6">
            <h2 className="text-xl font-semibold text-white">Data-Driven Market Intelligence</h2>
            <p className="text-neutral-400 text-sm mb-4 leading-relaxed">
              Remove subjectivity from card evaluation. Our system aggregates data points to provide actionable insights for collectors and investors.
            </p>
            <ul className="flex flex-col gap-4">
              {[
                { title: 'Evidence-Based Scoring', desc: 'Objective metrics applied consistently across all submissions.' },
                { title: 'Real-Time Market Data', desc: 'Valuations cross-referenced with recent verified sales channels.' },
                { title: 'Condition Profiling', desc: 'Detailed sub-grade analysis identifying specific anomalies.' },
              ].map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-success mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>
                    check_circle
                  </span>
                  <div>
                    <strong className="block text-white text-sm font-semibold">{item.title}</strong>
                    <span className="text-neutral-400 text-sm">{item.desc}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Abstract chart */}
          <div className="w-full md:w-1/2">
            <div className="bg-dark-surface border border-dark-border rounded-xl p-8 shadow-md">
              <div className="flex justify-between items-end h-48 gap-2 border-b border-dark-border pb-4">
                {[12, 24, 16, 32, 40, 28].map((h, i) => (
                  <div
                    key={i}
                    className={`w-1/6 rounded-t-sm ${i === 4 ? 'bg-primary' : i === 3 ? 'bg-secondary' : 'bg-dark-border'}`}
                    style={{ height: `${h * 2.5}%` }}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-4 font-mono text-xs text-neutral-400">
                <span>Q1</span><span>Q2</span><span>Q3</span><span>Q4</span><span>YTD</span><span>PROJ</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
