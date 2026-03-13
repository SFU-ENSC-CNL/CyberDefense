# CyberDefense v2 Integration Diff

## Overview

This document summarizes the integrated **CyberDefense v2** repository structure after consolidation and cleanup work.  
It reflects the **new repository layout** provided by the user on **March 12, 2026**.

## Integration Summary

The repository now appears organized into the following major layers:

- **Application entrypoints** at root
- **Database layer** under `database/`
- **Deployment assets** under `deploy/`
- **Core processing and ML logic** under `src/`
- **Frontend assets** under `static/` and `templates/`
- **Research / workflow tooling** under `tools/bgp_research_tools/`

This is a strong improvement over a flatter or partially duplicated structure because it separates:

- runtime app code
- deployment assets
- experiments and legacy research code
- reusable toolchain components
- UI/static resources

---

## Top-Level Structure

```text
.
├── .gitignore
├── app.py
├── app_offline.py
├── app_realtime.py
├── config.py
├── cyberdefense_v2_integration_diff.md
├── LICENSE
├── README.md
├── REPO_STRUCTURE.txt
├── requirements.txt
├── database/
├── deploy/
├── src/
├── static/
├── templates/
└── tools/
```

## Key Structural Changes Captured

### 1. Root-level app entrypoints are clearly separated
The repo now exposes three main application entry files:

- `app.py`
- `app_offline.py`
- `app_realtime.py`

This suggests a cleaner split between:
- shared/default app execution
- offline workflow mode
- realtime workflow mode

### 2. Database assets are isolated
Database logic and persisted DB files are now grouped under:

```text
database/
├── database.py
└── db_files/
    └── data.db
```

This is cleaner than mixing DB files with app logic.

### 3. Deployment assets are grouped
Deployment files are now under:

```text
deploy/docker-compose-CyberDefense/
```

Containing:
- `docker-compose.yml`
- image/build-related files
- deployment README
- deployment-specific `.gitignore`

This makes deployment packaging much easier.

### 4. Core source code is centralized under `src/`
The `src/` folder now acts as the main integration zone for:

- preprocessing
- data download
- feature extraction
- label generation
- progress / utility helpers
- model code
- historical datasets
- experimental notebooks
- feature selection
- model assets
- legacy and auxiliary algorithm implementations

### 5. Research tooling is now separated from main app code
The `tools/bgp_research_tools/` subtree is a good separation for:

- CLI workflows
- experiments
- SDK/docs
- reusable dataset pipelines
- feature extraction pipeline tooling
- training/evaluation helpers

This is preferable to mixing research automation directly into production app paths.

---

## Detailed Folder Notes

## `database/`

Purpose:
- persistent SQLite handling
- backend storage support

Contents:
- `database.py` for DB access logic
- `db_files/data.db` for actual database file

Recommendation:
- add `db_files/*.db` to `.gitignore` unless committed DB state is intentionally versioned

---

## `deploy/`

Purpose:
- containerized deployment assets

Current structure:
```text
deploy/
└── docker-compose-CyberDefense/
    ├── .gitignore
    ├── cyberdefense-python
    ├── cyberdefense-python-dev
    ├── docker-compose.yml
    └── README.md
```

Notes:
- deployment files are now grouped well
- naming is clearer than leaving compose assets spread across repo root
- consider renaming `docker-compose-CyberDefense` to `docker/` or `compose/` later for simpler pathing

---

## `src/`

Purpose:
- main implementation code and legacy algorithm modules

### Root Python utilities in `src/`
These appear to support the core data workflow:

- `check_versions.py`
- `dataDownload.py`
- `data_partition.py`
- `data_process.py`
- `featureExtraction.py`
- `label_generation.py`
- `progress.py`
- `progress_bar.py`
- `subprocess_cmd.py`
- `time_tracker.py`

These files indicate the pipeline likely includes:
1. data acquisition
2. transformation / partitioning
3. feature extraction
4. labeling
5. model-ready dataset generation

### Integrated submodules inside `src/`

#### `BiRNN_Running_Code/`
Contains BiRNN execution templates, datasets, and runtime generation helpers.

#### `CSharp_Tool_BGP/`
Contains the C# feature extraction tool and solution/project files.

This appears to be preserved as a legacy or dependent component for BGP feature extraction.

Recommendation:
- if only the built executable is needed, consider moving source-only legacy code under `legacy/` or `third_party/`
- if this code is actively maintained, keep it but document when it is used vs Python tooling

#### `data_historical/`
Contains sample/reference historical datasets such as:
- `Code_Red_I.csv`
- `Nimda.csv`
- `Slammer.csv`
- `WannaCrypt.csv`

This is useful for reproducibility and benchmarking.

#### `data_ripe/` and `data_routeviews/`
Contain scripts/parsers for RIPE and RouteViews data workflows.

#### `experimental/`
Contains notebook and script-based exploratory work for sliding windows.

This is correctly separated from primary runtime code.

#### `featureSelection/`
Holds feature selection logic.

#### `integrations/`
Currently present but appears empty.

Recommendation:
- use this folder for future system-level integration adapters
- or remove it until needed to avoid dead structure

#### `modelOcean/`
Contains model demo and serialized model artifacts:
- `gru_2layer_demo.py`
- `.pkl` files

Recommendation:
- version large binaries carefully
- consider Git LFS if model artifacts grow

#### `playground/`
Contains isolated experimentation code (`gbdt_offline_sample`)

This is a good place for non-production prototype work.

#### `RNN_Running_Code/`
Parallel structure to BiRNN code, containing runtime and dataset templates.

#### `VFBLS_v110/`
Contains VFBLS/BLS real-time model code and model artifacts.

---

## `static/`

Purpose:
- frontend static assets

Contents:
- CSS
- images
- JavaScript

This layout is conventional and clean for Flask-style apps.

Notable assets include:
- logos
- module diagrams
- architecture diagrams
- chart emission scripts
- interaction handlers

---

## `templates/`

Purpose:
- frontend HTML templates

Includes:
- `index.html`
- layout and contact templates
- offline/realtime UI templates

This appears correctly separated for a Flask/Jinja app structure.

---

## `tools/bgp_research_tools/`

Purpose:
- modular research, experimentation, CLI, and workflow tooling for BGP data processing

This subtree is one of the strongest parts of the new structure because it isolates research tooling into a self-contained package.

### Notable strengths
- dedicated docs (`docs/cli.md`, `docs/sdk.md`)
- examples
- test file
- CLI entrypoints
- modular `src/` organization by workflow stage

### Internal workflow modules include:
- dataset handling
- data download
- data labeling
- data merging
- data parsing
- data transformation
- exploratory analysis
- feature extraction
- feature selection
- model evaluation
- model training

### Important note
This tree also includes:

```text
feature_extraction/ConsoleApplication1.exe
```

If this executable is required for runtime, document:
- platform assumptions
- how it is built
- when it is invoked
- whether source in `src/CSharp_Tool_BGP/` is the authoritative source

---

## Observed Improvements vs Earlier State

Compared with the earlier cleanup issues discussed, this new structure suggests the following improvements:

### Improved
- deployment assets no longer appear mixed with unrelated files
- the repository is easier to scan at top level
- frontend/static/template separation is clear
- research tooling is isolated under `tools/`
- the data science / experimental / legacy code is mostly grouped under `src/`

### Still worth improving
- some legacy/experimental/model artifact content is still mixed into `src/`
- duplicated concepts may still exist between:
  - `src/featureExtraction.py`
  - `tools/bgp_research_tools/src/feature_extraction/...`
  - `src/CSharp_Tool_BGP/...`
- serialized artifacts (`.pkl`, `.npz`, `.db`, `.exe`) should be reviewed for versioning strategy
- naming convention is mixed:
  - snake_case
  - CamelCase
  - title-like folder names
- empty `src/integrations/` should either be used or removed

---

## Potential Duplication / Consolidation Areas

### Feature extraction
There are at least three feature-extraction-related areas:

1. `src/featureExtraction.py`
2. `src/CSharp_Tool_BGP/`
3. `tools/bgp_research_tools/src/feature_extraction/`

This may be fine if responsibilities differ, but should be documented clearly:
- production feature extraction path
- research feature extraction path
- legacy/native tool path

### RNN / BiRNN template structures
Both:
- `src/RNN_Running_Code/`
- `src/BiRNN_Running_Code/`

contain similar layouts and template patterns.

Possible future improvement:
- extract shared runtime/template generation logic
- reduce duplicated dataset/template folder structures

---

## Recommended Next Cleanup Pass

## High priority
1. Add or refine `.gitignore` rules for:
   - `*.db`
   - `*.pkl`
   - `*.npz`
   - generated datasets
   - logs
   - temporary notebook outputs

2. Document authoritative execution path in `README.md`:
   - which app file to run
   - which mode each app supports
   - whether `tools/bgp_research_tools` is optional or required

3. Clarify which folders are:
   - production
   - experimental
   - legacy
   - training-only

## Medium priority
1. Standardize naming conventions across folders/files
2. Move legacy language-specific code into `legacy/` or `native_tools/` if appropriate
3. Add architecture documentation for data flow:
   - ingest
   - parse
   - feature extraction
   - labeling
   - training
   - inference
   - frontend display

## Nice to have
1. Add `Makefile` or task runner
2. Add tests beyond `tools/bgp_research_tools/tests.py`
3. Add environment setup docs for Windows/Linux/macOS
4. Add per-module README files for complex subtrees

---

## Suggested Classification of Folders

| Folder | Suggested Role |
|---|---|
| `database/` | persistence |
| `deploy/` | deployment/infrastructure |
| `src/` | core + legacy ML/data pipeline code |
| `static/` | frontend assets |
| `templates/` | frontend views |
| `tools/` | research/CLI/tooling |

---

## Proposed Future Refinement

A future refined structure could eventually evolve toward:

```text
.
├── apps/
├── config/
├── database/
├── deploy/
├── docs/
├── src/
│   ├── pipeline/
│   ├── models/
│   ├── realtime/
│   ├── offline/
│   ├── legacy/
│   └── experiments/
├── static/
├── templates/
└── tools/
```

This is not required now, but it would make the repo even easier to maintain at scale.

---

## Conclusion

The new repository structure is significantly more organized and integration-ready than the earlier mixed state.

### Main strengths
- good separation of deployment, frontend, tooling, and source code
- research tooling isolated under `tools/`
- app entrypoints visible at root
- support data and model assets grouped more logically

### Main remaining risks
- legacy/runtime/experimental boundaries are not yet fully explicit
- potential duplication remains in feature extraction and RNN-related code
- binary/model/database artifacts should be reviewed for source-control hygiene

Overall, this structure is a solid **v2 integrated repo layout** and is a good foundation for:
- further cleanup
- Docker-based deployment
- better developer onboarding
- future modularization
