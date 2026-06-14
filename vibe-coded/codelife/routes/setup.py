from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import config_manager

setup_bp = Blueprint("setup", __name__)


@setup_bp.route("/")
def index():
    if config_manager.is_setup_complete():
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("setup.setup"))


@setup_bp.route("/setup", methods=["GET"])
def setup():
    return render_template("setup.html")


@setup_bp.route("/setup/save", methods=["POST"])
def save_setup():
    data = request.get_json()

    config_manager.update_config(
        user_name=data.get("user_name", ""),
        github_username=data.get("github_username", ""),
        devtrack_path=data.get("devtrack_path", ""),
        gitpush_path=data.get("gitpush_path", ""),
        daily_goal_hours=int(data.get("daily_goal_hours", 8)),
        roadmap_start_date=data.get("roadmap_start_date", ""),
        current_week=int(data.get("current_week", 1)),
        current_month=int(data.get("current_month", 1)),
        setup_complete=True,
    )

    return jsonify({"ok": True})


@setup_bp.route("/setup/validate-path", methods=["POST"])
def validate_path():
    data = request.get_json()
    path_type = data.get("type")
    path = data.get("path", "")

    if path_type == "devtrack":
        valid = config_manager.validate_devtrack_path(path)
    elif path_type == "gitpush":
        valid = config_manager.validate_gitpush_path(path)
    else:
        valid = False

    return jsonify({"valid": valid})


@setup_bp.route("/setup/reset")
def reset_setup():
    config_manager.update_config(setup_complete=False)
    return redirect(url_for("setup.setup"))
