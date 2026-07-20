interface EvidenceItem {
  name: string;
  status: 'pass' | 'fail' | 'caution' | 'neutral';
  confidence: number;
  description: string;
}

const statusConfig = {
  pass: { color: '#10B981', icon: '✓', label: 'OK' },
  fail: { color: '#EF4444', icon: '✗', label: 'Issue' },
  caution: { color: '#F59E0B', icon: '⚠', label: 'Review' },
  neutral: { color: '#6B7280', icon: '◇', label: 'N/A' },
};

export default function EvidenceCard({ evidence }: { evidence: EvidenceItem[] }) {
  return (
    <div>
      <h3 className="text-xl font-semibold text-white border-b border-dark-border pb-4 mb-4">
        Evidence Breakdown
      </h3>

      <div className="flex flex-col gap-4">
        {evidence.map((item, idx) => {
          const config = statusConfig[item.status];
          const pct = Math.round(item.confidence * 100);

          return (
            <div
              key={idx}
              className="bg-dark-surface rounded-lg border border-dark-border p-5 flex flex-col gap-3 hover:border-neutral-600 transition-colors"
            >
              {/* Header */}
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span
                    style={{ color: config.color }}
                    className="text-lg font-bold"
                  >
                    {config.icon}
                  </span>
                  <span className="font-semibold text-white text-sm">{item.name}</span>
                </div>
                <span
                  style={{ color: config.color }}
                  className="font-mono font-semibold text-sm"
                >
                  {pct}% Match
                </span>
              </div>

              {/* Description */}
              <p className="text-neutral-400 text-sm leading-relaxed">{item.description}</p>

              {/* Progress bar */}
              <div className="w-full bg-dark-border rounded-full h-1.5 mt-1">
                <div
                  style={{
                    backgroundColor: config.color,
                    width: `${pct}%`,
                    boxShadow: `0 0 5px ${config.color}80`,
                  }}
                  className="h-full rounded-full transition-all duration-500"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
