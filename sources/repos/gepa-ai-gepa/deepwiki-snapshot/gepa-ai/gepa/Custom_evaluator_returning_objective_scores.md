def evaluator(data: DefaultDataInst, response: str) -> EvaluationResult:
    quality = judge_quality(response)
    leakage_score = check_pii_leakage(response)
    
    total_score = (quality + leakage_score) / 2
    
    return EvaluationResult(
        score=total_score,
        feedback="...",
        objective_scores={"quality": quality, "leakage": leakage_score}
    )