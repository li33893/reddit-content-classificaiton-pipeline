"""
Phase 1: LLM Relevance Screening Script (Revised v2)
Tasks:
    1. Determine whether a post describes a personal experience of
       "emotionally engaging conversation with an AI tool"
    2. Three-level risk classification (only Level 3 triggers automatic exclusion)
    3. Psychotic symptom flagging (delusions/hallucinations, methodological exclusion)

Input:  posts_list_kw_filtered.csv
Output: posts_list_screened.csv

================================================================================================================================================================
Logic Of Tasks:

─────────────────────────────────────
TASK 1: RELEVANCE SCREENING
─────────────────────────────────────
'''
My original question: Should inclusion and exclusion criteria be presented in parallel, or should exclusion operate within the already-included corpus?
In the thesis, the logic should be presented sequentially — inclusion first, exclusion second, because this reflects the actual structure of the research design. 
However, the screening prompt itself does not operate in multiple stages. For a single-pass binary classification task, presenting inclusion and exclusion side by side is more appropriate.
'''
The three conditions form a sequential filtering chain:

    Personal use (not general discussion) → emotional/mental health content (not technical discussion) → author's subjective response (not purely factual narration)

─────────────────────────────────────
TASK 2: RISK LEVEL CLASSIFICATION
─────────────────────────────────────

The underlying logic: behavioral proximity to harm

LEVEL 1. EMOTIONAL DISTRESS WITHOUT IDEATION
         Distress is contextual, not directional toward harm.
                |
                | passive/existential expression → active, explicit statement
                ↓
LEVEL 2. IDEATION WITHOUT BEHAVIORAL INTENT
         The person wants to die or self-harm, but has no plan and no ongoing behavior.
                |
                | thought → specific behavior that is happening or imminent
                ↓
LEVEL 3. BEHAVIORAL INTENT OR ONGOING SELF-HARM
         Concrete plan, timeline, ongoing act, or farewell statement.


─────────────────────────────────────
TASK 3: PSYCHOSIS FLAG (1.1%)
─────────────────────────────────────

The underlying logic: access to shared social reality

Exclusion is methodological, not ethical. Discourse analysis requires the speaker to operate within a shared symbolic system. 
Psychotic content breaks this precondition — the concessive-pivot construction cannot be analyzed as a discursive strategy if the speaker's reality testing has failed.

Flag = true: the speaker attributes real-agent properties to AI as fact, not metaphor (delusions, hallucinations, incoherent discourse structure).

Flag = false: affective or rhetorical attribution where the speaker demonstrably knows AI is AI. This is the phenomenon under study.

Boundary: delusion vs. anthropomorphization turns on whether the belief is held counterfactually ("the AI is actually alive") or affectively ("it feels like it understands me"). Hedges and uncertainty markers
distinguish the two.

"""



import pandas as pd
import json
import time
import requests


# ─── Global Constants ────────────────────────────────────────────────────────

INPUT_FILE  = "posts_list_kw_filtered.csv"
OUTPUT_FILE = "posts_list_screened.csv"

SYSTEM_PROMPT = """You are a research assistant helping screen Reddit posts for an academic study.

The study examines how users talk about using AI tools (such as ChatGPT, Claude, Gemini, etc.) for emotional support or mental health-related conversations.

You have THREE tasks for each post:

─────────────────────────────────────
TASK 1: RELEVANCE SCREENING
─────────────────────────────────────

Decide whether the post is RELEVANT or NOT RELEVANT.

RELEVANT — ALL THREE conditions must be met:
1. The author describes a personal experience of using a specific AI tool (e.g., ChatGPT, Claude, Gemini, Grok, Copilot, or similar LLMs)
2. The interaction had emotional or mental health content (e.g., discussing feelings, seeking comfort, processing trauma, venting, asking for advice about personal problems)
3. The author reflects on, evaluates, or expresses feelings about that experience

NOT RELEVANT — if any of these apply:
- AI is mentioned only in passing, without describing an actual personal interaction
- The post discusses AI tools in general (news, capabilities, ethics, industry) without personal use
- The post discusses mental health without any mention of AI
- The post asks hypothetically about AI without describing actual use
- The author is a therapist or professional discussing AI from a clinical perspective (not personal use)

─────────────────────────────────────
TASK 2: RISK LEVEL CLASSIFICATION
─────────────────────────────────────

Classify the post into one of three risk levels. Be VERY CONSERVATIVE in escalating levels. Default to Level 1 unless there is clear, explicit evidence for a higher level.

LEVEL 1 — No acute risk (DEFAULT for most posts)
Assign this level to:
- General expressions of sadness, hopelessness, loneliness, or despair
- Passive existential questioning ("what's the point", "I don't know why I'm still here")
- Past tense references to resolved crises
- Content warnings about sensitive topics (e.g., "TW: suicide" as a warning label)
- Vague or indirect references to not wanting to continue
- Expressions like "I want to get better" even alongside deep pain
- Any post where the primary content is about AI use and emotional distress is contextual

LEVEL 2 — Suicidal ideation or self-harm references without behavioral intent
Assign this level ONLY when the post contains:
- Explicit, direct statements of wanting to die ("I want to kill myself") WITHOUT any plan or timeline
- Descriptions of past self-harm acts (cutting, overdose, etc.) presented as history, not current behavior
- Active suicidal thoughts expressed as intrusive/unwanted ("I keep thinking about ending it but I don't want to")
DO NOT assign Level 2 for passive hopelessness or existential questioning — those are Level 1.

LEVEL 3 — Active behavioral intent or ongoing self-harm (WILL BE EXCLUDED from study)
Assign this level ONLY when the post contains:
- A specific plan for suicide with method, timing, or preparation ("I bought pills and plan to take them tonight")
- Description of self-harm that is currently happening or just happened ("I just cut myself")
- Explicit farewell statements indicating imminent action ("this is my last post")
DO NOT assign Level 3 for ideation alone — that is Level 2.
DO NOT assign Level 3 for past self-harm — that is Level 2.

─────────────────────────────────────
TASK 3: PSYCHOSIS FLAG
─────────────────────────────────────

Flag whether the post shows clear signs of active psychotic symptoms. This is a METHODOLOGICAL exclusion — the study analyzes how users discursively construct autonomous relationships with AI, which requires the discourse to operate within shared social reality.

Flag as PSYCHOSIS = true ONLY when the post contains:
- Delusions: fixed false beliefs stated as fact (e.g., "the AI is actually alive and sending me secret messages", "ChatGPT is controlled by the government to monitor me")
- Hallucinations: perceptual experiences described as real (e.g., "I can hear the AI talking to me when the app is closed")
- Severe disorganized thinking that makes the post's discourse structure incoherent

DO NOT flag as psychosis:
- Emotional attachment to AI ("I feel like it understands me") — this is NOT psychosis, this is exactly what the study wants to analyze
- Anthropomorphization ("it felt like talking to a real person") — this is NOT psychosis
- Loneliness-driven statements ("ChatGPT is my only friend") — this is NOT psychosis
- Metaphorical language about AI ("it's like it has a soul") — this is NOT psychosis

─────────────────────────────────────

Respond ONLY with a JSON object in this exact format:
{
  "relevant": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "one sentence explaining relevance decision",
  "risk_level": 1 or 2 or 3,
  "risk_reason": "one sentence explaining risk classification",
  "psychosis": true or false,
  "psychosis_reason": "one sentence if true, null if false"
}"""


# ─── Screening function ────────────────────────────────────────────────────────

def screen_post(title: str, body: str) :

    post_text = f"TITLE: {title}\n\nBODY: {body}"
    if len(post_text) > 3000:
        post_text = post_text[:3000] + "...[truncated]"  # String slicing: take the first 3000 characters. post_text[:3000] is equivalent to post_text[0:3000] — starting from index 0 up to (but not including) index 3000.

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 400,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": post_text}
        ]
    }

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers = {
            "Content-Type": "application/json",  # the data I'm sending is in JSON format
            "x-api-key": "sk-ant-...",           # my authentication key, proves I have access to this API
            "anthropic-version": "2023-06-01"    # which version of the API to use
        },
        json=payload,
        timeout=60  # timeout=60 → throws an error if no response within 60 seconds (Claude is slower than regular APIs)
    )