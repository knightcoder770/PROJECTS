from flask import Blueprint, render_template, redirect, url_for
import config_manager
import data_store

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    if not config_manager.is_setup_complete():
        return redirect(url_for("setup.setup"))

    cfg = config_manager.load_config()
    today_stats = data_store.get_today_stats()
    weekly_stats = data_store.get_weekly_stats()
    goals = data_store.get_current_goals()
    devtrack_data = config_manager.get_devtrack_data()
    roadmap = data_store.get_roadmap_status()

    # Build roadmap topic list for current week
    roadmap_topics = get_week_topics(cfg["current_month"], cfg["current_week"])

    return render_template(
        "dashboard.html",
        cfg=cfg,
        today=today_stats,
        weekly=weekly_stats,
        goals=goals,
        devtrack=devtrack_data,
        roadmap=roadmap,
        roadmap_topics=roadmap_topics,
    )


def get_week_topics(month: int, week: int) -> list:
    """Return topic list for the given month/week of the AI engineering roadmap."""
    topics_map = {
        (1, 1): ["Python mini projects", "OOP basics", "File I/O", "JSON handling", "API calls"],
        (1, 2): ["NumPy arrays", "NumPy operations", "Pandas DataFrames", "Data cleaning", "Kaggle dataset"],
        (1, 3): ["Matplotlib basics", "Seaborn plots", "Chart types", "System monitor viz", "Dashboard"],
        (1, 4): ["End-to-end analysis", "EDA pipeline", "Data storytelling", "Portfolio project"],
        (2, 1): ["scikit-learn basics", "Linear regression", "Train/test split", "Model evaluation"],
        (2, 2): ["Classification", "Decision trees", "Random forests", "Cross-validation"],
        (2, 3): ["Clustering", "K-means", "Dimensionality reduction", "PCA"],
        (2, 4): ["ML pipeline", "Feature engineering", "Model deployment basics"],
        (3, 1): ["Neural networks", "PyTorch tensors", "Autograd", "MLP from scratch"],
        (3, 2): ["CNNs", "Image classification", "Transfer learning"],
        (3, 3): ["RNNs", "LSTMs", "Sequence models"],
        (3, 4): ["Deep learning project", "Voice/audio basics"],
        (4, 1): ["LLM fundamentals", "Prompt engineering", "OpenAI / Claude API"],
        (4, 2): ["LangChain basics", "Chains", "Agents"],
        (4, 3): ["RAG", "Vector stores", "Embeddings"],
        (4, 4): ["LLM project", "Multi-agent basics"],
    }
    return topics_map.get((month, week), ["Topics not mapped yet"])
