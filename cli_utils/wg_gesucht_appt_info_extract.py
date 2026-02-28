from bs4 import BeautifulSoup
import requests
import argparse
import re
import sys
from pathlib import Path


def fetch_html(url: str) -> str:
    """Fetch the HTML content of a WG-Gesucht listing."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def clean(text: str) -> str:
    """Collapse whitespace and strip a string."""
    return re.sub(r"\s+", " ", text).strip()


def extract_listing_info(soup: BeautifulSoup) -> dict:
    """Extract key apartment listing fields from parsed HTML."""
    info: dict[str, object] = {}

    # --- Titel ---
    title_tag = soup.find("h1", class_="detailed-view-title")
    if title_tag:
        info["Titel"] = clean(title_tag.get_text())

    # --- Größe & Gesamtmiete (key facts in section_footer_dark) ---
    for span in soup.find_all("span", class_="key_fact_detail"):
        label = clean(span.get_text())
        value_tag = span.find_next("b", class_="key_fact_value")
        if value_tag:
            info[label] = clean(value_tag.get_text())

    # --- Kosten section (Miete, Nebenkosten, Kaution, etc.) ---
    kosten_heading = soup.find(
        "h2", class_="section_panel_title", string=re.compile(r"Kosten")
    )
    if kosten_heading:
        kosten_panel = kosten_heading.find_parent("div", class_="section_panel")
        if kosten_panel:
            kosten_items: list[str] = []
            seen_labels: set[str] = set()
            # First pass: span-based detail/value pairs (Miete, Nebenkosten, etc.)
            for row in kosten_panel.find_all("div", class_="row", recursive=True):
                detail = row.find("span", class_="section_panel_detail")
                value = row.find("span", class_="section_panel_value")
                if detail and value:
                    label = clean(detail.get_text())
                    if label not in seen_labels:
                        seen_labels.add(label)
                        kosten_items.append(
                            f"  {label} {clean(value.get_text())}"
                        )
            # Second pass: link-based details (e.g. SCHUFA-Auskunft)
            for row in kosten_panel.find_all("div", class_="row", recursive=True):
                detail_a = row.find("a", class_="section_panel_detail")
                if detail_a:
                    label = clean(detail_a.get_text())
                    if label not in seen_labels:
                        seen_labels.add(label)
                        value_col = detail_a.find_parent("div").find_next_sibling("div")
                        if value_col:
                            val_text = clean(value_col.get_text())
                            kosten_items.append(f"  {label} {val_text}")
            if kosten_items:
                info["Kosten"] = "\n".join(kosten_items)

    # --- Adresse ---
    adresse_heading = soup.find(
        "h2", class_="section_panel_title", string=re.compile(r"Adresse")
    )
    if adresse_heading:
        addr_container = adresse_heading.find_next("span", class_="section_panel_detail")
        if addr_container:
            info["Adresse"] = clean(addr_container.get_text())

    # --- Verfügbarkeit (frei ab / frei bis) ---
    verfuegbar_heading = soup.find(
        "h2", class_="section_panel_title", string=re.compile(r"Verfügbarkeit")
    )
    if verfuegbar_heading:
        container = verfuegbar_heading.find_parent("div", class_="col-xs-12 col-sm-6") or \
                    verfuegbar_heading.find_parent("div")
        if container:
            avail_items: list[str] = []
            for row in container.find_all("div", class_="row"):
                detail = row.find("span", class_="section_panel_detail")
                value = row.find("span", class_="section_panel_value")
                if detail and value:
                    avail_items.append(
                        f"  {clean(detail.get_text())} {clean(value.get_text())}"
                    )
            if avail_items:
                info["Verfügbarkeit"] = "\n".join(avail_items)

    # --- Online seit ---
    online_label = soup.find(
        "span", class_="section_panel_detail", string=re.compile(r"Online")
    )
    if online_label:
        online_value = online_label.find_next("b")
        if online_value:
            info["Online seit"] = clean(online_value.get_text())
    else:
        # Fallback: look in the Verfügbarkeit area for "Online:" label
        online_label_alt = soup.find(
            "span", class_=re.compile(r"section_panel_detail"),
            string=re.compile(r"Online")
        )
        if online_label_alt:
            online_val = online_label_alt.find_next("b")
            if online_val:
                info["Online seit"] = clean(online_val.get_text())

    # --- Beschreibung (section_panel_tabs: Wohnung, Lage, Sonstiges, …) ---
    tabs_div = soup.find("div", class_="section_panel_tabs")
    if tabs_div:
        tab_names: list[str] = []
        for tab in tabs_div.find_all("div", class_="section_panel_tab"):
            h2 = tab.find("h2")
            if h2:
                tab_names.append(clean(h2.get_text()))

        desc_div = soup.find("div", id="ad_description_text")
        if desc_div:
            sections: list[str] = []
            for idx, freitext in enumerate(
                desc_div.find_all("div", class_="section_freetext")
            ):
                heading = tab_names[idx] if idx < len(tab_names) else f"Abschnitt {idx + 1}"
                body = clean(freitext.get_text())
                if body:
                    sections.append(f"  [{heading}]\n  {body}")
            if sections:
                info["Beschreibung"] = "\n\n".join(sections)

    # --- Angaben zum Objekt ---
    objekt_heading = soup.find(
        "h2", class_="section_panel_title", string=re.compile(r"Angaben zum Objekt")
    )
    if objekt_heading:
        icons_div = objekt_heading.find_next("div", class_="utility_icons")
        if icons_div:
            items: list[str] = []
            for icon_div in icons_div.find_all("div", class_="text-center"):
                text = clean(icon_div.get_text())
                if text:
                    items.append(f"  - {text}")
            if items:
                info["Angaben zum Objekt"] = "\n".join(items)

    # --- Benötigte Unterlagen ---
    unterlagen_heading = soup.find(
        "h2", class_="section_panel_title", string=re.compile(r"Benötigte Unterlagen")
    )
    if unterlagen_heading:
        panel = unterlagen_heading.find_parent("div", class_="section_panel")
        if panel:
            docs: list[str] = []
            for badge in panel.find_all("a", class_=re.compile(r"wgg_badge")):
                b_tag = badge.find("b")
                if b_tag:
                    docs.append(f"  - {clean(b_tag.get_text())}")
            # Pick up plain text badges too (non-link)
            for badge in panel.find_all("span", class_=re.compile(r"wgg_badge")):
                b_tag = badge.find("b")
                if b_tag:
                    docs.append(f"  - {clean(b_tag.get_text())}")
            if docs:
                info["Benötigte Unterlagen"] = "\n".join(docs)

    return info


def format_output(info: dict, url: str) -> str:
    """Format extracted info as readable text."""
    lines: list[str] = []
    lines.append(f"URL: {url}")
    lines.append("=" * 60)

    # Ordered keys for consistent output
    ordered_keys = [
        "Titel",
        "Größe",
        "Gesamtmiete",
        "Kosten",
        "Adresse",
        "Verfügbarkeit",
        "Online seit",
        "Beschreibung",
        "Angaben zum Objekt",
        "Benötigte Unterlagen",
    ]

    printed: set[str] = set()
    for key in ordered_keys:
        if key in info:
            lines.append("")
            lines.append(f"{key}:")
            lines.append(f"{info[key]}")
            printed.add(key)

    # Any remaining keys not in the ordered list
    for key, value in info.items():
        if key not in printed:
            lines.append("")
            lines.append(f"{key}:")
            lines.append(f"{value}")

    lines.append("")
    return "\n".join(lines)


def default_output_filename(url: str) -> str:
    """Derive a default output filename from the listing URL."""
    # Extract the numeric ad ID from the URL (e.g. 13046425)
    match = re.search(r"\.(\d+)\.html", url)
    if match:
        return f"wg_gesucht_{match.group(1)}.txt"
    return "wg_gesucht_listing.txt"


def main():
    parser = argparse.ArgumentParser(
        description="Extract apartment listing info from a WG-Gesucht URL."
    )
    parser.add_argument("url", help="URL of the WG-Gesucht apartment listing")
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: wg_gesucht_<ID>.txt in current directory)",
        default=None,
    )
    args = parser.parse_args()

    url: str = args.url
    output_path: str = args.output or default_output_filename(url)

    print(f"Fetching {url} ...")
    try:
        html = fetch_html(url)
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")
    info = extract_listing_info(soup)

    if not info:
        print("Warning: no listing data could be extracted.", file=sys.stderr)

    text = format_output(info, url)

    Path(output_path).write_text(text, encoding="utf-8")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()

