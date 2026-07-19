# PokeAuthAI MVP — Full Technical PRD

**Version:** 1.0  
**Date:** 2026-05-28  
**Duration:** 4 weeks (1 dev + AI assistance)  
**Status:** Ready for development

---

## 1. Executive Summary

PokeAuthAI is a Pokémon TCG card market intelligence & authenticity verification platform. Users scan/upload card photos. System:
1. Identifies the card (OCR + Pokémon TCG API match)
2. Verifies authenticity (rule-based + ML, 8 aspects)
3. Retrieves market prices across free sources
4. Shows verdict + price comparison dashboard

**Target users:** Casual collectors, resellers, educators  
**Not:** Official grading service (always disclaimed)

---

## 2. Product Goals (MVP)

By end of Week 4, system must:

1. Accept photo input via **upload OR tap-to-capture camera**
2. Identify card using **OCR + Pokémon TCG API v2**
3. Analyze 8 authenticity aspects (rule-based + ML)
4. Return verdict: `LIKELY_REAL` | `SUSPICIOUS` | `UNCERTAIN` | `INSUFFICIENT_EVIDENCE`
5. Fetch market prices from **≥1 free source** (Cardmarket primary, TCGPlayer secondary if legal)
6. Display result as **card metadata + auth badge + price table**
7. Mobile responsive (360px+)
8. Deploy to production (Vercel FE, Railway/Render BE)

**Out of scope (Phase 2+):**
- User accounts/history
- Real-time hologram detection
- Multi-language support
- Defect visualization
- Admin dashboard

---

## 3. Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL) — optional for MVP, can use JSON files for caching
- **ML/CV:** PyTorch, OpenCV, EasyOCR, ONNX Runtime
- **APIs:** Pokémon TCG API v2, Cardmarket API (free tier)
- **Deployment:** Railway or Render
- **Async:** asyncio, aiohttp (for parallel market price fetches)

### Frontend
- **Framework:** Next.js 15 (App Router)
- **UI:** React 19 + Tailwind CSS + shadcn/ui
- **Camera API:** Web API `getUserMedia`
- **Deployment:** Vercel
- **State:** React hooks (no Redux for MVP simplicity)

### Data
- **Model weights:** HuggingFace (hugginglearners/pokemon-card-checker ResNet34)
- **Ground truth:** Pokémon TCG API v2 (15,000+ official cards)
- **Market data cache:** JSON file (refresh daily or on-demand)

---

## 4. System Architecture

### 4.1 High-Level Flow

```
USER INPUT (Upload/Camera)
    ↓
PREPROCESSING (validate, normalize 300×420px)
    ↓
CARD IDENTIFICATION (OCR + TCG API match)
    ↓ (parallel)
┌─────────────────────┬──────────────────────┐
│ AUTHENTICITY CHECK  │  MARKET PRICE LOOKUP │
│ (8 aspects)         │  (Cardmarket, etc)   │
└─────────────────────┴──────────────────────┘
    ↓
ENSEMBLE SCORING (merge rule + ML)
    ↓
OUTPUT (verdict + prices + dashboard)
```

### 4.2 Backend Services Breakdown

```
pokeauthai-backend/
├─ app/
│  ├─ main.py                          # FastAPI app + routes
│  ├─ config.py                        # Settings, API keys, paths
│  ├─ routers/
│  │  ├─ scan.py                       # POST /v1/scan
│  │  ├─ result.py                     # GET /v1/result/{id}
│  │  ├─ health.py                     # GET /health
│  │  └─ market.py                     # GET /v1/market/{card_id}
│  ├─ services/
│  │  ├─ preprocessing.py              # Image crop, align, validate
│  │  ├─ ocr_service.py                # EasyOCR wrapper
│  │  ├─ tcg_api_service.py            # Pokémon TCG API client + caching
│  │  ├─ rule_detector.py              # OpenCV-based checks (7 aspects)
│  │  ├─ ml_service.py                 # PyTorch model inference
│  │  ├─ market_price_service.py       # Cardmarket, TCGPlayer scraping
│  │  ├─ ensemble.py                   # Score aggregation + verdict logic
│  │  └─ cache_manager.py              # JSON/Redis cache for market data
│  ├─ models/
│  │  ├─ schemas.py                    # Pydantic models (request/response)
│  │  └─ verdict.py                    # Enum: verdict types
│  ├─ ml/
│  │  ├─ model_loader.py               # Load ResNet34 from HF
│  │  ├─ print_quality_classifier.py   # Print texture detection
│  │  └─ hologram_classifier.py        # Hologram pattern detection
│  └─ utils/
│     ├─ logger.py                     # Logging setup
│     └─ validators.py                 # Input validation
├─ ml_models/                          # Model weights (gitignored, download on startup)
├─ cache/                              # JSON cache for market prices, TCG data
├─ tests/
│  ├─ test_ocr_service.py
│  ├─ test_rule_detector.py
│  ├─ test_ensemble.py
│  └─ test_golden_images.py            # Test with known cards
├─ requirements.txt
├─ Dockerfile
├─ .env.example
└─ README.md
```

---

## 5. Detailed Module Specifications

### 5.1 preprocessing.py

**Purpose:** Validate image quality, crop card region, normalize dimensions.

**Input:** PIL Image (from upload or camera)  
**Output:** Normalized image (300×420px) + metadata dict

**Functions:**
```python
def validate_image_quality(image: PIL.Image) -> bool:
    # Check: not blurry, proper exposure, not too dark/bright
    # Use Laplacian variance for blur detection
    # Return True if acceptable, else False

def crop_card_region(image: PIL.Image) -> PIL.Image:
    # Detect card boundaries using edge detection (Canny)
    # Crop to card region, ignore background
    # Return cropped image

def normalize_dimensions(image: PIL.Image) -> PIL.Image:
    # Resize to 300×420 (standard Pokémon card aspect ratio ~2.27:3)
    # Preserve aspect ratio, pad if needed
    # Return normalized image

def get_image_metadata(image: PIL.Image) -> dict:
    # Return: {width, height, aspect_ratio, file_size, brightness_avg, contrast}
```

**Error handling:**
- If blur detected: return `quality_warning: "Image too blurry"`
- If size too small: return `error: "Image too small (<200px width)"`
- If exposure bad: return `quality_warning: "Poor lighting"`

---

### 5.2 ocr_service.py

**Purpose:** Extract text fields from card (name, HP, text, ability).

**Input:** Image (front of card)  
**Output:** Dict with extracted fields + confidence scores

**Functions:**
```python
def extract_text(image: PIL.Image) -> dict:
    # Use EasyOCR to extract all visible text
    # Parse for patterns: "HP XXX", card name, ability text
    # Return: {
    #   card_name: str,
    #   hp: int | None,
    #   types: list[str],
    #   attack_names: list[str],
    #   ocr_confidence: float (0-1),
    #   raw_text: str,
    #   detected_fields: list[str]  # confidence per field
    # }

def parse_hp_from_text(text: str) -> int | None:
    # Regex pattern: "HP\s*(\d+)"
    # Return HP value or None if not found

def parse_card_name(text: str) -> str | None:
    # Heuristic: usually first significant text block
    # Filter out "Ability:", "Attack:", etc.
```

**Performance target:** ~1–2 sec per image  
**Language:** English only for MVP (non-Latin scripts deferred to Phase 3)

---

### 5.3 tcg_api_service.py

**Purpose:** Query Pokémon TCG API v2, cache results, retrieve ground truth card data.

**Input:** Card name (from OCR) + optional set filter  
**Output:** Card object with ID, HP, types, official image, rarity, etc.

**Functions:**
```python
def search_card(name: str, set_filter: str = None) -> Card | None:
    # Query https://api.pokemontcg.io/v2/cards?q=name:{name}
    # If multiple results, return closest match (fuzzy match on name)
    # If not found, return None
    # Cache result in JSON for 24 hours

def get_card_by_id(card_id: str) -> Card | None:
    # Direct lookup by Pokémon TCG ID
    # e.g., "sv04pt-1" for specific card

def get_official_image_url(card_id: str) -> str:
    # Return official card image URL from TCG API
    # Used as reference for comparison

class Card:
    id: str                    # e.g., "sv04pt-25"
    name: str                  # e.g., "Charizard ex"
    set_name: str              # e.g., "Scarlet & Violet"
    set_code: str              # e.g., "sv04pt"
    hp: int                    # 120, 230, etc.
    types: list[str]           # ["Fire"], ["Water", "Electric"]
    rarity: str                # "Rare", "Holo Rare", "VMAX"
    image_url: str             # Official image
    card_number: str           # e.g., "25/102"
    language: str              # "en", "jp", "ko"
```

**Error handling:**
- If card not found: return None (UI shows "Not found")
- If API rate limit: use cached data (graceful degradation)
- If API down: cached fallback

**Cache strategy:**
- Store in `cache/tcg_cards.json` (keyed by card_id)
- TTL: 7 days (refresh periodically)
- Initial load from API, subsequent requests from cache

---

### 5.4 rule_detector.py

**Purpose:** Implement rule-based checks via OpenCV (7 aspects, no ML).

**Input:** Processed image(s) + card metadata from TCG API  
**Output:** Dict with scores for each rule-based aspect

**Aspects & Logic:**

#### 1. **Print Quality** (Score: 0–1)
```python
def check_print_quality(image: np.ndarray) -> float:
    # Convert to grayscale, apply Laplacian sharpness filter
    # Check edge clarity, font definition
    # Return confidence: 0.0 (blurry) to 1.0 (perfect)
    # Threshold: >0.7 = PASS, 0.4–0.7 = SUSPICIOUS, <0.4 = FAIL
```

#### 2. **Text & HP Validation** (Score: 0–1) ⭐ HIGHEST WEIGHT
```python
def check_text_validation(ocr_hp: int, api_hp: int, 
                         ocr_types: list, api_types: list) -> float:
    # If HP mismatch: return 0.0 (FAIL — strong indicator of fake)
    # If types mismatch: return 0.3 (SUSPICIOUS)
    # If OCR confidence <0.6: return 0.5 (UNCERTAIN)
    # If all match: return 1.0 (PASS)
    # Weight: 25% of final score (most important)
```

#### 3. **Card Back Colour** (Score: 0–1)
```python
def check_card_back_colour(back_image: np.ndarray, 
                          reference_image_url: str) -> float:
    # Download reference image from TCG API
    # Compute histogram of back image
    # Compare histograms (L2 distance)
    # Threshold: distance <10 = PASS, 10–30 = SUSPICIOUS, >30 = FAIL
    # Return normalized score (1.0 - distance/50, clamped 0–1)
```

#### 4. **Card Dimensions** (Score: 0–1)
```python
def check_dimensions(image: np.ndarray) -> float:
    # Standard Pokémon card: 63mm × 88mm (aspect ratio ~2.27:3)
    # Measure image aspect ratio
    # Tolerance: ±5% deviation acceptable
    # Return: 1.0 if within tolerance, else <1.0 (scale proportionally)
```

#### 5. **Card Stock / Emboss** (Score: 0–1)
```python
def check_emboss_texture(image: np.ndarray) -> float:
    # Use Sobel edge detection to measure texture prominence
    # VMAX cards have embossed borders (higher edge strength)
    # Regular cards have smooth surface (lower edge strength)
    # Compare expected vs observed
    # Return confidence based on texture match
    # Note: May be N/A for non-holo cards
```

#### 6. **Card Back Pattern** (Score: 0–1)
```python
def check_back_pattern(back_image: np.ndarray, 
                       reference_image_url: str) -> float:
    # Use template matching (OpenCV matchTemplate)
    # Compare Pokéball swirl pattern on back
    # Return correlation score (0–1)
    # Threshold: >0.85 = PASS, 0.6–0.85 = SUSPICIOUS, <0.6 = FAIL
```

#### 7. **Font Anomaly** (Score: 0–1)
```python
def check_font_anomaly(ocr_confidence: float, 
                       ocr_text: str) -> float:
    # If OCR confidence <0.6 on key fields (name, HP): flag as anomaly
    # Check for unusual character spacing (via bounding boxes)
    # Return: 1.0 (normal), 0.5–0.7 (possible anomaly), <0.5 (strong anomaly)
```

**Output Format:**
```python
@dataclass
class RuleDetectionResult:
    print_quality: (score: float, label: str, detail: str)
    text_validation: (score: float, label: str, detail: str)
    card_back_colour: (score: float, label: str, detail: str)
    dimensions: (score: float, label: str, detail: str)
    emboss: (score: float, label: str, detail: str)
    card_back_pattern: (score: float, label: str, detail: str)
    font_anomaly: (score: float, label: str, detail: str)
    
    # Labels: "PASS", "FAIL", "SUSPICIOUS", "N/A"
```

---

### 5.5 ml_service.py

**Purpose:** Run pre-trained ML models for aspects 4 & 8 (hologram, print quality via CNN).

**Models used:**
1. **HuggingFace `hugginglearners/pokemon-card-checker`** (ResNet34, real/fake binary)
2. **Custom or pre-trained print quality CNN** (if available)
3. **Hologram classifier** (simple CNN for foil pattern)

**Functions:**
```python
def load_models() -> dict:
    # Download models from HuggingFace on startup
    # Load into ONNX Runtime or PyTorch
    # Return: {
    #   "binary_classifier": model,
    #   "print_quality": model,
    #   "hologram": model
    # }
    # Cache weights in ./ml_models/ locally

def infer_real_fake(image: np.ndarray) -> float:
    # Use binary classifier (ResNet34 from HF)
    # Return probability: 0.0 (fake) to 1.0 (real)
    # Note: This is redundant if rule-based is strong, but adds ML layer

def infer_print_quality_cnn(image: np.ndarray) -> float:
    # Alternative to OpenCV check using CNN
    # If time permits; otherwise fall back to rule-based only
    # Return confidence: 0–1

def infer_hologram(image: np.ndarray) -> float:
    # Classify hologram quality
    # Return: 0.0 (no holo / bad holo), 1.0 (good holo)
    # May return N/A if image doesn't contain hologram region
```

**Performance target:** <2 sec per image (CPU acceptable for MVP)

**Error handling:**
- If model fails to load: use rule-based only (graceful degradation)
- If model inference error: return None (aspect marked N/A)

---

### 5.6 market_price_service.py

**Purpose:** Fetch current market prices from free sources.

**Sources (MVP):**
1. **Cardmarket API** (primary, free tier available)
2. **TCGPlayer web scraping** (secondary, if legal cleared)

**Functions:**
```python
async def get_cardmarket_price(card_name: str, set_code: str) -> dict:
    # Query Cardmarket API for card
    # Return: {
    #   source: "Cardmarket",
    #   min_price: float,
    #   avg_price: float,
    #   max_price: float,
    #   currency: "EUR",
    #   timestamp: datetime,
    #   url: str,
    #   condition: "All"  # or specific condition
    # }
    # Handle: card not found, API down (return empty dict)

async def get_tcgplayer_price_scrape(card_name: str, set_code: str) -> dict:
    # Web scrape TCGPlayer (careful with TOS)
    # Return same format as Cardmarket
    # Optional: can skip in MVP if TOS risky

async def fetch_all_market_prices(card_id: str, card_name: str) -> list[dict]:
    # Call both services in parallel (asyncio.gather)
    # Return list of price dicts
    # Cache in JSON for 6 hours (prices change frequently)
    # Return empty list if all sources fail
```

**Caching Strategy:**
```python
# cache/market_prices.json
{
  "sv04pt-25": {  # Charizard ex
    "prices": [
      { "source": "Cardmarket", "avg": 45.50, "timestamp": "2026-05-28T..." },
      { "source": "TCGPlayer", "avg": 52.00, "timestamp": "2026-05-28T..." }
    ],
    "last_updated": "2026-05-28T12:00:00Z",
    "ttl_seconds": 21600  # 6 hours
  }
}
```

---

### 5.7 ensemble.py

**Purpose:** Combine rule-based + ML scores, apply weighting, generate final verdict.

**Weighting (tuned for reliability):**
```
Text & HP validation:        25%  (most critical — false positive if mismatch)
Print quality:               20%  (easier to detect on fakes)
Card back colour:            15%  (good indicator)
Hologram:                    15%  (strong if present)
Dimensions:                  10%  (consistent on fakes)
Font anomaly:                10%  (support indicator)
Card stock/emboss:           5%   (context-dependent)
```

**Functions:**
```python
def calculate_confidence_score(aspect_scores: dict) -> float:
    # aspect_scores: {
    #   "text_validation": 0.0,
    #   "print_quality": 0.3,
    #   "card_back_colour": 0.6,
    #   ...
    # }
    # Apply weights
    # Return: 0.0 (definitely fake) to 1.0 (definitely real)
    
    weights = {
        "text_validation": 0.25,
        "print_quality": 0.20,
        "card_back_colour": 0.15,
        "hologram": 0.15,
        "dimensions": 0.10,
        "font_anomaly": 0.10,
        "emboss": 0.05
    }
    
    score = sum(
        aspect_scores.get(aspect, 0.5) * weight
        for aspect, weight in weights.items()
    )
    return clamp(score, 0.0, 1.0)

def determine_verdict(confidence_score: float, 
                      num_photos: int) -> str:
    # Multi-photo boost: each additional photo increases confidence slightly
    # photo_boost = 1.0 + (num_photos - 1) * 0.05
    # adjusted_score = confidence_score * min(photo_boost, 1.2)
    
    if adjusted_score > 0.75:
        return "LIKELY_REAL"
    elif adjusted_score > 0.50:
        return "UNCERTAIN"
    elif adjusted_score > 0.25:
        return "SUSPICIOUS"
    else:
        return "INSUFFICIENT_EVIDENCE"
```

**Thresholds (MVP):**
- `LIKELY_REAL`: confidence > 0.75 (safe recommendation)
- `UNCERTAIN`: confidence 0.50–0.75 (needs more data)
- `SUSPICIOUS`: confidence 0.25–0.50 (warning flag)
- `INSUFFICIENT_EVIDENCE`: confidence < 0.25 (not enough info)

**Output:**
```python
@dataclass
class VerdictResult:
    verdict: str  # "LIKELY_REAL" | "UNCERTAIN" | "SUSPICIOUS" | "INSUFFICIENT_EVIDENCE"
    overall_confidence: float  # 0–1
    aspects: dict  # per-aspect breakdown
    recommendations: list[str]  # ["Upload hologram photo", "Check with official ref", ...]
    disclaimer: str  # "Not official authentication service..."
```

---

### 5.8 Pydantic Schemas (schemas.py)

**Request:**
```python
class ScanRequest(BaseModel):
    images: list[UploadFile]  # 1–5 files
    user_id: str | None = None  # Optional, for future login
    card_language: str = "en"  # Hints for OCR
    
class UploadFile(BaseModel):
    file: File
    photo_type: str  # "front", "back", "angle", "hologram", "cardback", "other"

class QueryMarketRequest(BaseModel):
    card_id: str  # e.g., "sv04pt-25"
```

**Response:**
```python
class ScanResponse(BaseModel):
    session_id: str  # UUID, for caching/retrieval
    card: CardInfo
    authenticity: AuthenticityResult
    market_prices: list[MarketPrice]
    verdict_summary: str  # Human-readable summary
    
class CardInfo(BaseModel):
    name: str
    set_name: str
    hp: int | None
    types: list[str]
    rarity: str
    image_url: str
    
class AuthenticityResult(BaseModel):
    verdict: str
    overall_confidence: float
    aspects: dict  # {aspect_name: {score, label, detail}}
    recommendations: list[str]
    
class MarketPrice(BaseModel):
    source: str  # "Cardmarket", "TCGPlayer"
    min_price: float
    avg_price: float
    max_price: float
    currency: str
    timestamp: datetime
    url: str
```

---

### 5.9 main.py (FastAPI App)

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import asyncio

app = FastAPI(title="PokeAuthAI", version="1.0")

@app.post("/v1/scan")
async def scan_card(files: list[UploadFile] = File(...)):
    """
    Endpoint: User uploads 1–5 card photos
    
    Process:
    1. Validate & preprocess each image
    2. OCR + card identification (use first valid image)
    3. Fetch official card data (TCG API)
    4. Parallel: rule-based checks + market price lookup
    5. Ensemble: generate verdict
    6. Return result
    
    Response: ScanResponse (JSON)
    """
    try:
        # Validate input
        if len(files) == 0 or len(files) > 5:
            return JSONResponse({"error": "1–5 files required"}, status_code=400)
        
        # Process images
        results = {}
        for file in files:
            image = await preprocess(file)
            if not image:
                continue
            
            # OCR (once is enough for card ID)
            if "card_name" not in results:
                ocr_result = ocr_service.extract_text(image)
                results["card_name"] = ocr_result.get("card_name")
                results["ocr_confidence"] = ocr_result.get("confidence")
        
        # Card identification
        card = tcg_api_service.search_card(results["card_name"])
        if not card:
            return JSONResponse({"error": "Card not found"}, status_code=404)
        
        # Parallel: auth check + market prices
        auth_task = asyncio.create_task(run_auth_checks(images, card))
        market_task = asyncio.create_task(market_price_service.fetch_all_market_prices(card.id, card.name))
        
        auth_result, market_prices = await asyncio.gather(auth_task, market_task)
        
        # Ensemble
        verdict = ensemble.determine_verdict(auth_result)
        
        # Build response
        return ScanResponse(
            session_id=str(uuid4()),
            card=card,
            authenticity=auth_result,
            market_prices=market_prices,
            verdict_summary=generate_summary(verdict, market_prices)
        )
    
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return JSONResponse({"error": "Processing failed"}, status_code=500)

@app.get("/v1/result/{session_id}")
async def get_result(session_id: str):
    """Retrieve cached result (if caching enabled in future)"""
    # For MVP: results are ephemeral (returned immediately, not stored)
    # Phase 2: add Supabase storage + retrieval
    return JSONResponse({"error": "Use scan endpoint"}, status_code=501)

@app.get("/v1/market/{card_id}")
async def get_market_price(card_id: str):
    """Get current market prices for a card"""
    prices = await market_price_service.fetch_all_market_prices(card_id)
    return {"card_id": card_id, "prices": prices}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}
```

---

## 6. Data Flow & Integration

### 6.1 Complete User Journey (Happy Path)

```
1. User taps camera → Photo captured
2. Image sent to /v1/scan endpoint
3. Backend preprocessing: validate, crop, normalize
4. EasyOCR extracts text (card name, HP, etc.)
5. TCG API queries: find matching card
6. If not found: return 404
7. If found: launch parallel tasks:
   - Task A: Rule-based checks (OpenCV, 7 aspects)
   - Task B: Market price fetch (Cardmarket + TCGPlayer)
8. Both tasks complete → Ensemble scoring
9. Generate verdict + recommendations
10. Return ScanResponse (card + auth + prices)
11. Frontend displays result dashboard
```

### 6.2 Error Handling

| Scenario | Handling |
|---|---|
| Image too blurry | Reject, ask for clearer photo |
| Card not found in TCG API | Return 404, suggest alternatives |
| OCR fails (no text detected) | Return INSUFFICIENT_EVIDENCE, ask for front photo |
| Market API down | Return prices=[empty], show note "Prices unavailable" |
| ML model load fails | Fall back to rule-based only |
| Processing timeout (>10 sec) | Return 408, suggest retry |

---

## 7. Deployment & Infrastructure

### 7.1 Backend Deployment (Railway or Render)

```
Environment Variables:
- POKEMONTCG_API_KEY= (if required)
- CARDMARKET_API_KEY= (if required)
- LOG_LEVEL=INFO
- CACHE_TTL=86400 (seconds)

Docker:
- Python 3.11 slim base
- Install requirements.txt
- Download models on startup
- Expose port 8000
```

### 7.2 Frontend Deployment (Vercel)

```
Environment Variables:
- NEXT_PUBLIC_API_BASE_URL=https://backend.railway.app
- NEXT_PUBLIC_APP_NAME=PokeAuthAI

Auto-deploys from GitHub main branch
```

### 7.3 Caching Strategy

```
Local JSON files (MVP):
- cache/tcg_cards.json (7-day TTL)
- cache/market_prices.json (6-hour TTL)
- cache/model_weights/ (permanent, except on update)

Future (Phase 2):
- Redis for distributed cache
- Supabase for persistent storage
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# test_ocr_service.py
def test_extract_hp_from_charizard():
    assert ocr_service.parse_hp_from_text("HP 230") == 230

def test_extract_hp_mismatch():
    # Fake shows HP 280, real is 230
    assert ensemble.check_text_validation(280, 230, ...) == 0.0

# test_rule_detector.py
def test_print_quality_sharp_image():
    score = rule_detector.check_print_quality(sharp_image)
    assert score > 0.7

def test_card_dimensions():
    score = rule_detector.check_dimensions(standard_card)
    assert score > 0.9

# test_ensemble.py
def test_verdict_likely_real():
    aspects = {
        "text_validation": 1.0,
        "print_quality": 0.9,
        "card_back_colour": 0.85,
        # ...
    }
    assert ensemble.determine_verdict(aspects) == "LIKELY_REAL"
```

### 8.2 Integration Tests

```python
# test_golden_images.py
def test_scan_known_real_card():
    # Use Charizard ex official image
    result = api_client.post("/v1/scan", files=[charizard_real_image])
    assert result.verdict == "LIKELY_REAL"
    assert result.confidence > 0.75

def test_scan_known_fake_card():
    # Use annotated fake Charizard
    result = api_client.post("/v1/scan", files=[charizard_fake_image])
    assert result.verdict == "SUSPICIOUS" or "UNLIKELY_REAL"
    assert result.confidence < 0.5
```

### 8.3 Load Testing

```
Simple k6 test:
- Simulate 10 concurrent users
- Each uploads 1 card photo
- Measure response time (target: <5 sec)
- No 5xx errors expected
```

---

## 9. Performance Targets (MVP)

| Component | Target |
|---|---|
| Image preprocessing | <500ms |
| OCR extraction | 1–2 sec |
| TCG API lookup (cached) | <100ms |
| Rule-based checks | 500ms–1 sec |
| ML inference | 1–2 sec (CPU) |
| Market price fetch | 1–2 sec (parallel) |
| **Total E2E latency** | **3–5 sec** |
| Simultaneous users | 10+ (Railway free tier) |

---

## 10. Phase 1 Implementation Breakdown (Week 1)

### Day 1–2: Setup & Core Infrastructure
- [ ] GitHub repo + branch strategy
- [ ] FastAPI skeleton with health endpoint
- [ ] Docker setup
- [ ] Config management (.env, settings)
- [ ] Logging infrastructure
- [ ] Pydantic schemas (ScanRequest, ScanResponse)

**Deliverable:** `GET /health` returns 200

### Day 3–4: Pokémon TCG API Integration
- [ ] TCG API client (search_card, get_card_by_id)
- [ ] JSON caching (cache/tcg_cards.json)
- [ ] Test with 5 known cards
- [ ] Error handling (card not found, API down)

**Deliverable:** `GET /v1/market/{card_id}` returns card metadata

### Day 5: Image Preprocessing + OCR
- [ ] preprocessing.py (validate, crop, normalize)
- [ ] ocr_service.py (EasyOCR integration)
- [ ] Parse HP, card name, types
- [ ] Test with sample Charizard image

**Deliverable:** OCR extracts HP from image correctly, matches TCG API

**End of Week 1:**
- [ ] `POST /v1/scan` accepts image file
- [ ] Returns card identification + raw OCR data
- [ ] No auth checks yet, just ID

---

## 11. Phase 2–4 Implementation (Weeks 2–4)

*See separate weekly breakdown document* — each week covers rule-based completion, ML integration, market prices, frontend, and camera.

---

## 12. Key Decisions & Rationale

| Decision | Rationale |
|---|---|
| **Use pre-trained ResNet34 from HF** | No time to train from scratch; pre-trained model is 70% of value with 10% effort |
| **Rule-based first, ML second** | Rules deliver immediate value; ML is enhancement layer |
| **Cardmarket API as primary market source** | Free tier, good coverage, reliable API |
| **No user auth in MVP** | Adds 2–3 days of work; Phase 2 feature |
| **Tap-to-capture camera (not real-time)** | Simpler implementation, avoids FPS pressure |
| **JSON cache instead of Supabase** | Faster MVP iteration; add DB in Phase 2 |
| **Docker from start** | Ensures consistent deployment, saves troubleshooting later |
| **Thresholds (0.75, 0.50, 0.25)** | Conservative to avoid false "REAL" verdicts (better safe than sorry) |

---

## 13. Acceptance Criteria (MVP Complete)

- ✅ System accepts photo upload OR tap-to-capture camera
- ✅ Card identified via OCR + TCG API (tested with 10+ known cards)
- ✅ All 8 authenticity aspects analyzed (rule-based + ML)
- ✅ Verdict returned (LIKELY_REAL, SUSPICIOUS, UNCERTAIN, INSUFFICIENT_EVIDENCE)
- ✅ Market prices fetched from ≥1 free source
- ✅ Result dashboard shows card + auth badge + price table
- ✅ Mobile responsive (tested on 360px–1024px widths)
- ✅ Latency <5 sec (85% of requests)
- ✅ Zero 5xx errors on happy path
- ✅ Disclaimer prominent ("Not official authentication")
- ✅ Backend deployed to Railway/Render
- ✅ Frontend deployed to Vercel
- ✅ Code on GitHub with README
- ✅ Test coverage >60% (key modules)

---

## 14. Known Limitations & Phase 2+ Scope

### Not in MVP (Why? When?)

| Feature | Why not | Phase |
|---|---|---|
| Real-time hologram detection | Edge cases, multi-frame processing complexity | 2 |
| User login & history | Auth system overhead; not critical for MVP | 2 |
| Multi-language OCR | Needs separate training per language; 1–2 weeks | 3 |
| Admin dashboard | No backend monitoring needed yet | 2 |
| Defect visualization | UI complexity; not essential for verdict | 3 |
| Professional grading API | Paywalls; not feasible | Never |
| Community dataset submissions | Governance model needed; Phase 4+ | 4 |
| Trend forecasting | Need 6+ months data history | 5+ |

---

## 15. Success Metrics (By end of Week 4)

**Quantitative:**
- 100+ test scans processed without error
- 95%+ card identification accuracy (on known cards)
- <5 sec latency for 90% of requests
- 0 5xx errors on happy path

**Qualitative:**
- Code review ready (no major refactoring)
- Deployable to production (Docker works)
- User can complete full flow in <30 sec
- Results feel accurate vs. manual inspection

---

*End of Technical PRD. Ready for Week 1 implementation.*
