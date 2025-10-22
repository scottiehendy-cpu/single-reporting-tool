def shape_for_destination(dest: str, payload: dict) -> dict:
    dest = (dest or "").strip().lower()
    if dest == "acsc":
        return _shape_acsc(payload)
    if dest == "homeaffairs":
        return _shape_home_affairs(payload)
    if dest == "oaic":
        return _shape_oaic(payload)
    if dest in ("apra", "asic", "rba", "tga", "accc/cdr", "accc", "cdr"):
        return _shape_generic(payload, dest.upper())
    return {"destination": dest, "payload": payload}

def _pick(d: dict, keys: list): return {k: d.get(k) for k in keys}

def _shape_acsc(p: dict) -> dict:
    return {
        "destination": "ACSC",
        "reporter": _pick(p.get("reporter", {}), ["first_name","surname","email","phone"]),
        "organisation": _pick(p.get("organisation", {}), ["name","abn","jurisdiction","postcode","country","address"]),
        "purpose": p.get("purpose", {}),
        "incident": p.get("incident", {}),
        "ransomware": p.get("ransomware"),
    }

def _shape_home_affairs(p: dict) -> dict:
    purpose = p.get("purpose", {})
    return {
        "destination": "Home Affairs",
        "ci_member": purpose.get("ci_member"),
        "ci_sectors": purpose.get("ci_sectors", []),
        "consent_home_affairs": purpose.get("consent_home_affairs"),
        "reporter": p.get("reporter", {}),
        "organisation": p.get("organisation", {}),
        "incident": p.get("incident", {}),
        "ransomware": p.get("ransomware"),
    }

def _shape_oaic(p: dict) -> dict:
    inc = p.get("incident", {})
    org = p.get("organisation", {})
    return {
        "destination": "OAIC",
        "organisation_name": org.get("name"),
        "jurisdiction": org.get("jurisdiction"),
        "incident_type": inc.get("type"),
        "occurrence_date": inc.get("occurrence_date"),
        "identified_date": inc.get("identified_date"),
        "narrative": inc.get("narrative"),
        "customers_impacted": inc.get("customers_impacted"),
    }

def _shape_generic(p: dict, label: str) -> dict:
    return {"destination": label, "payload": p}
