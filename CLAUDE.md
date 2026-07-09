# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monorepo for a Vietnam IT recruitment market dashboard: crawling → data processing → a FastAPI backend that serves Plotly figures as JSON → a React frontend that renders them. Vietnamese-language UI and column names throughout.

## Running the app

**Quick start (Windows):** double-click `run.bat` from the repo root — it opens two terminals, one for backend (`py -m uvicorn backend.main:app --reload`, run from `dashboard/`) and one for frontend (`npm run dev`, run from `dashboard/frontend/`). Frontend at `http://localhost:5173`, backend at `http://localhost:8000`.

**Manual:**
```bash
# Backend
cd dashboard/backend
pip install -r requirements.txt
cd dashboard          # uvicorn must be launched from dashboard/ since main.py imports "backend.xxx"
uvicorn backend.main:app --reload

# Frontend
cd dashboard/frontend
npm install
npm run dev
```

Frontend lint: `npm run lint` (from `dashboard/frontend`).

There is no automated test suite in this repo.

## Architecture

**Request flow (Client → Server → Client):**
1. A `Dashboard_pageN.jsx` component holds filter state (position, experience, region, sources, ...) via `useState`, and POSTs it with `axios` to an endpoint like `http://localhost:8000/api/dashboard/page1` on filter change (`useEffect`).
2. The matching `dashboard/backend/routers/router_pageN.py` decodes the JSON body into a Pydantic `FilterRequest` model, loads the dataset into a pandas DataFrame, and filters it.
3. The filtered DataFrame is passed to chart-building functions in `dashboard/backend/utils/charts_pageN.py`, which use Plotly Express/Graph Objects to build figures and compute KPI numbers. `apply_layout_styles()` in `dashboard/backend/utils/charts_common.py` is applied to every figure for consistent styling (also holds `PROVINCE_COORDINATES` for the choropleth/scatter map).
4. The router serializes each figure with `json.loads(fig.to_json())` and returns `{ kpis, charts: {...} }`.
5. The frontend passes `data.charts.xxx` straight into the `<PlotlyChart figure={...} />` wrapper component (backed by `react-plotly.js`), and numeric KPIs into `<KpiCard />`.

New dashboard pages follow this same router → chart-utils → PlotlyChart pattern; add a new `router_pageN.py` + `charts_pageN.py` pair and `include_router` it in `dashboard/backend/main.py`.

**Page 5 — AI analysis (`router_page5.py`)** is a separate flow: it prompts Gemini (`google-generativeai`, model `gemini-1.5-pro`, requires `GEMINI_API_KEY` env var — falls back to a canned dummy script if unset) to generate pandas/Plotly code against a DataFrame called `dff`, stores the generated code + a request id in `dashboard/backend/ai_history.json` for user review, and only runs it via `exec()` in `/api/ai/execute` after the user approves/edits it in the UI (`components/ai/Ai*.jsx`). Treat `ai_history.json` and the exec step as sensitive — it executes model-generated code server-side.

Every router computes `root_dir` as 4 parents up from its own file (i.e. the repo root, `TQH-FINAL-PROJECT-N5/`) and reads `data/processed/vietnam_it_jobs_processed.csv` — keep the dataset at that path.

## Data

- Main dataset: `data/processed/vietnam_it_jobs_processed.csv` — 18 columns, Vietnamese names: `ten_cong_viec`, `ten_cong_ty`, `nhom_vi_tri` (position group: Software Development/AI-ML-Data Science/Mobile-Game-Embedded/Cloud-DevOps-SRE/QA-Testing/Data Engineering-Database/...), `cap_do_kinh_nghiem` (Intern/Fresher/Junior/Middle/Senior...), `tinh_thanh` (province), `vung_mien` (region: Bắc/Trung/Nam/Từ xa/Khác), `luong_goc`/`luong_min`/`luong_max`/`luong_tb` (salary text and parsed triệu-VNĐ figures), `loai_luong` (range/negotiable/to/from), `ky_nang` (comma-separated skill list), `mo_ta`, `hinh_thuc_lam_viec`, `ngay_dang`, `thang_dang`, `nguon` (source: ITviec, TopCV, TopDev, Vieclam24h, JobsGO, VietJobs), `url`.
- `crawler/` holds raw scraped output (`crawler/output/*.json`) and saved HTML snapshots (`crawler/html_input/*.html`) used as crawler input/fixtures.
- `notebooks/crawling.ipynb`, `notebooks/eda.ipynb`, `notebooks/preprocessing.ipynb` cover the crawl → EDA → preprocessing pipeline that produces the processed CSV.
- `.gitignore` excludes `*.csv`/`*.json` broadly but explicitly re-includes `crawler/output/*.json`, `crawler/html_input/*.html`, and `data/vietnam_it_jobs_raw.csv` — keep new tracked data files' exceptions in `.gitignore` if you add any.

## Frontend structure

- `App.jsx` owns a single `activeTab` (1–5) state and conditionally renders `Dashboard_page{1..5}`; there is no router library, tabs are plain state.
- `components/PlotlyChart.jsx` is the shared wrapper around `react-plotly.js` used by every dashboard page.
- `components/ai/` (`AiRequestForm`, `AiHistoryPanel`, `AiChatMessage`, `AiService.js`) implement the page-5 AI request/approve/execute flow described above.
- Styles are plain CSS in `styles/` (`style.css` global + one `style_pageN.css` per page), not CSS modules.
