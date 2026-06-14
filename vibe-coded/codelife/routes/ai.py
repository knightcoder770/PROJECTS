import json
import urllib.request
import urllib.error
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import config_manager
import data_store

ai_bp = Blueprint("ai", __name__)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def call_gemini(prompt: str, api_key: str) -> str:
    """Call Gemini API and return text response."""
    url = f"{GEMINI_BASE}?key={api_key}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7},
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)["error"]["message"]
        except Exception:
            err = body
        raise RuntimeError(f"Gemini API error: {err}")


def get_api_key() -> str:
    return config_manager.get("gemini_api_key") or ""


@ai_bp.route("/ai")
def ai_brain():
    if not config_manager.is_setup_complete():
        return redirect(url_for("setup.setup"))
    cfg = config_manager.load_config()
    today = data_store.get_today_stats()
    api_key_set = bool(get_api_key())
    return render_template("ai.html", cfg=cfg, today=today, api_key_set=api_key_set)


@ai_bp.route("/api/ai/set-key", methods=["POST"])
def set_api_key():
    body = request.get_json()
    key = body.get("api_key", "").strip()
    if not key:
        return jsonify({"ok": False, "error": "API key is required"}), 400
    config_manager.update_config(gemini_api_key=key)
    return jsonify({"ok": True})


@ai_bp.route("/api/ai/commit-message", methods=["POST"])
def commit_message():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    body = request.get_json()
    changed_files = body.get("files", [])
    project = body.get("project", "")
    context = body.get("context", "")

    files_str = "\n".join([f"- [{f['status']}] {f['path']}" for f in changed_files]) if changed_files else context

    prompt = f"""You are a senior developer. Generate exactly 3 git commit message options for these changes.

Project: {project or 'Unknown'}
Changed files:
{files_str}

Rules:
- Use conventional commits format: feat:, fix:, docs:, refactor:, chore:
- Each message under 72 characters
- Return ONLY 3 lines numbered 1. 2. 3. — nothing else, no explanation"""

    try:
        result = call_gemini(prompt, api_key)
        options = []
        for line in result.splitlines():
            line = line.strip()
            if line and line[0].isdigit() and '. ' in line:
                options.append(line.split('. ', 1)[-1].strip())
        return jsonify({"ok": True, "options": options[:3]})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/daily-summary", methods=["POST"])
def daily_summary():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    cfg = config_manager.load_config()
    today = data_store.get_today_stats()
    goals = data_store.get_current_goals()
    roadmap = data_store.get_roadmap_status()

    done_goals = [g["text"] for g in goals if g["done"]]
    pending_goals = [g["text"] for g in goals if not g["done"]]

    prompt = f"""Write a daily coding summary for {cfg['user_name']}.

Today's stats:
- Hours coded: {today['total_hours']}h (goal: {cfg['daily_goal_hours']}h)
- Sessions: {today['sessions']}
- Projects: {', '.join(today['projects']) or 'none logged'}
- Day streak: {today['streak']} days
- Roadmap: Month {cfg['current_month']}, Week {cfg['current_week']}
- Goals completed: {', '.join(done_goals) or 'none'}
- Goals pending: {', '.join(pending_goals) or 'none'}
- Topics done: {', '.join(roadmap.get('topics_done', [])) or 'none yet'}

Write 3-4 sentences: what was accomplished, how it fits the journey, one motivating line for tomorrow.
Be direct and personal. No fluff."""

    try:
        result = call_gemini(prompt, api_key)
        return jsonify({"ok": True, "summary": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/linkedin-post", methods=["POST"])
def linkedin_post():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    body = request.get_json()
    context = body.get("context", "")
    cfg = config_manager.load_config()
    today = data_store.get_today_stats()

    prompt = f"""Write a LinkedIn post for a developer sharing their progress.

Developer: {cfg['user_name']} (@{cfg['github_username']})
Journey: 6-month AI engineering roadmap, Month {cfg['current_month']} Week {cfg['current_week']}
Today: {today['total_hours']}h coded, {today['streak']} day streak
What they built/learned: {context or 'kept pushing on the AI engineering roadmap'}

Rules:
- Max 150 words
- Hook first line (NOT "I am excited to share")
- Specific about what was built
- End with 3-4 hashtags
- Sound like a real human, not a corporate post
- Return ONLY the post text, nothing else"""

    try:
        result = call_gemini(prompt, api_key)
        return jsonify({"ok": True, "post": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/readme-generator", methods=["POST"])
def readme_generator():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    body = request.get_json()
    project_name = body.get("project_name", "").strip()
    description = body.get("description", "").strip()
    tech_stack = body.get("tech_stack", "").strip()
    features = body.get("features", "").strip()

    if not project_name:
        return jsonify({"ok": False, "error": "Project name is required"}), 400

    prompt = f"""Write a GitHub README in markdown for this project:

Project: {project_name}
Description: {description or 'A Python project'}
Tech stack: {tech_stack or 'Python'}
Key features: {features or 'See code'}

Include: title with emoji, shields.io badges, description, features list, installation, usage example, project structure, contributing section, MIT license.
Keep under 400 words. Return ONLY the markdown, no explanation."""

    try:
        result = call_gemini(prompt, api_key)
        return jsonify({"ok": True, "readme": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/error-explainer", methods=["POST"])
def error_explainer():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    body = request.get_json()
    error_text = body.get("error", "").strip()
    if not error_text:
        return jsonify({"ok": False, "error": "Paste an error first"}), 400

    prompt = f"""Explain this Python error and give the exact fix.

{error_text}

Respond in this exact format:
**What went wrong:** (1 sentence)
**Why it happened:** (2-3 sentences)
**Fix:** (exact code or steps)
**Pro tip:** (one line to avoid this in future)

Be direct. No fluff."""

    try:
        result = call_gemini(prompt, api_key)
        return jsonify({"ok": True, "explanation": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@ai_bp.route("/api/ai/end-of-day", methods=["POST"])
def end_of_day():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"ok": False, "error": "No Gemini API key set."}), 400

    body = request.get_json()
    context = body.get("context", "")
    cfg = config_manager.load_config()
    today = data_store.get_today_stats()
    goals = data_store.get_current_goals()
    weekly = data_store.get_weekly_stats()

    done_goals = [g["text"] for g in goals if g["done"]]
    total_week_hours = sum(d["hours"] for d in weekly["days"])

    prompt = f"""Write an end-of-day dev report for {cfg['user_name']}.

Today:
- Hours: {today['total_hours']}h / goal {cfg['daily_goal_hours']}h
- Sessions: {today['sessions']}
- Projects: {', '.join(today['projects']) or 'none logged'}
- Streak: {today['streak']} days
- Goals done: {', '.join(done_goals) or 'none'}
- Extra: {context or 'none'}
- This week total: {total_week_hours}h
- Roadmap: Month {cfg['current_month']} Week {cfg['current_week']} of 6-month AI engineering journey

Write exactly three sections:
**Today's wins** — 3 bullet points max
**Honest assessment** — 2 sentences on progress vs goal
**Tomorrow's focus** — 2-3 specific action items

Under 200 words. Direct, no fluff."""

    try:
        result = call_gemini(prompt, api_key)
        return jsonify({"ok": True, "report": result})
    except RuntimeError as e:
        return jsonify({"ok": False, "error": str(e)}), 500
