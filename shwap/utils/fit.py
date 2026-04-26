from typing import Dict, List, Optional


def evaluate_fit(
    garment: Dict[str, Optional[float]],
    profile: Dict[str, Optional[float]],
) -> Dict[str, str]:
    checks: List[str] = []
    score = 0
    total = 0

    def compare(label: str, key: str, threshold: float):
        nonlocal score, total
        garment_value = garment.get(key)
        profile_value = profile.get(key)
        if garment_value is None or profile_value is None:
            return

        total += 1
        delta = abs(float(garment_value) - float(profile_value))
        if delta <= threshold:
            score += 1
            checks.append(f"{label}: within range")
        elif delta <= threshold * 1.5:
            checks.append(f"{label}: close")
        else:
            checks.append(f"{label}: off range")

    compare("Chest", "chest_bust", 2.0)
    compare("Waist", "waist", 2.0)
    compare("Hip", "hip", 2.0)
    compare("Inseam", "inseam", 1.5)

    if total == 0:
        level = "Needs manual review"
    else:
        ratio = score / total
        if ratio >= 0.75:
            level = "Likely fits"
        elif ratio >= 0.45:
            level = "May fit"
        else:
            level = "Unlikely to fit"

    return {"fit_result": level, "explanation": "; ".join(checks) or "Insufficient measurements"}
