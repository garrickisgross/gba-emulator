def get_carry(a: int, b: int) -> bool:
    return (a & b) > 0

def get_half_carry(a: int, b: int) -> bool:
    return ((a & 0xF) + (b & 0xF)) >= 16