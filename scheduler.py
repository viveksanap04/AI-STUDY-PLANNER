def generate_schedule(topics, days=5):
    """Generate a simple 5-day study plan."""
    if not topics:
        return {}

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][:days]
    schedule = {day: [] for day in weekdays}

    for i, topic in enumerate(topics):
        day = weekdays[i % days]
        schedule[day].append(topic)

    for day in weekdays:
        if not schedule[day]:
            schedule[day].append("Free day — revise or relax!")

    return schedule
