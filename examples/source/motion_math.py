def clamp_unit(x):
    if x < 0:
        return 0
    if x > 1:
        return 1
    return x

def smoothstep(x):
    y = clamp_unit(x)
    return y * y * (3 - 2 * y)

def blend(a, b, t):
    u = smoothstep(t)
    return a + (b - a) * u


# tampered
