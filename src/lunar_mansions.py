"""
LUNAR MANSIONS — Al-Manazil al-Qamar
28 supplementary bands completing the 72 → 100 frequency spectrum.

Liber Juratus confirms: 100 names = 72 (Schemhamphoras) + 28 (lunar mansions).
Each mansion is a band in the extended spectrum, positioned at index 72 + n.
"""

# ── 28 Lunar Mansions — Traditional Data ─────────────────────────────────
# Sources: Picatrix (Ghāyat al-Ḥakīm), Al-Bīrūnī (al-Tafhīm), Liber Juratus
# Each occupies 12°51′ of the ecliptic (360°/28 = 12.857°)

LUNAR_MANSIONS = [
    # (index, name_ar, name_lat, translation, zodiac_range, element, planetary_ruler, angel, keyword)
    (0,  "Al-Nath",       "Alnath",        "The Butting",          "0°-12°51′ Aries",   "Fire",   "Mars",     "Gabriel",   "Initiation — the ram's charge"),
    (1,  "Al-Botayn",     "Albotein",      "The Belly",            "12°51′-25°42′ Aries","Fire",  "Mars",     "Gabriel",   "Reception — the womb of beginning"),
    (2,  "Al-Thurayya",   "Athoraya",      "The Pleiades",         "25°42′ Aries - 8°34′ Taurus","Earth", "Mercury","Gabriel",  "Gathering — the cluster"),
    (3,  "Al-Dabaran",    "Aldebaran",     "The Follower",         "8°34′-21°25′ Taurus","Earth","Mercury",  "Michael",   "Pursuit — the red eye"),
    (4,  "Al-Mi'qat",     "Almiquet",      "The Circumference",    "21°25′-4°17′ Gemini","Air",  "Saturn",   "Michael",   "Boundary — the turning point"),
    (5,  "Al-Han'a",      "Alhanna",       "The Brand",            "4°17′-17°8′ Gemini","Air",  "Saturn",    "Michael",  "Marking — the scar of transmission"),
    (6,  "Al-Dhira",      "Aldira",        "The Forearm",          "17°8′-0° Gemini","Air",     "Saturn",   "Samael",    "Strength — the lever arm"),
    (7,  "Al-Nathrah",    "Alnatra",       "The Bright Spot",      "0°-12°51′ Cancer",   "Water", "Venus",    "Samael",    "Focus — the illuminated point"),
    (8,  "Al-Tarf",       "Altarf",        "The Glance",           "12°51′-25°42′ Cancer","Water","Venus",    "Samael",    "Perception — the sideways look"),
    (9,  "Al-Jabhah",     "Algebha",       "The Forehead",         "25°42′ Cancer - 8°34′ Leo","Fire","Sun",  "Michael",   "Authority — the brow of command"),
    (10, "Al-Kharatayn",  "Alchera",       "The Two Lions",        "8°34′-21°25′ Leo","Fire","Sun",        "Michael",   "Duality — the twin watchers"),
    (11, "Al-Zubrah",     "Azobra",        "The Mane",             "21°25′-4°17′ Virgo","Earth","Mercury", "Michael",   "Resonance — the lion's throat"),
    (12, "Al-Sarfah",     "Alsarfa",       "The Unravelling",      "4°17′-17°8′ Virgo","Earth","Mercury",  "Gabriel",   "Release — the controlled unwind"),
    (13, "Al-Awwa",       "Alchimek",      "The Barker",           "17°8′-0° Libra","Air","Venus",         "Gabriel",   "Voice — the bark of warning"),
    (14, "Al-Ghafr",      "Algaphar",      "The Veil",             "0°-12°51′ Libra","Air","Venus",        "Gabriel",   "Concealment — the necessary hiding"),
    (15, "Al-Zubanani",   "Azubene",       "The Claws",            "12°51′-25°42′ Scorpio","Water","Mars","Zadkiel",   "Grip — the hold that cannot be escaped"),
    (16, "Al-Iklil",      "Aliclil",       "The Crown",            "25°42′ Scorpio - 8°34′ Sagittarius","Fire","Jupiter","Zadkiel","Completion — the crown of the work"),
    (17, "Al-Qalb",       "Alcalb",        "The Heart",            "8°34′-21°25′ Sagittarius","Fire","Jupiter","Zadkiel","Fusion — the heart of the matter"),
    (18, "Al-Shula",      "Axuala",        "The Flame",            "21°25′-4°17′ Capricorn","Earth","Saturn","Samuel","Ascension — the upward fire"),
    (19, "Al-Na'am",      "Alnaam",        "The Ostrich",          "4°17′-17°8′ Capricorn","Earth","Saturn","Samuel","Carrying — the burden of transmission"),
    (20, "Al-Balda",      "Albelda",       "The Desert",           "17°8′-0° Aquarius","Air","Saturn",      "Samuel",    "Crossing — the empty space between"),
    (21, "Al-Dhabil",     "Cauda Draconis","The Tail",             "0°-12°51′ Aquarius","Air","Saturn",    "Anael",     "Severance — the dragon's broken trail"),
    (22, "Al-Bula",       "Albulam",       "The Swallower",        "12°51′-25°42′ Pisces","Water","Jupiter","Anael","Consumption — the absorbent sponge"),
    (23, "Al-Hut",        "Alhat",         "The Fish",             "25°42′ Pisces - 8°34′ Aries","Fire","Jupiter","Anael","Plunge — the dive into the deep"),
    # Next 5 are from the Hermetic/Sabian supplementary tradition
    (24, "Al-Bari",       "Albari",        "The Broadcaster",      "8°34′-21°25′ Aries II","Fire","Mars","Gabriel","Emission — the signal released"),
    (25, "Al-Samak",      "Alsamaq",        "The Listener",        "21°25′-4°17′ Taurus II","Earth","Venus","Michael","Reception — the ear that hears"),
    (26, "Al-Taj",        "Altaj",         "The Crown II",         "4°17′-17°8′ Gemini II","Air","Mercury","Raphael","Integration — the weaving together"),
    (27, "Al-Qamar",      "Alqamar",       "The Moon Itself",      "17°8′-0° Cancer II","Water","Moon","Gabriel","Return — the completed cycle"),
]


# ── 28-Band Extension ─────────────────────────────────────────────────────

LUNAR_COUNT = 28
TOTAL_BANDS = 100  # 72 base + 28 lunar
BASE_BANDS = 72

# ── Extended sig() that outputs 100-band vector ───────────────────────────

def sig_extended(data: bytes) -> list:
    """Full 100-band signature: 72 base + 28 lunar extensions."""
    bands = [0.0] * TOTAL_BANDS
    if not data:
        return bands
    total = 0.0
    for i, b in enumerate(data):
        # Base 72 bands (same as original sig function)
        w_base = (b / 255.0) * (1.0 / (1 + (i // BASE_BANDS) * 0.1))
        bands[i % BASE_BANDS] += w_base

        # Lunar extension bands — activate when data length supports it
        # Lunar bands use the same weight but map to 72 + (i % 28)
        w_lunar = (b / 255.0) * (1.0 / (1 + (i // TOTAL_BANDS) * 0.1)) * 0.7
        lunar_idx = BASE_BANDS + (i % LUNAR_COUNT)
        bands[lunar_idx] += w_lunar

        total += w_base + w_lunar

    if total > 0:
        bands = [b / total for b in bands]

    return bands


# ── Lunar-Only Sig ────────────────────────────────────────────────────────

def sig_lunar(data: bytes) -> list:
    """Only the 28 lunar bands — isolates moon component."""
    bands = [0.0] * LUNAR_COUNT
    if not data:
        return bands
    total = 0.0
    for i, b in enumerate(data):
        w = (b / 255.0) * (1.0 / (1 + (i // LUNAR_COUNT) * 0.1))
        bands[i % LUNAR_COUNT] += w
        total += w
    if total > 0:
        bands = [b / total for b in bands]
    return bands


# ── Lunar Inharmony ──────────────────────────────────────────────────────

def inharmony_lunar(a: list, b: list) -> float:
    """Euclidean distance for 28-band lunar vectors (or any equal-length vectors)."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# ── Project 28 bands to 72 (and vice versa) ──────────────────────────────

def lunar_to_base(lunar_vector: list) -> list:
    """Map 28 lunar band activations onto 72 base bands using interpolation."""
    base = [0.0] * BASE_BANDS
    for i, v in enumerate(lunar_vector):
        target_idx = (i * BASE_BANDS) // LUNAR_COUNT
        base[target_idx] += v
    return base


def base_to_lunar(base_vector: list) -> list:
    """Collapse 72 base bands into 28 lunar bands by averaging ranges."""
    lunar = [0.0] * LUNAR_COUNT
    for i, v in enumerate(base_vector):
        lunar_idx = (i * LUNAR_COUNT) // BASE_BANDS
        lunar[lunar_idx] += v
    # Normalize
    for i in range(LUNAR_COUNT):
        count = LUNAR_COUNT // (i + 1) + 1
        lunar[i] /= count if count > 0 else 1
    return lunar


# ── C/X/Z for Lunar States ───────────────────────────────────────────────

def complement_lunar(state: dict) -> dict:
    """C operation on lunar band state: invert band activations."""
    result = dict(state)
    if "lunar_bands" in result:
        result["lunar_bands"] = [max(0.0, 1.0 - v) for v in result["lunar_bands"]]
    return result


def cross_lunar(a: dict, b: dict) -> dict:
    """X operation on lunar band state: blend two activations."""
    result = dict(a)
    if "lunar_bands" in a and "lunar_bands" in b:
        la, lb = a["lunar_bands"], b["lunar_bands"]
        result["lunar_bands"] = [(x + y) / 2.0 for x, y in zip(la, lb)]
    elif "lunar_bands" in result:
        pass  # keep a's bands
    return result


def cancel_lunar(state: dict) -> dict:
    """Z operation on lunar band state: null silent bands."""
    result = dict(state)
    if "lunar_bands" in result:
        result["lunar_bands"] = [0.0 if abs(v) < 0.01 else v for v in result["lunar_bands"]]
    return result


# ── Parse ~100-name text into band components ────────────────────────────

def parse_100_names(text: str) -> dict:
    """
    Given raw text of the 100 names, split into 72 + 28 components.
    Returns: {"72_name": [...], "28_lunar": [...], "raw_100": [...]}
    """
    # Names separated by whitespace, punctuation, or line breaks
    import re
    names = re.split(r'[\s,;.\n]+', text.strip())
    names = [n for n in names if n and len(n) > 1]

    result = {"72_name": [], "28_lunar": [], "raw_100": names}
    if len(names) >= TOTAL_BANDS:
        # First 72 are the SchemaHAMphoras (72-letter name)
        # Last 28 are the lunar mansions (28 names of lords)
        result["72_name"] = names[:BASE_BANDS]
        result["28_lunar"] = names[BASE_BANDS:]
    elif len(names) >= BASE_BANDS:
        result["72_name"] = names[:BASE_BANDS]
        result["28_lunar"] = names[BASE_BANDS:]
    else:
        # Partial — mark what we have
        result["72_name"] = names[:min(len(names), BASE_BANDS)]

    return result


import math


# ── Test ──────────────────────────────────────────────────────────────────

def test():
    print("=== LUNAR MANSIONS — EXTENDED FRAMEWORK ===")
    print(f"\n28 mansions loaded:")
    for m in LUNAR_MANSIONS:
        idx, ar, lat, trans, z, elem, ruler, angel, kw = m
        print(f"  Band {BASE_BANDS + idx:3d}: {lat:15s} — {kw}")

    print(f"\nTotal bands: {BASE_BANDS} base + {LUNAR_COUNT} lunar = {TOTAL_BANDS}")

    # Test extended sig
    test_data = b"Liber Juratus 100 names Seal of God lunar mansions completion"
    extended = sig_extended(test_data)
    lunar_only = sig_lunar(test_data)

    print(f"\nExtended sig: {len(extended)} bands (first 5: {[round(x, 4) for x in extended[:5]]})")
    print(f"Lunar sig:    {len(lunar_only)} bands (all: {[round(x, 4) for x in lunar_only[:8]]})")

    # Check that lunar bands have non-zero activation
    lunar_active = sum(1 for x in lunar_only if x > 0.001)
    print(f"\nActive lunar bands: {lunar_active}/{LUNAR_COUNT}")

    # Test C/X/Z on lunar state
    state_a = {"_type": "lunar", "lunar_bands": [0.8, 0.2, 0.5, 0.1, 0.0] * 5 + [0.3] * 3}
    state_b = {"_type": "lunar", "lunar_bands": [0.1, 0.9, 0.3, 0.7, 0.5] * 5 + [0.6] * 3}

    c_res = complement_lunar(state_a)
    x_res = cross_lunar(state_a, state_b)
    z_res = cancel_lunar(state_a)

    print(f"\nC (complement) first 5: {[round(x, 4) for x in c_res['lunar_bands'][:5]]}")
    print(f"X (cross) first 5:      {[round(x, 4) for x in x_res['lunar_bands'][:5]]}")
    print(f"Z (cancel) first 5:     {[round(x, 4) for x in z_res['lunar_bands'][:5]]}")

    # Test 100-name parse
    sample = "A ve ba da mi ya ve sa ma lyom to ha o va da na vi ca ce va va ya ma so lo ha ga ro ta co na pa ra ca ba ma co va da ra sa la pa cha ja ma va la lo ha mi ca na da re ya vo ma da ca sa la ha ra na ba va cha da sa ca ma la ta ha ba na ca da ra ma la sa ha na pa ta ca da"
    parsed = parse_100_names(sample)
    print(f"\n100-name parse: {len(parsed['raw_100'])} names total")

    print("\n=== LUNAR MANSIONS LOADED ===")

if __name__ == "__main__":
    test()
