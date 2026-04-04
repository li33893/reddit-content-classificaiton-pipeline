# AI-Mediated Mental Health Content: Screening, Coding, and Validation Workflow

A structured, multi-stage pipeline for screening, classifying, validating, and analysing Reddit posts about AI use in mental health contexts.

## Overview

This repository contains the technical workflow for a research project examining how Reddit users describe turning to AI for mental health-related support.

The pipeline processes approximately 2,000 posts through seven stages: LLM-based relevance screening, human–LLM agreement verification, data cleaning and stratified sampling, multi-dimensional content coding, coding validation, batch processing, and descriptive analysis.

The broader research project also involved classification framework design, detailed coding manual development, exclusion and decision rule specification, and interpretive discourse analysis — work that is not contained in this repository but informed the design of every stage documented here.

## Why This Project Matters

This workflow addresses a problem shared across AI evaluation, content policy, and AI governance: **how to systematically classify and assess AI-related content that is ambiguous, context-dependent, and resistant to simple categorisation.**

The pipeline demonstrates:

- **Evaluation framework design** — building a multi-dimensional classification system for content where categories overlap and boundary cases are frequent
- **Human–AI comparison methodology** — Three-stage human–LLM validation workflow — relevance screening showed strong agreement (κ = 0.856, AC1 = 0.857); pilot coding reached substantial agreement across Timeframe (κ = 0.765), Source (κ = 0.684), and Type (κ = 0.682); and held-out validation confirmed generalization across Timeframe (κ = 0.790), Source (κ = 0.806), and Type (κ = 0.758)
- **Decision rule development for ambiguous cases** — iterative refinement of classification guidelines through structured disagreement analysis
- **Scalable quality assurance** — designing a process that maintains consistency across 2,000+ items while preserving sensitivity to edge cases

These capabilities are directly relevant to:

- **AI policy and governance** — the project produces empirical evidence on how AI safety mechanisms (e.g., disclaimers) function in practice, with direct implications for regulatory frameworks such as Korea's AI Basic Act
- **AI evaluation and quality assurance** — the workflow operationalises the full cycle of evaluation standard design → pilot validation → batch deployment → quality verification
- **Content classification at scale** — the pipeline handles the core challenge of classifying content where meaning depends on social context, not surface features alone

## Workflow Stages

| Stage | Script | What It Does |
|-------|--------|-------------|
| 1. Screening | `screening_prompt.py` | LLM-based relevance screening with three parallel tasks: relevance judgment, risk-level classification, and psychosis-symptom flagging |
| 2. Agreement | `agreement_check.py` | Human–LLM agreement validation using Cohen's κ and Gwet's AC1 (addresses prevalence paradox under skewed distributions) |
| 3. Cleaning | `data_cleaning.py` | Filtering, deduplication, and proportional stratified sampling across subreddit communities |
| 4. Coding | `rickwood_coding.py` | Multi-dimensional content coding across three analytic dimensions (timeframe, help-seeking ecology, usage intent) |
| 5. Validation | `rickwood_validation.py` | Per-dimension κ computation, confusion matrix analysis, and systematic disagreement export for prompt refinement |
| 6. Batch Processing | `batch_coding.py` | Full-corpus coding with exponential backoff, checkpoint recovery, and cost estimation |
| 7. Analysis | `descriptive_stats.py` | Frequency tables with Wilson score confidence intervals, cross-tabulations by community |

## Repository Structure

```
├── screening_prompt.py          # Stage 1: LLM relevance screening
├── agreement_check.py           # Stage 2: human–LLM agreement check
├── data_cleaning.py             # Stage 3: filtering, dedup, stratified sampling
├── rickwood_coding.py           # Stage 4: multi-dimensional content coding
├── rickwood_validation.py       # Stage 5: coding validation and disagreement analysis
├── batch_coding.py              # Stage 6: full-corpus batch processing
├── descriptive_stats.py         # Stage 7: descriptive statistics
├── requirements.txt             # Python dependencies
└── README.md
```

## Key Design Decisions

- **Dual reliability metrics**: Both Cohen's κ and Gwet's AC1 are reported because κ alone can underestimate agreement under skewed class distributions (the prevalence paradox). Reporting both distinguishes genuine disagreement from statistical artefact.
- **Temperature = 0** for all coding stages to ensure reproducibility across batch runs.
- **Stratified proportional sampling** preserves the ecological distribution of source communities rather than equalising them, reflecting the actual variation in where users discuss AI mental health use.
- **Checkpoint recovery** in batch processing allows interrupted runs to resume without re-processing completed items.
- **Wilson score intervals** for confidence intervals on proportions, more accurate than normal approximation for categories with small counts.

## Research Context

The broader research project examines how users construct their relationship with AI in mental health contexts — including how safety mechanisms like disclaimers function not as warnings but as authorisation devices in user discourse. This finding has direct implications for AI governance frameworks that rely on transparency and disclosure as protective measures.

The coding framework adapts Rickwood and Thomas's (2012) help-seeking measurement framework for human–AI interaction, with usage intent categories drawn from Aghakhani and Rezapour (2026).

## How to Run

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Prepare input data for the relevant stage (see pipeline overview for file specifications).
4. Run the corresponding script (e.g., `python screening_prompt.py`).
5. Review outputs in the designated output files.

**Note**: LLM-based stages require an Anthropic API key configured as an environment variable.

## Scope

This repository covers the **technical workflow implementation** for one component of a broader research project. The classification framework design, coding manual, discourse analysis, and theoretical interpretation are documented in the research paper, not in this repository.
