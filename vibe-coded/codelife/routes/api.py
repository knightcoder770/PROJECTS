from flask import Blueprint, request, jsonify
import data_store
import config_manager
from datetime import datetime

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/session/log", methods=["POST"])
def log_session():
    body = request.get_json()
    project = body.get("project", "")
    duration = int(body.get("duration_minutes", 0))
    notes = body.get("notes", "")

    if duration <= 0:
        return jsonify({"ok": False, "error": "Duration must be > 0"}), 400

    data_store.log_session(project, duration, notes)
    return jsonify({"ok": True, "stats": data_store.get_today_stats()})


@api_bp.route("/stats/today", methods=["GET"])
def today_stats():
    return jsonify(data_store.get_today_stats())


@api_bp.route("/stats/weekly", methods=["GET"])
def weekly_stats():
    return jsonify(data_store.get_weekly_stats())


@api_bp.route("/goals", methods=["GET"])
def get_goals():
    return jsonify({"goals": data_store.get_current_goals()})


@api_bp.route("/goals/add", methods=["POST"])
def add_goal():
    body = request.get_json()
    text = body.get("text", "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Goal text is required"}), 400

    cfg = config_manager.load_config()
    data_store.add_goal(text, cfg["current_week"], cfg["current_month"])
    return jsonify({"ok": True, "goals": data_store.get_current_goals()})


@api_bp.route("/goals/toggle/<int:goal_id>", methods=["POST"])
def toggle_goal(goal_id: int):
    new_state = data_store.toggle_goal(goal_id)
    return jsonify({"ok": True, "done": new_state})


@api_bp.route("/roadmap/topic-done", methods=["POST"])
def mark_topic():
    body = request.get_json()
    topic = body.get("topic", "").strip()
    if topic:
        data_store.mark_topic_done(topic)
    return jsonify({"ok": True})


@api_bp.route("/config", methods=["GET"])
def get_config():
    cfg = config_manager.load_config()
    # Don't expose paths in the API, just metadata
    return jsonify({
        "user_name": cfg["user_name"],
        "github_username": cfg["github_username"],
        "current_week": cfg["current_week"],
        "current_month": cfg["current_month"],
        "daily_goal_hours": cfg["daily_goal_hours"],
        "devtrack_connected": bool(cfg["devtrack_path"]),
        "gitpush_connected": bool(cfg["gitpush_path"]),
    })


@api_bp.route("/config/update", methods=["POST"])
def update_config():
    body = request.get_json()
    allowed = ["current_week", "current_month", "daily_goal_hours", "user_name"]
    updates = {k: v for k, v in body.items() if k in allowed}
    config_manager.update_config(**updates)
    return jsonify({"ok": True})


@api_bp.route("/devtrack/summary", methods=["GET"])
def devtrack_summary():
    data = config_manager.get_devtrack_data()
    if not data:
        return jsonify({"connected": False})
    return jsonify({"connected": True, "data": data})


@api_bp.route("/time", methods=["GET"])
def current_time():
    now = datetime.now()
    return jsonify({
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%A, %B %d"),
        "greeting": get_greeting(now.hour),
    })


def get_greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


@api_bp.route("/roadmap/save-notes", methods=["POST"])
def save_notes():
    body = request.get_json()
    notes = body.get("notes", "")
    data = data_store.load_data()
    data["roadmap"]["notes"] = notes
    data_store.save_data(data)
    return jsonify({"ok": True})
