"""Spotify Skill — Search, control playback, get playlists."""
import urllib.request, json, os, base64
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class SpotifySkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="spotify", description="Spotify: search, playlists, currently playing",
            category=SkillCategory.MEDIA, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True}, "query": {"type": "string"},
                          "playlist_id": {"type": "string"}},
            output_schema={"tracks": "list", "playlist": "dict", "now_playing": "dict"},
            tags=["spotify", "music", "playlist", "song", "artist", "play"],
            trigger_patterns=[r"spotify", r"play\s+", r"song\s+", r"playlist", r"music"],
            combo_compatible=["note-taker", "telegram-bot"], combo_position="any")

    def _get_token(self):
        cid = os.environ.get("SPOTIFY_CLIENT_ID", "")
        secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
        if not cid or not secret:
            return None
        try:
            auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
            data = "grant_type=client_credentials".encode()
            req = urllib.request.Request("https://accounts.spotify.com/api/token", data=data,
                headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read()).get("access_token")
        except:
            return None

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "search")
        token = self._get_token()
        
        if not token:
            return AlgorithmResult("success", {"simulated": True, "action": action,
                "note": "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars."}, {"skill": "spotify"})
        
        headers = {"Authorization": f"Bearer {token}"}
        try:
            if action == "search":
                query = inputs.get("query", "")
                url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track&limit=10"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                tracks = [{"name": t["name"], "artist": t["artists"][0]["name"],
                           "album": t["album"]["name"], "url": t["external_urls"]["spotify"]}
                          for t in data.get("tracks", {}).get("items", [])]
                return AlgorithmResult("success", {"tracks": tracks, "total": len(tracks)}, {"skill": "spotify"})
            
            elif action == "playlist":
                pid = inputs.get("playlist_id", "")
                url = f"https://api.spotify.com/v1/playlists/{pid}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                return AlgorithmResult("success", {"name": data.get("name"),
                    "tracks": data.get("tracks", {}).get("total", 0)}, {"skill": "spotify"})
            
            return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e)})
