"""Small, dependency-free text helpers used by the matcher."""
import re
import unicodedata

# Words that carry no meaning for matching. (Question words such as
# who / what / where / how / which are deliberately KEPT.)
STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were", "be", "been", "to", "of", "in", "on",
    "for", "at", "by", "with", "it", "its", "this", "that", "these", "those", "i", "me", "my",
    "you", "your", "we", "our", "us", "do", "does", "did", "can", "could", "would", "should",
    "will", "shall", "may", "might", "please", "tell", "hi", "hello", "hey", "excuse", "just",
    "curious", "and", "or", "so", "if", "then", "there", "have", "has", "had", "want", "know",
    "would", "like", "about", "any", "some", "get", "give", "let", "also",
}

# Spelling / wording variants -> one canonical token
SYNONYMS = {
    "scooter": "scooty", "scooters": "scooty", "scooties": "scooty", "scootie": "scooty",
    "scootys": "scooty", "scotty": "scooty", "skooty": "scooty",
    "licence": "license", "licences": "license", "licenses": "license",
    "prices": "price", "pricing": "price", "costs": "cost", "costly": "cost", "expensive": "cost",
    "rate": "price", "rates": "price",
    "founder": "found", "founders": "found", "founded": "found", "founding": "found",
    "started": "found", "created": "found", "creator": "found", "invented": "found",
    "built": "found", "made": "found", "established": "found", "inventor": "found",
    "raining": "rain", "rainy": "rain", "rains": "rain", "rained": "rain", "monsoon": "rain",
    "birthplace": "born", "birth": "born",
    "originally": "origin", "nationality": "origin",
    "bangla": "bengali", "bangali": "bengali", "bengla": "bengali",
    "sunlight": "sun", "sunny": "sun", "sunshine": "sun",
    "documents": "document", "docs": "document", "doc": "document", "paperwork": "document",
    "papers": "paper", "nid": "nid", "taka": "bdt", "tk": "bdt",
    "purchase": "buy", "purchasing": "buy", "buying": "buy", "bought": "buy", "order": "buy",
    "eligibility": "eligible", "requirements": "requirement", "conditions": "condition",
    "charging": "charge", "charged": "charge", "charges": "charge", "recharge": "charge",
    "sharing": "share", "shared": "share", "shares": "share",
    "powered": "power", "powers": "power",
    "contact": "contact", "calling": "call", "phone": "phone", "mobile": "phone",
    "complain": "complaint", "complaints": "complaint",
    "thanks": "thank", "thx": "thank", "bye": "goodbye",
    "okey": "okay", "cheap": "cost", "cheaper": "cost", "affordable": "cost", "socket": "plug", "wat": "what", "wht": "what", "hw": "how", "whr": "where", "whn": "when",
}

_BENGALI = re.compile(r"[\u0980-\u09FF]")
_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)


def has_bengali(text: str, threshold: float = 0.3) -> bool:
    """True if a large part of the letters are Bengali script."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    bengali = sum(1 for c in letters if _BENGALI.match(c))
    return bengali / len(letters) >= threshold


def _stem(tok: str) -> str:
    if tok in SYNONYMS:
        return SYNONYMS[tok]
    if len(tok) > 4 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith(("ss", "us", "is")):
        tok = tok[:-1]
    return SYNONYMS.get(tok, tok)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("'", "")           # founder's -> founders
    text = _NON_WORD.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str, keep_stopwords: bool = False) -> list[str]:
    out = []
    for raw in normalize(text).split():
        if not keep_stopwords and raw in STOPWORDS:
            continue
        tok = _stem(raw)
        if not keep_stopwords and tok in STOPWORDS:
            continue
        out.append(tok)
    return out
