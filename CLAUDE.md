# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**光影参谋 (Light & Shadow Advisor)** — An AI-powered photography assistant, built as a lightweight Quick App (快应用).

- **Platform:** Quick App (快应用) — lightweight mini-app framework
- **Target users:** 18-35 year olds
- **Core principles:** Lightweight, non-intrusive, beginner-friendly
- **Status:** Pre-development / planning phase. The PDF `「光影参谋」AI拍照助手快应用.pdf` contains the product proposal and market analysis.

## Architecture

Full architecture document: **`ARCHITECTURE.md`** — covers tech stack, database design, API contracts, page layouts, and data flow.

### Tech Stack
- **Frontend:** Quick App (快应用) — Vue-like `.ux` SFCs
- **Backend:** Python FastAPI + SQLite + uvicorn
- **AI:** DeepSeek Vision API (initial) → BlueLM-2.5-3B on-device (semi-finals)
- **State:** qa-vuex for frontend state management

### Backend (`server/`)
- `python server/main.py` — start dev server on port 8000
- `pip install -r server/requirements.txt` — install dependencies

## Technology

Quick Apps use a Vue-like component model with:
- `ux` files (template + style in single file, similar to Vue SFCs)
- JavaScript (ES6+) for logic
- The `hap` CLI for building and debugging
- Manifest in `manifest.json`
- Routing via `src/app.ux` entry point and `src/manifest.json` pages array

Common commands (once initialized):
- `npm run build` / `hap build` — production build
- `npm run dev` / `hap server` — dev server with hot reload
- `npm run lint` — linting with ESLint

Build output goes to `dist/`.
