from datetime import datetime
from app.models.common import Scores

# Constants for coordinate normalization
TARGET_MIN = -30
TARGET_MAX = 30
SCORE_MIN = 0
SCORE_MAX = 100

def normalize_score(value: float, min_val: float, max_val: float, target_min: float, target_max: float) -> float:
    """
    Normalizes a value from [min_val, max_val] to [target_min, target_max].
    """
    if max_val - min_val == 0:
        return target_min
    
    # Standard min-max normalization
    normalized = (value - min_val) / (max_val - min_val)
    # Scale to target range
    scaled = normalized * (target_max - target_min) + target_min
    return scaled

def calculate_coordinates(scores: Scores) -> dict:
    """
    3D Galaxy Coordinate Calculation.
    Returns a dictionary matching the frontend `Coordinates3D` interface.
    """
    x = normalize_score(scores.inst_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    y = normalize_score(scores.acad_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    z = normalize_score(scores.media_score, SCORE_MIN, SCORE_MAX, TARGET_MIN, TARGET_MAX)
    
    radius = 10.0 + (scores.network_score / 5.0)
    
    return {
        "x": round(x, 2),
        "y": round(y, 2),
        "z": round(z, 2),
        "radius": round(radius, 2),
        "computed_at": datetime.utcnow().isoformat() + "Z",
        "algorithm": "normalize_v1"
    }
