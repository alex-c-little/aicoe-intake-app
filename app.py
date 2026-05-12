"""AICOE Use Case Intake App.

A small Flask app for tracking AI use case proposals through the AICOE intake flow:
    Backlog -> Refinement -> Under Review -> Approved

Renders fully without JavaScript. Enable optional progressive enhancements
(drag-and-drop, live filter, async detail pane) by setting ENABLE_JS_ENHANCEMENTS=true.
"""
from __future__ import annotations

from flask import (
    Flask, render_template, request, redirect, url_for,
    abort, flash, jsonify, Response,
)

import db
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.context_processor
    def inject_globals():
        return {
            "statuses": Config.STATUSES,
            "enable_js": Config.ENABLE_JS_ENHANCEMENTS,
            "genie_url": Config.GENIE_SPACE_URL,
            "ai_capabilities": Config.AI_CAPABILITIES,
            "value_streams": Config.VALUE_STREAMS,
            "funding_options": Config.FUNDING_OPTIONS,
        }

    @app.route("/")
    def root():
        return redirect(url_for("board"))

    @app.route("/board")
    def board():
        q = request.args.get("q", "").strip()
        selected_id = request.args.get("selected")

        cases = db.list_use_cases(q or None)
        by_status: dict[str, list[dict]] = {s: [] for s in Config.STATUSES}
        for c in cases:
            by_status.setdefault(c["status"], []).append(c)

        selected = db.get_use_case(selected_id) if selected_id else None

        return render_template(
            "board.html",
            by_status=by_status,
            selected=selected,
            q=q,
        )

    @app.route("/usecase/<uc_id>")
    def use_case_detail(uc_id):
        uc = db.get_use_case(uc_id)
        if not uc:
            abort(404)
        return render_template("detail_page.html", uc=uc)

    @app.route("/usecase/<uc_id>/fragment")
    def use_case_fragment(uc_id):
        """HTML fragment for async swap by the JS enhancement layer."""
        uc = db.get_use_case(uc_id)
        if not uc:
            abort(404)
        return render_template("_detail_pane.html", uc=uc)

    @app.route("/usecase/<uc_id>/status", methods=["POST"])
    def update_status(uc_id):
        new_status = request.form.get("status") or (request.json or {}).get("status")
        if new_status not in Config.STATUSES:
            return ("Invalid status", 400)
        if not db.get_use_case(uc_id):
            abort(404)
        db.update_status(uc_id, new_status)

        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": True, "id": uc_id, "status": new_status})
        return redirect(url_for("board", selected=uc_id))

    @app.route("/intake", methods=["GET", "POST"])
    def intake():
        if request.method == "POST":
            form = request.form
            data = {
                "title": form.get("title", "").strip(),
                "category": "Distribution",
                "status": "Backlog",
                "requestor_name": form.get("requestor_name"),
                "planview_tracking_number": form.get("planview_tracking_number"),
                "business_problem": form.get("business_problem"),
                "solution_description": form.get("solution_description"),
                "ai_capability": form.get("ai_capability"),
                "business_area": form.get("business_area"),
                "value_stream": form.get("value_stream"),
                "executive_sponsor": form.get("executive_sponsor"),
                "funding_status": form.get("funding_status"),
                "risks": form.get("risks"),
                "annual_value_low_m": _num(form.get("annual_value_low_m")),
                "annual_value_high_m": _num(form.get("annual_value_high_m")),
                "complexity": _int(form.get("complexity")),
                "time_to_value_low_mo": _int(form.get("time_to_value_low_mo")),
                "time_to_value_high_mo": _int(form.get("time_to_value_high_mo")),
                "data_sources": form.get("data_sources"),
                "prerequisites": form.get("prerequisites"),
            }
            if not data["title"]:
                flash("Use case title is required.", "error")
                return render_template("intake.html", form=form), 400

            uc_id = db.create_use_case(data)
            flash(f"Submitted '{data['title']}' to Backlog.", "success")
            return redirect(url_for("board", selected=uc_id))

        return render_template("intake.html", form={})

    @app.route("/genie")
    def genie():
        if not Config.GENIE_SPACE_URL:
            return Response(
                "GENIE_SPACE_URL is not configured. Set it in .env to point at your Genie space.",
                status=501,
                mimetype="text/plain",
            )
        return redirect(Config.GENIE_SPACE_URL)

    @app.route("/healthz")
    def healthz():
        return {"ok": True}

    return app


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _int(v):
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


app = create_app()


if __name__ == "__main__":
    import os
    db.init_schema()
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
