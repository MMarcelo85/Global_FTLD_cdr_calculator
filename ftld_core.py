"""FTLD-CDR Global scoring and CSV batch processing.

Standard library only, so it can be shared by the Streamlit app (main.py)
and the desktop app (desktop_app.py), and packaged into a small executable.
"""
import csv
import io

SCORES = (0, 0.5, 1, 2, 3)
CARE_SCORES = (0, 1, 2, 3)  # Personal care cannot be scored 0.5
LEVELS = SCORES             # "one level lower": 3 -> 2, 2 -> 1, 1 -> 0.5

DOMAINS = [
    ("memory", "Memory"),
    ("orientation", "Orientation"),
    ("judgment", "Judgment and Problem Solving"),
    ("community", "Community Affairs"),
    ("home", "Home and Hobbies"),
    ("care", "Personal Care"),
    ("behavior", "Behavior, Comportment and Personality"),
    ("language", "Language"),
]

INSTRUCTIONS = (
    "Two scores must be obtained:\n"
    "1. FTLD-CDR Box Sum (automatically calculated in REDCap): calculate the sum of values for all "
    "responses (including the two additional domains) and enter the total score in the provided space.\n"
    "2. FTLD-CDR Global: derived from the scores in each of the eight categories (\"box scores\"). "
    "This app calculates this score."
)
RULES_TITLE = ("The rules for determining the FTLD-CDR global score are as follows "
               "(remember, they involve the eight domains or boxes):")
RULE_3_INTRO = "If the maximum domain score is greater than 0.5 in any domain, the following applies:"

RULES = {
    "1": "Rule 1: If all domains are 0, the FTLD-CDR global score is 0.",
    "2": "Rule 2: If the maximum domain score is 0.5, the FTLD-CDR global score is 0.5.",
    "3a": "Rule 3A: If the maximum domain score is 1 and all other domains are 0, the FTLD-CDR global score is 0.5.",
    "3b": "Rule 3B: If the maximum domain score is 2 or 3 and all other domains are 0, the FTLD-CDR global score is 1.",
    "3c": ("Rule 3C: If the maximum domain score occurs only once, and there is another score other than zero, "
           "the FTLD-CDR global score is one level lower than the level corresponding to the maximum impairment "
           "(for example, if the maximum = 2, and there is another score other than zero, the FTLD-CDR global "
           "score is 1; if the maximum = 1, and there is another score other than zero, the FTLD-CDR global "
           "score is 0.5)."),
    "3d": ("Rule 3D: If the maximum domain score occurs more than once (for example, 1 in 2 domains, "
           "2 in 2 domains), then the FTLD-CDR global score is that maximum domain score."),
}


def rule_body(rule_id):
    """Rule text without the 'Rule 3A: ' prefix (for numbered lists)."""
    return RULES[rule_id].split(": ", 1)[1]


def _score(d):
    """d: the 8 domain scores. Returns (ftld_cdr_global, rule_id). Same results as the original app (25/02/26)."""
    mx = max(d)
    if mx == 0:
        return 0, "1"
    if mx == 0.5:
        return 0.5, "2"
    if d.count(0) == 7:  # only one domain impaired
        return (0.5, "3a") if mx == 1 else (1, "3b")
    if d.count(mx) == 1:  # maximum occurs once and another domain is not zero
        return LEVELS[LEVELS.index(mx) - 1], "3c"
    return mx, "3d"


def validate(scores):
    """Return an error message, or None if the eight scores are valid."""
    if len(scores) != len(DOMAINS):
        return f"expected {len(DOMAINS)} domain scores"
    for (key, label), value in zip(DOMAINS, scores):
        allowed = CARE_SCORES if key == "care" else SCORES
        if value not in allowed:
            return f"invalid {label} score: {fmt(value)} (allowed: {', '.join(fmt(a) for a in allowed)})"
    return None


def calculate_ftld_cdr(scores):
    """scores: the 8 domain scores in DOMAINS order (Memory, Orientation, Judgment, Community, Home,
    Personal care, Behavior, Language). Returns (ftld_cdr_global, rule_text)."""
    error = validate(scores)
    if error:
        raise ValueError(error)
    cdr, rule = _score(list(scores))
    return cdr, RULES[rule]


def fmt(x):
    """Format a score: 0, 0.5, 1, 2, 3."""
    return f"{x:g}" if isinstance(x, (int, float)) else str(x)


# ---------------------------------------------------------------- CSV batch

# Accepted column names (case, spaces, punctuation and accents ignored).
ALIASES = {
    "memory": {"memory", "memoria", "mem", "m", "cdrmem"},
    "orientation": {"orientation", "orientacion", "orient", "box1", "cdrorient"},
    "judgment": {"judgment", "judgement", "judgmentandproblemsolving", "juicio", "judg", "box2", "cdrjudge"},
    "community": {"community", "communityaffairs", "comunidad", "commun", "box3", "cdrcommun"},
    "home": {"home", "homeandhobbies", "homehobb", "hogar", "box4", "cdrhome"},
    "care": {"personalcare", "perscare", "care", "cuidadopersonal", "cuidado", "box5", "cdrcare"},
    "behavior": {"behavior", "behaviour", "behaviorcomportmentandpersonality", "behaviorcomportmentpersonality",
                 "comportment", "comport", "behav", "comportamiento", "conducta",
                 "comportamientoconductaypersonalidad", "box6", "cdrcomport"},
    "language": {"language", "lenguaje", "lang", "cdrlang", "box7"},
}

OUT_SCORE = "FTLD_CDR_global"
OUT_RULE = "Rule_applied"
OUT_NOTE = "FTLD_CDR_note"
OUT_COLUMNS = (OUT_SCORE, OUT_RULE, OUT_NOTE)
CSV_HELP = (
    "Use either exactly 8 columns in this order: Memory, Orientation, Judgment, Community, Home, "
    "Personal care, Behavior, Language (e.g. Memory, box1, ..., box7); or name the columns Memory, "
    "Orientation, Judgment, Community, Home, PersonalCare, Behavior, Language (other columns, such as "
    "IDs, are kept)."
)


def _norm(name):
    name = name.strip().lower()
    for a, b in zip("áéíóúñü", "aeiounu"):
        name = name.replace(a, b)
    return "".join(ch for ch in name if ch.isalnum())


def _parse_score(text):
    text = (text or "").strip().replace(",", ".")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return text


def find_columns(header):
    """Map each domain to a column index. Uses column names if all eight are found;
    otherwise, if the file has exactly 8 columns, uses them in DOMAINS order."""
    normed = [_norm(h) for h in header]
    mapping = {}
    for key, names in ALIASES.items():
        for i, n in enumerate(normed):
            if n in names and i not in mapping.values():
                mapping[key] = i
                break
    if len(mapping) == len(DOMAINS):
        return [mapping[k] for k, _ in DOMAINS]
    if len(header) == len(DOMAINS):
        return list(range(len(DOMAINS)))
    raise ValueError(f"Could not identify the FTLD-CDR columns. {CSV_HELP} Columns found: {', '.join(header)}")


def decode(data):
    """Decode uploaded bytes (UTF-8 with or without BOM, else Latin-1)."""
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def process_csv(text):
    """Score every row of a CSV text.
    Returns (header, rows, output_csv_text, summary). Original columns are kept
    unchanged; FTLD_CDR_global, Rule_applied and FTLD_CDR_note are added (replaced if present).
    Rows with missing or invalid scores are kept, with the reason in FTLD_CDR_note."""
    try:
        delimiter = csv.Sniffer().sniff(text[:5000], delimiters=",;\t").delimiter
    except csv.Error:
        delimiter = ","
    all_rows = [r for r in csv.reader(io.StringIO(text), delimiter=delimiter) if any(c.strip() for c in r)]
    if not all_rows:
        raise ValueError("The file is empty.")
    header, data = all_rows[0], all_rows[1:]

    # Drop output columns from a previous run so they are recalculated.
    keep = [i for i, h in enumerate(header) if h.strip() not in OUT_COLUMNS]
    header = [header[i] for i in keep]
    data = [[(r[i] if i < len(r) else "") for i in keep] for r in data]

    cols = find_columns(header)
    out_header = header + list(OUT_COLUMNS)
    out_rows, n_ok = [], 0
    for r in data:
        values = [_parse_score(r[i]) for i in cols]
        error = "missing score(s)" if None in values else validate(values)
        if error:
            score, rule = "", ""
        else:
            cdr, rule_id = _score(values)
            score, rule = fmt(cdr), RULES[rule_id]
            if delimiter == ";":  # Excel in Spanish/European locales: decimal comma
                score = score.replace(".", ",")
            n_ok += 1
        out_rows.append(r + [score, rule, error or ""])

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter, lineterminator="\n")
    writer.writerow(out_header)
    writer.writerows(out_rows)
    used = ", ".join(header[i] for i in cols)
    summary = (f"{n_ok} rows scored, {len(out_rows) - n_ok} rows with missing/invalid scores "
               f"(see {OUT_NOTE}). Columns used: {used}.")
    return out_header, out_rows, buf.getvalue(), summary
