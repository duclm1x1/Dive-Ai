"""Calendar Skill — Google Calendar integration."""
import urllib.request, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class CalendarSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="calendar", description="Google Calendar: list events, create, upcoming",
            category=SkillCategory.PRODUCTIVITY, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "title": {"type": "string"},
                          "start": {"type": "string"}, "end": {"type": "string"}, "date": {"type": "string"}},
            output_schema={"events": "list", "event": "dict"},
            tags=["calendar", "event", "schedule", "meeting", "appointment", "google"],
            trigger_patterns=[r"calendar\s+", r"event\s+", r"meeting\s+", r"schedule\s+meeting", r"upcoming\s+events"],
            combo_compatible=["email-send", "telegram-bot", "task-manager"],
            combo_position="any")

    def _local_file(self):
        d = os.path.expanduser("~/.dive-ai/calendar")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "events.json")

    def _load_local(self):
        f = self._local_file()
        if os.path.exists(f):
            with open(f) as fh: return json.load(fh)
        return []

    def _save_local(self, events):
        with open(self._local_file(), "w") as f: json.dump(events, f, indent=2)

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "list")
        google_token = os.environ.get("GOOGLE_CALENDAR_TOKEN", "")
        
        # Google Calendar API
        if google_token:
            headers = {"Authorization": f"Bearer {google_token}"}
            try:
                if action == "list":
                    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={now}&maxResults=10&orderBy=startTime&singleEvents=true"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read())
                    events = [{"title": e["summary"], "start": e["start"].get("dateTime", e["start"].get("date")),
                               "end": e["end"].get("dateTime", e["end"].get("date"))}
                              for e in data.get("items", [])]
                    return AlgorithmResult("success", {"events": events, "total": len(events), "source": "google"},
                                           {"skill": "calendar"})
            except Exception as e:
                pass  # Fall through to local
        
        # Local calendar fallback
        events = self._load_local()
        
        if action == "add":
            ev = {"id": str(int(time.time())), "title": inputs.get("title", "Event"),
                  "start": inputs.get("start", time.strftime("%Y-%m-%d %H:%M")),
                  "end": inputs.get("end", ""), "created": time.strftime("%Y-%m-%d %H:%M")}
            events.append(ev)
            self._save_local(events)
            return AlgorithmResult("success", {"added": ev, "total": len(events), "source": "local"},
                                   {"skill": "calendar"})
        
        elif action == "list":
            return AlgorithmResult("success", {"events": events[-10:], "total": len(events), "source": "local",
                "note": "Using local calendar. Set GOOGLE_CALENDAR_TOKEN for Google Calendar."},
                {"skill": "calendar"})
        
        elif action == "today":
            today = time.strftime("%Y-%m-%d")
            todays = [e for e in events if e.get("start", "").startswith(today)]
            return AlgorithmResult("success", {"events": todays, "date": today, "source": "local"},
                                   {"skill": "calendar"})
        
        return AlgorithmResult("failure", None, {"error": "action: list/add/today"})
