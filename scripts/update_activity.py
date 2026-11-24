"""Refresh public GitHub telemetry. Standard library only; no private repo data is saved."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IST = timezone(timedelta(hours=5, minutes=30))
LOGIN = os.environ.get("PROFILE_LOGIN", "ishaans04")
QUERY = '''query($login:String!,$since:DateTime!,$until:DateTime!){
user(login:$login){
contributionsCollection(to:$until){
totalCommitContributions
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}}
recent:contributionsCollection(from:$since,to:$until){
commitContributionsByRepository(maxRepositories:100){
repository{name nameWithOwner url isPrivate}
contributions(first:100){nodes{occurredAt commitCount} pageInfo{hasNextPage}}}}}}'''


def api(endpoint, payload=None):
    """Use the workflow token, or local gh auth without exposing its token."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        args = ["gh", "api", endpoint]
        if payload is not None:
            args += ["--input", "-"]
        result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                                capture_output=True, text=True, encoding="utf-8", check=True)
        return json.loads(result.stdout)
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request("https://api.github.com/"+endpoint, data=data,
                  headers={"Authorization": "Bearer "+token,
                           "Accept": "application/vnd.github+json",
                           "X-GitHub-Api-Version": "2022-11-28",
                           "User-Agent": "ishaans04-profile", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urlopen(req, timeout=40) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code < 500 or attempt == 2:
                raise
        except URLError:
            if attempt == 2:
                raise
        time.sleep(2*(attempt+1))
    raise RuntimeError("GitHub did not return a response")


def public_projects(entries, start, end):
    """Preserve owner-qualified identities; never serialize private repositories."""
    projects = []
    for entry in entries:
        repo = entry["repository"]
        if repo["isPrivate"] or repo["nameWithOwner"].lower() == f"{LOGIN}/{LOGIN}".lower():
            continue
        if entry["contributions"]["pageInfo"]["hasNextPage"]:
            raise ValueError("Incomplete daily contributions: refusing to publish truncated data")
        daily = Counter()
        for node in entry["contributions"]["nodes"]:
            day = node["occurredAt"][:10]
            if start <= day <= end:
                daily[day] += node["commitCount"]
        if sum(daily.values()):
            projects.append({"name": repo["name"], "full_name": repo["nameWithOwner"],
                             "url": repo["url"], "daily": dict(sorted(daily.items())),
                             "commits": sum(daily.values())})
    return sorted(projects, key=lambda x: (-x["commits"], x["full_name"]))


def fetch():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = (now.date()-timedelta(days=29)).isoformat()
    until = now.isoformat().replace("+00:00", "Z")
    result = api("graphql", {"query": QUERY, "variables": {
        "login": LOGIN, "since": start+"T00:00:00Z", "until": until}})
    if result.get("errors"):
        raise ValueError("GitHub GraphQL query failed: "+str(result["errors"]))
    user = result["data"]["user"]
    if user is None:
        raise ValueError("GitHub user not found")
    collection = user["contributionsCollection"]
    projects = public_projects(user["recent"]["commitContributionsByRepository"], start, now.date().isoformat())
    # A bounded sample, explicitly labeled in both the image and accessible text.
    hours = [0]*24
    seen = set()
    sampled_repos = []
    since = (now-timedelta(days=90)).isoformat().replace("+00:00", "Z")
    for repo in projects[:8]:
        endpoint = "repos/"+repo["full_name"]+"/commits?"+urlencode({
            "author": LOGIN, "since": since, "per_page": 100})
        commits = api(endpoint)
        sampled_repos.append(repo["full_name"])
        for commit in commits:
            sha = commit["sha"]
            if sha in seen:
                continue
            seen.add(sha)
            stamp = commit["commit"]["author"]["date"]
            dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(IST)
            hours[dt.hour] += 1
    days = [day for week in collection["contributionCalendar"]["weeks"] for day in week["contributionDays"]]
    return {"login": LOGIN, "updated_at": until,
            "calendar": {"total": collection["contributionCalendar"]["totalContributions"],
                         "commit_contributions": collection["totalCommitContributions"],
                         "days": days},
            "projects": {"from": start, "to": now.date().isoformat(), "window_days": 30,
                         "date_timezone": "UTC (GitHub contribution dates)", "items": projects},
            "commit_time_sample": {"hours_ist": hours, "count": sum(hours), "lookback_days": 90,
                                   "per_repo_limit": 100, "repositories": sampled_repos}}


def txt(x, y, value, size=20, fill="#eaf2ff", weight=400, mono=False, anchor="start"):
    family = "Consolas,'Liberation Mono',monospace" if mono else "'Segoe UI',Arial,Helvetica,sans-serif"
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'


def box(x, y, w, h, fill, rx=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'


def render(data):
    days = data["calendar"]["days"]
    projects = data["projects"]["items"][:6]
    date_end = datetime.fromisoformat(data["projects"]["to"]).date()
    hours = data["commit_time_sample"]["hours_ist"]
    peak = max(range(24), key=lambda i: sum(hours[(i+j) % 24] for j in range(3))) if sum(hours) else None
    peak_label = f"{peak:02d}:00–{(peak+3)%24:02d}:00 IST" if peak is not None else "No recent sample"
    height = 1080
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
         '<title id="title">Mission control: GitHub contributions and daily project commits</title>',
         f'<desc id="desc">{data["calendar"]["total"]} GitHub contributions in the last year. Public project activity over 30 days. Most active three-hour window in the sampled commits: {peak_label}.</desc>',
         box(0, 0, 1200, height, "#0b1422", 20),
         '<rect x="1" y="1" width="1198" height="1078" rx="20" fill="none" stroke="#23374a"/>',
         txt(42, 47, "MISSION CONTROL / GITHUB TELEMETRY", 18, "#a4df8a", 600, True),
         txt(1157, 47, data["updated_at"][:10]+" / UTC", 16, "#91a8bf", mono=True, anchor="end")]
    active = sum(1 for d in days if d["contributionCount"])
    metrics = [(data["calendar"]["total"], "CONTRIBUTIONS / LAST YEAR"),
               (data["calendar"]["commit_contributions"], "CREDITED COMMITS / LAST YEAR"),
               (active, "ACTIVE DAYS / LAST YEAR")]
    for i, (value, label) in enumerate(metrics):
        x = 42+i*384
        s += [box(x, 78, 360, 112, "#111f30", 12), txt(x+22, 130, f"{value:,}", 42, weight=700),
              txt(x+22, 164, label, 14, "#97abc1", mono=True)]
    # Calendar uses actual GitHub contribution dates and Sunday-first columns.
    s += [txt(42, 236, "THE LONG GAME", 16, "#a4df8a", 600, True)]
    first = datetime.fromisoformat(days[0]["date"]).date()
    origin = first-timedelta(days=(first.weekday()+1) % 7)
    last_month = None
    colors = ["#162738", "#284d37", "#3e7443", "#67a85b", "#a3df7c"]
    for day in days:
        dt = datetime.fromisoformat(day["date"]).date()
        week = (dt-origin).days//7
        x, y = 91+week*20, 277+day["weekday"]*20
        count = day["contributionCount"]
        level = 0 if not count else 1 if count < 4 else 2 if count < 10 else 3 if count < 20 else 4
        s.append(f'<g><title>{day["date"]}: {count} contributions</title>'+box(x,y,16,16,colors[level])+"</g>")
        if dt.month != last_month and day["weekday"] == 0 and week > 1:
            s.append(txt(x, 264, dt.strftime("%b"), 13, "#91a8bf", mono=True))
            last_month = dt.month
    for wd, label in [(1, "MON"), (3, "WED"), (5, "FRI")]:
        s.append(txt(42, 290+wd*20, label, 12, "#91a8bf", mono=True))
    s.append(txt(1005, 443, "LESS", 12, "#91a8bf", mono=True, anchor="end"))
    s.append(txt(1128, 443, "MORE", 12, "#91a8bf", mono=True))
    for i, color in enumerate(colors):
        s.append(box(1020+i*20, 429, 16, 16, color))
    # Six public repo rows; 30 dates, latest day on the right.
    s += [txt(42, 494, "ACTIVE MISSIONS / DAILY COMMITS", 16, "#a4df8a", 600, True),
          txt(1157, 494, "LAST 30 DAYS · UTC", 14, "#91a8bf", mono=True, anchor="end")]
    date_start = date_end-timedelta(days=29)
    for offset in (0, 7, 14, 21, 29):
        s.append(txt(435+offset*19, 525, (date_start+timedelta(days=offset)).strftime("%d %b"), 11, "#91a8bf", mono=True, anchor="middle"))
    for i, repo in enumerate(projects):
        y = 541+i*38
        display = repo["full_name"].removeprefix(LOGIN+"/")
        if len(display) > 31:
            display = display[:28]+"..."
        s += [txt(42, y+17, display, 19, weight=600),
              txt(1157, y+17, repo["commits"], 21, "#b8e79a", 600, True, "end")]
        for offset in range(30):
            stamp = (date_start+timedelta(days=offset)).isoformat()
            count = repo["daily"].get(stamp, 0)
            level = 0 if not count else 1 if count < 3 else 2 if count < 7 else 3 if count < 15 else 4
            s.append('<g><title>'+escape(f'{repo["full_name"]} / {stamp}: {count} commits')+'</title>'+box(426+offset*19, y, 15, 23, colors[level])+"</g>")
    if not projects:
        s.append(txt(42, 584, "No credited public project commits in this 30-day window.", 22, "#91a8bf"))
    # Hourly histogram: observed timestamps, no weekday assumptions.
    s += [txt(42, 823, "WHEN THE SUIT IS ONLINE", 16, "#a4df8a", 600, True),
          txt(1157, 823, peak_label, 19, "#c6e7ad", 600, anchor="end")]
    highest = max(hours) or 1
    for hour, count in enumerate(hours):
        bh = round(count/highest*103)
        hot = peak is not None and (hour-peak) % 24 < 3
        s.append(box(44+hour*46, 966-bh, 33, max(2,bh), "#a4df8a" if hot else "#355a4d", 3))
        if hour % 3 == 0:
            s.append(txt(60+hour*46, 991, f"{hour:02d}", 13, "#91a8bf", mono=True, anchor="middle"))
    sample = data["commit_time_sample"]
    s += [txt(42, 1030, f'{sample["count"]} unique public commit timestamps · up to 100/repo · {len(sample["repositories"])} active repos · 90-day lookback · IST', 14, "#91a8bf", mono=True),
          txt(42, 1058, "Public project rows exclude profile maintenance. Calendar follows GitHub's contribution rules.", 14, "#69829b")]
    s.append('</svg>')
    return ''.join(s)


def readme_log(data):
    end = datetime.fromisoformat(data["projects"]["to"]).date()
    dates = [(end-timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    lines = [f'**Last telemetry refresh:** {data["updated_at"][:10]} UTC · [Activity source](assets/activity.json)',
             '', '<details>', '<summary><b>Open the daily mission log — public commits by project</b></summary>', '',
             'Dates follow GitHub contribution days (UTC). Each cell is the number of credited commits.', '',
             '| Public project | '+' | '.join(d[5:] for d in dates)+' | 30-day total |',
             '| :--- | '+' | '.join(['---:']*8)+' |']
    for repo in data["projects"]["items"]:
        label = repo["full_name"].removeprefix(LOGIN+"/")
        lines.append(f'| [{label}]({repo["url"]}) | '+' | '.join(str(repo["daily"].get(d, 0)) for d in dates)+f' | {repo["commits"]} |')
    if not data["projects"]["items"]:
        lines += ['| No public project commits in this window | '+' | '.join(['0']*8)+' |']
    lines += ['', '</details>']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', help='Re-render saved public data without API calls')
    args = parser.parse_args()
    data_path = ROOT/'assets/activity.json'
    data = json.loads(data_path.read_text(encoding='utf-8')) if args.offline else fetch()
    # Fetch and render everything before replacing any last-known-good files.
    image = render(data)
    readme_path = ROOT/'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    content = '<!-- ACTIVITY:START -->\n'+readme_log(data)+'\n<!-- ACTIVITY:END -->'
    readme, count = re.subn(r'<!-- ACTIVITY:START -->.*?<!-- ACTIVITY:END -->', lambda _: content, readme, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one activity block in README')
    data_path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    (ROOT/'assets/activity.svg').write_text(image, encoding='utf-8')
    readme_path.write_text(readme, encoding='utf-8')
    print(f'Updated {data["login"]}: {data["calendar"]["total"]} contributions; {len(data["projects"]["items"])} active public repos; {data["commit_time_sample"]["count"]} sampled commits')


if __name__ == '__main__':
    main()
