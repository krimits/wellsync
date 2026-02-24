# WellSync — Τεχνική Σχεδίαση
## Φ3 Παραδοτέο | Ανάπτυξη Εφαρμογών Πληροφοριακών Συστημάτων, AUEB 2026

**Διδάσκων**: Ι. Κωτίδης
**Ομάδα**: [ΣΥΜΠΛΗΡΩΣΕ ΟΝΟΜΑΤΑ]
**Ημερομηνία**: Απρίλιος 2026
**Έκδοση**: 1.0

---

## 1. Εισαγωγή & Σύνοψη

**WellSync** είναι μια AI-powered εφαρμογή ολιστικής ευεξίας που απευθύνεται σε
φοιτητές και νέους ενήλικες (18–30). Ενοποιεί τρεις τομείς — φυσική δραστηριότητα,
διατροφή και ψυχική κατάσταση — και χρησιμοποιεί personalized ML μοντέλα για να
ανακαλύπτει ατομικά πρότυπα και να παρέχει προσαρμοστικές ημερήσιες συστάσεις.

### Το Πρόβλημα

Οι υπάρχουσες εφαρμογές ευεξίας είναι κατακερματισμένες: το MyFitnessPal καλύπτει
τη διατροφή, το Strava την άσκηση, το Headspace την ψυχική υγεία. Καμία δεν
συσχετίζει και τους τρεις τομείς ή προσαρμόζει τις συστάσεις στα ατομικά πρότυπα
κάθε χρήστη.

### Η Καινοτομία

Το WellSync αντιμετωπίζει τον χρήστη ως σύστημα: συλλέγει δεδομένα ημερήσιου
check-in (ύπνος, διάθεση, ενέργεια, άγχος), καταγραφές άσκησης και γευμάτων, και
εφαρμόζει ανά-χρήστη ML μοντέλα. Ένα agentic loop (APScheduler + Claude API) παράγει
εξατομικευμένες συστάσεις σε φυσική γλώσσα κάθε πρωί.

---

## 2. Λειτουργικές Απαιτήσεις

### 2.1 Λειτουργικές Απαιτήσεις (Functional Requirements)

| ID | Τίτλος | Περιγραφή | Acceptance Criteria |
|----|--------|-----------|---------------------|
| FR-01 | Εγγραφή Χρήστη | Νέος χρήστης εγγράφεται με email + κωδικό | Μετά την εγγραφή ο χρήστης λαμβάνει JWT token και κατευθύνεται στο Dashboard |
| FR-02 | Σύνδεση / Αποσύνδεση | Χρήστης συνδέεται με credentials και λαμβάνει access token | Token λήγει μετά 60 λεπτά· η αποσύνδεση καθαρίζει το token client-side |
| FR-03 | Ημερήσιο Check-in | Χρήστης συμπληρώνει ημερήσιο check-in (ύπνος, διάθεση, ενέργεια, άγχος) | Το σύστημα υπολογίζει Readiness Score 0–100 και αποθηκεύει την καταγραφή |
| FR-04 | Καταγραφή Άσκησης | Χρήστης καταγράφει άσκηση (τύπος, διάρκεια, RPE) | Η καταγραφή αποθηκεύεται· το Dashboard ενημερώνεται άμεσα |
| FR-05 | Καταγραφή Γεύματος | Χρήστης καταγράφει γεύμα (κατηγορία, ποιότητα, σχόλια) | Γεύμα αποθηκεύεται με timestamp· εμφανίζεται στην ιστορία ημέρας |
| FR-06 | Ημερήσια Σύσταση | Το σύστημα παράγει εξατομικευμένη σύσταση βάσει check-in | Η σύσταση εμφανίζεται στο Dashboard το αργότερο 30 δευτερόλεπτα μετά το check-in |
| FR-07 | AI Agentic Loop | Ο Morning Agent τρέχει αυτόματα στις 06:00 και παράγει σύσταση σε φυσική γλώσσα μέσω Claude API με RAG-enriched prompt | Η `agent_outputs` table περιέχει καταγραφή για κάθε χρήστη που έκανε check-in εκείνη την ημέρα. Η σύσταση ΠΡΕΠΕΙ να ενσωματώνει evidence από τουλάχιστον ένα established wellness guideline (retrieved via semantic search από την knowledge base). |
| FR-08 | ML Personalization | Μετά από 14 ημέρες δεδομένων το σύστημα ενεργοποιεί personalized μοντέλο | Ο ModelRetrainingAgent επαναεκπαιδεύει το μοντέλο κάθε βράδυ· η σύσταση αντικατοπτρίζει ατομικά πρότυπα |
| FR-09 | Insights Dashboard | Χρήστης βλέπει γραφήματα τάσεων (7/30 ημέρες) για ύπνο, διάθεση, Readiness | Τουλάχιστον 3 γραφήματα· δεδομένα φορτώνουν σε < 2 δευτερόλεπτα |
| FR-10 | Βραδινή Σύνοψη | Evening Agent παράγει σύντομη σύνοψη ημέρας στις 21:00 | Η βραδινή σύνοψη αποθηκεύεται στο `agent_outputs` και εμφανίζεται στο Dashboard |

### 2.2 Μη Λειτουργικές Απαιτήσεις

| Κατηγορία | Απαίτηση |
|-----------|---------|
| Απόδοση | API response < 500ms για 95% των αιτημάτων |
| Scalability | Single-instance Docker Compose (αρκεί για demo) |
| Αξιοπιστία | ML fallback: αν το Claude API αποτύχει, επιστρέφεται rule-based σύσταση |
| Ασφάλεια | Passwords hashed (bcrypt)· JWT auth σε όλα τα protected endpoints· API key αποκλειστικά server-side |
| Usability | Ο χρήστης ολοκληρώνει check-in σε < 2 λεπτά |

---

## 3. Αρχιτεκτονική Συστήματος

### 3.1 Tech Stack

| Επίπεδο | Τεχνολογία | Χρήση | Αιτιολόγηση |
|---------|-----------|-------|-------------|
| Frontend | React 18 + Vite | SPA UI | Γρήγορο dev, component-based, Chart.js integration |
| Frontend | Chart.js 4 | Γραφήματα τάσεων | Lightweight, δεν απαιτεί server |
| Backend | FastAPI (Python 3.10+) | REST API | Async-first, αυτόματο Swagger docs, type safety |
| Auth | python-jose (JWT) + passlib (bcrypt) | Authentication | Industry standard, stateless |
| Database | PostgreSQL 15 | Relational storage | ACID, JSON support, open-source |
| ORM | SQLAlchemy 2.0 | DB abstraction | Declarative models, migrations με Alembic |
| ML | scikit-learn 1.5 | Ridge Regression ανά χρήστη | Interpretable, lightweight, χωρίς GPU |
| LLM | Claude claude-haiku-4-5-20251001 (Anthropic API) | Φυσική γλώσσα συστάσεις | Cost-efficient, γρήγορο, bilingual (GR/EN) |
| Vector Search | pgvector (PostgreSQL extension) | Semantic similarity search στη knowledge base | Zero new infrastructure — PostgreSQL extension |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (384-dim) | Embedding generation για RAG | Free, local inference, no external API calls |
| Scheduling | APScheduler 3.10 | Cron jobs (06:00, 21:00, 00:00) | Embedded στο FastAPI, μηδέν extra Docker service |
| Event Bus | asyncio.Queue | In-process event transport | Απλό, χωρίς Redis για demo |
| Deploy | Docker Compose | Local + demo deployment | One-command startup |

### 3.2 Αρχιτεκτονικό Διάγραμμα

```
┌─────────────────────────────────────────────────────┐
│              React Frontend (Vite)                  │
│   Dashboard  |  CheckIn  |  LogWorkout  |  Insights │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON / JWT)
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌──────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │   Auth   │  │   Logging   │  │ Recommendation │  │
│  │ /auth/*  │  │  /checkin   │  │ /recommendation│  │
│  │          │  │  /workout   │  │  (reads agent_ │  │
│  └──────────┘  │  /meal      │  │   outputs)     │  │
│                └─────────────┘  └────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              Agentic Loop                    │   │
│  │  APScheduler → asyncio.Queue → EventGateway  │   │
│  │  MorningAgent  ·  EveningAgent  ·  RetrainAgent  │
│  └──────────────────────────────────────────────┘   │
└──────┬────────────────────────┬─────────────────────┘
       │                        │
┌──────▼──────┐       ┌─────────▼──────────┐
│ PostgreSQL  │       │    Claude API       │
│  users      │       │ claude-haiku-4-5   │
│  checkins   │       └────────────────────┘
│  workouts   │                ▲
│  meals      │       ┌────────┴───────────┐
│  agent_     │       │  ML Models (disk)  │
│   outputs   │       │  scikit-learn .pkl │
│  knowledge_ │       │  (per user)        │
│   chunks    │       └────────────────────┘
│  (pgvector) │
└──────┬──────┘
       │  cosine similarity (k=2)
┌──────▼──────────────────────────────────┐
│  WellnessRetriever (RAG layer)          │
│  sentence-transformers/all-MiniLM-L6-v2 │
│  → enriches Claude prompt with          │
│    evidence-based wellness guidelines   │
└─────────────────────────────────────────┘
```

### 3.3 Agentic Loop — Data Flow

```
[APScheduler — κάθε ώρα]
    ↓
 WellnessEvent(type="morning_recommendation", fired_at=06:00)
    ↓
 asyncio.Queue  (max 100 events, in-memory)
    ↓
 EventGateway.dispatch(event)   ← dict-based routing
    ↓
 MorningRecommendationAgent.handle(event, db)
    ├── Φέρνει today's check-in για κάθε ενεργό χρήστη
    ├── Υπολογίζει readiness_score (ML ή rule-based)
    ├── [RAG] WellnessRetriever.retrieve(query, k=2)
    │       └── pgvector cosine similarity → 2 wellness guidelines
    ├── Φτιάχνει enriched prompt (check-in + 7d ιστορικό + guidelines, < 600 tokens)
    ├── Claude API → evidence-based σύσταση (≤ 200 tokens)
    └── Αποθηκεύει στο agent_outputs table

[GET /recommendation/today]
    ├── Primary:  διαβάζει agent_outputs → επιστρέφει LLM text
    └── Fallback: αν δεν υπάρχει output → ML-only σύσταση
```

**Agents & Χρονοδιάγραμμα:**

| Agent | Ώρα | Λειτουργία |
|-------|-----|-----------|
| MorningRecommendationAgent | 06:00 | ML score + Claude API → πρωινή σύσταση |
| EveningInsightsAgent | 21:00 | Σύνοψη ημέρας + tip για αύριο |
| ModelRetrainingAgent | 00:00 | Επαναεκπαίδευση Ridge Regression ανά χρήστη |

### 3.4 Database Schema

```sql
-- Χρήστες
users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR UNIQUE NOT NULL,
    name            VARCHAR NOT NULL,
    password_hash   VARCHAR NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
)

-- Ημερήσιο check-in
checkins (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    date            DATE NOT NULL,
    sleep_hours     FLOAT NOT NULL,        -- 0–12
    sleep_quality   INTEGER NOT NULL,      -- 1–5
    mood            INTEGER NOT NULL,      -- 1–5
    energy          INTEGER NOT NULL,      -- 1–5
    stress          INTEGER NOT NULL,      -- 1–5
    readiness_score FLOAT,                 -- 0–100, computed on save
    UNIQUE(user_id, date)
)

-- Καταγραφές άσκησης
workouts (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    date            DATE NOT NULL,
    type            VARCHAR NOT NULL,      -- 'running', 'gym', 'cycling', ...
    duration_min    INTEGER NOT NULL,
    rpe             INTEGER NOT NULL       -- Rate of Perceived Exertion 1–10
)

-- Καταγραφές γευμάτων
meals (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    date            DATE NOT NULL,
    meal_type       VARCHAR NOT NULL,      -- 'breakfast', 'lunch', 'dinner', 'snack'
    quality         INTEGER NOT NULL,      -- 1–5 (1=junk, 5=excellent)
    notes           TEXT
)

-- Έξοδος AI agents
agent_outputs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    date            DATE NOT NULL,
    event_type      VARCHAR NOT NULL,      -- 'morning_recommendation', 'evening_summary'
    readiness_score FLOAT,
    intensity       VARCHAR,               -- 'high', 'moderate', 'low'
    llm_text        TEXT NOT NULL,         -- Claude-generated natural language
    model_used      VARCHAR DEFAULT 'claude-haiku-4-5-20251001',
    created_at      TIMESTAMP DEFAULT NOW()
)

-- RAG Knowledge Base (wellness guidelines corpus)
knowledge_chunks (
    id              SERIAL PRIMARY KEY,
    category        TEXT NOT NULL,         -- 'sleep' | 'nutrition' | 'exercise' | 'stress'
    content         TEXT NOT NULL,         -- wellness guideline text snippet (3–5 sentences)
    embedding       vector(384),           -- sentence-transformers/all-MiniLM-L6-v2
    source          TEXT                   -- e.g. 'ACSM 2024', 'Sleep Foundation', 'WHO'
)
-- Index: ivfflat για cosine similarity search
-- CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
```

### 3.5 API Endpoints

| Method | Path | Auth | Περιγραφή |
|--------|------|------|-----------|
| POST | `/auth/register` | — | Εγγραφή νέου χρήστη (email, name, password) |
| POST | `/auth/login` | — | Login → JWT access token |
| POST | `/checkin` | JWT | Ημερήσιο check-in· υπολογίζει & αποθηκεύει readiness score |
| GET | `/checkin/history` | JWT | Ιστορικό check-in (τελευταίες 30 μέρες) |
| POST | `/workout` | JWT | Καταγραφή άσκησης (type, duration, rpe) |
| POST | `/meal` | JWT | Καταγραφή γεύματος (meal_type, quality, notes) |
| GET | `/recommendation/today` | JWT | Σύσταση σήμερα — LLM primary, ML fallback |
| GET | `/insights/weekly` | JWT | Εβδομαδιαίες συσχετίσεις + δεδομένα για γραφήματα |
| GET | `/health` | — | Healthcheck για Docker |

---

## 4. ML Component

### 4.1 Readiness Score — Rule-Based (Cold Start, < 14 ημέρες δεδομένων)

Ο Readiness Score (0–100) υπολογίζεται από τα δεδομένα του ημερήσιου check-in:

```
readiness = (sleep_hours / 8.0  × 30)
          + (sleep_quality / 5  × 20)
          + (mood          / 5  × 20)
          + (energy        / 5  × 20)
          + ((6 - stress)  / 5  × 10)
```

**Βάρη:** Ύπνος (50%), Διάθεση + Ενέργεια (40%), Άγχος (10%)

**Αριθμητικό Παράδειγμα:**

```
Χρήστης: sleep_hours=6, sleep_quality=3, mood=3, energy=2, stress=4

readiness = (6/8 × 30) + (3/5 × 20) + (3/5 × 20) + (2/5 × 20) + (2/5 × 10)
          =   22.5     +    12.0     +    12.0     +     8.0    +     4.0
          = 58.5  →  "Μέτρια ετοιμότητα"
```

**Επίπεδα Σύστασης:**

| Score | Intensity | Σύσταση |
|-------|-----------|---------|
| ≥ 75 | High | Υψηλής έντασης άσκηση, ισορροπημένη διατροφή |
| 45–74 | Moderate | Μέτρια άσκηση, προτεραιότητα ύπνου απόψε |
| < 45 | Low | Ξεκούραση / ήπια δραστηριότητα, διαχείριση άγχους |

### 4.2 Personalized ML (≥ 14 ημέρες δεδομένων)

**Μοντέλο:** Ridge Regression ανά χρήστη
**Αποθήκευση:** `ml_models/{user_id}.pkl` (pickle, < 10KB ανά χρήστη)
**Επαναεκπαίδευση:** Καθημερινά στις 00:00 από τον ModelRetrainingAgent

**Input Features:**

```python
features = [
    sleep_hours,    # 0–12
    sleep_quality,  # 1–5
    mood,           # 1–5
    energy,         # 1–5
    stress,         # 1–5
    day_of_week,    # 0–6 (Monday=0)
]
```

**Target:** `workout_rpe` — ο πραγματικός RPE που κατέγραψε ο χρήστης εκείνη την ημέρα

**Χρήση στη Σύσταση:**
Το μοντέλο προβλέπει `predicted_rpe` για σήμερα. Αν `predicted_rpe > historical_mean + 0.5` → αύξηση readiness score κατά 10%. Αν `predicted_rpe < historical_mean − 0.5` → μείωση κατά 10%.

**Γιατί Ridge Regression και όχι Neural Network:**
- Ερμηνεύσιμο — μπορούμε να εξηγήσουμε γιατί το score αλλάζει
- Λειτουργεί με μικρό dataset (14–60 samples per user)
- Δεν απαιτεί GPU
- Κάθε μοντέλο < 10KB

### 4.3 Correlation Analysis (Insights)

Pearson correlation υπολογίζεται μεταξύ:

| Ζεύγος | Παράδειγμα Insight |
|--------|-------------------|
| `sleep_hours` ↔ `next_day_energy` | "Όταν κοιμάσαι > 7ώρες, η ενέργειά σου αυξάνεται κατά +28%" |
| `stress` ↔ `workout_rpe` | "Υψηλό άγχος μειώνει την απόδοσή σου κατά ~15%" |
| `mood` ↔ `workout_duration` | "Καλή διάθεση → +12 λεπτά μέση διάρκεια άσκησης" |

---

## 5. UI Mockups

> Τα mockups δείχνουν πραγματικά sample data για demo χρήστη "Νίκος Π."
> Hi-fi Figma/Canva prototype θα παραδοθεί μαζί με τον κώδικα στη Φ4.

---

### Screen 1: Home / Dashboard

```
┌─────────────────────────────────────┐
│  WellSync              👤 Νίκος    │
├─────────────────────────────────────┤
│                                     │
│   Readiness Score — Τρίτη 22/4     │
│                                     │
│         ╔══════════════╗            │
│         ║    58 / 100  ║            │
│         ║  ████████░░  ║            │
│         ║    ΜΕΤΡΙΟ    ║            │
│         ╚══════════════╝            │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ✨ AI Σύσταση (06:14)          │ │
│ │                                 │ │
│ │ "Νίκο, σήμερα ο ύπνος σου ήταν │ │
│ │  λίγος. Δοκίμασε ελαφρύ τρέξιμο│ │
│ │  20 λεπτών αντί για βάρη και   │ │
│ │  φρόντισε να φας πρωτεΐνη."    │ │
│ └─────────────────────────────────┘ │
│                                     │
│  [+ Check-in] [+ Άσκηση] [+ Γεύμα] │
│                                     │
│  Σήμερα                            │
│  ✓ Check-in 07:32                  │
│  🏃 Τρέξιμο · 20λ · RPE 5         │
└─────────────────────────────────────┘
```

**Στοιχεία:** Readiness gauge (0–100), AI recommendation card με badge "✨ AI-powered", quick-log buttons, σύνοψη δραστηριοτήτων ημέρας.

---

### Screen 2: Daily Check-in

```
┌─────────────────────────────────────┐
│  ←       Ημερήσιο Check-in         │
├─────────────────────────────────────┤
│                                     │
│  Πώς ήσουν σήμερα, Νίκο;          │
│                                     │
│  Ύπνος — Ώρες                      │
│  ├──●───────────────────┤  6.0ώρ  │
│                                     │
│  Ποιότητα Ύπνου                    │
│  ★★★☆☆  (3/5)                      │
│                                     │
│  Διάθεση                           │
│  😔  😐  🙂  😊  😄               │
│       ●                             │
│                                     │
│  Ενέργεια                          │
│  ⚡⚡░░░  (2/5)                      │
│                                     │
│  Άγχος                             │
│  Χαμηλό ├─────────●──┤ Υψηλό     │
│                    4/5              │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Readiness Preview: 58/100 │   │
│  │   Κατηγορία: ΜΕΤΡΙΟ   📊   │   │
│  └─────────────────────────────┘   │
│                                     │
│      [  Αποθήκευση Check-in  ]     │
└─────────────────────────────────────┘
```

**Στοιχεία:** Slider ύπνου, star rating ποιότητας, emoji mood picker, energy icons, stress slider, real-time readiness preview.

---

### Screen 3: Log Workout

```
┌─────────────────────────────────────┐
│  ←       Καταγραφή Άσκησης         │
├─────────────────────────────────────┤
│                                     │
│  Τύπος Άσκησης                     │
│  ┌────────┐ ┌────────┐ ┌────────┐  │
│  │🏃 Τρέξ.│ │🏋 Γυμν.│ │🚴 Ποδ. │  │
│  └────────┘ └───●────┘ └────────┘  │
│  ┌────────┐ ┌────────┐ ┌────────┐  │
│  │🏊 Κολ. │ │🧘 Yoga │ │➕ Άλλο │  │
│  └────────┘ └────────┘ └────────┘  │
│                                     │
│  Διάρκεια (λεπτά)                  │
│  ├───────────●───────────┤  45λ   │
│                                     │
│  Αντιληπτή Κόπωση (RPE 1–10)      │
│   1  2  3  4  5  6  7  8  9  10   │
│               ●                     │
│             Μέτριο (5)              │
│                                     │
│      [  Αποθήκευση Άσκησης  ]      │
└─────────────────────────────────────┘
```

**Στοιχεία:** Icon grid τύπου άσκησης (selected = highlighted), duration slider, RPE scale με label.

---

### Screen 4: Log Meal

```
┌─────────────────────────────────────┐
│  ←       Καταγραφή Γεύματος        │
├─────────────────────────────────────┤
│                                     │
│  Γεύμα                             │
│  ○ Πρωινό    ● Μεσημεριανό         │
│  ○ Βραδινό   ○ Σνακ                │
│                                     │
│  Ποιότητα  (1 = Junk · 5 = Άριστο)│
│                                     │
│  🍔    🍕    🥗    🥦    🥑        │
│  ──────────────●────────           │
│   1      2     3    4     5        │
│                   (4 — Υγιεινό)    │
│                                     │
│  Σχόλια (προαιρετικά)              │
│  ┌─────────────────────────────┐   │
│  │ Σαλάτα με κοτόπουλο         │   │
│  └─────────────────────────────┘   │
│                                     │
│      [  Αποθήκευση Γεύματος  ]     │
└─────────────────────────────────────┘
```

**Στοιχεία:** Radio buttons τύπου γεύματος, quality slider με emoji scale, optional notes field.

---

### Screen 5: Insights

```
┌─────────────────────────────────────┐
│  WellSync            Insights 📊   │
├─────────────────────────────────────┤
│                                     │
│    [ 7 μέρες ]  [ 30 μέρες ]      │
│                                     │
│  Readiness Score — Τελευταίες 7μ  │
│  100│             ●               │
│   80│       ●         ●           │
│   60│   ●       ●         ●       │
│   40│               ●             │
│   20│                             │
│     └──────────────────────────   │
│      Δε  Τρ  Τε  Πε  Πα  Σα  Κυ  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ 💡 AI Insight                │  │
│  │ Όταν κοιμάσαι > 7 ώρες,     │  │
│  │ η ενέργειά σου αυξάνεται     │  │
│  │ κατά +28%  (r = 0.71)        │  │
│  └──────────────────────────────┘  │
│                                     │
│  Μέσος ύπνος       6.4 ώρες       │
│  Ασκήσεις εβδ.     4 φορές        │
│  Καλύτερη μέρα     Σάββατο        │
└─────────────────────────────────────┘
```

**Στοιχεία:** Line chart Readiness (Chart.js), 7/30 toggle, AI insight card με correlation coefficient, summary stats.

---

### Screen 6: Profile

```
┌─────────────────────────────────────┐
│  ←             Profile             │
├─────────────────────────────────────┤
│                                     │
│       👤  Νίκος Παπαδόπουλος       │
│          nikos@aueb.gr              │
│          Μέλος από: 5/3/2026       │
│                                     │
│  Στατιστικά                        │
│  ─────────────────────────────     │
│  Check-ins:         48 ημέρες      │
│  Ασκήσεις:          32 sessions    │
│  Streak:            🔥 7 μέρες     │
│                                     │
│  ML Status                         │
│  ─────────────────────────────     │
│  ┌──────────────────────────────┐  │
│  │ ✅ Personalized Mode Active  │  │
│  │ Μοντέλο εκπαιδεύτηκε:       │  │
│  │ 22/4/2026 · 48 samples       │  │
│  └──────────────────────────────┘  │
│                                     │
│  Στόχοι                            │
│  ─────────────────────────────     │
│  🏃 Άσκηση 4×/εβδ.   ✓  4 / 4    │
│  😴 Ύπνος > 7ώρ.     ✗  5 / 7    │
│                                     │
│        [  Αποσύνδεση  ]            │
└─────────────────────────────────────┘
```

**Στοιχεία:** User info, activity stats, streak counter, ML model status badge (Personalized / Cold Start), goals progress bars.

---

## Παράρτημα: Σχέδιο Υλοποίησης (Φ4)

Το πλήρες implementation plan (TDD, task-by-task) βρίσκεται στο:
- `docs/plans/2026-02-19-wellsync-agentic-loop.md`

Σειρά εκτέλεσης για Φ4:

```
M1 (dependencies)
  → M2 (AgentOutput model)
  → Tasks 2–5 (backend core: auth, checkin, logs)
  → Task 6 (ML personalizer + insights)
  → Task 7 (event system: types, queue, gateway)
  → Task 8 (agent handlers: Morning, Evening, Retraining)
  → Task 9 (scheduler + FastAPI lifespan)
  → M6 (recommendation endpoint: LLM primary + ML fallback)
  → Tasks 8–11 (React frontend)
  → Task 12 (demo seed data)
  → Task 13 (README + Docker cleanup)
```

---

*Έγγραφο δημιουργήθηκε: Απρίλιος 2026 | WellSync Team | AUEB ΑΕΠΣ 2026*
