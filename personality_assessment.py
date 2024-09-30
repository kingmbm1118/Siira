def assess_personality(scores):
    traits = {}
    for trait, score in scores.items():
        if score <= 2:
            traits[trait] = "Low"
        elif score <= 4:
            traits[trait] = "Medium"
        else:
            traits[trait] = "High"
    return traits