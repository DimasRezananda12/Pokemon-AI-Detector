interface VerdictBadgeProps {
  verdict: string;
  confidence: number;
  description: string;
}

const verdictConfig: Record<string, {
  color: string; bgColor: string; icon: string; label: string; glowColor: string;
}> = {
  'LIKELY_REAL': {
    color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.1)', icon: '✓',
    label: 'Authentic', glowColor: 'rgba(16, 185, 129, 0.5)',
  },
  'UNCERTAIN': {
    color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.1)', icon: '⚠',
    label: 'Needs Review', glowColor: 'rgba(245, 158, 11, 0.5)',
  },
  'SUSPICIOUS': {
    color: '#EF4444', bgColor: 'rgba(239, 68, 68, 0.1)', icon: '✗',
    label: 'Likely Counterfeit', glowColor: 'rgba(239, 68, 68, 0.5)',
  },
  'INSUFFICIENT_EVIDENCE': {
    color: '#6B7280', bgColor: 'rgba(107, 114, 128, 0.1)', icon: '◇',
    label: 'Inconclusive', glowColor: 'rgba(107, 114, 128, 0.5)',
  },
};

export default function VerdictBadge({ verdict, confidence, description }: VerdictBadgeProps) {
  const config = verdictConfig[verdict] || verdictConfig['INSUFFICIENT_EVIDENCE'];
  const pct = Math.round(confidence * 100);

  return (
    <div
      style={{ backgroundColor: config.bgColor, borderColor: `${config.color}33` }}
      className="rounded-xl p-6 border"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <span
          style={{ color: config.color, filter: `drop-shadow(0 0 8px ${config.glowColor})` }}
          className="text-3xl font-bold"
        >
          {config.icon}
        </span>
        <h2
          style={{ color: config.color, filter: `drop-shadow(0 0 5px ${config.glowColor})` }}
          className="text-2xl font-bold"
        >
          {config.label}
        </h2>
      </div>

      {/* Description */}
      <p className="text-sm text-neutral-400 mb-5 leading-relaxed">{description}</p>

      {/* Confidence Bar */}
      <div>
        <div className="flex justify-between items-end mb-2">
          <span className="text-xs text-neutral-400 uppercase tracking-widest font-semibold">
            Overall Confidence
          </span>
          <span
            style={{ color: config.color, filter: `drop-shadow(0 0 5px ${config.glowColor})` }}
            className="font-mono font-bold text-lg"
          >
            {pct}%
          </span>
        </div>
        <div className="w-full bg-dark-border rounded-full h-2.5 overflow-hidden shadow-inner">
          <div
            style={{
              backgroundColor: config.color,
              width: `${pct}%`,
              boxShadow: `0 0 10px ${config.glowColor}`,
            }}
            className="h-full rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-white/20 w-full animate-shimmer" />
          </div>
        </div>
      </div>
    </div>
  );
}
