"""
Fetches FIFA World Cup 2026 results from API-Football and writes data/results.json.
Called by GitHub Actions every 30 minutes.

Output format:
{
  "updated": "2026-06-11T20:30:00Z",
  "games": {
    "1": { "hg": 2, "ag": 0, "fs": "México", "status": "FT", "min": 90 },
    ...
  },
  "final": { "champion": "", "runner_up": "", "third": "" }
}
"""

import os, json, requests, re
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
BASE    = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# ── Our game schedule (game_number → {home, away}) ───────────
# Minimal lookup table — only teams whose API name differs from our spreadsheet name
TEAM_MAP = {
    "south africa": "Africa do Sul",
    "south korea": "Coreia do Sul",
    "czech republic": "Chéquia",
    "bosnia-herzegovina": "Bósnia",
    "united states": "EUA",
    "usa": "EUA",
    "ivory coast": "Costa de Marfim",
    "cote d'ivoire": "Costa de Marfim",
    "netherlands": "Paises Baixos",
    "sweden": "Suecia",
    "cape verde": "Cabo Verde",
    "saudi arabia": "Arabia Saudita",
    "belgium": "Belgica",
    "egypt": "Egipto",
    "iran": "Irão",
    "new zealand": "Nova Zelandia",
    "jordan": "Jordânia",
    "iraq": "Iraque",
    "norway": "Noruega",
    "algeria": "Argélia",
    "croatia": "Croácia",
    "ghana": "Gana",
    "panama": "Panamá",
    "uzbekistan": "Uzbequistão",
    "colombia": "Colômbia",
    "england": "Inglaterra",
    "scotland": "Escócia",
    "curacao": "Curaçau",
    "ecuador": "Equador",
    "japan": "Japão",
    "turkey": "Turquia",
    "switzerland": "Suiça",
    "qatar": "Catar",
    "brazil": "Brasil",
    "canada": "Canadá",
    "paraguay": "Paraguai",
    "uruguay": "Uruguai",
    "austria": "Áustria",
    "france": "França",
    "argentina": "Argentina",
    "germany": "Alemanha",
    "spain": "Espanha",
    "australia": "Austrália",
    "morocco": "Marrocos",
    "senegal": "Senegal",
    "portugal": "Portugal",
    "mexico": "México",
    "haiti": "Haiti",
    "congo": "Congo",
    "costa d'ivoire": "Costa de Marfim",
}

# Our game schedule: (normalised_home, normalised_away) → game_number
SCHEDULE = {
    ("mexico","africa do sul"):1,("coreia do sul","chequia"):2,
    ("canada","bosnia"):3,("eua","paraguai"):4,
    ("catar","suica"):5,("brasil","marrocos"):6,
    ("haiti","escocia"):7,("australia","turquia"):8,
    ("alemanha","curacao"):9,("costa de marfim","equador"):10,
    ("paises baixos","japao"):11,("suecia","tunisia"):12,
    ("espanha","cabo verde"):13,("arabia saudita","uruguai"):14,
    ("belgica","egipto"):15,("irao","nova zelandia"):16,
    ("austria","jordania"):17,("franca","senegal"):18,
    ("iraque","noruega"):19,("argentina","argelia"):20,
    ("portugal","congo"):21,("inglaterra","croacia"):22,
    ("gana","panama"):23,("uzbequistao","colombia"):24,
    ("chequia","africa do sul"):25,("suica","bosnia"):26,
    ("canada","catar"):27,("mexico","coreia do sul"):28,
    ("turquia","paraguai"):29,("eua","australia"):30,
    ("escocia","marrocos"):31,("brasil","haiti"):32,
    ("tunisia","japao"):33,("paises baixos","suecia"):34,
    ("alemanha","costa do marfim"):35,("equador","curacao"):36,
    ("espanha","arabia saudita"):37,("belgica","irao"):38,
    ("uruguai","cabo verde"):39,("nova zelandia","egipto"):40,
    ("argentina","austria"):41,("franca","iraque"):42,
    ("noruega","senegal"):43,("jordania","argelia"):44,
    ("portugal","uzbequistao"):45,("inglaterra","gana"):46,
    ("panama","croacia"):47,("colombia","congo"):48,
    ("suica","canada"):49,("bosnia","catar"):50,
    ("escocia","brasil"):51,("marrocos","haiti"):52,
    ("chequia","mexico"):53,("africa do sul","coreia do sul"):54,
    ("equador","alemanha"):55,("curacao","costa do marfim"):56,
    ("japao","suecia"):57,("tunisia","paises baixos"):58,
    ("turquia","eua"):59,("paraguai","australia"):60,
    ("noruega","franca"):61,("senegal","iraque"):62,
    ("cabo verde","arabia saudita"):63,("uruguai","espanha"):64,
    ("egipto","irao"):65,("nova zelandia","belgica"):66,
    ("panama","inglaterra"):67,("croacia","gana"):68,
    ("colombia","portugal"):69,("congo","uzbequistao"):70,
    ("argelia","austria"):71,("jordania","argentina"):72,
}


def norm(t: str) -> str:
    if not t:
        return ""
    t = t.strip().lower()
    for old, new in [
        ("á","a"),("à","a"),("â","a"),("ã","a"),
        ("é","e"),("è","e"),("ê","e"),
        ("í","i"),("ì","i"),
        ("ó","o"),("ò","o"),("ô","o"),("õ","o"),
        ("ú","u"),("ù","u"),("û","u"),
        ("ç","c"),("ñ","n"),
    ]:
        t = t.replace(old, new)
    return re.sub(r"\s+", " ", t).strip()


def api_to_our(api_name: str) -> str:
    """Map API team name to our spreadsheet name."""
    lc = api_name.strip().lower()
    mapped = TEAM_MAP.get(lc)
    if mapped:
        return mapped
    # Capitalise first letter of each word as fallback
    return api_name.strip().title()


def find_game_num(home_api: str, away_api: str) -> int | None:
    h = norm(api_to_our(home_api))
    a = norm(api_to_our(away_api))
    return SCHEDULE.get((h, a))


def first_goal_team(events: list, home_our: str, away_our: str) -> str:
    goals = [e for e in events
             if e.get("type") == "Goal" and e.get("detail") != "Missed Penalty"]
    if not goals:
        return "NO GOALS"
    goals.sort(key=lambda e: (e.get("time", {}).get("elapsed") or 0))
    team_name = goals[0].get("team", {}).get("name", "")
    if not team_name:
        return "NO GOALS"
    # Map to our home/away name
    mapped = api_to_our(team_name)
    if norm(mapped) == norm(home_our):
        return home_our
    if norm(mapped) == norm(away_our):
        return away_our
    return mapped  # fallback


def main():
    if not API_KEY:
        print("ERROR: API_FOOTBALL_KEY secret not set")
        return

    out_path = Path("data/results.json")

    # Load existing results to preserve manual overrides
    existing = {}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
        except Exception:
            pass

    results = existing.get("games", {})
    final   = existing.get("final", {"champion": "", "runner_up": "", "third": ""})
    manual  = existing.get("manual_overrides", {})

    # ── Step 1: fetch all fixtures (scores + status) ──────────
    print("Fetching all WC2026 fixtures…")
    r = requests.get(f"{BASE}/fixtures?league=1&season=2026", headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    if data.get("errors"):
        print(f"API error: {data['errors']}")
        return

    fixtures = data.get("response", [])
    print(f"Got {len(fixtures)} fixtures from API")

    # Process scores
    need_events = []  # fixture IDs we need events for (finished, scorer unknown)
    game_meta   = {}  # fixtureId → {gameNum, home_our, away_our}

    for fx in fixtures:
        home_api = fx.get("teams", {}).get("home", {}).get("name", "")
        away_api = fx.get("teams", {}).get("away", {}).get("name", "")
        gn = find_game_num(home_api, away_api)
        if gn is None:
            continue

        home_our = api_to_our(home_api)
        away_our = api_to_our(away_api)
        fid      = fx.get("fixture", {}).get("id")
        status   = fx.get("fixture", {}).get("status", {}).get("short", "NS")
        elapsed  = fx.get("fixture", {}).get("status", {}).get("elapsed")
        hg       = fx.get("goals", {}).get("home")
        ag       = fx.get("goals", {}).get("away")

        LIVE      = {"1H","2H","ET","BT","P","INT"}
        FINISHED  = {"FT","AET","PEN"}

        if status not in LIVE and status not in FINISHED:
            continue
        if hg is None or ag is None:
            continue

        # Don't overwrite manual entries
        gn_str = str(gn)
        if manual.get(gn_str):
            continue

        existing_fs = results.get(gn_str, {}).get("fs", "NO GOALS")
        results[gn_str] = {
            "hg": hg, "ag": ag,
            "fs": existing_fs,
            "status": status,
            "min": elapsed,
        }

        # Queue for event fetch if finished and scorer not yet known
        if status in FINISHED and (existing_fs == "NO GOALS" or not existing_fs):
            need_events.append(fid)
            game_meta[fid] = {"gameNum": gn_str, "home": home_our, "away": away_our}

    # ── Step 2: fetch events for finished games without scorer ─
    if need_events:
        print(f"Fetching events for {len(need_events)} finished games…")
        for i in range(0, len(need_events), 20):
            batch = need_events[i:i+20]
            ids   = "-".join(str(x) for x in batch)
            try:
                r2 = requests.get(f"{BASE}/fixtures?ids={ids}", headers=HEADERS, timeout=30)
                r2.raise_for_status()
                data2 = r2.json()
                for fx2 in data2.get("response", []):
                    fid2 = fx2.get("fixture", {}).get("id")
                    meta = game_meta.get(fid2)
                    if not meta:
                        continue
                    events = fx2.get("events", [])
                    fs = first_goal_team(events, meta["home"], meta["away"])
                    gn_str = meta["gameNum"]
                    if gn_str in results:
                        results[gn_str]["fs"] = fs
                        print(f"  Game {gn_str}: {meta['home']} vs {meta['away']} → 1st scorer team: {fs}")
            except Exception as e:
                print(f"  Events batch error: {e}")

    # ── Step 3: check if competition has a winner (post-final) ─
    # The /standings endpoint has winner info after tournament ends
    if not final.get("champion"):
        try:
            rs = requests.get(f"{BASE}/standings?league=1&season=2026", headers=HEADERS, timeout=15)
            if rs.ok:
                sd = rs.json()
                for league_data in sd.get("response", []):
                    winner = league_data.get("league", {}).get("season", {}).get("winner")
                    if winner and winner.get("name"):
                        final["champion"] = api_to_our(winner["name"])
                        print(f"Champion detected: {final['champion']}")
        except Exception:
            pass

    # ── Write output ──────────────────────────────────────────
    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "games": results,
        "final": final,
        "manual_overrides": manual,
    }
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    done = sum(1 for v in results.values() if v.get("hg") is not None)
    print(f"Done. {done} games with results. Wrote {out_path}")


if __name__ == "__main__":
    main()
