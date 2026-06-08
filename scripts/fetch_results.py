"""
Fetches FIFA World Cup 2026 results from football-data.org and writes data/results.json.
Called by GitHub Actions every 30 minutes.

API docs: https://docs.football-data.org/general/v4/match.html
WC competition code: WC
Free tier: 10 req/min, no daily limit, includes goals array with scorer info.

Output format:
{
  "updated": "2026-06-11T20:30:00Z",
  "games": {
    "1": { "hg": 2, "ag": 0, "fs": "México", "status": "FT", "min": 90 },
    ...
  },
  "final": { "champion": "", "runner_up": "", "third": "" },
  "manual_overrides": {}
}
"""

import os, json, re, requests
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
BASE    = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

# Map football-data.org team names → our spreadsheet names
TEAM_MAP = {
    "south africa": "Africa do Sul",
    "korea republic": "Coreia do Sul",
    "south korea": "Coreia do Sul",
    "czechia": "Chéquia",
    "czech republic": "Chéquia",
    "bosnia-herzegovina": "Bósnia",
    "bosnia and herzegovina": "Bósnia",
    "united states": "EUA",
    "usa": "EUA",
    "ivory coast": "Costa de Marfim",
    "côte d'ivoire": "Costa de Marfim",
    "cote d'ivoire": "Costa de Marfim",
    "netherlands": "Paises Baixos",
    "sweden": "Suecia",
    "cape verde": "Cabo Verde",
    "saudi arabia": "Arabia Saudita",
    "belgium": "Belgica",
    "egypt": "Egipto",
    "ir iran": "Irão",
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
    "türkiye": "Turquia",
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
    "dr congo": "Congo",
}

# (norm_home, norm_away) → game number
SCHEDULE = {
    ("mexico","africa do sul"):1, ("coreia do sul","chequia"):2,
    ("canada","bosnia"):3, ("eua","paraguai"):4,
    ("catar","suica"):5, ("brasil","marrocos"):6,
    ("haiti","escocia"):7, ("australia","turquia"):8,
    ("alemanha","curacao"):9, ("costa de marfim","equador"):10,
    ("paises baixos","japao"):11, ("suecia","tunisia"):12,
    ("espanha","cabo verde"):13, ("arabia saudita","uruguai"):14,
    ("belgica","egipto"):15, ("irao","nova zelandia"):16,
    ("austria","jordania"):17, ("franca","senegal"):18,
    ("iraque","noruega"):19, ("argentina","argelia"):20,
    ("portugal","congo"):21, ("inglaterra","croacia"):22,
    ("gana","panama"):23, ("uzbequistao","colombia"):24,
    ("chequia","africa do sul"):25, ("suica","bosnia"):26,
    ("canada","catar"):27, ("mexico","coreia do sul"):28,
    ("turquia","paraguai"):29, ("eua","australia"):30,
    ("escocia","marrocos"):31, ("brasil","haiti"):32,
    ("tunisia","japao"):33, ("paises baixos","suecia"):34,
    ("alemanha","costa do marfim"):35, ("equador","curacao"):36,
    ("espanha","arabia saudita"):37, ("belgica","irao"):38,
    ("uruguai","cabo verde"):39, ("nova zelandia","egipto"):40,
    ("argentina","austria"):41, ("franca","iraque"):42,
    ("noruega","senegal"):43, ("jordania","argelia"):44,
    ("portugal","uzbequistao"):45, ("inglaterra","gana"):46,
    ("panama","croacia"):47, ("colombia","congo"):48,
    ("suica","canada"):49, ("bosnia","catar"):50,
    ("escocia","brasil"):51, ("marrocos","haiti"):52,
    ("chequia","mexico"):53, ("africa do sul","coreia do sul"):54,
    ("equador","alemanha"):55, ("curacao","costa do marfim"):56,
    ("japao","suecia"):57, ("tunisia","paises baixos"):58,
    ("turquia","eua"):59, ("paraguai","australia"):60,
    ("noruega","franca"):61, ("senegal","iraque"):62,
    ("cabo verde","arabia saudita"):63, ("uruguai","espanha"):64,
    ("egipto","irao"):65, ("nova zelandia","belgica"):66,
    ("panama","inglaterra"):67, ("croacia","gana"):68,
    ("colombia","portugal"):69, ("congo","uzbequistao"):70,
    ("argelia","austria"):71, ("jordania","argentina"):72,
}


def norm(t: str) -> str:
    if not t:
        return ""
    t = t.strip().lower()
    for old, new in [
        ("á","a"),("à","a"),("â","a"),("ã","a"),("ä","a"),
        ("é","e"),("è","e"),("ê","e"),("ë","e"),
        ("í","i"),("ì","i"),("î","i"),
        ("ó","o"),("ò","o"),("ô","o"),("õ","o"),("ö","o"),
        ("ú","u"),("ù","u"),("û","u"),("ü","u"),
        ("ç","c"),("ñ","n"),("ș","s"),("ş","s"),
    ]:
        t = t.replace(old, new)
    return re.sub(r"\s+", " ", t).strip()


def to_our(api_name: str) -> str:
    if not api_name:
        return ""
    lc = api_name.strip().lower()
    return TEAM_MAP.get(lc, api_name.strip())


def find_game(home_api: str, away_api: str):
    h = norm(to_our(home_api))
    a = norm(to_our(away_api))
    return SCHEDULE.get((h, a))


def first_goal_team(goals: list, home_our: str, away_our: str) -> str:
    """
    football-data.org goals array item:
    { "minute": 23, "team": { "id": 1, "name": "Portugal" }, "scorer": { "name": "..." }, ... }
    """
    if not goals:
        return "NO GOALS"
    goals_sorted = sorted(goals, key=lambda g: g.get("minute") or 0)
    team_name = goals_sorted[0].get("team", {}).get("name", "")
    if not team_name:
        return "NO GOALS"
    mapped = to_our(team_name)
    if norm(mapped) == norm(home_our):
        return home_our
    if norm(mapped) == norm(away_our):
        return away_our
    return mapped


def main():
    if not API_KEY:
        print("ERROR: API_FOOTBALL_KEY secret not set")
        return

    out_path = Path("data/results.json")

    # Load existing to preserve manual overrides
    existing = {}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
        except Exception:
            pass

    results = existing.get("games", {})
    final   = existing.get("final", {"champion": "", "runner_up": "", "third": ""})
    manual  = existing.get("manual_overrides", {})

    # ── Single call: all WC matches with goals ────────────────
    # football-data.org returns goals[] embedded in each match
    print("Fetching WC2026 matches from football-data.org…")
    r = requests.get(
        f"{BASE}/competitions/WC/matches",
        headers=HEADERS,
        timeout=30
    )

    if r.status_code == 400:
        # Season not started yet or no matches — not an error
        print("No matches available yet (tournament not started)")
        out_path.write_text(json.dumps({
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "games": results,
            "final": final,
            "manual_overrides": manual,
        }, ensure_ascii=False, indent=2))
        return

    r.raise_for_status()
    data = r.json()
    matches = data.get("matches", [])
    print(f"Got {len(matches)} matches")

    LIVE     = {"IN_PLAY", "PAUSED"}
    FINISHED = {"FINISHED"}

    for m in matches:
        home_api = m.get("homeTeam", {}).get("name", "") or m.get("homeTeam", {}).get("shortName", "")
        away_api = m.get("awayTeam", {}).get("name", "") or m.get("awayTeam", {}).get("shortName", "")
        gn = find_game(home_api, away_api)
        if gn is None:
            continue

        status = m.get("status", "SCHEDULED")
        if status not in LIVE and status not in FINISHED:
            continue

        score = m.get("score", {})
        ft    = score.get("fullTime", {})
        hg    = ft.get("home")
        ag    = ft.get("away")

        # For live games use current score if fullTime not set
        if (hg is None or ag is None) and status in LIVE:
            ht = score.get("halfTime", {})
            hg = ht.get("home")
            ag = ht.get("away")

        if hg is None or ag is None:
            continue

        gn_str = str(gn)
        if manual.get(gn_str):
            continue

        home_our = to_our(home_api)
        away_our = to_our(away_api)

        # Goals array — only present for finished/live matches
        goals = m.get("goals", [])
        existing_fs = results.get(gn_str, {}).get("fs", "NO GOALS")
        fs = first_goal_team(goals, home_our, away_our) if goals else existing_fs

        results[gn_str] = {
            "hg": hg,
            "ag": ag,
            "fs": fs,
            "status": "FT" if status == "FINISHED" else "LIVE",
            "min": m.get("minute"),
        }
        print(f"  Game {gn_str}: {home_our} {hg}-{ag} {away_our} | 1st: {fs}")

    # Check for competition winner
    if not final.get("champion"):
        winner = data.get("competition", {}).get("currentSeason", {}).get("winner")
        if winner and winner.get("name"):
            final["champion"] = to_our(winner["name"])
            print(f"Champion: {final['champion']}")

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "games": results,
        "final": final,
        "manual_overrides": manual,
    }
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    done = sum(1 for v in results.values() if v.get("hg") is not None)
    print(f"Done. {done} games with results.")


if __name__ == "__main__":
    main()