from typing import Optional

# Base gold value per stat point (League of Legends wiki baseline)
STAT_VALUE = {
    "FlatArmorMod": 20.0,
    "FlatSpellBlockMod": 18.0,
    "FlatPhysicalDamageMod": 35.0,
    "FlatMagicDamageMod": 20.0,       # Amplifying Tome = 400g / 20 AP
    "FlatHPPoolMod": 2.67,            # Ruby Crystal = 400g / 150 HP
    "PercentAttackSpeedMod": 25.0,    # Dagger = 250g / 10% (Riot stores 0.10, so multiply by 100)
    "FlatCritChanceMod": 40.0,        # Cloak = 600g / 15% (stored as 0.15, so multiply by 100)
    "FlatMovementSpeedMod": 12.0,     # Boots = 300g / 25 MS
    "PercentMovementSpeedMod": 39.5,  # Stored as a decimal (0.05 means 5%)
}

# Multipliers per champion class. Tune these with your game knowledge.
ROLE_WEIGHTS = {
    "Marksman": {"damage": 1.0, "attack_speed": 1.2, "crit": 1.2, "health": 0.4, "resist": 0.6, "move": 0.5, "haste": 0.3},
    "Fighter":  {"damage": 1.0, "attack_speed": 0.7, "crit": 0.3, "health": 1.0, "resist": 1.0, "move": 0.8, "haste": 1.2},
    "Tank":     {"damage": 0.4, "attack_speed": 0.1, "crit": 0.0, "health": 1.4, "resist": 1.3, "move": 0.5, "haste": 1.0},
    "Mage":     {"damage": 1.0, "attack_speed": 0.0, "crit": 0.0, "health": 0.6, "resist": 0.7, "move": 0.5, "haste": 1.2},
    "Assassin": {"damage": 1.2, "attack_speed": 0.3, "crit": 0.3, "health": 0.6, "resist": 0.6, "move": 0.8, "haste": 1.0},
    "Support":  {"damage": 0.5, "attack_speed": 0.0, "crit": 0.0, "health": 1.0, "resist": 1.0, "move": 0.5, "haste": 1.0},
}

CLASS_STRENGTH = 1.0   # 1.0 = full class weights, lower = pulled toward neutral
STAT_GROUPS = ("damage", "attack_speed", "crit", "health", "resist", "move", "haste")
SOFTEN_GROUPS = ("damage", "health", "resist")
NEUTRAL = {key: 1.0 for key in STAT_GROUPS}

# How much the primary class counts vs the secondary (1.0 = primary only, 0.5 = equal)
PRIMARY_SHARE = 0.7

# Flat gold-equivalent bonus for items tagged AbilityHaste (rough stand-in)
HASTE_BONUS = 400

# HP above this on a single item counts at half value (diminishing returns)
HP_SOFT_CAP = 500

# Crit chance caps at 100%, so more crit items than this are wasted
MAX_CRIT_ITEMS = 4

BURST_BASE = 0.6         # weight with zero burst threats
BURST_PER_THREAT = 0.05  # added per burst threat
BURST_MAX = 0.9          # ceiling

def get_role_weights(tags: list) -> dict:
    known = [ROLE_WEIGHTS[t] for t in tags if t in ROLE_WEIGHTS]
    if not known:
        return NEUTRAL

    if len(known) == 1:
        blended = known[0]
    else:
        primary, secondary = known[0], known[1]
        blended = {
            key: PRIMARY_SHARE * primary[key] + (1 - PRIMARY_SHARE) * secondary[key]
            for key in STAT_GROUPS
        }

    # Pull every weight toward 1.0 (neutral)
    return {
        key: (1.0 + CLASS_STRENGTH * (blended[key] - 1.0)) if key in SOFTEN_GROUPS else blended[key]
        for key in STAT_GROUPS
    }

def burst_factor(profile) -> float:
    threats = getattr(profile, "burst_count", 0)
    return min(BURST_MAX, BURST_BASE + BURST_PER_THREAT * threats)

def score_item(
    item: dict,
    profile,
    my_ad_share: float,
    current_bonus_hp: float = 0.0,
    role: Optional[dict] = None,
) -> tuple:
    role = role or NEUTRAL
    stats = item.get("stats", {})
    gold_cost = item.get("gold", {}).get("total", 0)
    if gold_cost <= 0:
        return 0.0, ""

    my_ap_share = max(0.0, 1.0 - my_ad_share)

    # 1. Survivability scaling
    burst_weight = burst_factor(profile)
    hp_synergy = 1.0 + min(0.5, current_bonus_hp / 2000.0)

    # 2. Offensive scaling (off-type damage is heavily penalized)
    ad_weight = my_ad_share ** 1.3
    ap_weight = my_ap_share ** 1.3

    # Percentage stats are stored as decimals in Data Dragon
    attack_speed_pct = stats.get("PercentAttackSpeedMod", 0) * 100
    crit_pct = stats.get("FlatCritChanceMod", 0) * 100
    ms_pct = stats.get("PercentMovementSpeedMod", 0) * 100

    # Diminishing returns: HP past the soft cap on one item counts at half value
    hp = stats.get("FlatHPPoolMod", 0)
    if hp > HP_SOFT_CAP:
        hp = HP_SOFT_CAP + 0.5 * (hp - HP_SOFT_CAP)

    parts = [
        (
            stats.get("FlatArmorMod", 0) * STAT_VALUE["FlatArmorMod"]
            * profile.ad_share * hp_synergy * role["resist"],
            f"Counters heavy physical damage ({round(profile.ad_share * 100)}% AD)",
        ),
        (
            stats.get("FlatSpellBlockMod", 0) * STAT_VALUE["FlatSpellBlockMod"]
            * profile.ap_share * hp_synergy * role["resist"],
            f"Counters heavy magic damage ({round(profile.ap_share * 100)}% AP)",
        ),
        (
            hp * STAT_VALUE["FlatHPPoolMod"] * burst_weight * role["health"],
            f"Survives enemy burst ({getattr(profile, 'burst_count', 0)} burst threats)",
        ),
        (
            stats.get("FlatPhysicalDamageMod", 0) * STAT_VALUE["FlatPhysicalDamageMod"]
            * ad_weight * role["damage"],
            f"Scales your physical damage ({round(my_ad_share * 100)}% AD profile)",
        ),
        (
            stats.get("FlatMagicDamageMod", 0) * STAT_VALUE["FlatMagicDamageMod"]
            * ap_weight * role["damage"],
            f"Scales your magic damage ({round(my_ap_share * 100)}% AP profile)",
        ),
        (
            attack_speed_pct * STAT_VALUE["PercentAttackSpeedMod"]
            * ad_weight * role["attack_speed"],
            "Boosts sustained auto-attack DPS",
        ),
        (
            crit_pct * STAT_VALUE["FlatCritChanceMod"] * ad_weight * role["crit"],
            "Amplifies physical critical strike scaling",
        ),
        (
            (
                stats.get("FlatMovementSpeedMod", 0) * STAT_VALUE["FlatMovementSpeedMod"]
                + ms_pct * STAT_VALUE["PercentMovementSpeedMod"]
            ) * role["move"],
            "Improves kiting and map rotation speed",
        ),
        (
            HASTE_BONUS * role["haste"] if "AbilityHaste" in item.get("tags", []) else 0,
            "Ability haste for more frequent spells",
        ),
    ]

    raw_weighted_gold = sum(points for points, _ in parts)

    # 3. Blend raw power (70%) with gold efficiency (30%)
    efficiency_ratio = raw_weighted_gold / gold_cost
    final_score = raw_weighted_gold * (0.7 + 0.3 * efficiency_ratio)

    best_part = max(parts, key=lambda p: p[0])
    reason = best_part[1] if best_part[0] > 0 else "Balanced utility stats"
    return final_score, reason


def recommend_build(
    items: dict,
    profile,
    my_ad_share: float,
    n: int = 6,
    completed_only: bool = True,
    owned_ids: Optional[set] = None,
    my_tags: Optional[list] = None,
) -> list:
    role = get_role_weights(my_tags or [])
    owned_ids = owned_ids or set()
    scored = []
    seen_names = set()

    # Estimate current bonus HP from owned items to scale resistance value
    current_bonus_hp = sum(
        items[i]["stats"].get("FlatHPPoolMod", 0) for i in owned_ids if i in items
    )

    for item_id, item in items.items():
        if item_id in owned_ids:
            continue

        gold_info = item.get("gold", {})
        if not gold_info.get("purchasable", True):
            continue
        if completed_only and item.get("into"):
            continue

        name = item.get("name", "")
        if name in seen_names:
            continue

        total, reason = score_item(item, profile, my_ad_share, current_bonus_hp, role)
        if total > 0:
            scored.append({
                "id": item_id,
                "item": item,
                "score": round(total),
                "efficiency": round((total / max(1, gold_info.get("total", 1))) * 100),
                "reason": reason,
            })
            seen_names.add(name)

    scored.sort(key=lambda s: s["score"], reverse=True)

        # At most one pair of boots and at most MAX_CRIT_ITEMS crit items
    has_boots = False
    crit_count = 0
    final_build = []
    for entry in scored:
        item = entry["item"]
        is_boots = "Boots" in item.get("tags", [])
        is_crit = (
            item.get("stats", {}).get("FlatCritChanceMod", 0) > 0
            or "CriticalStrike" in item.get("tags", [])
        )

        if is_boots and has_boots:
            continue
        if is_crit and crit_count >= MAX_CRIT_ITEMS:
            continue

        if is_boots:
            has_boots = True
        if is_crit:
            crit_count += 1

        final_build.append(entry)
        if len(final_build) == n:
            break

    return final_build