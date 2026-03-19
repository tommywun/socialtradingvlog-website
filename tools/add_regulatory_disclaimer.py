#!/usr/bin/env python3
"""
Add bilingual regulatory disclaimer to all non-English pages.
Inserts after the existing footer-disclaimer paragraph.
Idempotent — skips files that already contain the marker class.
"""

import pathlib
import re
import sys

BASE = pathlib.Path(__file__).parent.parent

LANG_DIRS = ["ar", "de", "es", "fr", "it", "ko", "nl", "pl", "pt"]

TRANSLATIONS = {
    "ar": "قد تكون المحتويات المقدمة مترجمة وقد لا تكون مُصمَّمة خصيصاً للمستخدمين في دولة معينة. قد تكون المنتجات والخدمات مقيّدة أو مُكيَّفة للامتثال للمتطلبات التنظيمية المحلية والولايات القضائية.",
    "de": "Die bereitgestellten Inhalte können übersetzt sein und sind möglicherweise nicht speziell auf Nutzer in einem bestimmten Land zugeschnitten. Produkte und Dienstleistungen können eingeschränkt oder angepasst sein, um lokale regulatorische Anforderungen und Rechtsprechungen einzuhalten.",
    "es": "El contenido proporcionado puede estar traducido y puede no estar específicamente adaptado para usuarios de un determinado país. Los productos y servicios pueden estar restringidos o adaptados para cumplir con los requisitos regulatorios locales y las jurisdicciones.",
    "fr": "Le contenu fourni peut être traduit et peut ne pas être spécifiquement adapté aux utilisateurs d'un pays donné. Les produits et services peuvent être restreints ou adaptés pour se conformer aux exigences réglementaires locales et aux juridictions.",
    "it": "Il contenuto fornito potrebbe essere tradotto e potrebbe non essere specificamente personalizzato per gli utenti di un determinato paese. I prodotti e i servizi potrebbero essere limitati o adattati per conformarsi ai requisiti normativi locali e alle giurisdizioni.",
    "ko": "제공된 콘텐츠는 번역된 것일 수 있으며 특정 국가의 사용자를 위해 특별히 맞춤화되지 않았을 수 있습니다. 제품 및 서비스는 현지 규정 요건 및 관할권을 준수하기 위해 제한되거나 조정될 수 있습니다.",
    "nl": "De verstrekte inhoud kan vertaald zijn en is mogelijk niet specifiek afgestemd op gebruikers in een bepaald land. Producten en diensten kunnen beperkt of aangepast zijn om te voldoen aan lokale wettelijke vereisten en jurisdicties.",
    "pl": "Dostarczone treści mogą być tłumaczone i mogą nie być specjalnie dostosowane dla użytkowników w określonym kraju. Produkty i usługi mogą być ograniczone lub dostosowane w celu spełnienia lokalnych wymogów regulacyjnych i jurysdykcji.",
    "pt": "O conteúdo fornecido pode estar traduzido e pode não ser especificamente adaptado para utilizadores de um determinado país. Os produtos e serviços podem ser restritos ou adaptados para cumprir os requisitos regulatórios locais e as jurisdições.",
}

RTL_LANGS = {"ar"}

ENGLISH_TEXT = (
    "The content provided may be translated and may not be specifically tailored "
    "for users in a certain country. Products and services may be restricted or "
    "adapted to comply with local regulatory requirements and jurisdictions."
)

MARKER = "regulatory-disclaimer"

# Regex: match the footer-disclaimer paragraph (article pages)
FOOTER_DISCLAIMER_RE = re.compile(
    r'(<p class="footer-disclaimer">.*?</p>)',
    re.DOTALL,
)

# Regex: match the opening of tool-footer div (calculator pages)
TOOL_FOOTER_RE = re.compile(
    r'(<div class="tool-footer">)',
)


def build_block(lang: str, indent: str = "      ") -> str:
    translation = TRANSLATIONS[lang]
    rtl = ' dir="rtl"' if lang in RTL_LANGS else ""
    return (
        f'\n{indent}<div class="risk-warning {MARKER}" style="margin-top:16px;font-size:0.82rem;"{rtl}>\n'
        f'{indent}  <p>"{ENGLISH_TEXT}"</p>\n'
        f'{indent}  <p>"{translation}"</p>\n'
        f'{indent}</div>'
    )


def process_file(path: pathlib.Path, lang: str, dry_run: bool = False) -> str:
    """Returns 'skipped', 'modified', or 'no_anchor'."""
    content = path.read_text(encoding="utf-8")

    if MARKER in content:
        return "skipped"

    # Try article footer first
    match = FOOTER_DISCLAIMER_RE.search(content)
    if match:
        block = build_block(lang, indent="      ")
        new_content = content[: match.end()] + block + content[match.end() :]
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        return "modified"

    # Fallback: calculator tool-footer — insert block BEFORE the div
    match = TOOL_FOOTER_RE.search(content)
    if match:
        block = build_block(lang, indent="  ")
        new_content = content[: match.start()] + block + "\n\n  " + content[match.start() :]
        if not dry_run:
            path.write_text(new_content, encoding="utf-8")
        return "modified"

    return "no_anchor"


def main(dry_run: bool = False):
    counts = {lang: {"modified": 0, "skipped": 0, "no_anchor": 0} for lang in LANG_DIRS}

    for lang in LANG_DIRS:
        lang_dir = BASE / lang
        if not lang_dir.exists():
            print(f"  [{lang}] directory not found — skipping")
            continue
        files = sorted(lang_dir.rglob("*.html"))
        for f in files:
            result = process_file(f, lang, dry_run=dry_run)
            counts[lang][result] += 1

    print("\n=== Results ===")
    total_modified = 0
    total_skipped = 0
    total_no_anchor = 0
    for lang in LANG_DIRS:
        c = counts[lang]
        total_modified += c["modified"]
        total_skipped += c["skipped"]
        total_no_anchor += c["no_anchor"]
        print(
            f"  {lang}: {c['modified']} modified, {c['skipped']} skipped, {c['no_anchor']} no_anchor"
        )
    print(f"\nTotal: {total_modified} modified, {total_skipped} skipped, {total_no_anchor} no_anchor")
    if dry_run:
        print("(DRY RUN — no files written)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
