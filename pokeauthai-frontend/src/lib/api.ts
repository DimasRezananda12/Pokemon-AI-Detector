const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ScanResponse {
  session_id: string;
  status: string;
  verdict: string;
  scores: {
    ocr_confidence: number;
    visual_quality: number;
    rule_match: number;
    final_score: number;
  };
  ocr_data: {
    card_name: string | null;
    hp: number | null;
    types: string[];
    raw_text: string;
  };
  matched_card: {
    id: string | null;
    name: string | null;
    set_name: string | null;
    hp: number | null;
    types: string[];
    image_url: string | null;
  };
  anomalies: string[];
  warnings: string[];
}

export interface PriceData {
  source: string;
  currency: string;
  low: number | null;
  mid: number | null;
  high: number | null;
  market: number | null;
  url: string | null;
  status: string;
}

export interface MarketResponse {
  card: Record<string, unknown>;
  pricing: PriceData[];
}

export async function scanCard(file: File): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/v1/scan`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Scan failed' }));
    throw new Error(err.detail || 'Scan failed');
  }
  return response.json();
}

export async function getResult(sessionId: string): Promise<ScanResponse> {
  const response = await fetch(`${API_BASE}/v1/result/${sessionId}`);
  if (!response.ok) throw new Error('Result not found');
  return response.json();
}

export async function getMarketPrices(cardId: string): Promise<MarketResponse> {
  const response = await fetch(`${API_BASE}/v1/market/${cardId}`);
  if (!response.ok) throw new Error('Prices not available');
  return response.json();
}
