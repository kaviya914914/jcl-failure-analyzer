import json
import re
import sys
from collections import OrderedDict

ABEND_RE = re.compile(
    r"IEF450I\s+(?P<job>\S+)\s+(?P<step>\S+)\s+-\s+ABEND=(?P<sys>S[0-9A-F]{3})\s+(?P<user>U\d{4})"
)
COND_RE = re.compile(
    r"IEF142I\s+(?P<job>\S+)\s+(?P<step>\S+)\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE\s+(?P<cc>\d{4})"
)


def load_knowledge_base(path="abends.json"):
    with open(path) as f:
        return json.load(f)


def parse_log(path):
    """Return {job: [events]}, where each event is a step result or an abend."""
    jobs = OrderedDict()
    with open(path) as f:
        for line in f:
            m = COND_RE.search(line)
            if m:
                jobs.setdefault(m["job"], []).append(
                    {"step": m["step"], "kind": "step", "cc": int(m["cc"])}
                )
                continue
            m = ABEND_RE.search(line)
            if m:
                # A user abend shows as S000 plus a U-code, so report the U-code
                code = m["user"] if m["sys"] == "S000" else m["sys"]
                jobs.setdefault(m["job"], []).append(
                    {"step": m["step"], "kind": "abend", "code": code}
                )
    return jobs


def print_report(jobs, kb):
    total_abends = 0
    total_warnings = 0
    for job, events in jobs.items():
        print(f"\nJOB {job}")
        for e in events:
            if e["kind"] == "step":
                if e["cc"] == 0:
                    print(f"  {e['step']:<8} OK (RC 0000)")
                else:
                    total_warnings += 1
                    print(f"  {e['step']:<8} WARNING (RC {e['cc']:04d})")
            else:
                total_abends += 1
                info = kb.get(e["code"])
                if info:
                    print(f"  {e['step']:<8} ABEND {e['code']}: {info['name']}")
                    print(f"           Meaning: {info['meaning']}")
                    print("           Check first:")
                    for i, check in enumerate(info["first_checks"], 1):
                        print(f"             {i}. {check}")
                else:
                    print(f"  {e['step']:<8} ABEND {e['code']}: not in knowledge base yet")
                    print("           Add it to abends.json")
    s = "" if total_warnings == 1 else "s"
    print(f"\nSummary: {len(jobs)} jobs, {total_abends} abends, {total_warnings} warning{s}")
    return total_abends


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <job_log_file>")
        sys.exit(2)
    kb = load_knowledge_base()
    jobs = parse_log(sys.argv[1])
    if not jobs:
        print("No job step or abend messages found in this log.")
        sys.exit(2)
    abends = print_report(jobs, kb)
    sys.exit(1 if abends else 0)