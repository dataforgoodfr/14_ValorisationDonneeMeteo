#!/usr/bin/env python3
"""
Convert Trivy JSON output into a minimal OpenVEX document.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _now_rfc3339() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _iter_vulns(trivy: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    """
    Yield (target, vulnerability_obj) from Trivy JSON.
    """
    for res in trivy.get("Results", []) or []:
        target = res.get("Target") or "unknown"
        for v in res.get("Vulnerabilities", []) or []:
            yield target, v


def _product_to_purl(product: str) -> str:
    """
    Best-effort mapping to a PURL identifier (container images => pkg:docker).
    """
    # product like "ghcr.io/org/repo/backend:sha"
    if "://" in product:
        product = product.split("://", 1)[1]
    return f"pkg:docker/{product}"


def _pkg_to_purl(vuln: Dict[str, Any]) -> Optional[str]:
    """
    Best-effort mapping to purl.
    """
    name = vuln.get("PkgName") or vuln.get("PackageName")
    ver = vuln.get("InstalledVersion")
    if not name:
        return None
    if ver:
        return f"pkg:generic/{name}@{ver}"
    return f"pkg:generic/{name}"


def _openvex_statement(
    *,
    vuln_id: str,
    product_purl: str,
    component_purl: Optional[str],
    status: str,
    summary: Optional[str],
    url: Optional[str],
) -> Dict[str, Any]:
    products: List[Dict[str, Any]] = [{"@id": product_purl}]
    if component_purl:
        products.append({"@id": component_purl})

    statement: Dict[str, Any] = {
        "vulnerability": {"name": vuln_id},
        "products": products,
        "status": status,
    }

    if summary or url:
        note_parts = []
        if summary:
            note_parts.append(summary.strip())
        if url:
            note_parts.append(f"Info: {url}")
        statement["impact_statement"] = " | ".join(note_parts)

    return statement


def trivy_json_to_openvex(trivy: Dict[str, Any], *, product: str) -> Dict[str, Any]:
    product_purl = _product_to_purl(product)

    statements: List[Dict[str, Any]] = []
    for _target, v in _iter_vulns(trivy):
        vuln_id = v.get("VulnerabilityID") or v.get("ID") or "UNKNOWN"
        primary_url = v.get("PrimaryURL")
        title = v.get("Title") or v.get("Description")
        component_purl = _pkg_to_purl(v)

        statements.append(
            _openvex_statement(
                vuln_id=str(vuln_id),
                product_purl=product_purl,
                component_purl=component_purl,
                status="affected",
                summary=title,
                url=primary_url,
            )
        )

    doc: Dict[str, Any] = {
        "@context": "https://openvex.dev/ns/v0.2.0",
        "@id": f"urn:uuid:{uuid.uuid4()}",
        "author": "BotanESGI/14_ValorisationDonneeMeteo",
        "timestamp": _now_rfc3339(),
        "version": 1,
        "statements": statements,
    }
    return doc


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--trivy-json", required=True, help="Path to Trivy JSON output")
    p.add_argument("--product", required=True, help="Scanned product (e.g. image:tag)")
    p.add_argument("--out", required=True, help="Output OpenVEX JSON path")
    args = p.parse_args(argv)

    trivy = _load_json(args.trivy_json)
    openvex = trivy_json_to_openvex(trivy, product=args.product)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(openvex, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

