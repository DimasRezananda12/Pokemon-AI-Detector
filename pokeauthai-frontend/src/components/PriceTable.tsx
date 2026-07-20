import type { PriceData } from '@/lib/api';

export default function PriceTable({ prices }: { prices: PriceData[] }) {
  const available = prices.filter(p => p.status === 'available');

  if (available.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-semibold text-white border-b border-dark-border pb-4 mb-4">
          Current Market Prices
        </h3>
        <div className="bg-dark-surface rounded-lg border border-dark-border p-6 text-center">
          <p className="text-neutral-400 text-sm">Market pricing data is currently unavailable.</p>
        </div>
      </div>
    );
  }

  // Compute average market price
  const marketPrices = available.filter(p => p.market != null).map(p => p.market!);
  const avgMarket = marketPrices.length > 0
    ? marketPrices.reduce((a, b) => a + b, 0) / marketPrices.length
    : null;

  return (
    <div>
      <h3 className="text-xl font-semibold text-white border-b border-dark-border pb-4 mb-4">
        Current Market Prices
      </h3>

      <div className="bg-dark-surface rounded-lg border border-dark-border p-6">
        {/* Table header */}
        <div className="flex justify-between mb-4 pb-3 border-b border-dark-border">
          <span className="text-xs text-neutral-400 uppercase tracking-widest font-semibold">Source</span>
          <span className="text-xs text-neutral-400 uppercase tracking-widest font-semibold">Price Range</span>
        </div>

        {/* Price rows */}
        <div className="flex flex-col gap-3">
          {available.map((price, idx) => (
            <div
              key={idx}
              className="flex justify-between items-center bg-dark-bg/50 p-3 rounded-md border border-dark-border/50"
            >
              <div>
                <span className="text-neutral-200 text-sm capitalize">{price.source}</span>
                <span className="text-neutral-400 text-xs ml-2">({price.currency})</span>
              </div>
              <div className="flex gap-4 font-mono text-sm">
                {price.low != null && (
                  <span className="text-neutral-400">
                    Low: <span className="text-white">${price.low.toFixed(2)}</span>
                  </span>
                )}
                {price.market != null && (
                  <span className="text-neutral-400">
                    Market: <span className="text-white font-semibold">${price.market.toFixed(2)}</span>
                  </span>
                )}
                {price.high != null && (
                  <span className="text-neutral-400">
                    High: <span className="text-white">${price.high.toFixed(2)}</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Average */}
        {avgMarket != null && (
          <div className="mt-4 pt-4 border-t border-dark-border flex justify-between items-center bg-primary/10 p-4 rounded-md border border-primary/20">
            <span className="font-semibold text-white">Average Estimate</span>
            <span
              className="font-mono text-primary font-bold text-xl"
              style={{ filter: 'drop-shadow(0 0 5px rgba(230, 57, 70, 0.3))' }}
            >
              ${avgMarket.toFixed(2)}
            </span>
          </div>
        )}

        {/* Link to source */}
        {available[0]?.url && (
          <div className="mt-3 text-right">
            <a
              href={available[0].url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-secondary hover:underline"
            >
              View on {available[0].source} →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
