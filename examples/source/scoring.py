from .motion_math import blend, smoothstep

def reward_score(coverage, smoothness, pressure):
    return smoothstep(coverage) + smoothstep(smoothness) - smoothstep(pressure)

def zone_pressure(distance, threat):
    proximity = 1 - smoothstep(distance)
    return blend(proximity, threat, 0.35)

