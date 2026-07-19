# PokeAuthAI MVP v2 — Scope Clarity & Timeline

**Project:** Market Intelligence + Authenticity Checker untuk Pokémon TCG  
**Duration:** 4 weeks (1 dev + AI Agent assistance)  
**Status:** Pre-development clarification document

---

## A. Card Identification & Metadata ✅

### Decision:
- **Use Pokémon TCG API v2** untuk ground truth card database (15.000+ official cards)
- **Not found case:** Show "Card not found in official database" → suggest manual entry or similar card
- **Scope:** English cards first, other languages Phase 2+

---

## B. Market Price Sources 🔍

### Decision: Free/Open sources only (MVP stage)

**Feasible for 4 weeks:**

| Source | Type | Free Tier | Reliability | Implementation Effort |
|---|---|---|---|---|
| **TCGPlayer** | Official API | ❌ Paid only | ⭐⭐⭐⭐⭐ | Medium (need key) |
| **Cardmarket** | API + Web | ✅ Free tier exists | ⭐⭐⭐⭐ | Medium |
| **eBay** | Scraping (TOS risk) | ⚠️ Limited | ⭐⭐⭐ | High + legal gray |
| **Sakura Shop** | Manual/Scraping | ❌ Not practical | ⭐⭐⭐ | High |
| **Scryfall-style aggregators** | Community data | ✅ Free | ⭐⭐⭐ | Low-Medium |
| **TCGPrice (if exists)** | Crowdsourced | ✅ Free | ⭐⭐ | Unknown |
| **Reddit/Community posts** | Manual mining | ✅ Free | ⭐⭐ | Very high effort |

### MVP Recommendation:
**Phase 1 (Week 2–3):**
1. **Cardmarket API** (free tier, good coverage for EU)
2. **TCGPlayer web scraping** (careful, TOS edge case — use sparingly)

**Phase 2 (future):**
- TCGPlayer official API (if monetizing)
- eBay API (if legal cleared)
- Integrate more regional markets

---

## C. Authenticity Scope (4 weeks) 🔍

### Decision: Full 8-aspect analysis WITH realistic MVP caveats

**8 Aspects to implement:**

1. ✅ **Print Quality** (CNN texture analysis) — Medium complexity
2. ✅ **Text & HP Validation** (OCR vs TCG API) — Low complexity ⭐ PRIORITY
3. ✅ **Card Back Colour** (histogram matching) — Low complexity
4. ✅ **Hologram Effect** (visual pattern detection, not real-time) — Medium complexity
5. ✅ **Card Dimensions** (aspect ratio + contour detection) — Low complexity
6. ✅ **Card Stock/Emboss** (edge detection) — Medium complexity
7. ✅ **Card Back Pattern** (template matching) — Medium complexity
8. ✅ **Font Anomaly** (OCR confidence + NLP) — Medium complexity

### Reality check for 4 weeks:
- **Rule-based** (1–3, 5–7): Can implement all in 2–3 weeks (OpenCV mostly)
- **ML-based** (4, 8): Stretch goal; pre-trained models help a lot
- **Pre-trained models:** Use HuggingFace `hugginglearners/pokemon-card-checker` (ResNet34) as baseline

### What's NOT in MVP (explain why):

| Feature | Why not in MVP | When? |
|---|---|---|
| **Real-time hologram detection via camera** | Requires: (1) multi-frame processing, (2) angle calibration, (3) lighting normalization. Too many edge cases. Scope creep risk. | Phase 2 (Week 5+) |
| **Multi-language OCR** (JP, KR, ID) | TCG API v2 has EN cards mostly; OCR training for non-Latin scripts takes extra 1–2 weeks. | Phase 3 (Week 9+) |
| **Defect mapping** (visualize exact location of fake markers on card) | Complex UI + backend; not critical for MVP verdict. | Phase 3 |
| **User community voting** (crowdsourced auth) | Requires auth system + reputation tracking. Out of scope. | Phase 4+ (monetization) |
| **Professional grading comparison** (PSA/BGS/CGC data) | APIs locked behind paywalls or TOS restrictions. | Not planned |
| **Trend forecasting** (predict price spike) | Requires 6+ months historical data. Don't have it. | Phase 5+ (when data exists) |
| **Blockchain provenance** | Overkill for MVP; not user-requested. | Never (unless pivoting to Web3) |

---

## D. Camera Feature 📷

### Decision: Simple tap-to-capture for MVP

**Implementation:**
- Tap button → Open device camera
- Take photo → Auto-process (no real-time feedback)
- Fallback to upload if camera access denied

**FPS/Performance realistic estimate:**
- **Real-time preview FPS:** Not needed (single-frame processing, tap-to-capture)
- **Processing FPS:** ~0.5–1 FPS (3–5 sec per photo is acceptable for user)
  - Image resize: 50ms
  - OCR: 1–2 sec
  - CV checks: 500ms
  - ML inference: 1–2 sec (depends on GPU, likely CPU on mobile browser)
- **Total expected latency:** 3–5 seconds per photo → UX shows loader
- **Mobile browser limitation:** WebGL/WASM can run CV + ML client-side, but slow. Backend processing is more reliable.

**MVP camera flow:**
```
Tap camera icon 
  → Open device camera (Web API: getUserMedia)
  → User frames card + taps capture
  → Send photo to backend
  → Process (3–5 sec) + return verdict
  → Show results table
```

**NOT in MVP:**
- Real-time card outline detection (augmented reality)
- Batch multi-photo processing (sequential is fine)
- HDR or image stacking
- All resolved in Phase 2+

---

## E. Team & Timeline ✅

### Team Structure:
**1 dev (you) + AI Agent (Claude) assistance**

This is realistic if:
- You focus on **architecture decisions** + **integration**
- Claude handles **boilerplate code generation** + **debugging**
- Scope stays **tightly focused** (no feature creep)

### 4-Week Realistic Timeline

```
WEEK 1: Foundation & Backend Core
├─ Day 1–2: Project setup (FastAPI, Supabase, GitHub)
├─ Day 3–4: Pokémon TCG API integration + OCR pipeline
├─ Day 5: Rule-based detector (dimensions, card back colour)
└─ Deliverable: API endpoint POST /v1/scan working with rules only

WEEK 2: Rule-based Completion & First Market Integration
├─ Day 1–2: Complete rule-based checks (text validation, pattern matching, emboss)
├─ Day 3–4: Integrate Cardmarket free API for price lookup
├─ Day 5: Ensemble scoring logic (weight per aspect)
└─ Deliverable: /v1/scan returns verdict + 1 market price source

WEEK 3: ML + Frontend Start
├─ Day 1–2: Load pre-trained model (HuggingFace) + integrate hologram + print quality
├─ Day 3–4: Next.js frontend: upload page + result dashboard
├─ Day 5: Camera integration (simple tap-to-capture)
└─ Deliverable: Full end-to-end flow working (upload → verdict → prices)

WEEK 4: Polish & Second Market Source
├─ Day 1–2: Add 2nd market price source (e.g., TCGPlayer scraping if legal cleared)
├─ Day 3–4: UI refinements (Pokéball colours, responsive design, loading states)
├─ Day 5: Testing, documentation, deploy
└─ Deliverable: MVP launch-ready
```

### Realistic velocity:
- **Week 1–2:** High output (setup is fast, rules are straightforward)
- **Week 3:** Medium output (ML integration + frontend takes time; camera adds 1–2 days)
- **Week 4:** Delivery push (polish + bugfix)

### Risk factors:
- ⚠️ **If Cardmarket/TCGPlayer API integration is slow:** Reduce to 1 market source in MVP
- ⚠️ **If ML model loading is problematic:** Fall back to rule-based only (still 85% of value)
- ⚠️ **If camera causes TLS/HTTPS issues on localhost:** Remove camera from MVP, add Week 5 as stretch

---

## Success Criteria for MVP

By end of Week 4:

1. ✅ User can upload photo OR tap camera to capture
2. ✅ System identifies card from photo (OCR + TCG API match)
3. ✅ Authenticity verdict shown (8 aspects analyzed, rule-based + ML)
4. ✅ Market prices from ≥1 free source integrated
5. ✅ Result shown as table: Card | Auth Status | Price Source A | Price Source B | Your card value estimate
6. ✅ Mobile responsive (360px+)
7. ✅ Disclaimer visible (not official authentication)
8. ✅ Code deployed (Vercel for frontend, Railway/Render for backend)

---

## Things We're NOT doing (scope out):

- ❌ User accounts / history saving (Phase 2)
- ❌ Admin dashboard (Phase 2)
- ❌ Community submissions (Phase 3)
- ❌ Real-time hologram camera detection (Phase 2)
- ❌ Blockchain / NFT integration (Never, probably)
- ❌ Multiple language support (Phase 3)
- ❌ Professional grading API (Never, locked)
- ❌ Defect visualization (Phase 3)

---

## Next Steps

Once you confirm this scope:
1. Aku bikin **full technical PRD** (Phase 1: Backend architecture + Phase 2: Frontend spec)
2. Break down setiap modul (reader.py, validator.py, aggregator.py, dll)
3. Prepare Claude Code prompts untuk masing-masing component
4. Start Week 1 dengan confident scope & timeline

---

**Ready?** Atau ada pertanyaan lagi sebelum we lock this down?
