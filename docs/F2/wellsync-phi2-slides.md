# WellSync — Φ2 Παρουσίαση (Slides)

**Μάθημα**: Ανάπτυξη Εφαρμογών Πληροφοριακών Συστημάτων — AUEB 2026
**Deadline Φ2**: 16–26/3/2026 (παρουσίαση στην τάξη + PDF στο eclass)
**Βαθμός**: 15%

> Κάθε slide έχει τίτλο, bullet points για ομιλητή, και σημειώσεις (speaker notes).
> Συνολικά: ~10 slides, ~8–10 λεπτά παρουσίαση.

---

## SLIDE 1 — Title

**Τίτλος (μεγάλα γράμματα):**
```
WellSync
AI Holistic Wellness Coach
```

**Subtitle:**
```
Ανάπτυξη Εφαρμογών Πληροφοριακών Συστημάτων
AUEB — Εαρινό 2026
[Ονόματα ομάδας]
```

**Οπτικό:** Logo / εικόνα smartphone με dashboard

---

## SLIDE 2 — Το Πρόβλημα

**Τίτλος:** Γνωρίζεις πώς σε επηρεάζει ο ύπνος στην προπόνηση;

**Bullets:**
- Κοιμάσαι 5 ώρες → πας γυμναστήριο → αποτυγχάνεις → δεν ξέρεις γιατί
- 3 εφαρμογές ανοιχτές: MyFitnessPal, Strava, Headspace
- Καμία δεν τις συνδέει — **κανεμία δεν σε ξέρει**

**Οπτικό:** 3 εικονίδια apps με "silos" / τείχη ανάμεσά τους

**Speaker notes:**
> Ξεκίνα με ρητορική ερώτηση. Το πρόβλημα είναι απλό και σχετικό
> για κάθε φοιτητή στην αίθουσα. Παύση μετά τη δεύτερη γραμμή.

---

## SLIDE 3 — Η Λύση

**Τίτλος:** WellSync — Μία εφαρμογή που σε καταλαβαίνει

**Bullets:**
- Καθημερινό 2-λεπτο check-in: ύπνος · διάθεση · ενέργεια · στρες
- Καταγραφή προπόνησης και γευμάτων
- **AI Readiness Score** (0–100) κάθε πρωί
- **Εξατομικευμένη σύσταση** σε φυσική γλώσσα — όχι template

**Quote (μεγάλα, στο κέντρο):**
> "Κοιμήθηκες 5.5h και χθες ήταν high intensity.
> Σήμερα: yoga 20', πρωτεΐνη στο γεύμα.
> Αποφύγαμε HIIT — επέστρεψε στη ρουτίνα σου αύριο."

**Οπτικό:** Screenshot Home screen με ReadinessGauge + RecommendationCard

**Speaker notes:**
> Διάβασε το quote αργά. Αυτό είναι το WOW moment της παρουσίασης.
> Τόνισε ότι αυτό δεν είναι γενική συμβουλή — είναι για εσένα, σήμερα.

---

## SLIDE 4 — Πώς Λειτουργεί (User Flow)

**Τίτλος:** Η καθημερινή ροή

**Visual flow (οριζόντιο):**
```
Πρωί            Μέρα              Βράδυ
   │                │                │
[Check-in]    [Log Workout]    [Insights]
2 λεπτά       [Log Meal]       Correlations
   │                              Trends
   ↓
[AI Agent]
ML + Claude AI
   │
[Σύσταση ημέρας]
```

**Bullets:**
- **Πρωί**: 5 sliders (ύπνος, διάθεση, ενέργεια, στρες) → Readiness Score
- **Μέρα**: log προπόνηση + γεύματα σε < 1 λεπτό
- **Βράδυ**: graphs που δείχνουν patterns ("καλύτερος ύπνος → +23% energy")

**Speaker notes:**
> Η ροή είναι σκόπιμα απλή. Το value δεν είναι στο logging —
> είναι στο τι βγάζει το σύστημα από αυτά τα δεδομένα.

---

## SLIDE 5 — Η Καινοτομία #1: Cross-Domain ML

**Τίτλος:** ML που συνδέει τομείς — per-user, όχι generic

**Bullets:**
- Ridge Regression ανά χρήστη (scikit-learn)
- Ανακαλύπτει **ατομικά** patterns:
  - Πόσο επηρεάζει ο ύπνος σου την απόδοσή σου;
  - Πότε είσαι πιο productive στο gym;
- **Cold start**: rule-based formula (άμεση αξία από μέρα 1)
- **Personalized mode**: ενεργοποιείται μετά 14 μέρες δεδομένων
- Παράδειγμα insight: *"Ύπνος < 6h → performance drop 38% (για εσένα)"*

**Οπτικό:** Scatter plot (sleep_hours vs RPE) με regression line

**Speaker notes:**
> Εδώ δείχνεις ότι καταλαβαίνεις ML. Τόνισε ότι δεν είναι
> global statistics — είναι model που εκπαιδεύεται στα δικά σου δεδομένα.

---

## SLIDE 6 — Η Καινοτομία #2: Agentic Loop

**Τίτλος:** Proactive AI — όχι passive app

**Αρχιτεκτονικό διάγραμμα (απλό):**
```
[Scheduler 06:00]
       ↓
   [Event Queue]
       ↓
  [Event Gateway]
       ↓
  [Morning Agent]
    ├── ML readiness score
    ├── RAG: top-2 scientific guidelines  ← ΝΕΟ
    └── Claude AI (enriched prompt)
       ↓
  [agent_outputs DB]
       ↓
 [Σύσταση στο Frontend]
```

**Bullets:**
- Το σύστημα **δουλεύει** ενώ εσύ κοιμάσαι
- 3 scheduled agents: πρωί (σύσταση), βράδυ (wrap-up), μεσάνυχτα (ML retraining)
- ML + **επιστημονικές οδηγίες (ACSM/WHO)** + Claude AI → evidence-based output
- Fallback: αν το AI δεν απάντησε → ML-only σύσταση (πάντα δουλεύει)

**Speaker notes:**
> Αυτό διαφοροποιεί το WellSync από ένα απλό CRUD app.
> Η εφαρμογή δεν περιμένει τον χρήστη — δράει μόνη της.

---

## SLIDE 7 — Στοχευόμενο Κοινό

**Τίτλος:** Για ποιον είναι το WellSync;

**Persona (με εικόνα):**
```
Νίκος, 21 ετών, φοιτητής AUEB
✓ Πηγαίνει γυμναστήριο 2-3 φορές/εβδομάδα
✓ Ακανόνιστος ύπνος (εξεταστική)
✗ Έχει εγκαταλείψει 3 wellness apps
✗ Δεν ξέρει γιατί κάποιες μέρες "δεν έχει κέφι"
→ Χρειάζεται εξήγηση, όχι απλά tracking
```

**Market size (bullet):**
- Ελλάδα: ~400,000 φοιτητές
- Global: 1.8 δισ. millennials/Gen-Z με smartphone
- Wellness app market: $5.6B (2024) → $15B (2030)

**Speaker notes:**
> Μείνε στον Νίκο — είναι πιο πειστικός από ένα market size number.
> Ο καθηγητής θα εκτιμήσει ότι γνωρίζεις το target user σου.

---

## SLIDE 8 — Ανταγωνιστική Ανάλυση

**Τίτλος:** Γιατί όχι τα υπάρχοντα;

**Πίνακας:**
```
                 Workout  Nutrition  Mental  Cross-domain  AI Rec
MyFitnessPal       ±         ✓        ✗          ✗           ✗
Strava             ✓         ✗        ✗          ✗           ✗
Headspace          ✗         ✗        ✓          ✗           ✗
Apple Health       ±         ±        ±          ✗           ✗
──────────────────────────────────────────────────────────────────
WellSync           ✓         ✓        ✓          ✓           ✓
```

**Λεζάντα:** WellSync είναι το μόνο που συνδυάζει και τα 5

**Speaker notes:**
> Διάβασε τον πίνακα γρήγορα — η εικόνα μιλά μόνη της.
> Τόνισε το τελευταίο column (AI Rec) — εκεί είναι το gap.

---

## SLIDE 9 — Τεχνολογία (High-Level)

**Τίτλος:** Πώς το χτίζουμε

**Δύο στήλες:**

**Backend / ML / RAG**
- Python 3.10 + FastAPI
- PostgreSQL + **pgvector** (vector search)
- scikit-learn (Ridge Regression)
- sentence-transformers (semantic embeddings)
- APScheduler + asyncio Queue
- Claude AI API (Anthropic)

**Frontend / Deploy**
- React 18 + Vite
- Chart.js (trend graphs)
- Docker Compose
- JWT Authentication

**Αρχιτεκτονικό overview (απλό):**
```
React ←→ FastAPI ←→ PostgreSQL
              ↕
         ML Engine
              ↕
          Claude AI
```

**Speaker notes:**
> Μην εξηγείς κάθε τεχνολογία. Αρκεί να δείξεις ότι έχεις
> σκεφτεί την αρχιτεκτονική. Η Claude AI integration είναι το highlight.

---

## SLIDE 10 — Roadmap & Demo

**Τίτλος:** Πού είμαστε — Πού πάμε

**Timeline:**
```
Φεβρ 2026  ████████  Ιδέα + αρχιτεκτονικός σχεδιασμός ✓
Μάρτιος    ████      Φ1 Φόρμα ✓ | Φ2 Παρουσίαση ← ΤΩΡΑ
Απρίλιος   ░░░░      Φ3: Technical design + UI mockups
Μάιος      ░░░░      Φ4: Υλοποίηση + Demo ← ΤΕΛΙΚΟΣ ΣΤΟΧΟΣ
```

**MVP Demo (Φ4) θα περιλαμβάνει:**
- Live check-in → Readiness Score
- AI agent εκτελείται → φυσική γλώσσα σύσταση
- Insights screen με real correlation graphs
- `docker compose up --build` → πλήρης εφαρμογή

**Speaker notes:**
> Κλείσε με αυτό που θα δείξεις στη Φ4 demo.
> "Σε 2 λεπτά κάνεις check-in και βλέπεις το AI να παράγει
> εξατομικευμένη σύσταση — live."

---

## SLIDE 11 — Κλείσιμο

**Τίτλος (μεγάλα):**
```
WellSync
"Γνώρισε τον εαυτό σου — μέσα από τα δεδομένα σου."
```

**Ομάδα:**
```
[Ονόματα μελών]
[email επικοινωνίας]
```

**Ερωτήσεις;**

---

## Οδηγίες για Παρουσίαση

### Διάρκεια
- Στόχος: **8–10 λεπτά** + 2-3 λεπτά ερωτήσεις
- Κατανομή: ~45 δευτ/slide

### Σειρά ομιλητών (αν 3μελής ομάδα)
```
Μέλος Α: Slides 1–3 (πρόβλημα + λύση)
Μέλος Β: Slides 4–6 (flow + καινοτομίες)
Μέλος Γ: Slides 7–11 (κοινό + ανταγωνισμός + tech + κλείσιμο)
```

### Tips
- Ξεκίνα με ρητορική ερώτηση (Slide 2) — τραβά προσοχή
- Διάβασε αργά το AI-generated quote (Slide 3) — είναι το WOW moment
- Ο πίνακας ανταγωνισμού (Slide 8) — δείξε τον και προχώρα γρήγορα
- Μην διαβάζεις bullets — μίλα στο κοινό

### Εργαλείο
Συστήνεται: **Google Slides** ή **Canva** (free, εύκολη συνεργασία)

---

## Checklist Παράδοσης Φ2

- [ ] PDF εξαγωγή από Google Slides / Canva / PowerPoint
- [ ] Ονόματα ομάδας στο Slide 1 και 11
- [ ] Upload PDF στο eclass πριν την παρουσίαση
- [ ] Εξάσκηση timing (8-10 λεπτά — μετρήστε)
- [ ] Handoff plan αν ο ένας ομιλητής κολλήσει
