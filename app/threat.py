from app.models import ThreatProfile
from app.tags import BURST_MAGES


def build_threat_profile(enemies: list, champs: dict) -> ThreatProfile:
    total_ad = 0
    total_ap = 0
    tank_count = 0
    burst_count = 0

    for enemy in enemies:
        champ = champs[enemy["champion"]]
        info = champ["info"]

        # fed enemies count more; never go below 1
        weight = max(1, 1 + enemy["kills"] - enemy["deaths"])

        total_ad += info["attack"] * weight
        total_ap += info["magic"] * weight

        if "Tank" in champ["tags"]:
            tank_count += 1

        if "Assassin" in champ["tags"] or enemy["champion"] in BURST_MAGES:
            burst_count += 1

    total = total_ad + total_ap
    if total == 0:
        ad_share = 0.5
        ap_share = 0.5
    else:
        ad_share = total_ad / total
        ap_share = total_ap / total

    return ThreatProfile(
        ad_share=ad_share,
        ap_share=ap_share,
        tank_count=tank_count,
        burst_count=burst_count,
    )