#!/usr/bin/env python3
"""
Generate translated SEO-optimised video landing pages.

Creates /{lang}/video/SLUG/index.html for each language with:
  - Full translated article content
  - Localised SEO (keyphrase, meta description, h1, FAQs)
  - Hreflang tags linking all language variants
  - Same template structure as English pages
  - Correct asset paths (3 levels deep)

Usage:
    python3 tools/generate_translated_pages.py              # generate all
    python3 tools/generate_translated_pages.py --lang es     # Spanish only
    python3 tools/generate_translated_pages.py --force       # regenerate
"""

import sys
import os
import re
import html
import json
import pathlib
import argparse

BASE_DIR = pathlib.Path(__file__).parent.parent

# ── Asset prefix for translated pages (3 levels deep: /es/video/slug/) ────────
ASSET_PREFIX = "../../../"

# ── Base URL ──────────────────────────────────────────────────────────────────
BASE_URL = "https://socialtradingvlog.com"

# ── Translated UI strings per language ────────────────────────────────────────
UI_STRINGS = {
    "es": {
        "social_trading": "Trading Social",
        "copy_trading": "Copy Trading",
        "updates": "Novedades",
        "videos": "Vídeos",
        "about": "Sobre nosotros",
        "faq": "Preguntas frecuentes",
        "try_etoro": "Prueba eToro",
        "in_this_article": "En este artículo",
        "prefer_reading": "¿Prefieres leer? La transcripción completa está abajo.",
        "watch_on_youtube": "Ver en YouTube con subtítulos",
        "risk_warning_label": "Advertencia de riesgo",
        "risk_warning_banner": "Advertencia de riesgo: el 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Tu capital está en riesgo.",
        "risk_warning_full": "eToro es una plataforma de inversión multi-activos. El valor de tus inversiones puede subir o bajar. El 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Deberías considerar si puedes permitirte asumir el alto riesgo de perder tu dinero.",
        "risk_warning_footer": "Tu capital está en riesgo. El 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Este sitio web es solo para fines educativos e informativos y no constituye asesoramiento de inversión. El Copy Trading no equivale a asesoramiento de inversión.",
        "risk_warning_sidebar": "El 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Deberías considerar si puedes permitirte asumir el alto riesgo de perder tu dinero. Este es un enlace de afiliado — Tom puede ganar una comisión sin coste para ti.",
        "important_reminder": "Recordatorio importante",
        "important_reminder_text": "El 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Deberías considerar si puedes permitirte asumir el alto riesgo de perder tu dinero. El rendimiento pasado no es indicación de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversión.",
        "ready_to_try": "¿Listo para probar eToro?",
        "toms_affiliate": "Tom lleva en eToro desde 2017. Aquí está su enlace de afiliado.",
        "explore_etoro": "Explorar eToro →",
        "ready_cta_inline": "¿Listo para probar eToro? — Enlace de afiliado de Tom.",
        "more_guides": "Más guías",
        "guide_social": "¿Qué es el Trading Social?",
        "guide_copy": "¿Qué es el Copy Trading?",
        "guide_returns": "¿Cuánto puedes ganar?",
        "guide_scam": "¿Es eToro una estafa?",
        "guide_profits": "Tomar ganancias",
        "guide_pi": "Programa Popular Investor",
        "guide_all_videos": "Todos los vídeos",
        "footer_brand": "Documentando el viaje del copy trading desde 2017. Independiente, honesto y siempre aprendiendo.",
        "footer_guides": "Guías",
        "footer_site": "Sitio",
        "footer_updates": "Actualizaciones de trading",
        "footer_about": "Sobre nosotros",
        "footer_faq": "Preguntas frecuentes",
        "footer_contact": "Contacto",
        "home": "Inicio",
        "faq_heading": "Preguntas frecuentes",
        "by_tom": "Por Tom",
        "breadcrumb_home": "Inicio",
        "breadcrumb_videos": "Vídeos",
    },
    "de": {
        "social_trading": "Social Trading",
        "copy_trading": "Copy Trading",
        "updates": "Updates",
        "videos": "Videos",
        "about": "Über uns",
        "faq": "FAQ",
        "try_etoro": "eToro testen",
        "in_this_article": "In diesem Artikel",
        "prefer_reading": "Lieber lesen? Die vollständige Transkription findest du unten.",
        "watch_on_youtube": "Auf YouTube mit Untertiteln ansehen",
        "risk_warning_label": "Risikohinweis",
        "risk_warning_banner": "Risikohinweis: 51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Ihr Kapital ist gefährdet.",
        "risk_warning_full": "eToro ist eine Multi-Asset-Investmentplattform. Der Wert Ihrer Investitionen kann steigen oder fallen. 51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Sie sollten abwägen, ob Sie es sich leisten können, das hohe Risiko einzugehen, Ihr Geld zu verlieren.",
        "risk_warning_footer": "Ihr Kapital ist gefährdet. 51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Diese Website dient nur zu Bildungs- und Informationszwecken und stellt keine Anlageberatung dar. Copy Trading stellt keine Anlageberatung dar.",
        "risk_warning_sidebar": "51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Sie sollten abwägen, ob Sie es sich leisten können, das hohe Risiko einzugehen, Ihr Geld zu verlieren. Dies ist ein Affiliate-Link — Tom kann eine Provision erhalten, ohne Kosten für Sie.",
        "important_reminder": "Wichtiger Hinweis",
        "important_reminder_text": "51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Sie sollten abwägen, ob Sie es sich leisten können, das hohe Risiko einzugehen, Ihr Geld zu verlieren. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Ergebnisse. Dieser Inhalt dient nur zu Bildungszwecken und stellt keine Anlageberatung dar.",
        "ready_to_try": "Bereit, eToro auszuprobieren?",
        "toms_affiliate": "Tom ist seit 2017 auf eToro. Hier ist sein Affiliate-Link.",
        "explore_etoro": "eToro entdecken →",
        "ready_cta_inline": "Bereit, eToro auszuprobieren? — Toms Affiliate-Link.",
        "more_guides": "Weitere Anleitungen",
        "guide_social": "Was ist Social Trading?",
        "guide_copy": "Was ist Copy Trading?",
        "guide_returns": "Wie viel kann man verdienen?",
        "guide_scam": "Ist eToro Betrug?",
        "guide_profits": "Gewinne mitnehmen",
        "guide_pi": "Popular Investor Programm",
        "guide_all_videos": "Alle Videos",
        "footer_brand": "Dokumentiert die Copy-Trading-Reise seit 2017. Unabhängig, ehrlich und immer lernend.",
        "footer_guides": "Anleitungen",
        "footer_site": "Seite",
        "footer_updates": "Trading-Updates",
        "footer_about": "Über uns",
        "footer_faq": "FAQ",
        "footer_contact": "Kontakt",
        "home": "Startseite",
        "faq_heading": "Häufig gestellte Fragen",
        "by_tom": "Von Tom",
        "breadcrumb_home": "Startseite",
        "breadcrumb_videos": "Videos",
    },
    "fr": {
        "social_trading": "Trading Social",
        "copy_trading": "Copy Trading",
        "updates": "Actualités",
        "videos": "Vidéos",
        "about": "À propos",
        "faq": "FAQ",
        "try_etoro": "Essayer eToro",
        "in_this_article": "Dans cet article",
        "prefer_reading": "Tu préfères lire ? La transcription complète est ci-dessous.",
        "watch_on_youtube": "Regarder sur YouTube avec sous-titres",
        "risk_warning_label": "Avertissement sur les risques",
        "risk_warning_banner": "Avertissement sur les risques : 51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils tradent des CFD avec eToro. Votre capital est exposé à un risque.",
        "risk_warning_full": "eToro est une plateforme d'investissement multi-actifs. La valeur de vos investissements peut augmenter ou diminuer. 51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils tradent des CFD avec eToro. Vous devriez considérer si vous pouvez vous permettre de prendre le risque élevé de perdre votre argent.",
        "risk_warning_footer": "Votre capital est exposé à un risque. 51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils tradent des CFD avec eToro. Ce site web est à des fins éducatives et informatives uniquement et ne constitue pas un conseil en investissement. Le Copy Trading ne constitue pas un conseil en investissement.",
        "risk_warning_sidebar": "51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils tradent des CFD avec eToro. Vous devriez considérer si vous pouvez vous permettre de prendre le risque élevé de perdre votre argent. Ceci est un lien d'affiliation — Tom peut recevoir une commission sans frais pour vous.",
        "important_reminder": "Rappel important",
        "important_reminder_text": "51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils tradent des CFD avec eToro. Vous devriez considérer si vous pouvez vous permettre de prendre le risque élevé de perdre votre argent. Les performances passées ne préjugent pas des résultats futurs. Ce contenu est à des fins éducatives uniquement et ne constitue pas un conseil en investissement.",
        "ready_to_try": "Prêt à essayer eToro ?",
        "toms_affiliate": "Tom est sur eToro depuis 2017. Voici son lien d'affiliation.",
        "explore_etoro": "Découvrir eToro →",
        "ready_cta_inline": "Prêt à essayer eToro ? — Lien d'affiliation de Tom.",
        "more_guides": "Plus de guides",
        "guide_social": "Qu'est-ce que le Trading Social ?",
        "guide_copy": "Qu'est-ce que le Copy Trading ?",
        "guide_returns": "Combien peut-on gagner ?",
        "guide_scam": "eToro est-il une arnaque ?",
        "guide_profits": "Prendre ses bénéfices",
        "guide_pi": "Programme Popular Investor",
        "guide_all_videos": "Toutes les vidéos",
        "footer_brand": "Documenter le parcours du copy trading depuis 2017. Indépendant, honnête et toujours en apprentissage.",
        "footer_guides": "Guides",
        "footer_site": "Site",
        "footer_updates": "Mises à jour trading",
        "footer_about": "À propos",
        "footer_faq": "FAQ",
        "footer_contact": "Contact",
        "home": "Accueil",
        "faq_heading": "Questions fréquentes",
        "by_tom": "Par Tom",
        "breadcrumb_home": "Accueil",
        "breadcrumb_videos": "Vidéos",
    },
    "pt": {
        "social_trading": "Trading Social",
        "copy_trading": "Copy Trading",
        "updates": "Atualizações",
        "videos": "Vídeos",
        "about": "Sobre",
        "faq": "Perguntas frequentes",
        "try_etoro": "Experimente o eToro",
        "in_this_article": "Neste artigo",
        "prefer_reading": "Prefere ler? A transcrição completa está abaixo.",
        "watch_on_youtube": "Assistir no YouTube com legendas",
        "risk_warning_label": "Aviso de risco",
        "risk_warning_banner": "Aviso de risco: 51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com o eToro. Seu capital está em risco.",
        "risk_warning_full": "eToro é uma plataforma de investimento multi-ativos. O valor dos seus investimentos pode subir ou descer. 51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com o eToro. Você deve considerar se pode se dar ao luxo de assumir o alto risco de perder seu dinheiro.",
        "risk_warning_footer": "Seu capital está em risco. 51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com o eToro. Este site é apenas para fins educacionais e informativos e não constitui aconselhamento de investimento. O Copy Trading não constitui aconselhamento de investimento.",
        "risk_warning_sidebar": "51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com o eToro. Você deve considerar se pode se dar ao luxo de assumir o alto risco de perder seu dinheiro. Este é um link de afiliado — Tom pode receber uma comissão sem custo para você.",
        "important_reminder": "Lembrete importante",
        "important_reminder_text": "51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com o eToro. Você deve considerar se pode se dar ao luxo de assumir o alto risco de perder seu dinheiro. Desempenho passado não é indicação de resultados futuros. Este conteúdo é apenas para fins educacionais e não constitui aconselhamento de investimento.",
        "ready_to_try": "Pronto para experimentar o eToro?",
        "toms_affiliate": "Tom está no eToro desde 2017. Aqui está seu link de afiliado.",
        "explore_etoro": "Explorar eToro →",
        "ready_cta_inline": "Pronto para experimentar o eToro? — Link de afiliado do Tom.",
        "more_guides": "Mais guias",
        "guide_social": "O que é Trading Social?",
        "guide_copy": "O que é Copy Trading?",
        "guide_returns": "Quanto você pode ganhar?",
        "guide_scam": "O eToro é golpe?",
        "guide_profits": "Realizando lucros",
        "guide_pi": "Programa Popular Investor",
        "guide_all_videos": "Todos os vídeos",
        "footer_brand": "Documentando a jornada do copy trading desde 2017. Independente, honesto e sempre aprendendo.",
        "footer_guides": "Guias",
        "footer_site": "Site",
        "footer_updates": "Atualizações de trading",
        "footer_about": "Sobre",
        "footer_faq": "Perguntas frequentes",
        "footer_contact": "Contato",
        "home": "Início",
        "faq_heading": "Perguntas frequentes",
        "by_tom": "Por Tom",
        "breadcrumb_home": "Início",
        "breadcrumb_videos": "Vídeos",
    },
    "ar": {
        "social_trading": "التداول الاجتماعي",
        "copy_trading": "نسخ التداول",
        "updates": "تحديثات",
        "videos": "فيديوهات",
        "about": "عن الموقع",
        "faq": "أسئلة شائعة",
        "try_etoro": "جرّب eToro",
        "in_this_article": "في هذا المقال",
        "prefer_reading": "تفضّل القراءة؟ النص الكامل أدناه.",
        "watch_on_youtube": "شاهد على يوتيوب مع ترجمة",
        "risk_warning_label": "تحذير المخاطر",
        "risk_warning_banner": "تحذير المخاطر: 51% من حسابات المستثمرين الأفراد تخسر أموالها عند تداول عقود الفروقات مع eToro. رأس مالك في خطر.",
        "risk_warning_full": "eToro هي منصة استثمار متعددة الأصول. قد ترتفع أو تنخفض قيمة استثماراتك. 51% من حسابات المستثمرين الأفراد تخسر أموالها عند تداول عقود الفروقات مع eToro. يجب أن تفكر فيما إذا كنت تستطيع تحمّل المخاطر العالية لخسارة أموالك.",
        "risk_warning_footer": "رأس مالك في خطر. 51% من حسابات المستثمرين الأفراد تخسر أموالها عند تداول عقود الفروقات مع eToro. هذا الموقع لأغراض تعليمية ومعلوماتية فقط ولا يشكل نصيحة استثمارية. نسخ التداول لا يعتبر نصيحة استثمارية.",
        "risk_warning_sidebar": "51% من حسابات المستثمرين الأفراد تخسر أموالها عند تداول عقود الفروقات مع eToro. يجب أن تفكر فيما إذا كنت تستطيع تحمّل المخاطر العالية لخسارة أموالك. هذا رابط تابع — قد يحصل توم على عمولة دون أي تكلفة عليك.",
        "important_reminder": "تذكير مهم",
        "important_reminder_text": "51% من حسابات المستثمرين الأفراد تخسر أموالها عند تداول عقود الفروقات مع eToro. يجب أن تفكر فيما إذا كنت تستطيع تحمّل المخاطر العالية لخسارة أموالك. الأداء السابق ليس مؤشراً على النتائج المستقبلية. هذا المحتوى لأغراض تعليمية فقط وليس نصيحة استثمارية.",
        "ready_to_try": "مستعد لتجربة eToro؟",
        "toms_affiliate": "توم على eToro منذ 2017. إليك رابطه التابع.",
        "explore_etoro": "استكشف eToro ←",
        "ready_cta_inline": "مستعد لتجربة eToro؟ — رابط توم التابع.",
        "more_guides": "المزيد من الأدلة",
        "guide_social": "ما هو التداول الاجتماعي؟",
        "guide_copy": "ما هو نسخ التداول؟",
        "guide_returns": "كم يمكنك أن تربح؟",
        "guide_scam": "هل eToro احتيال؟",
        "guide_profits": "جني الأرباح",
        "guide_pi": "برنامج المستثمر الشعبي",
        "guide_all_videos": "جميع الفيديوهات",
        "footer_brand": "نوثّق رحلة نسخ التداول منذ 2017. مستقل، صادق، ودائماً نتعلم.",
        "footer_guides": "أدلة",
        "footer_site": "الموقع",
        "footer_updates": "تحديثات التداول",
        "footer_about": "عن الموقع",
        "footer_faq": "أسئلة شائعة",
        "footer_contact": "اتصل بنا",
        "home": "الرئيسية",
        "faq_heading": "أسئلة شائعة",
        "by_tom": "بقلم توم",
        "breadcrumb_home": "الرئيسية",
        "breadcrumb_videos": "فيديوهات",
    },
}

# ── Translation data directory ────────────────────────────────────────────────
TRANSLATIONS_DIR = pathlib.Path(__file__).parent / "translations"

def load_translations_from_json(video_id, translations_dict):
    """Load any JSON translation files for a video and merge into translations_dict."""
    if not TRANSLATIONS_DIR.exists():
        return
    for json_file in TRANSLATIONS_DIR.glob(f"{video_id}_*.json"):
        lang = json_file.stem.split("_")[-1]  # e.g. "daMK1Y54M-E_de" → "de"
        if lang not in translations_dict["translations"]:
            with open(json_file, "r", encoding="utf-8") as f:
                translations_dict["translations"][lang] = json.load(f)
            print(f"  Loaded {lang} translation from {json_file.name}")


# ── Translation data ──────────────────────────────────────────────────────────
# Each entry: video_id → { en_slug, translations: { lang: { slug, h1, ... } } }

TRANSLATIONS = {
    "daMK1Y54M-E": {
        "en_slug": "why-do-most-etoro-traders-lose-money",
        "video_id": "daMK1Y54M-E",
        "tag": "Platform reality",
        "cta_url": "https://etoro.tw/4cuYCBg",
        "translations": {
            "es": {
                "slug": "por-que-la-mayoria-pierde-dinero-en-etoro",
                "keyphrase": "¿Por qué la mayoría pierde dinero en eToro?",
                "h1": "¿Por qué el 76% de los traders de eToro pierden dinero?",
                "tag": "Realidad de la plataforma",
                "description": "La verdad incómoda sobre las estadísticas de pérdidas en eToro — Tom explica por qué la mayoría de traders pierden dinero y qué hacer diferente.",
                "intro": "Como afiliado de eToro, tengo que mostrar una advertencia de riesgo en todas mis páginas — y en su punto más alto, decía que el 76% de los inversores minoristas pierden dinero en la plataforma. Eso es más de tres cuartas partes. Entonces, ¿qué está pasando, por qué tanta gente pierde, y cómo te aseguras de no ser uno de ellos?",
                "sections": [
                    {
                        "h2": "La estadística del 76% — Lo que realmente significa",
                        "paragraphs": [
                            "Como afiliado de eToro, TENGO que mostrar una pequeña advertencia en todas mis páginas, y actualizarla cada vez que eToro me lo pide. En este momento dice:",
                            {"type": "note", "text": "Advertencia de riesgo: el 51% de las cuentas de inversores minoristas pierden dinero al operar con CFDs en eToro. Tu capital está en riesgo."},
                            "En el pasado, esa pequeña advertencia (que es un requisito legal) ha llegado a ser del 76%. El 76% pierde dinero usando la plataforma — ¡menuda cifra para reflexionar! Eso es más de 3 cuartas partes. Es una estadística realmente aterradora para los nuevos usuarios — así que, ¿cómo nos aseguramos de no formar parte de esa mayoría?",
                            "eToro ha hecho un trabajo brillante haciendo el trading accesible. La interfaz parece una red social, algo a lo que todos estamos acostumbrados — perfiles bonitos, fondos blancos, todo diseñado con mucho cuidado. Aunque nos lo pone todo fácil y posible para los novatos, puede que también sea parte del problema — pensamos que estamos posiblemente más seguros de lo que realmente estamos.",
                            "Compáralo con algo como MetaTrader 4, que parece un panel de control de la NASA, y entenderás por qué la gente se va a eToro. Pero esa accesibilidad puede crear una falsa sensación de simplicidad. El trading no es simple. La plataforma lo es. Los mercados no.",
                        ]
                    },
                    {
                        "h2": "La trampa de hacerse rico rápido",
                        "paragraphs": [
                            "Si hay una sola razón que explica la mayor parte de ese 76%, es esta: el deseo de hacerse rico rápido.",
                            "De niño, mis ideas sobre el trading y la inversión venían de las películas y la tele. Tipos ricos con cara de estrés pero ganando, Lamborghinis blancos, rascacielos de cristal en Manhattan, cenas y clubs caros. Todos eran guapos, las casas eran enormes, todos miraban números que yo no entendía. Ni idea de cómo lo hacían, pero pintaba genial.",
                            "Así que cuando sitios como eToro empezaron a aparecer, mis ideas sobre inversión y trading estaban alimentadas por la esperanza de por fin ser parte de todo aquello — ¡vamos allá!",
                            {"type": "h3", "text": "Lo que pasa después"},
                            "Entonces, ¿qué hacemos? Encontramos algo llamado 'apalancamiento' que nos permite amplificar el tamaño de nuestras operaciones y pensamos \"¡sí, por favor!\" Sin tener la más mínima idea de lo que estamos haciendo ni de cómo funcionan los mercados, nos lanzamos a operaciones apalancadas, y empezamos a entrar en pánico inmediatamente cuando el mercado se mueve en nuestra contra. Perseguir activos volátiles, comprar por pánico siguiendo tendencias, doblar la apuesta para recuperar pérdidas — pero debajo de todo eso está el mismo impulso. La gente llega a eToro esperando convertir una pequeña cantidad de dinero en una cantidad que les cambie la vida, rápido. Y esa mentalidad casi con toda seguridad te hará perder dinero.",
                            {"type": "h3", "text": "¿Cuánto ganan realmente los profesionales?"},
                            "Los mejores fondos de inversión del mundo — Quantum Fund, Berkshire Hathaway, los mejores de los mejores — generan rendimientos de alrededor del 16-20% anual. Son personas con décadas de experiencia, equipos de analistas y miles de millones bajo gestión. Y ganan un 20%.",
                            "Cuando un nuevo usuario deposita $500 y espera convertirlos en $2,000 en un año, está esperando superar a Warren Buffett por un factor de cuatro. No es realista, y perseguir ese tipo de rendimiento lleva a decisiones terribles.",
                        ]
                    },
                    {
                        "h2": "Por qué las cantidades pequeñas lo empeoran todo",
                        "paragraphs": [
                            "La mayoría de nosotros no somos ricos. Llegamos a eToro con quizás unos pocos cientos de dólares, o incluso un par de miles. Si metes $100, ¿estarías contentísimo con $20 de beneficio después de un año? Eso es un 20% — estás al nivel de los mejores del mundo. Pero nadie quiere $20 después de un año. ¿Qué estamos buscando realmente?",
                            "Estamos buscando dinero que pueda marcar una diferencia significativa en nuestras vidas. $500 tienen que producir otros $500. Como mínimo. Incluso así, no marcará mucha diferencia, pero no hay forma de que $50 en un año merezca siquiera nuestro tiempo. Pero eso es un retorno del 100%. Es casi completamente imposible. Si lo has conseguido, es porque has asumido cantidades increíbles de riesgo y de alguna forma has salido ganando. Estadísticamente, la mayoría de la gente pierde esta apuesta.",
                            {"type": "h3", "text": "Piensa en porcentajes, no en dinero"},
                            "Tenemos que pensar en términos de porcentajes, no en cantidades de dinero. ¿Qué significa esto? Significa que cuando vemos grandes beneficios en efectivo reportados por los Warren Buffett del mundo, tenemos que darnos cuenta de que empezaron con mucho más dinero, así que es fácil generar rendimientos aparentemente enormes asumiendo menos riesgo que el inversor minorista promedio.",
                            "Invierten un millón y al final del año se llevan $100,000 de beneficio. ¡Guau! decimos — ¡$100,000! Pero eso es un retorno del 10%. Podrían haber mantenido su riesgo razonablemente bajo para conseguir ese rendimiento.",
                            {"type": "h3", "text": "La mentalidad de \"no tengo nada que perder\""},
                            "Los que queremos hacernos ricos generalmente pensamos \"Mira, no tengo mucho dinero. He metido $500 — o pego un pelotazo y me cambia un poco la vida, o pierdo $500 y estoy prácticamente en la misma situación que ahora. Mis $500 no me van a llevar a ningún sitio de todas formas.\"",
                            "¿Y qué pasa? Empiezas a fijarte en los traders que van un 200%, 400% arriba. \"¡Este es mi hombre!\" Empiezas a usar apalancamiento. Empiezas a hacer operaciones manuales por instinto. (Créeme, al principio yo intentaba operar con Oro con apalancamiento X20 antes siquiera de estar completamente despierto — habría sido un sketch cómico si no estuviera perdiendo dinero real tan rápido.) Y antes de que te des cuenta, ya formas parte del 76%.",
                            "La ironía es que un 20% sobre $500 es genuinamente excelente. Es un rendimiento de nivel mundial. Pero no se siente así cuando la cifra son solo $100. Esta es una trampa psicológica, y atrapa a casi todos los que empiezan con poco.",
                        ]
                    },
                    {
                        "h2": "Apalancamiento: el asesino de cuentas",
                        "paragraphs": [
                            "El apalancamiento es una forma de amplificar tu operación — eToro te presta dinero extra para que puedas controlar una posición más grande de lo que tu saldo normalmente permitiría. Y para los principiantes, es la forma más rápida de destrozar tu cuenta.",
                            {"type": "h3", "text": "Un ejemplo rápido: la operación con Apple"},
                            "Digamos que quieres abrir una operación de $100 en acciones de Apple. Pero entonces ves el botón de apalancamiento \"X10\".",
                            "¡De repente tu operación de $100 podría ser una operación de $1000! \"Guau\" piensas…, \"¡si las acciones de Apple suben un 10%, ganaré $100! — Apple siempre va bien — ¡vamos!\" Y así, abres tu nueva operación con Apple.",
                            "Metes $100 y eliges apalancamiento X10, así que el tamaño de tu posición es en realidad $1000. ¡Es como magia! No tenemos mucho dinero así que esto parece una gran manera de nivelar el campo de juego y tener operaciones de verdad abiertas.",
                            "La cosa con los mercados es que nunca suben o bajan en línea recta — lleva tiempo acostumbrarse a esto, pero al principio, estos movimientos en zigzag pueden ser aterradores. Los mercados se pueden mover rápido, y las pérdidas pueden aparecer de repente.",
                            "Las acciones de Apple caen un 2%. Estamos vigilando nuestra operación como un halcón, y no es el 2% de $100 lo que hemos perdido (unos manejables $2), es el 2% de $1000 lo que hemos perdido (por nuestro apalancamiento) — unos algo más difíciles $20. Y es un mal día, así que sigue cayendo (esto pasa a menudo). Ahora vamos un 4% abajo — $40 dólares en menos de una hora.",
                            {"type": "h3", "text": "Cuando el pánico toma el volante"},
                            "Con el tiempo, puede que te acostumbres a esta fluctuación y no te preocupe tanto — empiezas a mirar tendencias a más largo plazo, pero al principio, cuando ves tu dinero desaparecer y realmente no sabes por qué, estadísticamente tomarás decisiones terribles basadas en la emoción y el pánico, y perderás dinero. Mantenemos posiciones cuando deberíamos cortar pérdidas. Vendemos por pánico cuando deberíamos haber aguantado, doblamos la apuesta para perseguir nuestras pérdidas, y estadísticamente en general, perdemos más de lo que ganamos.",
                            "El otro problema es que cuando nuestra operación con Apple pierde un 5%, habremos perdido $50 de nuestra inversión original de $100, ya que es el 5% de $1000 lo que hemos perdido debido a nuestro uso del apalancamiento. Esto podría llevar a que eToro cierre nuestra posición automáticamente para que no perdamos demasiado dinero — en algunos casos establecen 'stop-losses' obligatorios en las operaciones como protección… De repente, hemos perdido la mitad de nuestros $100, estamos fuera de la operación y nos preguntamos qué acaba de pasar.",
                            "Así que, al principio, cuidado con el apalancamiento. Puedes hacer lo que quieras, ¡esto no es asesoramiento financiero! Pero ten en cuenta que MUCHA gente se mete en problemas usándolo antes de entender los mercados o cómo funciona el apalancamiento…",
                        ]
                    },
                    {
                        "h2": "El miedo a perderse algo (FOMO)",
                        "paragraphs": [
                            "El FOMO — el miedo a perderse algo — es otro gran generador de pérdidas. Es esa sensación de 'si no hago esta operación ahora mismo, nunca tendré otra oportunidad.' Cada oportunidad parece urgente. Cada movimiento de precio parece el último tren saliendo de la estación.",
                            "La realidad es exactamente lo contrario. En los mercados financieros, hay una nueva oportunidad cada cinco minutos. Hay miles de instrumentos para operar — acciones, cripto, materias primas, forex — y los mercados están abiertos casi las 24 horas. Los traders experimentados lo saben. No se precipitan. Esperan la configuración correcta.",
                            "Pero cuando eres nuevo y estás desesperado por ganar dinero, todo parece ahora o nunca. Y esa urgencia lleva a operar en exceso, perseguir tendencias que ya han tocado techo, y entrar en posiciones sin un análisis adecuado.",
                            {"type": "h3", "text": "Las lecciones de vida que nadie menciona"},
                            "Es algo curioso del trading y la inversión que muchas de las lecciones que necesitamos aprender no son sobre matemáticas o análisis técnico o analizar empresas (¡aunque si vamos a operar manualmente, tendremos que aprender todo eso también!), sino que hay un montón de lecciones de desarrollo personal que aprender. Cómo mantenerse distante y racional en vez de dejar que nuestras emociones nos controlen — cómo soltar ese miedo tentador de que \"¡Si no hago esta operación, nunca habrá otra igual! ¡Esta es mi gran oportunidad!\"",
                            "Suena exageradamente dramático pero ya lo verás :) Este pensamiento aparece para todos, y vuelve una y otra vez a lo largo de nuestro ciclo de vida como inversores — los de ventas y marketing intentan activarlo en nosotros diciendo que hay stock limitado, y \"¡solo quedan 20 plazas!\" etc. Es un disparador emocional muy poderoso, y tenemos que aprender a reconocerlo y no caer en la trampa…",
                        ]
                    },
                    {
                        "h2": "La montaña rusa emocional",
                        "paragraphs": [
                            "Un patrón increíblemente común en eToro — y puedes verlo en cientos de perfiles — es el ciclo de auge y caída. Un trader tiene unos meses geniales, las ganancias vuelan, todo parece brillante. Luego un mal mes arrasa con todo.",
                            "Esto pasa porque las estrategias que producen grandes ganancias suelen ser las mismas que conllevan un gran riesgo. Si sigues tirando los dados, y la avaricia toma el control, eventualmente, estadísticamente, sale mal.",
                            {"type": "h3", "text": "Los Popular Investors lo tienen aún peor"},
                            "Y si estás planeando convertirte en un popular investor en la plataforma y esperas que la gente copie tus operaciones (puede ser muy lucrativo si te va lo suficientemente bien en el programa de popular investors), es otro nivel completamente distinto…",
                            "No puedo decirte cuántas veces he visto esto, incluso con popular investors. Reúnen montones de nuevos copiadores durante sus meses de ganancias enormes. Sube y sube, y todos alaban al trader que están copiando por lo que parece una habilidad casi mágica para ganar en los mercados.",
                            "Entonces empiezan las pérdidas, y los seguidores se ponen agresivos — comentarios constantes sobre \"¡¿qué está pasando con mi dinero?!\" Sugerencias de gente que lleva solo unas semanas en la plataforma, pero de repente todos son profesionales diciéndole cómo debería hacerse, y ves al trader empezar a derrumbarse bajo la presión…",
                            "En vez de seguir su plan cuidadosamente construido y tomarse las cosas con calma, reaccionan a la presión y al miedo y empiezan a tomar malas decisiones — operaciones que normalmente evitarían por el riesgo de repente se convierten en su única forma de 'recuperarlo todo' y muy pronto han perdido el 80% de su cuenta y todos los copiadores se han ido.",
                            "No los envidio — teniendo un canal y teniendo mi cuenta tan pública, es muy fácil empezar a pensar \"¿Qué dirán todos?\" antes de tomar decisiones de inversión, y esa es una motivación terrible. La inversión y el trading realmente requieren lógica fría y dura — es otra de esas lecciones de vida que todos necesitamos aprender si esperamos hacer que esto realmente funcione para nosotros.",
                        ]
                    },
                    {
                        "h2": "Lo que hace diferente el 24% que sí gana",
                        "paragraphs": [
                            "Si el 76% pierde, ¿qué está haciendo bien el 24%? Tras años de observar perfiles en eToro, algunos patrones emergen.",
                            "Aceptan rendimientos más bajos. Un retorno anual del 15-20% con drawdowns bajos es su objetivo, no el 400%. Entienden que ganancias consistentes y aburridas se convierten en riqueza real con el tiempo gracias al interés compuesto.",
                            "Usan poco o nada de apalancamiento. Al operar con su propio dinero (apalancamiento x1), evitan comisiones nocturnas, reducen el riesgo drásticamente, y pueden aguantar caídas temporales sin verse obligados a cerrar.",
                            "SÍ HAY traders experimentados y excelentes que emplean el apalancamiento como parte de su estrategia, pero son traders que realmente entienden lo que hacen — las estadísticas muestran que para los principiantes, el uso del apalancamiento es uno de los mayores riesgos, y tiende más a la apuesta que al trading o la inversión. No soy un profesional, no soy asesor financiero, ¡pero vaya si parece causarnos problemas a todos como principiantes, así que estáis avisados!",
                            "Invierten más capital con menos riesgo, en vez de menos capital con más riesgo. Es mejor meter $5,000 y esperar un 20% ($1,000 de ganancia) que meter $500 y perseguir un 200% ($1,000 de ganancia). El retorno esperado es el mismo pero el perfil de riesgo es completamente diferente.",
                            {"type": "h3", "text": "La trampa de la emoción"},
                            "Creo que cuando llegamos, todo es tan emocionante que estamos rebosando de entusiasmo — entramos constantemente a ver nuestro dinero — ¿cuánto hemos ganado? ¿Elegí bien? ¿Qué dice la gente? Es emocionante, es nuevo y queremos ver acción.",
                            "Lo que necesitamos entender es que todo puede ser mucho más lento de lo que anticipábamos. Si lo enfocamos sensatamente, esperando un 15% en un año, y hemos metido $1000, entonces estamos hablando de $150 de beneficio después de 12 meses. No vamos a ver grandes movimientos todo el tiempo. Va a ser mucho más lento de lo que esperamos…",
                            "Así que la tentación puede ser intentar forzar que algo pase — abrir operaciones extra, usar apalancamiento para que las cosas se muevan más rápido, saltar constantemente a un nuevo activo que pueda generar algo de movimiento y crear emoción. Es comprensible, y es otra pequeña trampa — si estamos aquí por el chute de dopamina, es otra versión del enfoque equivocado. Esto requiere cierto desapego (¡lo sé! ¡Yo también quiero adrenalina! pero este no es el lugar para eso, ya que estadísticamente es ahí donde se acumulan las pérdidas)",
                            {"type": "h3", "text": "\"¡¿Por qué no estás operando?!\""},
                            "Lo mismo aplica al copy trading — veo a mucha gente nueva copiar a un trader que tiene años de estadísticas estables mostrando beneficios. Pero el novato es impaciente, y el trader que ha copiado se está tomando las cosas con calma, observando los mercados, esperando su punto de entrada correcto. \"¿Por qué no estás operando?\" viene el comentario del novato… \"¿Qué le pasa a este tío?\" dice otro — Es muy familiar :) Queremos acción — queremos ver esos grandes movimientos que pasan en las películas.",
                            "Ten en cuenta que mientras copias a alguien, lo que buscamos es éxito a largo plazo — ese es el objetivo. Déjalos encargarse de los altibajos y preocupaciones del día a día. Lleva un tiempo acostumbrarse ya que nos damos cuenta de que simplemente tenemos que seguir con nuestra vida normal — esto no va a cambiarlo todo en un mes… de nuevo — más soltar y lecciones de vida :)",
                            "No entran en pánico. Tienen un plan, lo siguen, y no reaccionan emocionalmente a cada bajada. Si un trader copiado tiene un mal mes pero sus estadísticas a largo plazo son sólidas, mantienen el rumbo.",
                        ]
                    },
                    {
                        "h2": "El copy trading tampoco es un atajo",
                        "paragraphs": [
                            "El copy trading elimina un gran problema — no necesitas saber cómo operar. Pero introduce sus propios riesgos. Si estás copiando a alguien que opera con un estilo de auge y caída, obtendrás los mismos resultados de auge y caída.",
                            "La clave es elegir a quién copiar con mucho cuidado. Busca puntuaciones de riesgo bajas, drawdowns bajos y rendimientos consistentes durante al menos 12 meses. Los traders que parecen emocionantes — subiendo un 80% un mes, bajando un 40% al siguiente — son los que más probablemente arruinen tu cuenta junto con la suya.",
                            {"type": "h3", "text": "Cómo ha cambiado mi enfoque"},
                            "Con el tiempo mi enfoque sobre a quién copio ha cambiado. He intentado copiar a algunos de los traders que parecen superar enormemente a todos los demás y no han tenido ningún mes en pérdidas durante más de un año, solo para verlos perderlo todo después de un par de meses terribles y ese temido cambio de comportamiento.",
                            "Antes pensaba que 12 meses de historial era suficiente, pero ahora creo que cuanto más largo mejor — ahora busco al menos dos años de historial de trading, y he aprendido a revisar sus gráficos buscando grandes pérdidas repentinas ocultas y otros patrones que podrían señalar problemas en el futuro. He hecho vídeos sobre eso si te interesa.",
                            {"type": "h3", "text": "Qué buscar al elegir un trader"},
                            "Te acostumbras la verdad — a mirar todas las estadísticas que se muestran y hacerte una idea general de su estilo de trading. Eso lleva un poco de tiempo, pero como regla general busco unos cuantos años de historial de trading y estabilidad por encima de todo. Ya no puedo con los tipos de auge/caída porque pasas dos años acumulando ganancias solo para perderlo todo en un mes, ¡y de repente esos dos años enteros fueron una pérdida de tiempo!",
                            "La página de copiar personas de eToro fue renovada hace un tiempo, e incluyeron algunas opciones de filtrado nuevas y útiles — 'más consistente' ha sido mi favorito y así encontré algunos traders realmente buenos. También puedes filtrar por los que superaron a los mercados en general y cosas así — se ha vuelto más útil con el tiempo y hay un gran grupo de traders, pero siguen siendo los mejores los que de alguna forma consiguen igualar o superar a los mercados generales pero también evitar las inevitables caídas los que atraen a todos los copiadores. Cuando se hacen demasiado grandes, eToro suele subir la cantidad necesaria para copiarlos, así que hay cierto arte en elegir el momento de copiar.",
                            "Si quieres operar manualmente en vez de copiar, invierte en educación primero. Haz un curso de verdad. Aprende los fundamentos antes de arriesgar dinero real. El coste de un buen curso de trading es casi siempre menor que el coste de aprender perdiendo dinero en la plataforma.",
                            {"type": "h3", "text": "Invierte solo lo que puedas permitirte perder"},
                            "Dicen \"invierte solo lo que puedas permitirte perder\" y suena genial, pero como principiantes, simplemente esperamos no perder y a menudo puede ser dinero que realmente necesitamos. Tienes que tener cuidado con esto — como todos sabemos, las cosas surgen inesperadamente en la vida y de repente necesitamos dinero para algo urgente. Invertir puede ser un proceso largo y lento, y si tenemos que cerrar operaciones solo porque necesitamos desesperadamente el efectivo y no tenemos otra reserva, puede significar cerrar operaciones en el momento equivocado e incurrir en pérdidas significativas.",
                            "A menos que planees ser un trader increíblemente activo y sea tu profesión, entiende que si de alguna forma dependes de esto como fuente principal de ingresos, tenderás a apostar para conseguir el tipo de ganancias que necesitas. Los profesionales hacen de ello su vida — es lento, metódico, y tienen un plan. Para los más pasivos entre nosotros, tenemos que entender que a veces la inversión estará en pérdidas y puede quedarse así durante bastante tiempo antes de que las cosas se recuperen. Podría ser una buena idea tener tu fondo de emergencia para imprevistos de la vida separado de tu cuenta de trading si es posible, para evitar ventas forzadas en malos momentos.",
                            {"type": "h3", "text": "Cuando las pérdidas se vuelven reales"},
                            "También tienes que darte cuenta de que las pérdidas son una enorme realidad potencial. Si el dinero con el que operas es realmente dinero que necesitas y no dinero que genuinamente puedes permitirte perder, te va a generar mucho estrés. ¿Merece la pena? Es una situación horrible cuando has perdido dinero que tú o tu familia necesitáis y no quieres contárselo.",
                            "\"Quizás puedo recuperarlo sin decírselo…\" Es una frase clásica que muchos han pensado antes que nosotros, y que a menudo lleva a asumir riesgos enormes y perder aún más. Esa es una situación terrible para cualquiera, y antes de empezar, date cuenta de que es una posibilidad real y hay gente que se encuentra en esta situación.",
                            "Es muy fácil ver las enormes ganancias potenciales que podríamos obtener y simplemente apartar los riesgos a un lado, pero si pasa lo peor, simplemente no merece la pena ni siquiera las enormes ganancias potenciales. Esto requiere verdadera disciplina, ya que todos nos sentimos tentados cuando probamos esto.",
                            "Dicen \"Solo arriesga lo que puedas permitirte perder\". Creo que hay verdadera sabiduría en eso. Puede que nos salga bien durante un tiempo, pero eventualmente si no seguimos esta regla, el estrés va a ser enorme.",
                            {"type": "note", "text": "Yo diría que lo más importante que he aprendido es esto: no es un esquema para hacerse rico rápido. Puede generar dinero — eso lo creo — pero es un esquema para hacerse rico lentamente. O más honestamente, un esquema para ganar-algo-de-dinero-lentamente. Cuanto antes aceptes eso, antes dejas de cometer los errores que te ponen en el 76%."},
                        ]
                    },
                    {
                        "h2": "La conclusión de Tom",
                        "paragraphs": [
                            "76% es un número grande, real y aterrador. Y no es porque eToro sea una estafa o las comisiones sean injustas — es porque el trading es inherentemente arriesgado, y la accesibilidad de la plataforma hace que la gente subestime ese riesgo.",
                            "Si estás empezando, esto es lo que te sugeriría: usa la cuenta virtual primero, copia a traders de bajo riesgo, olvídate de hacerte rico rápido, y mete dinero que genuinamente puedas permitirte dejar ahí durante años. Los rendimientos parecerán pequeños al principio, pero eso es exactamente lo que parece una inversión sostenible.",
                            "La gente que gana dinero en eToro es la paciente. La aburrida. La que no intenta convertir $500 en un Lamborghini para el mes que viene. ¡Espero estar finalmente aprendiendo a ser una de esas personas!",
                        ]
                    },
                ],
                "faqs": [
                    {"q": "¿Por qué la mayoría de los traders de eToro pierden dinero?", "a": "Las razones principales son el exceso de apalancamiento, perseguir beneficios rápidos, mala gestión del riesgo y tomar decisiones emocionales. La plataforma de eToro hace que el trading parezca sencillo, lo que puede llevar a los principiantes a subestimar los riesgos de los CFDs y el apalancamiento."},
                    {"q": "¿Qué porcentaje de traders de eToro son rentables?", "a": "Según la propia divulgación de riesgos de eToro, alrededor del 76% de las cuentas de inversores minoristas pierden dinero al operar con CFDs. Solo aproximadamente el 24% de los traders son consistentemente rentables en la plataforma."},
                    {"q": "¿Cómo puedo evitar perder dinero en eToro?", "a": "Evita el apalancamiento alto, usa primero la cuenta de práctica virtual, copia solo a traders de menor riesgo con rendimientos consistentes a largo plazo, y nunca inviertas más de lo que puedas permitirte perder. Trátalo como una inversión a largo plazo, no como un esquema para hacerte rico rápido."},
                    {"q": "¿Es eToro una estafa?", "a": "No. eToro es una plataforma regulada autorizada por la FCA, CySEC y ASIC. La estadística del 76% refleja el riesgo inherente de operar con CFDs, no un problema con la plataforma en sí. La mayoría de traders pierden dinero en todas las plataformas de CFDs, no solo en eToro."},
                    {"q": "¿Qué rendimientos debería esperar de forma realista del copy trading en eToro?", "a": "Los rendimientos anuales realistas al copiar traders de menor riesgo son de alrededor del 10-25% por año. Los mejores fondos de inversión del mundo promedian un 16-20% anual. Cualquiera que prometa significativamente más que eso está asumiendo un riesgo significativo."},
                ],
            },
            # DE, FR, PT translations will be added via the add_translation() calls below
        },
    },
}

# ── Helper: slugify ───────────────────────────────────────────────────────────
def slugify(text):
    """Convert heading text to URL-safe anchor id."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def build_hreflang_tags(video_id, translation_data):
    """Build hreflang link tags for all language variants."""
    en_slug = translation_data["en_slug"]
    lines = []
    # English (default + en)
    en_url = f"{BASE_URL}/video/{en_slug}/"
    lines.append(f'  <link rel="alternate" hreflang="en" href="{en_url}" />')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{en_url}" />')
    # Each translation
    for lang, t in sorted(translation_data["translations"].items()):
        url = f"{BASE_URL}/{lang}/video/{t['slug']}/"
        lines.append(f'  <link rel="alternate" hreflang="{lang}" href="{url}" />')
    return "\n".join(lines)


def build_toc(sections):
    """Build table of contents from H2 headings."""
    items = []
    for sec in sections:
        anchor = slugify(sec["h2"])
        items.append(f'<li><a href="#{anchor}">{html.escape(sec["h2"])}</a></li>')
    return "\n".join(items)


def render_article_body(sections):
    """Render all sections as HTML."""
    parts = []
    for sec in sections:
        anchor = slugify(sec["h2"])
        parts.append(f'        <h2 id="{anchor}">{html.escape(sec["h2"])}</h2>')
        for p in sec["paragraphs"]:
            if isinstance(p, dict):
                if p["type"] == "note":
                    parts.append(f'        <p class="toms-note">{html.escape(p["text"])}</p>')
                elif p["type"] == "h3":
                    parts.append(f'        <h3>{html.escape(p["text"])}</h3>')
            else:
                parts.append(f'        <p>{html.escape(p)}</p>')
    return "\n".join(parts)


def render_faq_html(faqs):
    """Render FAQ section HTML."""
    parts = ['        <section class="faq-section">']
    for faq in faqs:
        parts.append('    <div class="faq-item">')
        parts.append(f'      <h3 class="faq-q">{html.escape(faq["q"])}</h3>')
        parts.append(f'      <p class="faq-a">{html.escape(faq["a"])}</p>')
        parts.append('    </div>')
    parts.append('</section>')
    return "\n".join(parts)


def render_faq_schema(faqs):
    """Render FAQPage JSON-LD schema."""
    entities = []
    for faq in faqs:
        entities.append({
            "@type": "Question",
            "name": faq["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["a"],
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return json.dumps(schema, indent=2, ensure_ascii=False)


def generate_page(lang, video_id, translation_data, trans):
    """Generate a full translated HTML page."""
    ui = UI_STRINGS[lang]
    slug = trans["slug"]
    h1 = trans["h1"]
    desc = trans["description"]
    intro = trans["intro"]
    sections = trans["sections"]
    faqs = trans["faqs"]
    tag = trans.get("tag", translation_data.get("tag", ""))
    cta_url = translation_data.get("cta_url", "https://etoro.tw/4cuYCBg")
    en_slug = translation_data["en_slug"]

    canonical = f"{BASE_URL}/{lang}/video/{slug}/"
    hreflang_tags = build_hreflang_tags(video_id, translation_data)
    toc_items = build_toc(sections)
    article_body = render_article_body(sections)
    faq_html = render_faq_html(faqs)
    faq_schema = render_faq_schema(faqs)

    # Heading for FAQ section
    faq_heading = ui.get("faq_heading", "FAQ")

    # VideoObject schema
    video_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": h1,
        "description": desc,
        "thumbnailUrl": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        "embedUrl": f"https://www.youtube.com/embed/{video_id}",
        "uploadDate": "2024-01-01",
        "publisher": {
            "@type": "Organization",
            "name": "Social Trading Vlog",
            "url": BASE_URL,
        }
    }, indent=2, ensure_ascii=False)

    # Breadcrumb schema
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["breadcrumb_home"], "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": ui["breadcrumb_videos"], "item": f"{BASE_URL}/videos.html"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": canonical},
        ]
    }, indent=2, ensure_ascii=False)

    p = ASSET_PREFIX  # ../../../
    dir_attr = ' dir="rtl"' if lang == "ar" else ""

    page_html = f'''<!DOCTYPE html>
<html lang="{lang}"{dir_attr}>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(desc)}" />
  <meta property="og:title" content="{html.escape(h1)} | SocialTradingVlog" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" />
  <link rel="canonical" href="{canonical}" />
{hreflang_tags}
  <title>{html.escape(h1)} | SocialTradingVlog</title>
  <link rel="stylesheet" href="{p}css/style.css" />
  <script type="application/ld+json">
  {video_schema}
  </script>
  <script type="application/ld+json">
  {faq_schema}
  </script>
  <script type="application/ld+json">
  {breadcrumb_schema}
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-PBGDJ951LL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-PBGDJ951LL');
  </script>
</head>
<body>

  <nav>
    <div class="container nav-inner">
      <a href="{p}index.html" class="nav-logo">Social<span>Trading</span>Vlog</a>
      <ul class="nav-links">
        <li><a href="{p}social-trading.html">{html.escape(ui["social_trading"])}</a></li>
        <li><a href="{p}copy-trading.html">{html.escape(ui["copy_trading"])}</a></li>
        <li><a href="{p}updates.html">{html.escape(ui["updates"])}</a></li>
        <li><a href="{p}videos.html">{html.escape(ui["videos"])}</a></li>
        <li><a href="{p}about.html">{html.escape(ui["about"])}</a></li>
        <li><a href="{p}faq.html">{html.escape(ui["faq"])}</a></li>
        <li><a href="#etoro-cta" class="nav-cta">{html.escape(ui["try_etoro"])}</a></li>
      </ul>
      <button class="nav-hamburger" id="nav-hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="nav-drawer">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
  <div class="nav-drawer" id="nav-drawer" role="navigation" aria-label="Mobile navigation">
    <ul>
      <li><a href="{p}social-trading.html">{html.escape(ui["social_trading"])}</a></li>
      <li><a href="{p}copy-trading.html">{html.escape(ui["copy_trading"])}</a></li>
      <li><a href="{p}updates.html">{html.escape(ui["updates"])}</a></li>
      <li><a href="{p}videos.html">{html.escape(ui["videos"])}</a></li>
      <li><a href="{p}about.html">{html.escape(ui["about"])}</a></li>
      <li><a href="{p}faq.html">{html.escape(ui["faq"])}</a></li>
      <li><a href="#etoro-cta" class="nav-cta">{html.escape(ui["try_etoro"])}</a></li>
    </ul>
  </div>

  <div class="risk-warning-banner">
    <span>{html.escape(ui["risk_warning_label"])}:</span> {ui["risk_warning_banner"].split(": ", 1)[-1] if ": " in ui["risk_warning_banner"] else ui["risk_warning_banner"]}
  </div>

  <div class="article-hero">
    <div class="container">
      <div class="article-tag">{html.escape(tag)}</div>
      <h1>{html.escape(h1)}</h1>
      <p class="article-meta">{ui["by_tom"]} &nbsp;&middot;&nbsp; Social Trading Vlog</p>
    </div>
  </div>

  <div class="container">
    <div class="article-body">

      <article class="article-content">

        <img
          src="https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
          alt="{html.escape(h1)}"
          style="width:100%;height:auto;border-radius:8px;margin:0 0 24px;display:block;"
          loading="eager"
          width="480" height="270"
        >

        <p class="article-intro">{html.escape(intro)}</p>

        <nav class="toc" aria-label="Contents"><h4>{html.escape(ui["in_this_article"])}</h4><ul>
{toc_items}
</ul></nav>

        <div class="video-embed">
          <iframe
            src="https://www.youtube.com/embed/{video_id}"
            title="{html.escape(h1)}"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            loading="lazy">
          </iframe>
        </div>
        <p style="font-size:0.85rem;color:var(--muted);margin-top:-8px;margin-bottom:24px;">
          {html.escape(ui["prefer_reading"])} &nbsp;&middot;&nbsp;
          <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener">{html.escape(ui["watch_on_youtube"])}</a>
        </p>

        <div class="risk-warning">
          <strong>{html.escape(ui["risk_warning_label"])}</strong>
          {html.escape(ui["risk_warning_full"])}
        </div>

        <div class="inline-cta">
          <p class="inline-cta-text">{html.escape(ui["ready_cta_inline"])}</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
        </div>

{article_body}

        <section class="faq-section">
  <h2>{html.escape(faq_heading)}</h2>
{faq_html.replace('<section class="faq-section">', '').replace('</section>', '')}
</section>

        <div class="risk-warning">
          <strong>{html.escape(ui["important_reminder"])}</strong>
          {html.escape(ui["important_reminder_text"])}
        </div>

      </article>

      <aside class="article-sidebar">
        <div class="sidebar-cta" id="etoro-cta">
          <h3>{html.escape(ui["ready_to_try"])}</h3>
          <p>{html.escape(ui["toms_affiliate"])}</p>
          <a href="{cta_url}" class="btn btn-primary" target="_blank" rel="noopener sponsored">{html.escape(ui["explore_etoro"])}</a>
          <div class="risk-warning">
            <strong>{ui["risk_warning_sidebar"].split('.')[0]}.</strong>
            {'.'.join(ui["risk_warning_sidebar"].split('.')[1:])}
          </div>
        </div>
        <div class="sidebar-nav">
          <h4>{html.escape(ui["more_guides"])}</h4>
          <ul>
            <li><a href="{p}social-trading.html">{html.escape(ui["guide_social"])}</a></li>
            <li><a href="{p}copy-trading.html">{html.escape(ui["guide_copy"])}</a></li>
            <li><a href="{p}copy-trading-returns.html">{html.escape(ui["guide_returns"])}</a></li>
            <li><a href="{p}etoro-scam.html">{html.escape(ui["guide_scam"])}</a></li>
            <li><a href="{p}taking-profits.html">{html.escape(ui["guide_profits"])}</a></li>
            <li><a href="{p}popular-investor.html">{html.escape(ui["guide_pi"])}</a></li>
            <li><a href="{p}videos.html">{html.escape(ui["guide_all_videos"])}</a></li>
          </ul>
        </div>
      </aside>

    </div>
  </div>

  <footer>
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="nav-logo">Social<span style="color:var(--accent)">Trading</span>Vlog</div>
          <p>{html.escape(ui["footer_brand"])}</p>
        </div>
        <div class="footer-col">
          <h4>{html.escape(ui["footer_guides"])}</h4>
          <ul>
            <li><a href="{p}social-trading.html">{html.escape(ui["guide_social"])}</a></li>
            <li><a href="{p}copy-trading.html">{html.escape(ui["guide_copy"])}</a></li>
            <li><a href="{p}etoro-scam.html">{html.escape(ui["guide_scam"])}</a></li>
            <li><a href="{p}copy-trading-returns.html">{html.escape(ui["guide_returns"])}</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>{html.escape(ui["footer_site"])}</h4>
          <ul>
            <li><a href="{p}updates.html">{html.escape(ui["footer_updates"])}</a></li>
            <li><a href="{p}about.html">{html.escape(ui["footer_about"])}</a></li>
            <li><a href="{p}faq.html">{html.escape(ui["footer_faq"])}</a></li>
            <li><a href="{p}contact.html">{html.escape(ui["footer_contact"])}</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 SocialTradingVlog.com</p>
        <p class="footer-disclaimer">{html.escape(ui["risk_warning_footer"])}</p>
      </div>
    </div>
  </footer>

  <script src="{p}js/lightbox.js"></script>
  <script src="{p}js/nav.js"></script>
  <script>
  document.addEventListener('click', function(e) {{
    var link = e.target.closest('a.btn-primary');
    if (!link) return;
    if (typeof gtag === 'function') {{
      gtag('event', 'cta_click', {{
        'event_category': 'affiliate',
        'event_label': link.textContent.trim(),
        'link_url': link.href || '',
        'page_path': location.pathname
      }});
    }}
  }});
  </script>
</body>
</html>'''

    return page_html


def main():
    parser = argparse.ArgumentParser(description="Generate translated video pages")
    parser.add_argument("--lang", help="Generate only this language (es, de, fr, pt, ar)")
    parser.add_argument("--video-id", help="Generate only for this video ID")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pages")
    args = parser.parse_args()

    count = 0
    for video_id, data in TRANSLATIONS.items():
        if args.video_id and video_id != args.video_id:
            continue
        # Load any additional translations from JSON files
        load_translations_from_json(video_id, data)
        for lang, trans in data["translations"].items():
            if args.lang and lang != args.lang:
                continue

            slug = trans["slug"]
            out_dir = BASE_DIR / lang / "video" / slug
            out_file = out_dir / "index.html"

            if out_file.exists() and not args.force:
                print(f"  SKIP {lang}/video/{slug}/ (exists)")
                continue

            out_dir.mkdir(parents=True, exist_ok=True)
            page_html = generate_page(lang, video_id, data, trans)
            out_file.write_text(page_html, encoding="utf-8")
            count += 1
            print(f"  WROTE {lang}/video/{slug}/index.html")

    print(f"\nDone — {count} translated page(s) generated.")


if __name__ == "__main__":
    main()
