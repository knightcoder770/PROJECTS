import json
from pathlib import Path
from datetime import datetime, date

DATA_PATH = Path(__file__).parent / "codelife_data.json"

DEFAULT_DATA = {
    "sessions": [],
    "daily_logs": {},
    "streak": {
        "current": 0,
        "longest": 0,
        "last_active": "",
    },
    "goals": {
        "weekly": [],
        "completed": [],
    },
    "roadmap": {
        "month": 1,
        "week": 1,
        "topics_done": [],
    },
}


def load_data() -> dict:
    if not DATA_PATH.exists():
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        return {**DEFAULT_DATA, **data}
    except (json.JSONDecodeError, IOError):
        return DEFAULT_DATA.copy()


def save_data(data: dict) -> None:
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


def log_session(project: str, duration_minutes: int, notes: str = "") -> None:
    """Save a completed work session."""
    data = load_data()
    today = date.today().isoformat()

    session = {
        "date": today,
        "time": datetime.now().strftime("%H:%M"),
        "project": project,
        "duration_minutes": duration_minutes,
        "notes": notes,
    }
    data["sessions"].append(session)

    # Update daily log
    if today not in data["daily_logs"]:
        data["daily_logs"][today] = {"total_minutes": 0, "sessions": 0, "projects": []}

    log = data["daily_logs"][today]
    log["total_minutes"] += duration_minutes
    log["sessions"] += 1
    if project and project not in log["projects"]:
        log["projects"].append(project)

    # Update streak
    update_streak(data, today)
    save_data(data)


def update_streak(data: dict, today: str) -> None:
    """Recalculate streak based on activity."""
    last = data["streak"].get("last_active", "")
    if last == today:
        return

    if last:
        last_date = date.fromisoformat(last)
        today_date = date.fromisoformat(today)
        delta = (today_date - last_date).days
        if delta == 1:
            data["streak"]["current"] += 1
        elif delta > 1:
            data["streak"]["current"] = 1
    else:
        data["streak"]["current"] = 1

    data["streak"]["last_active"] = today
    if data["streak"]["current"] > data["streak"]["longest"]:
        data["streak"]["longest"] = data["streak"]["current"]


def get_today_stats() -> dict:
    """Return stats for today."""
    data = load_data()
    today = date.today().isoformat()
    log = data["daily_logs"].get(today, {
        "total_minutes": 0,
        "sessions": 0,
        "projects": []
    })
    return {
        "date": today,
        "total_minutes": log.get("total_minutes", 0),
        "total_hours": round(log.get("total_minutes", 0) / 60, 1),
        "sessions": log.get("sessions", 0),
        "projects": log.get("projects", []),
        "streak": data["streak"]["current"],
        "longest_streak": data["streak"]["longest"],
    }


def get_weekly_stats() -> dict:
    """Return stats for the last 7 days."""
    data = load_data()
    from datetime import timedelta
    today = date.today()
    weekly = []

    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        log = data["daily_logs"].get(day, {})
        weekly.append({
            "date": day,
            "day": (today - timedelta(days=i)).strftime("%a"),
            "minutes": log.get("total_minutes", 0),
            "hours": round(log.get("total_minutes", 0) / 60, 1),
        })

    return {"days": weekly}


def add_goal(text: str, week: int, month: int) -> None:
    data = load_data()
    data["goals"]["weekly"].append({
        "id": len(data["goals"]["weekly"]) + 1,
        "text": text,
        "week": week,
        "month": month,
        "done": False,
        "created": date.today().isoformat(),
    })
    save_data(data)


def toggle_goal(goal_id: int) -> bool:
    """Toggle a goal's done state. Returns new state."""
    data = load_data()
    for goal in data["goals"]["weekly"]:
        if goal["id"] == goal_id:
            goal["done"] = not goal["done"]
            save_data(data)
            return goal["done"]
    return False


def get_current_goals() -> list:
    data = load_data()
    import config_manager
    week = config_manager.get("current_week")
    month = config_manager.get("current_month")
    return [g for g in data["goals"]["weekly"]
            if g["week"] == week and g["month"] == month]


def get_roadmap_status() -> dict:
    data = load_data()
    return data.get("roadmap", DEFAULT_DATA["roadmap"])


def mark_topic_done(topic: str) -> None:
    data = load_data()
    if topic not in data["roadmap"]["topics_done"]:
        data["roadmap"]["topics_done"].append(topic)
    save_data(data)
