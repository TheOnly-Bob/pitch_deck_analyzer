import json
from groq import Groq
from pydantic import BaseModel, Field
from typing import List
from enum import Enum


def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


class ScoredCriterion(BaseModel):
    score: int = Field(ge=1, le=5, description="Integer score between 1 and 5")
    rationale: str


class DataCompleteness(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Verdict(str, Enum):
    STRONG_PASS = "Strong Pass"
    PASS_ = "Pass"
    BORDERLINE = "Borderline"
    NOT_NOW = "Pass — Not Now"


class PitchDeckEvaluation(BaseModel):
    investor_communication_and_clarity: ScoredCriterion
    narrative_and_storytelling: ScoredCriterion
    problem_solution_fit: ScoredCriterion
    strengths: List[str]
    weaknesses: List[str]
    investor_insights_and_risks: List[str]
    data_completeness: DataCompleteness
    verdict: Verdict
    verdict_rationale: str


SYSTEM_EVALUATION_PROFILE = """
EVALUATION PROFILE: Venture Capital Pitch Deck Assessment
TARGET ROLE: Investment Committee Analyst

ASSESSMENT CRITERIA:
1. Investor Communication & Clarity: Evaluate text density, grammatical precision, and slide readability.
2. Narrative & Storytelling: Evaluate the logical progression from problem identification to proposed solution and funding request. Note structural inconsistencies.
3. Problem-Solution Fit: Validate the causal relationship between the validated market pain point and the proposed solution.

BOUNDARY CONDITIONS:
- Evidence Constraints: Assessments must rely strictly on explicit text provided in the source document.
- Missing Data Handling: Unstated metrics, financial figures, or facts must be explicitly flagged as 'null' or 'Not Disclosed'. Do not extrapolate or estimate missing data.
- Processing Requirement: Generate internal rationales for each criterion prior to assigning numerical scores.

CALIBRATION BENCHMARKS:

Benchmark A: Airbnb 2008 (High Fidelity)
- Excerpt: "Problem: Price is a concern. Hotels leave you disconnected from the city. Solution: A web platform where users can rent out their space to host travelers."
- Output Mapping: Problem-Solution Fit (5/5); Narrative & Storytelling (5/5). 
- Verdict Output: Strong Pass

Benchmark B: Generic AI Startup (Low Fidelity)
- Excerpt: "Problem: People need AI. Solution: We built an AI platform that does everything for everyone. Traction: We are experiencing rapidly growing interest from major enterprises."
- Output Mapping: Problem-Solution Fit (2/5); Investor Communication & Clarity (2/5).
- Verdict Output: Pass — Not Now
"""


def evaluate_deck(client: Groq, deck_text: str) -> PitchDeckEvaluation:
    schema_str = json.dumps(PitchDeckEvaluation.model_json_schema(), indent=2)
    system_prompt = f"{SYSTEM_EVALUATION_PROFILE}\n\nEnforce schema validation:\n{schema_str}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": deck_text}
        ],
        temperature=0.2,
        max_tokens=1024,
        response_format={"type": "json_object"}
    )
    
    return PitchDeckEvaluation.model_validate_json(response.choices[0].message.content)
