def get_cell_radius_indexes(radius: int) -> list[tuple[int, int]]:
    """Cell offsets covered by a disc brush."""
    r_sq = radius * radius
    return [
        (dx, dy)
        for dy in range(-radius, radius + 1)
        for dx in range(-radius, radius + 1)
        if dx * dx + dy * dy <= r_sq
    ]