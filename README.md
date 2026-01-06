# FindUrCite: AI-Powered Research Assistant with Multi-Agent Debate

**FindUrCite** is an advanced academic research tool that automates literature review, code discovery, and paper analysis. It uses a **Multi-Agent Debate System** (Student & Advisor) to ensure high-quality, hallucination-free analysis.

## Key Features

1.  **Multi-Agent Debate**: Uses a "Student" agent to draft analysis and an "Advisor" agent to critique and refine it, ensuring rigor and accuracy.
2.  **Deep Read Pipeline**: Automatically downloads PDFs, extracts text, and performs full-text analysis for high-relevance papers.
3.  **Expanded Search**: Generates multiple search queries (Broad, Specific, Niche) to find a wider range of papers from Semantic Scholar and ArXiv.
4.  **Parallel Processing**: Concurrent PDF downloads and code searches for maximum speed.
5.  **Evidence-Based**: Requires direct quotes ("Evidence") from the text to support claims.
6.  **Code Discovery**: Automatically finds relevant GitHub repositories and stars.
7.  **Excel-Aligned Report**: Outputs a detailed 23-column Markdown report compatible with Excel import.

## Installation

1.  **Prerequisites**:
    *   Python 3.8+
    *   [Ollama](https://ollama.com/) running locally (default model: `qwen2.5:7b`)

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Prepare your input**: Create a text file (e.g., `draft.txt`) with your research idea or abstract.
2.  **Run the system**:
    ```bash
    python src/main.py draft.txt
    ```
    Or use the test script:
    ```bash
    tests/run_test.bat
    ```

## Output

Results are saved in a timestamped folder (e.g., `research_output_20260101_120000/`), containing:
*   `research_result.md`: The comprehensive analysis report.
*   `pdfs/`: Downloaded full-text PDFs.

## Architecture

*   `src/agents/`: Contains the LLM agents (Student, Advisor).
*   `src/workflow.py`: Orchestrates the debate loop.
*   `src/searcher.py`: Handles multi-source paper search.
*   `src/pdf_processor.py`: Manages PDF download and text extraction.
*   `src/code_finder.py`: Finds relevant code on GitHub.

## License

MIT License
