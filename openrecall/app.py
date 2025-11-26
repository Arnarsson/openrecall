from threading import Thread
import os

import numpy as np
from flask import Flask, render_template_string, request, send_from_directory, jsonify
from flask_cors import CORS
from jinja2 import BaseLoader

from openrecall.config import appdata_folder, screenshots_path
from openrecall.database import (
    create_db, get_all_entries, get_timestamps,
    get_entries_paginated, get_entry_by_id, get_unique_apps,
    get_stats, search_entries, get_entry_count
)
from openrecall.nlp import cosine_similarity, get_embedding
from openrecall.screenshot import record_screenshots_thread
from openrecall.utils import human_readable_time, timestamp_to_human_readable

app = Flask(__name__, static_folder='static/dist', static_url_path='/app')
CORS(app)  # Enable CORS for React development

# App version
APP_VERSION = "1.0.0"

# Recording status (can be updated by controller)
recording_status = {"active": True, "paused": False}

app.jinja_env.filters["human_readable_time"] = human_readable_time
app.jinja_env.filters["timestamp_to_human_readable"] = timestamp_to_human_readable

base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TotalRecall</title>
  <!-- Bootstrap CSS -->
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
  <style>
    .slider-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }
    .slider {
      width: 80%;
    }
    .slider-value {
      margin-top: 10px;
      font-size: 1.2em;
    }
    .image-container {
      margin-top: 20px;
      text-align: center;
    }
    .image-container img {
      max-width: 100%;
      height: auto;
    }
  </style>
</head>
<body>
<nav class="navbar navbar-light bg-light">
  <div class="container">
    <form class="form-inline my-2 my-lg-0 w-100 d-flex" action="/search" method="get">
      <input class="form-control flex-grow-1 mr-sm-2" type="search" name="q" placeholder="Search" aria-label="Search">
      <button class="btn btn-outline-secondary my-2 my-sm-0" type="submit">
        <i class="bi bi-search"></i>
      </button>
    </form>
  </div>
</nav>
{% block content %}

{% endblock %}

  <!-- Bootstrap and jQuery JS -->
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  
</body>
</html>
"""


class StringLoader(BaseLoader):
    def get_source(self, environment, template):
        if template == "base_template":
            return base_template, None, lambda: True
        return None, None, None


app.jinja_env.loader = StringLoader()


@app.route("/")
def timeline():
    # connect to db
    timestamps = get_timestamps()
    return render_template_string(
        """
{% extends "base_template" %}
{% block content %}
{% if timestamps|length > 0 %}
  <div class="container">
    <div class="slider-container">
      <input type="range" class="slider custom-range" id="discreteSlider" min="0" max="{{timestamps|length - 1}}" step="1" value="{{timestamps|length - 1}}">
      <div class="slider-value" id="sliderValue">{{timestamps[0] | timestamp_to_human_readable }}</div>
    </div>
    <div class="image-container">
      <img id="timestampImage" src="/static/{{timestamps[0]}}.webp" alt="Image for timestamp">
    </div>
  </div>
  <script>
    const timestamps = {{ timestamps|tojson }};
    const slider = document.getElementById('discreteSlider');
    const sliderValue = document.getElementById('sliderValue');
    const timestampImage = document.getElementById('timestampImage');

    slider.addEventListener('input', function() {
      const reversedIndex = timestamps.length - 1 - slider.value;
      const timestamp = timestamps[reversedIndex];
      sliderValue.textContent = new Date(timestamp * 1000).toLocaleString();  // Convert to human-readable format
      timestampImage.src = `/static/${timestamp}.webp`;
    });

    // Initialize the slider with a default value
    slider.value = timestamps.length - 1;
    sliderValue.textContent = new Date(timestamps[0] * 1000).toLocaleString();  // Convert to human-readable format
    timestampImage.src = `/static/${timestamps[0]}.webp`;
  </script>
{% else %}
  <div class="container">
      <div class="alert alert-info" role="alert">
          Nothing recorded yet, wait a few seconds.
      </div>
  </div>
{% endif %}
{% endblock %}
""",
        timestamps=timestamps,
    )


@app.route("/search")
def search():
    q = request.args.get("q")
    entries = get_all_entries()
    embeddings = [np.frombuffer(entry.embedding, dtype=np.float64) for entry in entries]
    query_embedding = get_embedding(q)
    similarities = [cosine_similarity(query_embedding, emb) for emb in embeddings]
    indices = np.argsort(similarities)[::-1]
    sorted_entries = [entries[i] for i in indices]

    return render_template_string(
        """
{% extends "base_template" %}
{% block content %}
    <div class="container">
        <div class="row">
            {% for entry in entries %}
                <div class="col-md-3 mb-4">
                    <div class="card">
                        <a href="#" data-toggle="modal" data-target="#modal-{{ loop.index0 }}">
                            <img src="/static/{{ entry['timestamp'] }}.webp" alt="Image" class="card-img-top">
                        </a>
                    </div>
                </div>
                <div class="modal fade" id="modal-{{ loop.index0 }}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl" role="document" style="max-width: none; width: 100vw; height: 100vh; padding: 20px;">
                        <div class="modal-content" style="height: calc(100vh - 40px); width: calc(100vw - 40px); padding: 0;">
                            <div class="modal-body" style="padding: 0;">
                                <img src="/static/{{ entry['timestamp'] }}.webp" alt="Image" style="width: 100%; height: 100%; object-fit: contain; margin: 0 auto;">
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
{% endblock %}
""",
        entries=sorted_entries,
    )


@app.route("/static/<filename>")
def serve_image(filename):
    return send_from_directory(screenshots_path, filename)


# =============================================================================
# JSON API Endpoints for React Frontend
# =============================================================================

# Tag generation helper
APP_CATEGORY_MAP = {
    'Development': [
        'VS Code', 'Visual Studio', 'Code', 'IntelliJ', 'WebStorm', 'PyCharm',
        'Xcode', 'Android Studio', 'Terminal', 'iTerm', 'Sublime', 'Cursor',
        'Atom', 'Vim', 'Emacs', 'Neovim', 'nvim', 'code-server'
    ],
    'Browser': [
        'Chrome', 'Firefox', 'Safari', 'Edge', 'Arc', 'Brave', 'Opera', 'Chromium'
    ],
    'Communication': [
        'Slack', 'Discord', 'Teams', 'Zoom', 'Messages', 'Mail',
        'Outlook', 'Telegram', 'WhatsApp', 'Signal'
    ],
    'Design': [
        'Figma', 'Sketch', 'Photoshop', 'Illustrator', 'Canva',
        'Adobe XD', 'Affinity', 'GIMP', 'Inkscape'
    ],
    'Productivity': [
        'Notion', 'Obsidian', 'Notes', 'Evernote', 'Bear',
        'Word', 'Excel', 'PowerPoint', 'Pages', 'Numbers', 'Keynote',
        'Google Docs', 'Google Sheets'
    ],
    'Media': [
        'Spotify', 'Music', 'VLC', 'QuickTime', 'Photos', 'Preview', 'YouTube'
    ],
    'System': [
        'Finder', 'Explorer', 'Settings', 'System Preferences', 'Activity Monitor'
    ]
}


def generate_tags(app_name: str, window_title: str) -> list:
    """Generate tags based on app name and window title."""
    tags = []
    app_lower = (app_name or "").lower()

    # Find category for app
    for category, apps in APP_CATEGORY_MAP.items():
        if any(app.lower() in app_lower for app in apps):
            tags.append(category)
            break

    # Add simplified app name as tag
    if app_name and app_name not in ["Unknown", "", "unknown"]:
        # Clean up app name (remove .exe, .app, etc.)
        clean_name = app_name.replace('.exe', '').replace('.app', '').strip()
        if clean_name and clean_name not in tags:
            tags.append(clean_name)

    # Extract file extension tags from title
    if window_title:
        import re
        ext_match = re.search(r'\.(\w+)(?:\s|$|-|—)', window_title)
        if ext_match:
            ext = ext_match.group(1).lower()
            ext_tags = {
                'tsx': 'React', 'jsx': 'React',
                'ts': 'TypeScript', 'js': 'JavaScript',
                'py': 'Python', 'go': 'Go', 'rs': 'Rust',
                'md': 'Markdown', 'json': 'Config',
                'html': 'HTML', 'css': 'CSS', 'scss': 'SCSS'
            }
            if ext in ext_tags and ext_tags[ext] not in tags:
                tags.append(ext_tags[ext])

    return list(dict.fromkeys(tags))  # Remove duplicates while preserving order


def entry_to_dict(entry, similarity_score=None):
    """Convert Entry namedtuple to JSON-serializable dict."""
    result = {
        "id": entry.id,
        "app": entry.app or "Unknown",
        "title": entry.title or "",
        "text": entry.text or "",
        "timestamp": entry.timestamp,
        "screenshot_url": f"/static/{entry.timestamp}.webp",
        "formatted_time": timestamp_to_human_readable(entry.timestamp),
        "relative_time": human_readable_time(entry.timestamp),
        "tags": generate_tags(entry.app, entry.title)
    }
    if similarity_score is not None:
        result["similarity_score"] = round(similarity_score, 4)
    return result


@app.route("/api/entries")
def api_get_entries():
    """
    Get paginated list of entries.

    Query params:
        page (int): Page number, default 1
        limit (int): Items per page, default 50, max 200
        start_date (int): Unix timestamp filter start
        end_date (int): Unix timestamp filter end
        app (str): Filter by app name
    """
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)
    start_date = request.args.get("start_date", type=int)
    end_date = request.args.get("end_date", type=int)
    app_filter = request.args.get("app", type=str)

    entries, total = get_entries_paginated(
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        app_filter=app_filter
    )

    return jsonify({
        "entries": [entry_to_dict(e) for e in entries],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": (page * limit) < total
    })


@app.route("/api/entries/<int:entry_id>")
def api_get_entry(entry_id):
    """Get a single entry by ID."""
    entry = get_entry_by_id(entry_id)
    if entry is None:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify(entry_to_dict(entry))


@app.route("/api/search")
def api_search():
    """
    Search entries using semantic similarity.

    Query params:
        q (str): Search query (required)
        limit (int): Max results, default 20
    """
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 20, type=int)

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = search_entries(query, limit=limit)

    return jsonify({
        "query": query,
        "results": [entry_to_dict(entry, score) for entry, score in results],
        "total": len(results)
    })


@app.route("/api/timeline")
def api_timeline():
    """
    Get timestamps for timeline navigation.

    Query params:
        date (str): Optional ISO date filter (YYYY-MM-DD)
    """
    timestamps = get_timestamps()

    date_range = {
        "start": timestamps[-1] if timestamps else None,
        "end": timestamps[0] if timestamps else None
    }

    return jsonify({
        "timestamps": timestamps,
        "date_range": date_range,
        "total_count": len(timestamps)
    })


@app.route("/api/stats")
def api_stats():
    """Get system statistics."""
    stats = get_stats()
    stats["memory_status"] = "active" if recording_status["active"] and not recording_status["paused"] else "paused" if recording_status["paused"] else "inactive"
    stats["version"] = APP_VERSION
    return jsonify(stats)


@app.route("/api/apps")
def api_get_apps():
    """Get list of unique applications with counts."""
    apps = get_unique_apps()

    # Add category information
    result = []
    for app_name, count in apps:
        category = None
        app_lower = (app_name or "").lower()
        for cat, cat_apps in APP_CATEGORY_MAP.items():
            if any(a.lower() in app_lower for a in cat_apps):
                category = cat
                break
        result.append({
            "name": app_name or "Unknown",
            "count": count,
            "category": category
        })

    return jsonify({"apps": result})


@app.route("/api/status")
def api_status():
    """Get current recording status."""
    timestamps = get_timestamps()
    return jsonify({
        "status": "active" if recording_status["active"] else "inactive",
        "recording": recording_status["active"] and not recording_status["paused"],
        "paused": recording_status["paused"],
        "last_capture": timestamps[0] if timestamps else None,
        "version": APP_VERSION
    })


# =============================================================================
# React Frontend Serving
# =============================================================================

@app.route("/app")
@app.route("/app/")
@app.route("/app/<path:path>")
def serve_react_app(path=""):
    """Serve the React frontend application."""
    # Check if built frontend exists
    dist_path = os.path.join(os.path.dirname(__file__), 'static', 'dist')
    index_path = os.path.join(dist_path, 'index.html')

    if os.path.exists(index_path):
        # If requesting a static asset, serve it
        if path and os.path.exists(os.path.join(dist_path, path)):
            return send_from_directory(dist_path, path)
        # Otherwise serve index.html for SPA routing
        return send_from_directory(dist_path, 'index.html')
    else:
        return """
        <html>
        <head><title>TotalRecall</title></head>
        <body style="font-family: system-ui; padding: 40px; text-align: center;">
            <h1>TotalRecall Frontend Not Built</h1>
            <p>The React frontend has not been built yet.</p>
            <p>Run the following commands:</p>
            <pre style="background: #f5f5f5; padding: 20px; display: inline-block; text-align: left;">
cd frontend
npm install
npm run build
            </pre>
            <p>Or use the legacy interface at <a href="/">/</a></p>
        </body>
        </html>
        """, 200


if __name__ == "__main__":
    import sys
    import signal
    import threading

    # If CLI arguments are provided, delegate to the CLI module
    if len(sys.argv) > 1:
        from openrecall.cli import main
        main()
    else:
        # Legacy mode - run directly without menu bar
        create_db()

        print(f"Appdata folder: {appdata_folder}")
        print("Dashboard: http://localhost:8082")
        print("Press Ctrl+C to stop.")
        print("")
        print("Tip: Run 'openrecall --install' to enable auto-start at login (macOS)")
        print("")

        # Create stop/pause events for the screenshot thread
        stop_event = threading.Event()
        pause_event = threading.Event()

        # Start screenshot recording thread
        t = Thread(
            target=record_screenshots_thread,
            args=(stop_event, pause_event),
            daemon=True,
        )
        t.start()

        # Run Flask on main thread (legacy behavior)
        try:
            app.run(port=8082)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            stop_event.set()
            t.join(timeout=5)
