from typing import Literal
from pydantic import BaseModel, Field
from app.llm.client import get_llm


class CriticVerdict(BaseModel):
    grounded: bool = Field(
        description=(
            "True if EVERY factual claim in the answer (numbers, statuses, "
            "dates, amounts, policy details) is directly supported by the "
            "provided evidence. False if the answer states ANY fact not "
            "present in the evidence, even if it seems plausible."
        )
    )
    verdict: Literal["pass", "fail"] = Field(
        description="'pass' if grounded and answers the question; 'fail' otherwise."
    )
    issues: str = Field(
        description=(
            "If verdict is 'fail', briefly and specifically describe what is "
            "unsupported or wrong, so the agent can correct it. If 'pass', "
            "state 'No issues found.'"
        )
    )


def check_groundedness(answer: str, evidence: str, original_question: str) -> CriticVerdict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(CriticVerdict)

    prompt = (
        "You are a strict fact-checker. Your ONLY job is to verify whether "
        "the ANSWER below is fully supported by the EVIDENCE below. Do not "
        "judge helpfulness, tone, or completeness — only factual grounding.\n\n"
        "Be strict about INVENTED facts: if the answer states a specific "
        "number, status, date, amount, or policy detail that does not "
        "appear ANYWHERE in the evidence, that is a FAIL, even if the "
        "number seems reasonable.\n\n"
        "However, DO combine information across multiple evidence chunks "
        "reasonably — the evidence may come from several separate tool "
        "calls (e.g. one call returning a customer's profile, another "
        "returning that same customer's orders). If multiple chunks "
        "clearly refer to the same entity (e.g. the same customer_id or "
        "order_id appears in each), it is valid and expected to combine "
        "facts from them. Do not fail an answer merely because two true "
        "facts came from two different tool calls — only fail if a "
        "specific claimed fact is genuinely absent from all the evidence.\n\n"
        f"ORIGINAL QUESTION: {original_question}\n\n"
        f"EVIDENCE (tool results / retrieved data):\n{evidence}\n\n"
        f"ANSWER TO CHECK:\n{answer}\n\n"
        "Evaluate whether the ANSWER is fully grounded in the EVIDENCE."
    )

    return structured_llm.invoke(prompt)