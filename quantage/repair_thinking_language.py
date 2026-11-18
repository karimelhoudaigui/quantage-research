"""Extract a single final JSON answer after recorded, budgeted local reasoning."""
from .repair_language import parse_proposal


def parse_thinking_proposal(raw, n):
    if not isinstance(raw, str) or raw.count("</think>") != 1:
        return {"valid": False, "error": "one closing thinking marker required before final JSON"}
    reasoning, final = raw.split("</think>", 1)
    if "<think>" in final or "</think>" in final:
        return {"valid": False, "error": "ambiguous final-answer boundary"}
    parsed = parse_proposal(final.strip(), n)
    return dict(parsed, reasoning_prefix_removed=True,
                answer_start_offset=len(reasoning) + len("</think>"))
