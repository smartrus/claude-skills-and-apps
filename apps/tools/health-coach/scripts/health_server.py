#!/usr/bin/env python3
"""
health_server.py — Local HTTP server for health dashboard sync.

Serves the health_data.json file and accepts updates from both
the browser dashboard and AI agent integrations.

Usage:
    python3 health_server.py [--port 8777] [--data-file ./data/health_data.json]

Endpoints:
    GET  /           -> Serves the dashboard (index.html)
    GET  /data       -> Returns health_data.json
    POST /data       -> Overwrites health_data.json (from dashboard saves)
    POST /checkin    -> Accepts individual habit updates (from agents)
    GET  /health     -> Health check endpoint
"""

import json
import os
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser(description="Health habits sync server")
    parser.add_argument("--port", type=int, default=8777, help="Port to listen on")
    parser.add_argument(
        "--data-file",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "data", "health_data.json"),
        help="Path to health_data.json",
    )
    parser.add_argument(
        "--dashboard-dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "dashboard"),
        help="Path to dashboard directory",
    )
    return parser.parse_args()


ARGS = None


class HealthHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.dashboard_dir = os.path.abspath(ARGS.dashboard_dir)
        super().__init__(*args, directory=self.dashboard_dir, **kwargs)

    ALLOWED_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:8777")

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", self.ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _get_water_goal(self):
        """Read water goal from user_profile.json, default to 8.

        Supports both top-level keys (waterGoal, water_goal) and the
        documented nested schema (targets.water_glasses).
        """
        profile_path = os.path.join(
            os.path.dirname(os.path.abspath(ARGS.data_file)), "user_profile.json"
        )
        try:
            with open(profile_path, "r") as f:
                profile = json.load(f)
            # Prefer explicit top-level water goal fields (backwards-compatible)
            goal = profile.get("waterGoal") or profile.get("water_goal")
            if isinstance(goal, int) and goal > 0:
                return goal
            # Fall back to documented nested schema: targets.water_glasses
            targets = profile.get("targets") or {}
            if isinstance(targets, dict):
                goal = targets.get("water_glasses")
                if isinstance(goal, int) and goal > 0:
                    return goal
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
        return 8

    def _read_data(self):
        data_file = os.path.abspath(ARGS.data_file)
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        if not os.path.exists(data_file):
            with open(data_file, "w") as f:
                json.dump({}, f)
            return {}
        with open(data_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                backup = data_file + ".bak"
                try:
                    os.replace(data_file, backup)
                except OSError:
                    pass
                with open(data_file, "w") as nf:
                    json.dump({}, nf)
                return {}

    def _write_data(self, data):
        data_file = os.path.abspath(ARGS.data_file)
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            data = self._read_data()
            self._send_json(data)
        elif self.path == "/health":
            self._send_json({"status": "ok"})
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if self.path == "/data":
            if not isinstance(payload, dict):
                self._send_json(
                    {"error": "Invalid payload; expected JSON object"}, 400
                )
                return
            self._write_data(payload)
            self._send_json({"ok": True})

        elif self.path == "/checkin":
            if not isinstance(payload, dict):
                self._send_json(
                    {"error": "Invalid payload; expected JSON object"}, 400
                )
                return
            date = payload.get("date")
            habit_id = payload.get("habit_id")
            value = payload.get("value")

            if not all([date, habit_id, value is not None]):
                self._send_json(
                    {"error": "Missing required fields: date, habit_id, value"}, 400
                )
                return

            data = self._read_data()
            if date not in data:
                data[date] = {"habits": {}, "water": 0, "notes": ""}

            day = data[date]

            if habit_id == "water":
                try:
                    water_value = int(value)
                except (TypeError, ValueError):
                    self._send_json(
                        {"error": "Invalid water value; expected integer"}, 400
                    )
                    return
                day["water"] = max(day.get("water", 0), min(water_value, 20))
                # Derive l1 from water count (goal from user profile)
                day["habits"]["l1"] = day["water"] >= self._get_water_goal()
            elif habit_id == "notes":
                existing = day.get("notes", "")
                day["notes"] = f"{existing} | {value}" if existing else value
            else:
                # Parse boolean values explicitly
                if isinstance(value, bool):
                    parsed = value
                elif isinstance(value, str):
                    parsed = value.lower() in ("true", "1", "yes", "done")
                else:
                    parsed = bool(value)
                # Additive logging: once true, don't overwrite with false
                existing = day.get("habits", {}).get(habit_id, False)
                if parsed or not existing:
                    day["habits"][habit_id] = parsed

            self._write_data(data)

            # Calculate progress — l1 is derived from water, not double-counted
            habit_ids = (
                [f"n{i}" for i in range(1, 8)]
                + [f"e{i}" for i in range(1, 5)]
                + [f"l{i}" for i in range(1, 6)]
            )
            done = sum(1 for h in habit_ids if day.get("habits", {}).get(h, False))
            total = len(habit_ids)
            pct = done / total * 100 if total > 0 else 0

            self._send_json({
                "ok": True,
                "date": date,
                "habit_id": habit_id,
                "progress": f"{done}/{total}",
                "percentage": round(pct),
            })

        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[health-server] {args[0]}")


def main():
    global ARGS
    ARGS = get_args()

    server = HTTPServer(("127.0.0.1", ARGS.port), HealthHandler)
    print(f"Health sync server running at http://localhost:{ARGS.port}")
    print(f"  Dashboard: http://localhost:{ARGS.port}/")
    print(f"  Data API:  http://localhost:{ARGS.port}/data")
    print(f"  Check-in:  POST http://localhost:{ARGS.port}/checkin")
    print(f"  Data file: {os.path.abspath(ARGS.data_file)}")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
