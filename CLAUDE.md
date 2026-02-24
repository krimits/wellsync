# CLAUDE.md — aeps-2026

## Course Context

**Μάθημα**: Ανάπτυξη Εφαρμογών Πληροφοριακών Συστημάτων
**Εξάμηνο**: Εαρινό 2026
**Διδάσκων**: Ι. Κωτίδης (AUEB)
**Ομάδα**: 2–3 άτομα (ορίστε υπεύθυνο φάσης σε κάθε παράδοση)

---

## Project Phases & Deadlines

| Φάση | Περιγραφή | Deadline | Βαθμός |
|------|-----------|----------|--------|
| Φ0 | Ορισμός ομάδας + Lean Canvas email | 2–3 πρώτες εβδομάδες | — |
| Φ1 | Φόρμα συμμετοχής στον εικονικό διαγωνισμό (PDF στο eclass) | 14/3/2026 | 15% |
| Φ2 | Παρουσίαση ιδέας στην τάξη (PDF στο eclass) | 16/3–26/3/2026 | 15% |
| Φ3 | Τεχνική σχεδίαση: απαιτήσεις, αρχιτεκτονική, UI mockups (PDF) | 20/4–23/4/2026 | 20% |
| Φ4 | Υλοποίηση + GitHub παράδοση + Επίδειξη | 25/5–28/5/2026 | 50% |

> **Προσοχή**: Ελάχιστος βαθμός 50% σε κάθε φάση. Απουσία από παρουσίαση = μηδέν στη φάση.

---

## Deliverables per Phase

### Φ1 — Φόρμα Συμμετοχής
- Συμπλήρωση φόρμας από eclass
- Upload ως PDF στο eclass

### Φ2 — Παρουσίαση Ιδέας
Πρέπει να καλύπτει:
- Κεντρική ιδέα & καινοτομία
- Κοινό-στόχος
- Ανταγωνιστικά προϊόντα
- Μεθοδολογία υλοποίησης

### Φ3 — Τεχνική Σχεδίαση
Πρέπει να περιλαμβάνει:
1. Λειτουργικές απαιτήσεις (functional requirements)
2. Αρχιτεκτονική συστήματος (tech stack, frameworks, databases, APIs)
3. UI mockups με δοκιμαστικά δεδομένα

### Φ4 — Υλοποίηση
- Κώδικας παραδοτέος μέσω GitHub
- README με οδηγίες εγκατάστασης και εκτέλεσης
- Demo με πραγματικά δεδομένα

---

## Project: WellSync

- **Τίτλος**: WellSync — AI Holistic Wellness Coach
- **Περιγραφή**: Web app που συνδυάζει daily check-in (ύπνος/διάθεση/ενέργεια/στρες),
  workout & meal logging, και AI agent loop που παράγει εξατομικευμένες συστάσεις
- **Καινοτομία**: Cross-domain Ridge Regression per user + event-driven agentic loop
  (Scheduler→Queue→Gateway→Agent→Claude API) — όχι static templates
- **Cold start**: Rule-based συστάσεις <14 days · Personalized ML ≥14 days

## Tech Stack (confirmed)

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10 + FastAPI |
| ML | scikit-learn (Ridge Regression per user) |
| LLM | Anthropic API — claude-haiku-4-5-20251001 |
| Database | PostgreSQL |
| Frontend | React 18 + Vite + Chart.js |
| Auth | JWT (python-jose) |
| Scheduling | APScheduler (embedded in FastAPI lifespan) |
| Events | asyncio.Queue + EventGateway |
| Deploy | Docker Compose (3 containers) |

---

## Project Structure

```
aeps-2026/
├── src/           # Πηγαίος κώδικας εφαρμογής
├── tests/         # Unit/integration tests
├── docs/          # Παρουσιάσεις, diagrams, STATUS.md
│   ├── STATUS.md  # Συντονισμός multi-agent (αν χρησιμοποιηθεί)
│   ├── F1/        # Φόρμα Φ1
│   ├── F2/        # Slides Φ2
│   ├── F3/        # Technical design Φ3
│   └── F4/        # Demo scripts, screenshots Φ4
├── CLAUDE.md      # Αυτό το αρχείο
└── README.md      # Οδηγίες εγκατάστασης (για Φ4)
```

---

## Claude Code Guidelines for This Project

### General
- **Πριν από κάθε νέα συνεδρία**: διάβασε `docs/STATUS.md` + το τελευταίο `docs/context-YYYY-MM-DD.md`
- Πρόκειται για **σύνθετο project** — χρησιμοποίησε το multi-agent workflow (δες `~/.claude/CLAUDE.md`)
- Κάθε φάση έχει διαφορετικούς στόχους — τρέχουσα κατάσταση πάντα στο `docs/STATUS.md`
- **Στο τέλος κάθε συνεδρίας**: ενημέρωσε `docs/STATUS.md` + τρέξε `claude-md-management:revise-claude-md`

### Code Standards
- Ακολούθα τα πρότυπα γλώσσας που ορίζονται στο `~/.claude/CLAUDE.md`
- Συμπεριέλαβε πάντα `README.md` με οδηγίες εκκίνησης
- Για backend Python: type hints, PEP 8, pytest
- Για Java backend: Javadoc, JUnit 5, Java 17+
- Για frontend: component-based αρχιτεκτονική, responsive design

### Innovation Focus
- Η εφαρμογή **πρέπει να διαφοροποιείται** από υπάρχουσες λύσεις
- Κάθε design decision να τεκμηριώνεται ως προς την καινοτομία

### Git
- Commits στα αγγλικά, imperative mood (π.χ. `Add F2 speaker script`)
- Branches ανά φάση: `phase/F1`, `phase/F2`, `phase/F3`, `phase/F4`
- Το GitHub repo θα παραδοθεί στη Φ4 — κράτα καθαρό history
- Δεν υπάρχει ακόμα git repo — να δημιουργηθεί πριν τη Φ4

---

## Grading Reminder

- Εργασία: **80%** του τελικού βαθμού
- Τελικό διαγώνισμα: **20%** (ελάχιστο 4/10 για να προσμετρήσει η εργασία)
- Ελάχιστο ανά φάση: **50%**
