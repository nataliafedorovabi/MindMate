import json


def format_practice(row) -> str:
    steps = []
    if row["steps_json"]:
        try:
            steps = json.loads(row["steps_json"]) or []
        except Exception:
            steps = []
    steps_text = "\n".join([f"• {s}" for s in steps]) if steps else ""
    desc = row["description"] or ""
    timer = row["timer_seconds"]
    timer_text = f"\n⏱️ Попробуй уделить этому {timer} секунд. Я напомню, когда время выйдет." if timer else ""
    return f"<b>{row['title']}</b>\n\n{desc}\n\n{steps_text}{timer_text}"


