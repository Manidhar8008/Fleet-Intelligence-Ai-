# 🧹 Repository Cleanup Report - Fleet Intelligence AI

**Status**: Ready for Production Consolidation  
**Date**: March 27, 2026  
**Objective**: Create lean, maintainable codebase

---

## 📊 Current State Analysis

### **Directory Overview**
```
ROOT/
├── app/                      [NEW] Production Streamlit app (KEEP)
├── app.py                   [OLD] Legacy Streamlit wrapper (REMOVE)
├── core/                    [GOOD] Clean processing modules (CONSOLIDATE)
├── src/                     [OLD] Legacy folder with overlaps (REMOVE)
├── models/                  [MINIMAL] Only risk_model.py (INTEGRATE)
├── utils/                   [GOOD] Config & logging (KEEP & ENHANCE)
├── data/                    [KEEP] Data storage
├── docs/                    [REVIEW] Documentation
├── notebooks/               [LEGACY] Jupyter notebooks (ARCHIVE)
├── scripts/                 [LEGACY] Old scripts (REVIEW)
├── tests/                   [LEGACY] Old tests (REVIEW)
└── reports/                 [LEGACY] Generated reports (ARCHIVE)
```

---

## 🔍 File Duplication Analysis

### **DUPLICATE MODULES** (Choose winner)
| Module | Location 1 | Location 2 | Status |
|--------|-----------|-----------|--------|
| `data_loader.py` | `/core/` | `/src/` | **CONSOLIDATE** - core/ is better |
| `decision_engine.py` | `/core/` | `/src/` | **CONSOLIDATE** - core/ is better |
| `config.py` | `/utils/` | Root level? | **KEEP** - /utils/config.py |
| `logger.py` | `/utils/` | N/A | **KEEP** |

### **REDUNDANT FOLDERS**
- `/src/` - Legacy structure, modules duplicated in `/core/` → **DELETE**
- `/models/` - Only has `risk_model.py` → **INTEGRATE into /core/models/**
- Old `/notebooks/`, `/scripts/`, `/reports/` → **ARCHIVE** (keep for reference, don't load)

### **LEGACY FILES** (Root level)
- `app.py` - Old Streamlit app, imports from deleted `/src/` → **DELETE**
- `clear_db.py` - Database cleanup script → **Review/Archive**
- `CLEANUP_REPORT.md` - Old report → **DELETE**
- `DEPLOYMENT_READY.md` - Old deployment guide → **DELETE** (use new DEPLOYMENT.md in /app/)

---

## ✅ Target Clean Structure

```
lime-iot-ml-platform/
│
├── app/                          [Production Streamlit Application]
│   ├── main.py                   # Main Streamlit dashboard
│   ├── requirements.txt           # Dependencies
│   ├── run.bat / run.sh          # Startup scripts
│   ├── README.md                 # Quick start guide
│   ├── ARCHITECTURE.md           # System design
│   ├── DEPLOYMENT.md             # Deployment options
│   ├── Dockerfile                # Container config
│   ├── .streamlit/
│   │   └── config.toml           # Streamlit theming
│   ├── utils/                    # App utilities
│   │   ├── config.py             # Configuration
│   │   ├── logger.py             # Logging
│   │   └── file_utils.py         # File operations
│   ├── core/                     # Processing pipeline
│   │   ├── data_loader.py        # CSV/demo data loading
│   │   ├── preprocessing.py      # Data cleaning
│   │   ├── feature_engineering.py # ML features
│   │   ├── decision_engine.py    # Business logic
│   │   └── insights_engine.py    # AI insights
│   ├── models/                   # ML models
│   │   ├── risk_model.py         # Risk scoring
│   │   ├── decision_logic.py     # Decision rules
│   │   └── config.py             # Model params
│   └── data/
│       └── sample_fleet.csv      # Demo data
│
├── tests/                        [Automated Tests]
│   ├── test_models.py            # Model tests
│   ├── test_pipeline.py          # Pipeline tests
│   └── conftest.py               # Pytest config
│
├── docs/                         [Documentation]
│   ├── DATA_FORMAT.md            # CSV specifications
│   ├── API_REFERENCE.md          # Future API docs
│   ├── CONTRIBUTING.md           # Dev guidelines
│   └── analysis_and_insights/    # Keep analysis docs
│
├── scripts/                      [Utility Scripts]
│   └── export_sample.py          # Sample data export
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD pipeline
│
├── data/                         [Data Storage]
│   ├── raw/                      # Raw input data
│   ├── processed/                # Processed data
│   └── final/                    # Final outputs
│
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment template
├── README.md                     # Project overview
├── SETUP.md                      # Setup instructions
├── requirements.txt              # Root dependencies (if needed)
└── docker-compose.yml            # Multi-container setup
```

---

## 🗑️ DELETION LIST (Safe to remove)

### **Directories to Delete**
- [ ] `/src/` - Legacy code, all modules duplicated in `/core/` and `/app/core/`
- [ ] `/notebooks/` - Keep reference copy, don't use in production
- [ ] `/scripts/old_*` - Any old experimental scripts
- [ ] `/reports/` - Auto-generated, not maintained

### **Files to Delete**
- [ ] `app.py` - Legacy Streamlit wrapper (new one is `/app/main.py`)
- [ ] `clear_db.py` - Old database script
- [ ] `CLEANUP_REPORT.md` - Old report
- [ ] `DEPLOYMENT_READY.md` - Old deployment docs
- [ ] `MODEL_CARD.md` - Outdated model info
- [ ] `EXECUTIVE_DECISION_BRIEF.md` - Old executive brief
- [ ] `sample_lime_data_20251109_123053.json` - Old sample
- [ ] `*.pyc`, `__pycache__/` - Compiled Python files

### **Files to Keep / Refactor**
- [ ] `README.md` - Update with new structure
- [ ] `SETUP.md` - Refactor for new layout
- [ ] `requirements.txt` - Consolidate dependencies
- [ ] `data/` folder - Keep data structure
- [ ] `docs/` - Consolidate documentation

---

## 🔧 Consolidation Tasks

### **Task 1: Move core modules to app/**
```bash
cp -r core/* app/core/
cp -r models/* app/models/
cp -r utils/* app/utils/
```

### **Task 2: Delete source duplicates**
```bash
rm -rf src/
rm -rf models/
rm -rf utils/
```

### **Task 3: Update imports everywhere**
- Files should import from: `app.core.*`, `app.models.*`, `app.utils.*`
- OR symlink: `from core import ...` → works because `/app/` is root

### **Task 4: Update dependencies**
New consolidated `requirements.txt`:
```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
streamlit>=1.28.0
plotly>=5.17.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

### **Task 5: Documentation consolidation**
- Move all docs to `/docs/`
- Keep `/app/README.md`, `/app/ARCHITECTURE.md`, `/app/DEPLOYMENT.md`
- Archive historical docs to `/docs/archive/`

---

## 📋 Step-by-Step Cleanup Plan

### **Phase 1: Safety (No deletions)**
- [x] Analyze structure ✓
- [ ] Run tests on current code
- [ ] Create backup branch: `git checkout -b backup-before-cleanup`
- [ ] Document what each old file does

### **Phase 2: Consolidation**
- [ ] Move `/core/` modules to `/app/core/`
- [ ] Move `/models/` to `/app/models/`
- [ ] Move `/utils/` to `/app/utils/`
- [ ] Update all imports
- [ ] Run tests again

### **Phase 3: Cleanup**
- [ ] Delete `/src/` folder
- [ ] Delete `/models/` folder (now in app/models/)
- [ ] Delete `/utils/` folder (now in app/utils/)
- [ ] Delete old `app.py`, `clear_db.py`, etc.
- [ ] Remove old documentation files

### **Phase 4: Documentation**
- [ ] Write new `/README.md` (root level overview)
- [ ] Keep `/app/README.md` (quick start)
- [ ] Consolidate `/docs/`
- [ ] Archive historical files

### **Phase 5: Validation**
- [ ] All imports work
- [ ] Streamlit app runs
- [ ] Tests pass
- [ ] No broken references

---

## 🎯 Post-Cleanup Benefits

| Benefit | Current | After Cleanup |
|---------|---------|---------------|
| **Clarity** | 7+ overlapping locations | Single `/app/` structure |
| **Maintenance** | Update code in 2-3 places | Update once, use everywhere |
| **Onboarding** | "Which version am I using?" | Clear: use what's in `/app/` |
| **Build time** | Longer (imports scattered) | Faster (consolidated) |
| **Test coverage** | Unclear which to test | Test `/app/` and `/tests/` |
| **Deployment** | Confusing, multiple entry points | Single `app/main.py` |

---

## ⚠️ Risk Assessment

| Risk | Probability | Mitigation |
|------|------------|-----------|
| Lose old code | LOW | Git backup branch kept |
| Break imports | MEDIUM | Run tests after each change |
| Data loss | VERY LOW | `/data/` folder untouched |
| Deployment fails | LOW | Test locally before commit |

---

## 🚀 Success Criteria

- [ ] **Single source of truth**: All code in `/app/`
- [ ] **No duplicates**: No overlapping modules
- [ ] **Clean imports**: All imports resolve correctly
- [ ] **Tests pass**: 100% of unit tests pass
- [ ] **App runs**: Streamlit dashboard launches successfully
- [ ] **Documentation clear**: README and docs accurately reflect structure
- [ ] **Production ready**: Can deploy without lingering questions

---

## 📊 Estimated Impact

**Before Cleanup**:
- Directory count: 10+ folders
- Duplicate files: 3-5 modules living in multiple places
- Documentation: Scattered, inconsistent
- Deployment process: Unclear which entry point to use

**After Cleanup**:
- Directory count: 5 focused folders
- Duplicate files: ZERO
- Documentation: Centralized, consistent
- Deployment process: Crystal clear (`/app/main.py`)

---

## 🔐 Backup Strategy

**Before making any changes:**
```bash
# Create backup branch
git checkout -b backup-20260327

# Push to remote
git push origin backup-20260327

# Mark current state
git tag cleanup-start-20260327
```

**Rollback if needed:**
```bash
git reset --hard backup-20260327
# or
git revert <commit-hash>
```

---

## 📝 Notes for Your Team

> **This repository evolved over multiple iterations.** The `/core/`, `/utils/`, and new `/app/` structure represent the latest, best-practice design. The `/src/` folder is legacy and can be safely removed once we verify nothing depends on it.

> **After cleanup, this becomes production-grade.** Clean structure, single entry point, scalable architecture.

---

**Status**: Ready for execution  
**Owner**: You (Fleet Intelligence AI Founder)  
**Priority**: HIGH (blocks production deployment)
