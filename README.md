# Reddit Content Classification Pipeline
Python pipeline for Reddit data collection, filtering, and content classification support

## Overview
This repository contains the code-side workflow for a research project on how Reddit users describe turning to AI for mental health-related support.

The workflow covers multiple stages of dataset preparation and review, including LLM-based screening, agreement checking between model and human labels, data cleaning and stratified sampling, Rickwood-dimension coding, validation of LLM-assisted coding, batch coding, and descriptive statistics.

While the broader project also involved coding framework design and detailed coding manual development, this repository focuses on the technical workflow used to support screening, coding, validation, and downstream analysis.

## Workflow Stages

This repository supports a multi-stage workflow for screening, coding, validating, and analyzing Reddit posts related to AI-mediated mental health support.

1. **Screening**  
   Initial relevance screening, exclusion-oriented filtering, and risk-related flagging.

2. **Agreement Checking**  
   Comparison between model-generated labels and human judgment on sampled cases.

3. **Data Cleaning and Sampling**  
   Filtering, deduplication, and preparation of structured datasets for downstream coding.

4. **Rickwood-Dimension Coding**  
   Batch coding of retained posts across key analytic dimensions.

5. **Validation and Review**  
   Review of LLM-assisted coding outputs, disagreement checking, and rule refinement.

6. **Batch Processing and Output Generation**  
   Large-scale coding runs, export handling, and structured output generation.

7. **Descriptive Analysis**  
   Summary statistics and basic cross-tabulation for coded outputs.

## Repository Structure

- `screening_prompt.py` – supports relevance screening, exclusion checks, and risk-related flagging
- `agreement_check.py` – compares model-generated labels with human judgment on sampled cases
- `data_cleaning.py` – handles filtering, deduplication, and sampling for downstream coding
- `rickwood_coding.py` – supports coding across the main analytic dimensions
- `rickwood_validation.py` – validates LLM-assisted coding against reviewed labels
- `batch_coding.py` – runs large-scale coding workflows and manages structured outputs
- `descriptive_stats.py` – generates summary statistics and basic cross-tabulations

## Why This Project Matters

This project demonstrates practical experience in building and supporting a structured screening, coding, and validation workflow for ambiguous content.

The workflow is relevant to AI Quality and Trust & Safety work because it combines classification support, human–AI comparison, review consistency, and decision-rule refinement.

## Research Relevance

The broader research project examines how users describe turning to AI for mental health-related support in ways that often involve ambiguity, boundary cases, and overlapping categories.

These issues are also relevant to AI safety and governance because they show that evaluating AI-related content is not only a matter of surface meaning, but also of how support, risk, and legitimacy are interpreted in social context.

## Skills Demonstrated

- Python-based workflow development
- structured data filtering and preparation
- batch coding support
- LLM-assisted content classification
- human review and validation
- disagreement analysis and calibration support
- decision-rule refinement for ambiguous cases
- descriptive statistics and basic cross-tabulation

## How to Run

1. Clone this repository.
2. Install the required Python packages listed in `requirements.txt`.
3. Prepare the necessary input files for the relevant workflow stage.
4. Run the corresponding script depending on the task (e.g., screening, coding, validation, or descriptive analysis).
5. Review the generated outputs in the designated output files or folders.
