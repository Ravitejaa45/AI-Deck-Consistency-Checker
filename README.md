# AI Deck Consistency Checker with Docling & LLM Validation

AI-powered tool designed to automatically analyze business presentation decks (PPTX) for **inconsistencies, metric mismatches, and contradictory claims**. The system combines **Docling** for high-quality PowerPoint parsing, **rule-based numeric/text checks**, and **LLM-based reasoning** to ensure data integrity, factual accuracy, and messaging consistency across slides.

Whether you’re preparing investor pitches, quarterly business reviews, or marketing decks - this tool helps catch hidden contradictions before they reach your audience.


## What This Project Does

This application transforms static PPTX decks into structured, machine-readable text, then applies multiple layers of validation:

- **Structural Parsing**: Converts PPTX slides into clean, consistent text representations using **Docling**.
- **Rule-Based Checks**: Identifies numeric inconsistencies (e.g., “10% growth” vs “15% growth”) and text contradictions.
- **LLM Validation**: Uses a Large Language Model (LLM) to detect subtle logical or semantic conflicts.
- **Deduplication & Merging**: Consolidates similar issues into clear, concise reports.
- **Report Generation**: Outputs results in both **JSON** (machine-readable) and **Markdown** (human-readable) formats.

## Technical Stack Summary

| **Layer**             | **Tools / Libraries** |
|-----------------------|-----------------------|
| **Document Parsing**  | [Docling](https://github.com/docling-project/docling) for PPTX parsing and text extraction. |
| **Rule-Based Checks** | Custom Python regex and comparison logic for numeric/text validation. |
| **LLM Backend**       | Gemini API (configurable for other LLMs). |
| **Deduplication**     | Message normalization & fuzzy matching. |
| **Secrets Management**| `python-dotenv` for `.env` API key handling. |
| **Output Formats**    | JSON, Markdown reports. |

## Supported File Formats

While optimized for **PPTX**, the Docling parser can be extended to handle additional document types (PDF, DOCX, etc.) with minimal changes.

**Currently supported:**
- `.pptx` – Microsoft PowerPoint presentations.

## Why Docling?

Docling provides **layout-aware parsing** that preserves text grouping, slide structure, and reading order, making it ideal for semantic consistency checks.

**Key advantages:**
- Accurate extraction of bullet points, titles, and body text.
- Handles embedded objects and complex slide layouts.
- Outputs clean text for downstream LLM/rule-based processing.

## Key Features

- **Hybrid Validation**: Combines deterministic rule checks with probabilistic LLM reasoning.
- **Multi-Layer Deduplication**: Removes redundant issues with fuzzy string normalization.
- **Customizable**: Easily adjust numeric tolerance thresholds, regex patterns, and LLM prompts.
- **Traceable**: Output includes affected slide numbers and extracted text snippets.
- **LLM-Agnostic**: Swappable backend (Gemini, OpenAI, Claude, etc).

## Project Structure

```text
ai-deck-consistency-checker/
├── detectors/
│   ├── numeric.py        
│   ├── text.py        
│   └── timeline.py      
├── out/                
├── utils/
│   ├── io.py                
│   ├── text_norm.py   
├── extractor_docling.py 
├── extractor_pptx.py 
├── llm_client.py 
├── main.py               
├── .env                        
├── requirements.txt             
└── README.md             
```

# Setup Instructions

## 1. Clone the repository

```bash
git clone <path to source_code .git>
cd AI-Deck-Consistency-Checker
```

## 2. Create & activate venv

```bash
python -m venv <env_name>
venv\Scripts\activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Add your API keys in `.env`

```bash
GEMINI_API_KEY=<your_gemini_api_key>
```

## 5. Run the checker

```bash
python main.py --pptx ./NoogatAssignment.pptx --parser docling
```

## Sample Output

```bash
Found 8 issues. See out/report.json and out/report.md
```

## Sample Use Case

Upload a **pitch deck** before a board meeting:

- Finds conflicting KPI numbers across slides.
- Detects semantic contradictions like “AI model deployed” vs “AI model under development”.
- Outputs a clean, reviewable report for the presentation team.


## Summary

The AI Deck Consistency Checker ensures presentation decks are **factually consistent, semantically aligned, and free from conflicting claims**. With **Docling-powered parsing** and **LLM-backed reasoning**, it’s a must-have tool for high-stakes business communication.

Key highlights:

- **Docling-powered** structured parsing of PPTX.
- Hybrid rule-based + LLM validation pipeline.
- Deduplication for clean, actionable reports.
- Flexible CLI workflow with API key management via `.env`.  
