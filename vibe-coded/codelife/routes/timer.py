from flask import Blueprint, render_template, redirect, url_for
import config_manager
import data_store

timer_bp = Blueprint("timer", __name__)


@timer_bp.route("/timer")
def timer():
    if not config_manager.is_setup_complete():
        return redirect(url_for("setup.setup"))

    cfg = config_manager.load_config()
    today = data_store.get_today_stats()
    goals = data_store.get_current_goals()

    return render_template(
        "timer.html",
        cfg=cfg,
        today=today,
        goals=goals,
    )


@timer_bp.route("/study")
def study():
    if not config_manager.is_setup_complete():
        return redirect(url_for("setup.setup"))

    cfg = config_manager.load_config()
    from routes.dashboard import get_week_topics
    topics = get_week_topics(cfg["current_month"], cfg["current_week"])
    roadmap = data_store.get_roadmap_status()
    weekly = data_store.get_weekly_stats()

    return render_template(
        "study.html",
        cfg=cfg,
        topics=topics,
        roadmap=roadmap,
        weekly=weekly,
    )
