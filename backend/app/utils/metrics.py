def calculate_accuracy(correct: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 2)


def calculate_chars_per_minute(total_chars: int, total_time_ms: int) -> float:
    if total_time_ms <= 0:
        return 0.0
    minutes = total_time_ms / 60000
    return round(total_chars / minutes, 2)
