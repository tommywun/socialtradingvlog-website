#!/usr/bin/env python3
"""Build the German translation JSON file for FAQ, Contact, and all 27 update posts."""
import json

output = {}

# ============================================================
# FAQ
# ============================================================
output["faq"] = {
    "slug": "haeufig-gestellte-fragen",
    "meta_description": "Häufig gestellte Fragen zu Copy Trading und eToro — ist es kostenlos, welche Gebühren gibt es, warum bewerbe ich eToro, und mehr.",
    "title": "Häufig gestellte Fragen | SocialTradingVlog",
    "article_tag": "FAQ",
    "h1": "Häufig gestellte Fragen",
    "article_meta": "Dieser Bereich wächst mit der Zeit, wenn neue Fragen auftauchen.",
    "questions": [
        {
            "question": "Warum bewirbst du eToro?",
            "answer": "Es ist die beste Social-Trading-Plattform, die ich bisher gefunden habe. Ich nutze sie seit 2016 und dokumentiere dort meine eigene Copy-Trading-Erfahrung. Ich habe eine Affiliate-Partnerschaft mit eToro — wenn du dich über meinen Link anmeldest, erhalte ich möglicherweise eine Provision, ohne dass dir zusätzliche Kosten entstehen. Diese Partnerschaft beeinflusst nicht, was ich schreibe oder wie ich über meine Erfahrungen berichte."
        },
        {
            "question": "Ist Copy Trading kostenlos?",
            "answer": "Ja. Es gibt Gebühren, die beim Handel auf allen Börsen anfallen — eToro eingeschlossen — aber das Kopieren der Trades eines anderen Investors ist kostenlos. Du musst der Person, die du kopierst, keine Provision oder Beteiligung zahlen. Sie investieren mit ihrem eigenen Geld; dein Konto kopiert einfach automatisch alle ihre Trades. Die Person, die du kopierst, erhält Anreize von eToro — je mehr Leute sie kopieren und je mehr Geld mit ihnen investiert wird, desto mehr zahlt eToro ihnen. Sie profitieren von der Situation, nur nicht direkt von dir."
        },
        {
            "question": "Welche Gebühren gibt es bei eToro?",
            "answer": "Es gibt einige, die du kennen solltest:<ul><li><strong>Spread-Gebühren</strong> — in jeden Trade eingebaut. Wenn du einen Trade eröffnest, wirst du feststellen, dass er sofort mit einem kleinen Verlust startet. Das ist die Spread-Gebühr. Sobald sich der Kurs zu deinen Gunsten bewegt, holst du sie wieder auf und gehst dann in den Gewinn.</li><li><strong>Auszahlungsgebühr</strong> — eToro berechnet eine Pauschalgebühr, wenn du Geld von der Plattform abhebst.</li><li><strong>Währungsumrechnung</strong> — da auf eToro alles in USD gehandelt wird, fällt ein Wechselkurs an, wenn du in einer anderen Währung ein- oder auszahlst.</li><li><strong>Übernacht-/Wochenendgebühren</strong> — wenn du gehebelte Positionen über Nacht hältst, können zusätzliche Gebühren anfallen. Wenn du die Copy-Trading-Funktion ohne Hebel nutzt, ist das weniger relevant.</li></ul>"
        },
        {
            "question": "Brauche ich Trading-Erfahrung?",
            "answer": "Nein — genau das ist der Sinn von Copy Trading. Die ganze Idee ist, dass du von der Erfahrung von Leuten profitieren kannst, die wissen, was sie tun, ohne selbst ein Experte werden zu müssen. Du musst trotzdem sorgfältig auswählen, wen du kopierst, und die Risiken verstehen, aber du musst keine Charts lesen oder Märkte analysieren können."
        },
        {
            "question": "Kann ich Geld verlieren?",
            "answer": "Ja. Copy Trading eliminiert kein Risiko — es ist immer noch eine Geldanlage. Wenn die Person, die du kopierst, Verluste macht, machst du auch Verluste. Du solltest nur Geld investieren, dessen Verlust du dir leisten kannst. Lies den Artikel <a href=\"copy-trading-returns.html\">Wie viel kann man verdienen?</a> für einen realistischen Blick auf Risiko und Rendite."
        },
        {
            "question": "Ist eToro reguliert?",
            "answer": "Ja. eToro wird von mehreren Finanzaufsichtsbehörden reguliert, darunter die FCA (Großbritannien), CySEC (Zypern) und ASIC (Australien). Regulierung bedeutet, dass es Aufsicht und rechtliche Verantwortlichkeit gibt. Lies meinen vollständigen Artikel <a href=\"etoro-scam.html\">Ist eToro Betrug?</a> für mehr dazu."
        },
        {
            "question": "Wie fange ich mit Copy Trading an?",
            "answer": "Die grundlegenden Schritte sind: Eröffne ein eToro-Konto, verifiziere deine Identität, zahle Geld ein, durchsuche den Bereich 'Copy People', wähle jemanden aus, dessen Statistiken dir gefallen, lege deinen Kopierbetrag fest und klicke auf Kopieren. Der <a href=\"copy-trading.html\">Copy-Trading-Leitfaden</a> behandelt das im Detail."
        }
    ],
    "sidebar_h3": "Bereit, Copy Trading auszuprobieren?",
    "sidebar_p": "Hier ist mein eToro-Affiliate-Link zum Starten.",
    "sidebar_nav_h4": "Nützliche Anleitungen"
}

# ============================================================
# CONTACT
# ============================================================
output["contact"] = {
    "slug": "kontakt",
    "meta_description": "Kontaktiere Social Trading Vlog — Fragen zu Copy Trading, eToro oder der Website.",
    "title": "Kontakt | SocialTradingVlog",
    "article_tag": "Kontakt",
    "h1": "Kontakt",
    "intro": "Hast du eine Frage zu Copy Trading, eToro oder etwas auf der Website? Schreib mir gerne. Bitte beachte, dass ich kein Finanzberater bin und keine Anlageberatung geben kann — aber ich beantworte gerne Fragen zur Funktionsweise der Plattform oder teile meine Erfahrungen.",
    "form_labels": {
        "name": "Dein Name",
        "name_placeholder": "z.B. Max Mustermann",
        "email": "E-Mail-Adresse",
        "email_placeholder": "du@beispiel.de",
        "message": "Nachricht",
        "message_placeholder": "Deine Frage oder Nachricht...",
        "submit": "Nachricht senden"
    },
    "reminder_title": "Hinweis",
    "reminder_text": "Diese Website dient ausschließlich Bildungs- und Informationszwecken. Nichts hierin stellt eine Finanz- oder Anlageberatung dar. 51% der Privatanlegerkonten verlieren Geld beim CFD-Handel mit eToro. Dein Kapital ist gefährdet."
}

# ============================================================
# UPDATES
# ============================================================
updates = {}

# ---- social-trading-update-jun-2017 ----
updates["social-trading-update-jun-2017"] = {
    "slug": "copy-trading-update-juni-2017",
    "meta_description": "Copy Trading Update — Juni 2017. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — Juni 2017 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Juni 2017",
    "h1": "Copy Trading Update — Juni 2017",
    "content_blocks": [
        {"type": "p", "text": "21. Juni 2017 Das hier ist von 2017, als ich noch manuell gehandelt habe und Kryptos gerade aufkamen. Ich hatte ziemliche Schwierigkeiten, meine Ethereum-Position zu halten... Ich wünschte, ich hätte einfach 5 Monate gewartet :) Im Nachhinein ist man immer schlauer."},
        {"type": "h3", "text": "Sieh dir mein Profil selbst an"},
        {"type": "p", "text": "Mein Profil ansehen"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-28-nov-2017 ----
updates["copy-trading-update-28-nov-2017"] = {
    "slug": "copy-trading-update-28-november-2017",
    "meta_description": "Copy Trading Update — 28. November 2017. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 28. Nov. 2017 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · November 2017",
    "h1": "Copy Trading Update — 28. Nov. 2017",
    "content_blocks": [
        {"type": "h3", "text": "Schau dir mein Profil an..."},
        {"type": "p", "text": "Hoffentlich läuft es gut :) Du kannst hier nachschauen. Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Mein aktuelles Profil auf eToro"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-jul-2018 ----
updates["copy-trading-update-jul-2018"] = {
    "slug": "copy-trading-update-juli-2018",
    "meta_description": "Copy Trading Update — Juli 2018. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — Juli 2018 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Juli 2018",
    "h1": "Copy Trading Update — Juli 2018",
    "content_blocks": [
        {"type": "p", "text": "9. Juli 2018 Immer noch in Italien, gebe ich ein kurzes Update zu meinem Copy Trading auf eToro. Es geht alles sehr langsam und ich warte eigentlich nur ab. Ich habe einen neuen Trader kopiert, und wir werden sehen, wie es läuft."},
        {"type": "p", "text": "Ich spreche auch über diese Website und warum ich angefangen habe, sie aufzubauen. Danke fürs Zuschauen!"},
        {"type": "p", "text": "Wenn du mein Profil oder Portfolio auf eToro sehen möchtest, kannst du hier klicken. Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "h3", "text": "Willst du mein Portfolio sehen?"},
        {"type": "p", "text": "Hoffentlich läuft es heute gut! Schau dir mein Portfolio an :)"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Hier klicken"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-23-aug-2018 ----
updates["copy-trading-update-23-aug-2018"] = {
    "slug": "copy-trading-update-23-august-2018",
    "meta_description": "Copy Trading Update — 23. August 2018. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 23. Aug. 2018 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · August 2018",
    "h1": "Copy Trading Update — 23. Aug. 2018",
    "content_blocks": [
        {"type": "p", "text": "23. August 2018 Hier ist mein neuestes Copy-Trading-Update über meine Abenteuer auf eToro. Diesmal bespreche ich, warum ich einen der Trader, die ich kopiert habe, fallen gelassen habe, und rede auch über die anderen, die ich noch kopiere."},
        {"type": "p", "text": "Es waren ein paar harte Monate, und sie haben durchgehend Geld verloren, also fange ich an, über neue Trader nachzudenken."},
        {"type": "p", "text": "Ich bespreche auch, wie Affiliate-Zahlungen bei eToro funktionieren und wie sie diese kürzlich geändert haben, anscheinend um den neuen europäischen ESMA-Regulierungen zu entsprechen."},
        {"type": "p", "text": "Es ist sehr frustrierend beim Copy Trading, wenn die Leute, die man kopiert, einfach immer weiter langsam Geld verlieren. Ich möchte immer festhalten und einfach warten, bis sie die Verluste wieder reinholen, aber manchmal muss man einfach sagen 'genug ist genug', die Kopie stoppen, die Verluste hinnehmen und neue Leute finden."},
        {"type": "p", "text": "Dieses Video habe ich wieder in Malta gefilmt, in der Wohnung meines Bruders. Entschuldigung für das viele Schwitzen :) Im August wird es in Malta sehr heiß..."},
        {"type": "h3", "text": "Willst du sehen, wie es mir geht?"},
        {"type": "p", "text": "Meine Statistiken auf eToro"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-25-nov-2018 ----
updates["copy-trading-update-25-nov-2018"] = {
    "slug": "copy-trading-update-25-november-2018",
    "meta_description": "Copy Trading Update — 25. November 2018. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 25. Nov. 2018 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · November 2018",
    "h1": "Copy Trading Update — 25. Nov. 2018",
    "content_blocks": [
        {"type": "p", "text": "Der 'Copy Stop Loss' ist eine Möglichkeit, automatisch festzulegen, wie viel Geld du bereit bist, bei jedem Trader, den du kopierst, zu verlieren, damit das System die Kopie automatisch stoppt, wenn dieser Betrag jemals erreicht wird."},
        {"type": "p", "text": "Ich spreche auch über die anderen Trader in meinem Portfolio, wie ich meine Gewinnerwartungen nach den wilden Krypto-Tagen von 2017 gesenkt habe, und warum ich manchmal denke, dass die Trader, die wir kopieren, ein bisschen mehr Empathie und vielleicht Raum zum Nachdenken brauchen, als wir ihnen geben..."},
        {"type": "p", "text": "Ich weiß, es mag so aussehen, als würde ich sie in Schutz nehmen, aber kannst du dir wirklich vorstellen, wie viel Zeit und Energie es diese Leute kostet, auf all die Kommentare und Fragen zu antworten, die sie erhalten?"},
        {"type": "p", "text": "Das könnte erklären, warum nach dem Beitritt zum 'PI'-Programm (Popular Investor — die Leute, die wir auf eToro kopieren können) viele Trader plötzlich einen Leistungseinbruch und große Veränderungen in ihrem Handelsstil verzeichnen. Vielleicht sollten wir sie einfach in Ruhe lassen und das tun lassen, was sie vorher gemacht haben :) Bin mir nicht sicher..."},
        {"type": "p", "text": "Als PI auf eToro muss man bis zu einem gewissen Grad mit den Leuten kommunizieren, die einen kopieren. Das steht sogar in den Regeln. Aber wenn wir Ergebnisse wollen, könnte eToro ihnen vielleicht einen optionalen 'Stumm'-Knopf geben :)"},
        {"type": "h3", "text": "Willst du sehen, wie es mir gerade geht?"},
        {"type": "p", "text": "Mein Profil und meine Statistiken ansehen"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-14-dec-2018 ----
updates["copy-trading-update-14-dec-2018"] = {
    "slug": "copy-trading-update-14-dezember-2018",
    "meta_description": "Copy Trading Update — 14. Dezember 2018. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 14. Dez. 2018 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Dezember 2018",
    "h1": "Copy Trading Update — 14. Dez. 2018",
    "content_blocks": [
        {"type": "p", "text": "Ich gehe die Statistikseiten jedes Traders durch und zeige ein bisschen die Handelshistorie, um eine Vorstellung von ihrer Methodik und Leistung zu bekommen. Alle Kopien sind neu, also ist es bei jedem noch früh, und ich beobachte, wie sie sich machen."},
        {"type": "p", "text": "Im Laufe von 2018 war ich viel passiver, weil ich meine Kopien nicht schließen und die Verluste all dieser Kryptos realisieren wollte, die das ganze Jahr über Geld verloren haben. Aber schließlich wurden diese Kopien geschlossen, und jetzt bin ich wieder viel aktiver und suche nach den besten Tradern für mein neues Portfolio."},
        {"type": "h3", "text": "Willst du sehen, wie es mir jetzt geht?"},
        {"type": "p", "text": "Meine Statistiken und mein aktuelles Portfolio"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-11-jan-2019 ----
updates["copy-trading-update-11-jan-2019"] = {
    "slug": "copy-trading-update-11-januar-2019",
    "meta_description": "Copy Trading Update — 11. Januar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 11. Jan. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Januar 2019",
    "h1": "Copy Trading Update — 11. Jan. 2019",
    "content_blocks": [
        {"type": "p", "text": "Hier ist mein Profil auf eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Jeder Handel birgt Risiken. Riskiere nur Kapital, dessen Verlust du verkraften kannst. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Resultate. Dieser Inhalt dient nur zu Bildungszwecken und ist keine Anlageberatung."},
        {"type": "p", "text": "Zunächst habe ich meinen Krypto-Trader \"SaveTheAnimals\" nicht mehr kopiert, weil im Moment alles etwas flach war und ich denke, dass das Geld anderswo besser eingesetzt werden kann. Ich halte aber weiterhin Ausschau nach Krypto-Tradern zum Kopieren, da ich glaube, dass die Zukunft von Kryptos immer noch riesig sein wird."},
        {"type": "p", "text": "Ich spreche auch über \"ChineseTiger\" — einen Trader, den ich erst kürzlich kopiert habe und der einige wirklich riskante Trades gemacht hat. Ich habe aufgehört, ihn zu kopieren, da er in nur wenigen Tagen über 10% von dem verloren hat, was ich bei ihm investiert hatte, und sein Risikomanagement praktisch nicht existent schien. Das ist nicht das, was ich für das Portfolio will — großes Risiko und große Schwankungen sind nichts mehr für mich. Ich bespreche seine Charts und wie es durchaus eine Logik hinter seinen Verlusttrades zu geben scheint, aber es ist einfach bei Weitem nicht der Handelsstil, den ich suche — viel zu riskant für mich."},
        {"type": "p", "text": "Ich rede auch darüber, dass mit den Statistiken etwas nicht zu stimmen scheint. Ich bin mir nicht sicher, was dort los ist, aber sie scheinen in ziemlich vielen Fällen falsch zu sein. eToro hat mir gesagt, ich soll Bescheid geben, wenn ich Fehler finde, also habe ich meine Bedenken an sie weitergegeben, und bisher haben sie sich nicht bei mir gemeldet. Meine Kopie von DazPanda zeigt auch unrealistische Statistiken, was ich bei DazPanda angesprochen habe, und er hat es auch bemerkt. Mal sehen, was passiert. Ich verstehe noch nicht vollständig, wie sie die Handelsstatistiken berechnen — es ist einfach sehr schwierig zu erkennen, was dort wirklich passiert."},
        {"type": "p", "text": "Ich habe auch den Trader 'Chocowin' kopiert, da ich kürzlich seine Statistiken neu analysiert habe und mich entschieden habe, ihm eine Chance zu geben..."},
        {"type": "h3", "text": "Willst du sehen, wie es mir geht?"},
        {"type": "p", "text": "Du kannst dir meine Statistiken hier ansehen :) Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Meine Statistiken..."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-13-jan-2019 ----
updates["copy-trading-update-13-jan-2019"] = {
    "slug": "copy-trading-update-13-januar-2019",
    "meta_description": "Copy Trading Update — 13. Januar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 13. Jan. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Januar 2019",
    "h1": "Copy Trading Update — 13. Jan. 2019",
    "content_blocks": [
        {"type": "p", "text": "13. Januar 2019 Ich habe zwei neue Trader kopiert — einer ist auf Forex spezialisiert, der andere handelt eine Reihe von Vermögenswerten, hauptsächlich aber Aktien."},
        {"type": "p", "text": "Hier ist mein Profil auf eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Jeder Handel birgt Risiken. Riskiere nur Kapital, dessen Verlust du verkraften kannst. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Resultate. Dieser Inhalt dient nur zu Bildungszwecken und ist keine Anlageberatung."},
        {"type": "h3", "text": "Warum habe ich sie kopiert?"},
        {"type": "p", "text": "Also, Citadelpoint scheint einfach Ahnung zu haben. Er ist ein hochqualifizierter Zahlenmensch und arbeitet tatsächlich in der Handelsbranche — ich habe eine seiner wissenschaftlichen Arbeiten gelesen und sie war extrem klug. Ich weiß, er hat nicht viel Handelshistorie auf eToro, aber ich will ihm eine Chance geben und sehen, wie es läuft..."},
        {"type": "p", "text": "Chocowin hat eine nachgewiesene Erfolgsbilanz — ich hatte sein Profil tatsächlich vor ein paar Monaten schon einmal überprüft und mich gegen das Kopieren entschieden, aber nachdem ich alles neu analysiert habe, habe ich mich entschieden, ihn zu kopieren und seinen Fortschritt zu beobachten. Er handelt hauptsächlich Aktien, beschränkt sich aber nicht darauf — es gibt auch ab und zu Indizes und Rohstoffe in seinem Portfolio, und er scheint die Zusammenhänge zwischen den verschiedenen Vermögenswerten zu verstehen ('Korrelationen'), was ihm hoffentlich ermöglicht, von verschiedenen Marktbedingungen zu profitieren. Denn wenn ein Vermögenswert nicht gut performt, weiß er, zu welchem anderen er wechseln muss, um Gewinne zu erzielen. Wir werden sehen!"},
        {"type": "p", "text": "Seit einiger Zeit meide ich Aktien-Trader, weil ich mir Sorgen über den Buy-and-Hold-Ansatz gemacht habe, den viele Trader 2017 verwendet haben... Was passiert, wenn der Abschwung, den so viele vorhersagen, tatsächlich kommt — ich will kein Portfolio voller Trader, die einfach abwarten und mein ganzes Geld verlieren. Also habe ich nach jemandem gesucht, der zwar Aktienexposure hat, aber auch in der Lage ist, Verluste zu begrenzen und zu anderen Anlageklassen zu wechseln, sollte sich der Marktkontext ändern. Ich hoffe, dass Chocowin dieser jemand ist."},
        {"type": "h3", "text": "Willst du sehen, wie es mir heute geht?"},
        {"type": "p", "text": "Sieh dir meine aktuellen Statistiken und meine Performance hier an... Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Hier ansehen"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-29-jan-2019 ----
updates["copy-trading-update-29-jan-2019"] = {
    "slug": "copy-trading-update-29-januar-2019",
    "meta_description": "Copy Trading Update — 29. Januar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 29. Jan. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Januar 2019",
    "h1": "Copy Trading Update — 29. Jan. 2019",
    "content_blocks": [
        {"type": "p", "text": "29. Januar 2019 Hier ist ein weiteres Update über meine Copy-Trading-Abenteuer auf eToro. Diesmal stelle ich einen neuen Trader im Portfolio vor — Olivier Danvel."},
        {"type": "p", "text": "Hier ist mein Profil auf eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Er ist ein sehr risikoarmer Trader mit ein paar Jahren Geschichte und statistisch gesehen keinerlei monatlichen Verlusten. Das habe ich noch nie gesehen — normalerweise gibt es ziemlich viele Verluste, wenn man sich die Statistiken über 3 Jahre ansieht, aber nicht so bei Olivier."},
        {"type": "p", "text": "Er hatte sein Profil anscheinend bis vor Kurzem privat gehalten (ich habe gefragt, warum ich ihn noch nie auf der Seite gesehen habe) und jetzt, wo er sichtbar ist, denke ich, werden die Kopierer in Scharen kommen. Er handelt hauptsächlich Forex und wartet viel länger als ich es je gesehen habe auf die richtigen Einstiegspunkte in Trades — er ist vorsichtig und geduldig — zwei sehr bewundernswerte Eigenschaften bei einem Trader für mich heutzutage."},
        {"type": "p", "text": "Ich tendiere immer mehr dazu, die sichereren, risikoärmeren Trader auszuwählen, um die Dinge so stabil wie möglich zu halten. Das bedeutet geringere Gewinne zu erwarten, aber ehrlich gesagt hat mir die Jagd nach großen Gewinnen nie etwas gebracht..."},
        {"type": "p", "text": "Jeder Handel birgt Risiken. Riskiere nur Kapital, dessen Verlust du verkraften kannst. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Resultate. Dieser Inhalt dient nur zu Bildungszwecken und ist keine Anlageberatung."},
        {"type": "h3", "text": "Willst du meine Statistiken sehen?"},
        {"type": "p", "text": "Mein Profil"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-03-feb-2019 ----
updates["copy-trading-update-03-feb-2019"] = {
    "slug": "copy-trading-update-03-februar-2019",
    "meta_description": "Copy Trading Update — 03. Februar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 03. Feb. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Februar 2019",
    "h1": "Copy Trading Update — 03. Feb. 2019",
    "content_blocks": [
        {"type": "p", "text": "3. Februar 2019 Mein neuestes Copy-Trading-Update! Es ist Sonntagabend, die Märkte öffnen in etwa sechs Stunden wieder, und es wird fast Zeit für eine neue Handelswoche."},
        {"type": "p", "text": "Hier ist mein Profil auf eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Jeder Handel birgt Risiken. Riskiere nur Kapital, dessen Verlust du verkraften kannst. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Resultate. Dieser Inhalt dient nur zu Bildungszwecken und ist keine Anlageberatung."},
        {"type": "h3", "text": "Was ist also passiert?"},
        {"type": "p", "text": "Es war bisher ein etwas holpriger Start in den Monat, da 'DazPanda' — ein sehr neuer Zugang zum Portfolio — mich in wenigen Tagen etwa 1% meines gesamten Portfoliowerts gekostet hat... Es lief nicht gut. Ein weiterer Trader, Manusabrina, hat ebenfalls ziemlich schlecht abgeschnitten, und ich frage mich langsam, ob es Zeit ist, diese beiden Kopien zu beenden."},
        {"type": "p", "text": "Es gab gerade eine große Entscheidung und Stimmungsänderung rund um die Zinssätze in den USA, und ich weiß, dass das einen großen Einfluss darauf haben kann, wie alle handeln, also warte ich im Moment ein wenig ab, ob diese beiden Trader von einem Trendwechsel profitieren können, den die neuen Zinsinformationen auslösen könnten..."},
        {"type": "h3", "text": "Wie verändert sich das Portfolio?"},
        {"type": "p", "text": "Die anderen im Portfolio haben alle gut gehandelt, wobei die meisten niedrigere Risikoscores und Volatilität (Schwankungen nach oben und unten) haben als DazPanda und Manusabrina. Ich schaue mich nach anderen Tradern zum Kopieren um, und bei meiner Suche bin ich tatsächlich zu einigen der älteren Trader zurückgekehrt — diejenigen, die hoch im Kurs standen und beliebt waren, als ich 2016 angefangen habe, eToro zu nutzen. Als das Krypto-Fieber 2017 einsetzte, wurden diese stabileren Trader vergessen, da alle (einschließlich mir) die riesigen Gewinne der Krypto-Trader sahen und aufsprangen."},
        {"type": "p", "text": "Jetzt aber suche ich gezielt nach risikoärmeren Leuten zum Kopieren, und Berrau ist definitiv einer, den ich im Auge habe. Ich habe auch nochmal CatyFX angeschaut, den ich 2017 tatsächlich für kurze Zeit kopiert habe, bevor ich die Kopie gestoppt habe, um mein Geld in den Krypto-Bereich zu stecken... Der andere Trader, den ich mir ansehe und den ich wirklich kopieren möchte, ist Harshsmith, der hauptsächlich Aktien handelt, aber nach eigener Aussage auf mögliche Abschwünge vorbereitet ist und wirklich gutes Risikomanagement auf seinen Handel und sein Portfolio anwendet. Ich würde auch gerne sehen, ob die neuen Zinsbewegungen in Amerika von jemandem wie ihm ausgenutzt werden können..."},
        {"type": "p", "text": "Alle drei haben sehr niedrige Drawdowns, innerhalb meiner groben 15%-Grenze, was großartig ist. Harshsmith sieht aber wie mein wahrscheinlichster Kandidat aus, obwohl es durch das Kopieren von ihm etwas schwieriger wird, mich zu kopieren, wegen der Mindesthandelsgrößen-Regel beim Copy Trading. Das erkläre ich in einem anderen Video, da es etwas kompliziert ist. Ich denke noch nach. Als Trader finde ich ihn eine gute Wahl."},
        {"type": "h3", "text": "Willst du meine aktuelle Performance sehen?"},
        {"type": "p", "text": "Meine Performance"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-07-feb-2019 ----
updates["copy-trading-update-07-feb-2019"] = {
    "slug": "copy-trading-update-07-februar-2019",
    "meta_description": "Copy Trading Update — 07. Februar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 07. Feb. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Februar 2019",
    "h1": "Copy Trading Update — 07. Feb. 2019",
    "content_blocks": [
        {"type": "p", "text": "7. Februar 2019 Es war eine harte Woche — einer meiner Trader hat seinen Stop Loss ausgelöst, und ich musste einen anderen manuell schließen..."},
        {"type": "p", "text": "Hier ist mein Profil auf eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Jeder Handel birgt Risiken. Riskiere nur Kapital, dessen Verlust du verkraften kannst. Vergangene Ergebnisse sind kein Hinweis auf zukünftige Resultate. Dieser Inhalt dient nur zu Bildungszwecken und ist keine Anlageberatung."},
        {"type": "h2", "text": "Ein Copy Stop Loss wurde ausgelöst..."},
        {"type": "p", "text": "Der Trader 'DazPanda' wurde aus meinem Portfolio entfernt! Er hat tatsächlich meinen Copy Stop Loss ausgelöst — eine Funktion, die automatisch deine Kopie eines Traders stoppt, wenn dieser einen vordefinierten Geldbetrag verliert. Als ich sah, dass der Copy Stop Loss ausgelöst wurde, hatte ich das Gefühl, etwas zu verpassen, aber insgesamt ist es eine gute Sache, da es mit meinen Risikomanagement-Ideen übereinstimmt."},
        {"type": "p", "text": "Ein weiterer Trader, 'Manusabrina', ist ebenfalls aus dem Portfolio verschwunden, obwohl ich diese Kopie manuell gestoppt habe, da sein Risikoscore auch zu hoch war und ich wirklich ein stabileres Portfolio möchte."},
        {"type": "h3", "text": "Was ich als Nächstes getan habe"},
        {"type": "p", "text": "Danach habe ich 'Berrau' und 'Harshsmith' kopiert und dann wieder entkopiert — es war ein bisschen Panik, da ich das Geld aus den gestoppten DazPanda- und Manusabrina-Kopien so schnell wie möglich wiederverwendet wollte. Panik ist aber nie gut, also habe ich die Mittel einfach in meine bestehenden Trader reinvestiert und werde mir Zeit nehmen, um darüber nachzudenken, wen ich als Nächstes kopiere."},
        {"type": "p", "text": "Ich gehe die anderen Trader im Portfolio durch, rede über Aimstraders aktuelle Probleme und warum ich abwarte."},
        {"type": "h3", "text": "Statistik-Probleme"},
        {"type": "p", "text": "Ich habe gehört, dass Leute Probleme und Bedenken bezüglich der Statistiken auf eToro haben, und es gab viel Verwirrung darüber, welche Statistiken richtig sind und warum es bestimmte Widersprüche und unterschiedliche Ergebnisse gibt. Ehrlich gesagt bin ich mir immer noch nicht sicher, was los ist, aber ich gleiche jetzt das normale Handelsstastistik-Diagramm mit den geschlossenen Trades im 'Verlauf'-Bereich des Portfolios ab. Außerdem versuche ich, das mit dem Chart für jeden Trader abzugleichen, um ein vollständiges Bild zu bekommen. Ich halte euch auf dem Laufenden."},
        {"type": "p", "text": "Ich suche auch nach einem guten risikoarmen Rohstoff-Trader — falls du einen kennst, sag mir bitte Bescheid!"},
        {"type": "h3", "text": "Meine aktuelle Performance ansehen"},
        {"type": "p", "text": "Wie geht es mir heute? Hier nachschauen."},
        {"type": "p", "text": "Copy Trading stellt keine Anlageberatung dar. Der Wert deiner Investitionen kann steigen oder fallen. Dein Kapital ist gefährdet."},
        {"type": "p", "text": "Meine Statistiken..."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-14-feb-2019 ----
updates["copy-trading-update-14-feb-2019"] = {
    "slug": "copy-trading-update-14-februar-2019",
    "meta_description": "Copy Trading Update — 14. Februar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 14. Feb. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Februar 2019",
    "h1": "Copy Trading Update — 14. Feb. 2019",
    "content_blocks": [
        {"type": "h2", "text": "14. Februar 2019 Eine besorgniserregende Woche... Diese Woche war ein bisschen beunruhigend wegen eines meiner Trader — 'Citadelpoint', der die ganze Woche auf und ab ging..."},
        {"type": "p", "text": "Er hat USD/SEK mit 100% des Geldes, das ich bei ihm investiert hatte, gehebelt verkauft. Der Trade lief in die falsche Richtung und er hat innerhalb von 3 Tagen über 3% meines gesamten Portfoliowerts verloren... Beängstigend. Und als meine Statistiken fielen, sind auch die Leute, die mich kopieren, geflüchtet."},
        {"type": "h3", "text": "Werde ich Citadelpoint weiter kopieren?"},
        {"type": "p", "text": "Ich denke schon, dass Citadelpoint ein sehr kluger Kopf ist — er hat einen Doktortitel von Cambridge, wo er an der Vorhersage von Risikovolatilität gearbeitet hat. Aber diese Woche war beängstigend. Sein Risikoscore sprang auf 8 von 10. Letztendlich lag er mit der Richtung des Assets richtig, aber die Art, wie er handelt, ist einfach zu riskant für mein aktuelles Portfolio."},
        {"type": "p", "text": "Also... ich versuche gerade herauszufinden, ob ich ihn im Portfolio behalten soll oder nicht. Sein maximaler jährlicher Drawdown hat bereits die 15%-Marke überschritten, die ich bei den Leuten anstrebe, die ich kopiere... Kein gutes Zeichen. Um ihn also weiterhin kopieren zu können (ich denke, er ist talentiert), aber weniger seinem neuen riskanteren Verhalten ausgesetzt zu sein, habe ich den Anteil des Portfolios reduziert, der ihn kopiert."},
        {"type": "h2", "text": "Wie geht es den anderen Tradern in meinem Portfolio?"},
        {"type": "p", "text": "Das ist ein sehr bedeutsamer Wert, aber ich bin mir noch nicht ganz sicher, was ich mit ihm anfangen soll — ich werde ihn vorerst genau im Auge behalten und meine Exposure bei ihm im Portfolio reduzieren."},
        {"type": "p", "text": "Mir wurde auch gesagt, dass er möglicherweise keine Gebühren zahlen muss, weil er ein 'Islamisches Konto' hat, obwohl ich das noch überprüfen müsste."},
        {"type": "h3", "text": "Er scheint verkehrt herum zu handeln"},
        {"type": "p", "text": "Ich denke, wenn er all seine letzten Trades andersherum eröffnet hätte (zum Beispiel kaufen statt verkaufen oder verkaufen statt kaufen), hätte er tatsächlich eine Menge Geld verdient. Aber so ist es eben — ich kann seine Trades nicht im Detail steuern, und diese Leute scheinen sich nicht so schnell an veränderte Marktbedingungen anzupassen, also wird er wohl auf absehbare Zeit bei seiner aktuellen Strategie bleiben. Ich werde weiter beobachten und sehen, wie es in den kommenden Wochen läuft."},
        {"type": "h2", "text": "Mein Portfolio im Allgemeinen"},
        {"type": "p", "text": "Die meisten meiner Trader handeln Forex, um hoffentlich von den ständigen Marktbewegungen zu profitieren und größeren Abschwüngen bei Aktien aus dem Weg zu gehen, sollten diese eintreten."},
        {"type": "h3", "text": "Popular Investor sein"},
        {"type": "p", "text": "Jetzt, da ich Popular Investor auf eToro bin, fange ich an, darüber nachzudenken, wie ich die Stufen des PI-Sternesystems aufsteigen kann. Das würde bedeuten, 20.000 € auf meinem Handelskonto zu haben, und an diesem Punkt würde ich definitiv Trader kopieren wollen, die einen starken Fokus auf niedriges Risiko haben. Diese Überlegung beeinflusst jetzt wirklich alle meine Entscheidungen, wen ich kopiere. Es ist eine Sache, 500 € zu riskieren (obwohl ich das eigentlich auch nicht wirklich riskieren will), aber 20.000 € zu riskieren ist ein ganz anderes Level..."},
        {"type": "p", "text": "Also versuche ich wirklich, ein profitables Portfolio mit sehr niedrigem Risiko aufzubauen. Wir werden sehen, wie es läuft."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-20-feb-2019 ----
updates["copy-trading-update-20-feb-2019"] = {
    "slug": "copy-trading-update-20-februar-2019",
    "meta_description": "Copy Trading Update — 20. Februar 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 20. Feb. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Februar 2019",
    "h1": "Copy Trading Update — 20. Feb. 2019",
    "content_blocks": [
        {"type": "p", "text": "20. Februar 2019 Willkommen zu meinem neuesten Copy-Trading-Update, in dem ich mein Portfolio durchgehe und schaue, wie alles läuft..."},
        {"type": "h2", "text": "Aimstrader"},
        {"type": "p", "text": "Er hat wirklich ziemlich schlecht abgeschnitten — er eröffnet verschiedene Short-Positionen auf Indizes, wenn es Longs sein sollten, und eröffnet Longs, wenn es Shorts sein sollten... Anscheinend hatte er sich im Januar strenge Risikomanagement-Richtlinien gesetzt, aber er scheint diese selbst auferlegten Richtlinien zu durchbrechen. Das ist nicht gut, falls es stimmt."},
        {"type": "p", "text": "Gibt es also gute Gründe für die Trades, die er macht? Ich denke schon — er sucht nach Korrekturen basierend auf großen kürzlichen Preisbewegungen, aber er scheint das Timing einfach schlecht zu treffen und dann Verlusttrades länger zu halten, als er vielleicht sollte."},
        {"type": "p", "text": "Wenn ich mir die Charts der Assets ansehe, die er handelt, kann ich etwas grundlegende technische Analyse anwenden und sehen, dass es starke Unterstützungs- und Widerstandslinien gibt, in deren Nähe seine Assets gerade gehandelt werden. Im Grunde denke ich, ich kann nachvollziehen, warum er tut, was er tut, aber es läuft nicht gut und viele seiner Kopierer sind derzeit besorgt..."},
        {"type": "p", "text": "Obwohl Aimstrader mir Geld verloren hat, haben die anderen Trader in meinem Portfolio den Ausfall aufgefangen."},
        {"type": "h2", "text": "Citadelpoint"},
        {"type": "p", "text": "Er hat sich diese Woche viel besser geschlagen. Die großen riskanten Züge sind weg — ich habe den Betrag reduziert, mit dem ich ihn kopiere, und es hat sich in letzter Zeit gut entwickelt."},
        {"type": "p", "text": "Er nutzt kleinere Anteile seines Gesamtkontos und macht kürzere Trades und holt sich kleine Gewinne aus dem Markt. Insgesamt gute Nachrichten im Moment..."},
        {"type": "h2", "text": "Chocowin"},
        {"type": "p", "text": "Chocowin profitiert vom jüngsten Aktienanstieg und macht sich gut, obwohl ich nicht weiß, was er tun würde, wenn ein Bärenmarkt käme. Da müssen wir abwarten."},
        {"type": "h2", "text": "Alnayef"},
        {"type": "p", "text": "Er hat in letzter Zeit viele kleine Trades gemacht, was gut zu sehen ist — manchmal frage ich mich, ob er einfach verschwunden ist... Er scheint zeitweise zu verschwinden, und niemand weiß so recht, wohin er gegangen ist oder was los ist. Er taucht aber immer wieder auf und handelt dann eine Zeit lang viel häufiger, bevor er wieder verstummt."},
        {"type": "p", "text": "Einige seiner Trades sind immer noch sehr lange offen, und er hält sie weiterhin offen und wartet darauf, dass sie grün werden. Das ist nach wie vor ein Problem, das ich weiter beobachte. Ich möchte ihn vorerst nicht entkopieren, da ich denke, dass er immer noch risikoarm ist und in Zukunft potenziell profitabel sein könnte."},
        {"type": "h2", "text": "Olivier Danvel"},
        {"type": "p", "text": "Er hat das gemacht, was ich von ihm erwarte. Kleine Trades, warten auf die besten Einstiegspunkte (also Phasen mit sehr wenig Aktivität). Er hat ja auch gesagt, dass er das so machen würde, also habe ich es erwartet."},
        {"type": "p", "text": "Sein erster Trade war ein 3%-Trade, was innerhalb seiner Risikomanagement-Richtlinien liegt. Sein erklärtes Ziel ist etwa 1% Gewinn pro Monat, und bisher scheint er auf Kurs zu sein. Er ist einer der Leute, die ich mit dem höchsten Anteil meiner Mittel kopiere."},
        {"type": "h2", "text": "Analisisciclico"},
        {"type": "p", "text": "Er liegt diesen Monat bisher im Minus, hält sich aber an seinen risikoarmen Geldmanagement-Ansatz. Seine Trades liegen alle bei etwa 2-3% seiner Kontogröße, wie erwartet. Ich bleibe bei ihm — es gibt im Moment nichts, was Alarmglocken läuten lässt, also lasse ich ihn seine Methoden anwenden."},
        {"type": "h3", "text": "Hat Olivier Danvel seine Statistiken von einer anderen Plattform übertragen?"},
        {"type": "p", "text": "Ich habe ihn direkt gefragt, da ich gehört hatte, dass er das möglicherweise getan hat, und er gab eine etwas kryptische Antwort, sagte aber im Grunde, dass nein, er die ganze Zeit auf eToro war und nur irgendwie versteckt war. Ich bin mir nicht sicher, aber ich muss nehmen, was er sagt..."},
        {"type": "h3", "text": "Aimstrader stand ziemlich unter Beschuss wegen seines Handels..."},
        {"type": "p", "text": "Ich habe in letzter Zeit ein bisschen Mitleid mit Aimstrader. Der 'soziale' Teil von eToro kann manchmal ziemlich rau sein, und mit unbegründeten Gerüchten, dass er zwei vorherige Handelskonten auf eToro in den Sand gesetzt hat, war es eine schwere Zeit für ihn... Ich hoffe, er schafft die Wende."},
        {"type": "h3", "text": "Kommt ein Bärenmarkt?"},
        {"type": "p", "text": "Könnte sein — es gibt viele Leute, die darüber reden, dass es möglich ist, und einige sogar als Wahrscheinlichkeit. Das ist einer der Gründe, warum ich im Moment vor Aktien-Trades zurückschrecke — ich bin mir nicht sicher, wie schnell sie alle reagieren würden, wenn es schlecht läuft... Es könnte sein, dass Aimstrader wirklich auf den Bärenmarkt wartet und gerade etwas häufiger auf der falschen Seite der Trades erwischt wird. Ich bin mir nicht sicher..."},
        {"type": "h3", "text": "Popular Investor sein"},
        {"type": "p", "text": "Ich denke daran, einige Videos darüber zu machen, wie es ist, Popular Investor auf eToro zu sein, da es mich wirklich interessiert und vielleicht auch andere Leute daran Spaß hätten. Ich würde auch gerne einige Videos über das Affiliate-Dasein machen, also schauen wir mal, was daraus wird."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-01-mar-2019 ----
updates["copy-trading-update-01-mar-2019"] = {
    "slug": "copy-trading-update-01-maerz-2019",
    "meta_description": "Copy Trading Update — 01. März 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 01. März 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · März 2019",
    "h1": "Copy Trading Update — 01. März 2019",
    "content_blocks": [
        {"type": "p", "text": "1. März 2019 Welcher dieser Trader ist zu riskant?"},
        {"type": "p", "text": "Wenn ich mein Portfolio betrachte, sind da ein paar offensichtlich riskantere Trader drin, und ich frage mich langsam, ob das Risiko bei ihnen die mögliche Belohnung nicht wert ist..."},
        {"type": "p", "text": "Aber warum sollte das so sein? Risiko geht schließlich mit Rendite einher, also je höhere Renditen ich anstrebe, desto höheres Risiko sollte ich bereit sein zu akzeptieren. Das stimmt auch. Ein Trader wie Citadelpoint ist nur deshalb in meinem Portfolio, weil er sich mit den Märkten gut auszukennen scheint — ein gebildeter Mann mit fundierter Analysemethodik und einer Vergangenheit in der Risikoanalyse an der Universität Cambridge. Er ist aus guten Gründen im Portfolio (denke ich*). Aber sollte ich ihn dort behalten?"},
        {"type": "h2", "text": "Die Popular-Investor-Überlegungen"},
        {"type": "p", "text": "Das klingt eher nach einer geschäftlichen als nach einer Trading-Entscheidung, und das ist es auch wirklich... Kurz nachdem ich Popular Investor auf eToro wurde, habe ich ausgerechnet, dass ich potenziell viel mehr Geld als Popular Investor mit viel verwaltetem Vermögen verdienen könnte als durch mein eigentliches Trading. Warum ist das so?"},
        {"type": "p", "text": "Sagen wir, ich könnte 2% pro Monat machen (was im Vergleich zu Branchenstandards für Anlageprodukte eine sehr, sehr hohe Rendite ist). Wie viel müsste ich auf meinem Handelskonto haben, damit 2% Gewinn $1.000/Monat entsprechen?"},
        {"type": "p", "text": "2% von $10.000 = $200"},
        {"type": "p", "text": "2% von $20.000 = $400"},
        {"type": "p", "text": "2% von $40.000 = $800"},
        {"type": "p", "text": "2% von $50.000 = $1.000"},
        {"type": "p", "text": "Also, wenn ich jeden Monat 2% machen würde und hoffe, diese 2% kontinuierlich abzuheben, um davon zu leben, bräuchte ich $50.000 auf meinem Handelskonto. Das ist SEHR viel Geld..."},
        {"type": "h2", "text": "Wie könnte ich dieses Geld sonst mit dem eToro PI-Programm verdienen?"},
        {"type": "p", "text": "Nun, wenn ich das rote Stern 'Champion'-Level in eToros Popular-Investor-Programm erreichen kann, bekomme ich $1.000 pro Monat direkt von eToro."},
        {"type": "p", "text": "Mindestens $5.000 auf meinem Handelskonto und mindestens 10 Kopierer, die zusammen $150.000 bei mir investiert haben."},
        {"type": "p", "text": "Jetzt sage ich nicht, dass es einfach ist, diese Kopierer mit diesem verwalteten Vermögen zu bekommen... Aber es ist wahrscheinlich realistischer, als irgendwie $50.000 für mein Handelskonto aufzutreiben. Also ändert sich sofort meine Denkweise... Und plötzlich frage ich mich, ob diese riskanten Trader mit ihren Drawdowns potenzielle Kopierer abschrecken."},
        {"type": "p", "text": "Die Wahrheit ist, ich sollte mich eigentlich mehr um diese Drawdowns für mein eigenes Portfolio und meine Copy-Trading-Ziele sorgen. Aber ich scheine immer noch etwas von Gier geblendet zu sein, also setze ich mich höherem Risiko aus auf der Suche nach höheren Auszahlungen, und das geht häufig nach hinten los. Die Hoffnung, als PI mehr Geld zu verdienen (eigentlich Gier), überwiegt und überschreibt die Gier, die mich zu schlechten Risikoentscheidungen bei der Auswahl der zu kopierenden Trader führt :) Es ist ein Balanceakt, und ich bin mir noch nicht sicher, wo das Gleichgewicht liegt."},
        {"type": "h2", "text": "Sorgen um Handelsstatistiken"},
        {"type": "p", "text": "Ich mache mir plötzlich viel mehr Gedanken über meine Statistiken als Folge von all dem. Konsistenz ist jetzt das, was ich anstrebe. 2017 war es für mich okay, in einem Monat 30% Drawdown zu haben, wenn ich glaubte, dass es im nächsten Monat 60% nach oben schwingen würde. Meine Statistiken waren damals nicht auf die gleiche Weise wichtig."},
        {"type": "p", "text": "Insgesamt wollte ich 'große Gewinne' statt konstantem, kleinerem Wachstum. Natürlich wollte ich nie einen 30% Drawdown sehen! ABER mein Fokus lag damals viel mehr auf den großen Gewinnen, also solange ich glaubte, dass die Trader, die ich kopierte, oder meine eigenen Trades insgesamt Gewinner sein würden, war es mir egal, wie meine Statistiken auf dem Weg aussahen."},
        {"type": "h3", "text": "Gehe ich zu wenig Risiko ein? Oder mache ich mir zu viele Sorgen um die Handelsstatistiken?"},
        {"type": "p", "text": "Kann man zu sehr auf seine Handelsstatistiken fokussiert sein? Einige Leute haben sich kürzlich über einige PIs auf eToro beschwert und gesagt, sie seien zu besorgt um ihre Statistiken. Ist das möglich? Kann man zu besorgt um seine Statistiken sein? Schließlich ist das die Grundlage, auf der wir entscheiden, wen wir kopieren. Wir sind alle hier, um Geld zu verdienen, also warum sollten wir nicht extrem besorgt darüber sein, wie ein Trader bisher abgeschnitten hat..."},
        {"type": "p", "text": "Es stimmt, dass durchgehend grüne, konsistente Statistiken unsere beste Visitenkarte und Werbung als PIs sind. Es könnte aber auch stimmen, dass wir, wenn wir Trades verpassen und bestimmte Risiken nicht eingehen, nicht mehr wirklich natürlich handeln. Und das könnte bedeuten, dass wir unser eigenes Handelssystem stören, was uns am Ende Probleme bereiten wird."},
        {"type": "p", "text": "Das ist bei mir natürlich anders, da ich nur Copy Trading mache. Aber selbst in meinem Fall — verändere ich mein System zur Auswahl von Tradern so stark, dass es zu einem echten Problem werden könnte? Ich bin mir noch nicht sicher — mal sehen. Aber ich denke immer mehr wie ein 'Copy-Fondsmanager' als irgendetwas anderes. Ich bin mir noch nicht sicher, was ich davon halten soll. Es ist auf jeden Fall interessant. Und aufregend :) Wir werden sehen, wie es läuft."},
        {"type": "p", "text": "Ich weiß, dass ich beim Investieren des Geldes meiner Eltern auf eToro sofort die risikoarme Strategie gewählt habe. Kapitalerhalt war sofort mein Hauptanliegen. Ich würde mit ihrem Geld viel weniger Risiko eingehen als mit meinem eigenen. Und tatsächlich hat ihr Konto viel mehr Gewinn gemacht als meines. Das hat mich auch zum Nachdenken gebracht... Vielleicht sollte ich meinen eigenen Rat befolgen!"},
        {"type": "h2", "text": "Also... sollten ein paar Trader aus dem Portfolio fliegen?"},
        {"type": "p", "text": "Ich überlege ernsthaft, ein paar Trader aus meinem Portfolio zu entfernen — Aimstrader und Citadelpoint. Nun, Citadelpoint ist tatsächlich der am besten performende Trader in meinem Portfolio. Aber er ist auch bei Weitem der riskanteste... Behalte ich ihn wegen der potenziellen Gewinne? Oder werde ich ihn los wegen der potenziellen Verluste, die er auch verursachen könnte, wenn die Dinge schieflaufen?"},
        {"type": "p", "text": "Das wäre eine tolle Lösung, aber leider habe ich nicht genug zusätzliches Geld, um es meinem Portfolio hinzuzufügen. Ich müsste viel mehr Geld hinzufügen, als ich habe, damit Citadelpoint etwa 3% meines Portfolios ausmacht. Ich denke, bei 3% meines Portfolios würde ich mich wohl fühlen, ihn mit meinen aktuellen Risikozielen zu kopieren... Aber ich habe einfach nicht genug Mittel, um mein Portfolio auf diese Weise umzustrukturieren. Zumindest nicht im Moment."},
        {"type": "p", "text": "Ich bin mir nicht sicher, was ich tun werde... Aber ich tendiere dazu, dass ihn fallen zu lassen die klügste Entscheidung wäre."},
        {"type": "risk_warning"}
    ]
}

# Save part 1 and continue building
# We'll add the rest of the updates next

# ---- copy-trading-update-13-mar-2019 ----
updates["copy-trading-update-13-mar-2019"] = {
    "slug": "copy-trading-update-13-maerz-2019",
    "meta_description": "Copy Trading Update — 13. März 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 13. März 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · März 2019",
    "h1": "Copy Trading Update — 13. März 2019",
    "content_blocks": [
        {"type": "h2", "text": "13. März 2019 Die riskantesten Trader gewinnen immer noch in meinem Portfolio... Die zwei riskantesten Trader in meinem Portfolio — Citadelpoint und Aimstrader — machen mir IMMER NOCH das meiste Geld, obwohl ich die Kopierbeträge reduziert habe und sie jetzt mit niedrigeren Anteilen meines Portfolios kopiere als die anderen Trader darin..."},
        {"type": "h2", "text": "Alnayef hält Trades immer noch sehr lange offen..."},
        {"type": "p", "text": "Du erinnerst dich vielleicht, wie ich über den Trader Alnayef in meinem Portfolio gesprochen habe. Er ist derjenige, der Trades sehr lange offen hält und jede Menge Gebühren ansammelt. Nun, er macht es immer noch."},
        {"type": "p", "text": "Ich glaube, er eröffnet einfach Trades und wartet dann so lange, bis der Trade grün wird. Das klingt okay, aber es verursacht viele Übernacht- und Wochenendgebühren, da er Hebel bei seinen Trades einsetzt und die Gebühren deshalb anfallen."},
        {"type": "p", "text": "Es könnte daran liegen, dass er ein 'Islamisches Konto' hat — er muss die Gebühren nicht zahlen, aber ich schon. Das ist allerdings noch nur ein Gerücht, ich habe noch nicht nachgeschaut, was ein 'Islamisches Konto' wirklich beinhaltet. Ich würde mir vorstellen, dass eToro einen anderen Weg gefunden hat, mit Leuten mit diesen sogenannten 'Islamischen Konten' Geld zu verdienen, also gibt es möglicherweise andere Kosten, die ihm berechnet werden, aber mir nicht."},
        {"type": "p", "text": "Bin mir nicht sicher... Ich bleibe aber vorerst bei ihm. Ich hoffe, dass sich etwas ändert und diese Trades grün werden oder er anfängt, neue gewinnende Trades zu machen."},
        {"type": "h2", "text": "Aimstrader"},
        {"type": "h2", "text": "Was tun mit dem Geld, das ich bei Aimstrader kopiert hatte?"},
        {"type": "p", "text": "Ich wollte einen neuen Trader namens 'Harshsmith' kopieren. Ich beobachte seine Performance schon eine Weile und er ist einer der Trader, die mich am meisten interessieren. Aber es gibt ein Problem mit dem Geld, das ich zum Kopieren bräuchte."},
        {"type": "p", "text": "Es hat mit den 'Mindesthandelsgrößen'-Beschränkungen für Copy Trading auf eToro zu tun."},
        {"type": "h3", "text": "Was ist die Mindesthandelsgröße?"},
        {"type": "p", "text": "Die Mindesthandelsgröße ist der kleinste Betrag, den du bei einem Trade verwenden kannst. Beim Copy Trading funktioniert das ganz anders als beim normalen manuellen Handel (wenn du selbst handelst)."},
        {"type": "p", "text": "eToro hat Standard-Mindesthandelsgrößen für alle verschiedenen Anlageklassen festgelegt, die auf ihrer Seite gehandelt werden können. Wenn du in ihren Hilfebereich gehst und 'Mindesthandelsgröße' eingibst, siehst du die Liste mit allen Details für Aktien, ETFs, Kryptos, Indizes, Rohstoffe usw."},
        {"type": "p", "text": "Beim Copy Trading funktioniert es ein wenig anders. Wenn du jemanden kopierst und er einen Trade macht, machst du auch einen Trade. Sagen wir, er setzt 10% seines Gesamtgeldes auf einen Apple-Trade. Du als Kopierer setzt 10% DES GELDES, MIT DEM DU IHN KOPIERT HAST, auf denselben Apple-Trade."},
        {"type": "p", "text": "Wenn er gekauft hat, hast du gekauft; wenn er Hebel benutzt hat (oder nicht), tust du es auch. Der Unterschied liegt im Geld, das tatsächlich für den Trade verwendet wird. Es funktioniert als Prozentsatz."},
        {"type": "p", "text": "Wenn er einen neuen Trade macht, versucht eToro, denselben Trade für dich zu eröffnen — das ist das Schöne am Kopieren von Tradern. Es ist automatisch. Aber wenn es versucht, den Trade zu eröffnen, und der resultierende Trade in deinem Konto weniger als $1 betragen würde, wird er einfach nicht für dich eröffnet. Die Mindesthandelsgröße für kopierte Trades beträgt $1."},
        {"type": "h3", "text": "Ein schnelles Beispiel..."},
        {"type": "p", "text": "Du kopierst Trader A"},
        {"type": "p", "text": "Trader A kauft Apple-Aktien mit 0,3% seines gesamten Kontogeldes."},
        {"type": "p", "text": "Du hast Trader A mit dem Mindestkopierbetrag von $200 kopiert (zum Zeitpunkt dieses Artikels)."},
        {"type": "p", "text": "eToro versucht, eine exakte Kopie des Apple-Trades für dich zu eröffnen. Apple-Aktien kaufen, mit 0,3% der $200, die du bei Trader A kopiert hast."},
        {"type": "p", "text": "0,3% von $200 = 60 Cent. Das ist unter $1, also wird der Trade nicht eröffnet..."},
        {"type": "h2", "text": "Ist das das Problem beim Kopieren von Harshsmiths Trades?"},
        {"type": "p", "text": "Ja. Er hat zuvor gesagt, dass er mindestens 0,24% seiner Kontogröße für einen neuen Trade verwendet. Wenn ich ihn also nur mit $200 kopiere, kann ich, wie du im vorherigen Beispiel gesehen hast, nicht alle seine zukünftigen Trades kopieren. Alles unter einem 0,5%-Trade, den er in Zukunft eröffnet, kann ich nicht kopieren..."},
        {"type": "p", "text": "0,5% von $200 = $1 (das Minimum, mit dem ich einen kopierten Trade eröffnen kann)"},
        {"type": "p", "text": "Also habe ich nachgerechnet und herausgefunden, dass ich Harshsmith mit $460 kopieren müsste, um sicherzustellen, dass selbst wenn er in Zukunft einen Trade mit 0,24% seiner gesamten Kontogröße macht, ich diesen Trade auch automatisch eröffne, da er über $1 liegen wird."},
        {"type": "p", "text": "Im Moment kann ich es mir nicht leisten, ihn mit so viel zu kopieren, also kann ich ihn noch nicht kopieren. Das ist wirklich schade, aber Mathematik ist Mathematik und dagegen kann man nichts sagen :)"},
        {"type": "p", "text": "Ich will ihn aber definitiv in Zukunft kopieren, da er sehr niedrige Risikoscores hat (aktuell 1 von 10 möglichen!). Er handelt Aktien, scheint aber auch für den Fall eines Bärenmarktes vorzuplanen. Sein maximaler jährlicher Drawdown liegt unter meinem 15%-Ziel, und er ist ein sehr aktiver und scheinbar kompetenter Trader."},
        {"type": "h2", "text": "Und die anderen Trader in meinem Portfolio?"},
        {"type": "p", "text": "Sie ticken so ziemlich stetig vor sich hin und verdienen generell langsam Geld. Mein Fokus liegt wirklich darauf, was ich mit den riskanteren machen soll und wie ich das Problem der Portfolio-Umschichtung löse, wenn ich kein zusätzliches Geld auf mein Konto einzahlen kann. Ich kann es einfach nicht, also muss ich vorerst abwarten."},
        {"type": "p", "text": "Daumen drücken für die nächsten Wochen. Mein 15% Copy Stop Loss ist allerdings bei jedem der Trader, die ich kopiere, immer noch aktiv. Das bedeutet, selbst wenn sie anfangen, katastrophale Verluste zu machen, wird die Kopie einfach automatisch beendet. Es wäre trotzdem keine tolle Situation, also hoffe ich, dass sie sicher bleiben, bis ich mehr Geld einzahlen kann..."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-26-mar-2019 ----
updates["copy-trading-update-26-mar-2019"] = {
    "slug": "copy-trading-update-26-maerz-2019",
    "meta_description": "Copy Trading Update — 26. März 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 26. März 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · März 2019",
    "h1": "Copy Trading Update — 26. März 2019",
    "content_blocks": [
        {"type": "h2", "text": "26. März 2019 Ich habe wieder einen meiner Trader gewechselt! Ich habe Analisisciclico gegen Berrau getauscht. Berrau ist drin, und Analisisciclico ist raus..."},
        {"type": "p", "text": "Beide Trader haben ungefähr die gleichen Risikoscores und konzentrieren sich auf den Forex-Handel. Von den beiden kann ich bei Berrau einfach mehr Geschichte sehen, also ist er die sicherere Wahl. Ich werde Analisisciclico vielleicht in Zukunft wieder kopieren, wenn ich mehr Geld habe, aber vorerst gehe ich mit Berrau."},
        {"type": "h2", "text": "Wie geht es den anderen Tradern?"},
        {"type": "p", "text": "Citadelpoint liegt immer noch klar in Führung und verdient mir das meiste Geld. In letzter Zeit war sein Risikomanagement super: weniger Hebel, Vermeidung großer Nachrichtenereignisse, regelmäßige Gewinnmitnahmen und Begrenzung von Verlierern."},
        {"type": "p", "text": "Ich habe tatsächlich jedes Mal, wenn er $10 neue Gewinne für mich macht, Geld aus meiner Kopie bei ihm abgezogen und diese Gewinne meinen risikoärmeren Tradern hinzugefügt. Es fühlt sich sehr kontraintuitiv an, da es so ist, als würde man den besten Performer bestrafen, aber es hat einen Grund... Es ist Teil meiner Niedrigrisiko-Strategie, also mache ich vorerst weiter."},
        {"type": "p", "text": "Das Ziel ist nach wie vor, die Exposure meines Portfolios gegenüber ihm zu reduzieren, damit ich nicht zu stark betroffen bin, wenn sein riskantes Verhalten mal in die falsche Richtung geht. Möge seine Siegesserie aber weitergehen! Es ist unglaublich."},
        {"type": "h2", "text": "Chocowin handelt ebenfalls hervorragend"},
        {"type": "p", "text": "Chocowin hat auch außergewöhnlich gut gehandelt, stetige Gewinne gemacht und eine Reihe von Anlageklassen gehandelt. Er hat Gelegenheiten genutzt, wie der Markt sie bietet, was großartig ist. Ich bin immer sehr beeindruckt davon, wie manche Trader die Korrelationen zwischen Vermögenswerten zu verstehen scheinen."},
        {"type": "p", "text": "Sie können von Rohstoffen zu Aktien zu Forex wechseln, verstehen die Zusammenhänge zwischen allem und nutzen ihr Verständnis, um profitable Handelsideen zu entwickeln. Das ist beeindruckend und gut zu sehen."},
        {"type": "h2", "text": "Ist Olivier Danvel immer noch im Grünen?"},
        {"type": "p", "text": "Ja, ist er :) Er hat diesen Monat etwa 1% verdient, was im Grunde sein Monatsziel ist. Olivier lässt sich weiterhin Zeit mit seinen Einstiegspunkten — er stürzt sich nicht in Trades. Er setzt, soweit ich das bisher sehen kann, auf Timing und begrenzte Exposition."},
        {"type": "p", "text": "Er nutzt einen kleinen Anteil seiner Kontogröße pro Trade, kauft sich langsam in Trades ein und scheint auch definierte Ausstiegsziele zu haben. All das hilft ihm, seine Risikoscores wirklich niedrig zu halten."},
        {"type": "p", "text": "Er macht sich gut, und seine Konstanz ist weiterhin sehr beruhigend. Die Märkte sind volatil, Trading ist riskant, aber Herr Danvel scheint eine Methode gefunden zu haben, das alles ziemlich stabil zu durchsegeln. Ausgezeichnet."},
        {"type": "h2", "text": "Macht Alnayef immer noch Sorgen?"},
        {"type": "p", "text": "Ja — er hält immer noch an einigen sehr alten Trades fest — hält sie offen, bis sie grün werden. Die Gebühren steigen und die Trades sind noch nicht profitabel. Ich denke, er hatte in letzter Zeit etwas Pech, da viele der Trades, die er eröffnet hat, gegen ihn gelaufen sind. Das Problem ist, dass er die Verlust-Trades offen hält und damit das Kapital bindet, das ich zum Kopieren verwendet habe."},
        {"type": "p", "text": "Irgendwann sehe ich es so weit kommen, dass das gesamte Geld, das ich bei ihm investiert habe, in Verlust-Trades gebunden ist. Bis jetzt hatte er noch einige zusätzliche Mittel verfügbar, um kleine profitable Nebentrades zu machen..."},
        {"type": "p", "text": "Der Zeitpunkt nähert sich aber, an dem er keine zusätzlichen Mittel zum Handeln hat, weil alles gebunden ist. Das wäre eine wirklich nicht gute Situation, da es keinen Spielraum mehr gäbe. Sehr frustrierend... Ich kopiere ihn weiterhin, aber es gibt eine zunehmende Anzahl von Kommentaren, die fragen warum, angesichts seiner jüngsten Performance. Ich werde noch etwas abwarten..."},
        {"type": "h2", "text": "Wie macht sich der neue Trader Berrau?"},
        {"type": "p", "text": "Es ist eine dieser schwierigen Situationen, wo man einen neuen Trader kopiert, genau wenn er anfängt zu verlieren. Es ist psychologisch schwierig, rote statt grüne Ergebnisse zu sehen, aber das ist nicht immer der beste Indikator für das, was passiert..."},
        {"type": "p", "text": "Wenn ich zum Beispiel Alnayef betrachte, war sein Gewinn für mich viel höher und ist in den letzten Wochen deutlich gesunken. Wenn ich das Geld, das er verloren hat, mit den Gebühren kombiniere, die er mir verursacht hat, denke ich, dass Berrau eigentlich immer noch besser abschneidet als Alnayef. Aber wenn man Grün sieht, auch wenn es weniger Grün ist als vorher, ist es psychologisch immer noch einfacher als jede Menge Rot."},
        {"type": "p", "text": "Es ist aber kein großartiger Indikator dafür, wie gut es allen vergleichsweise geht. Ich bleibe bei Berrau und gebe ihm die Zeit und den Raum zu zeigen, was er kann. Er war tatsächlich einer der ersten Popular Investors, die ich auf eToro gesehen habe, als ich 2016 beigetreten bin."},
        {"type": "p", "text": "Damals war er der Superstar der Plattform, aber inmitten der Achterbahn / Raketenfahrt des Krypto-Booms 2017 geriet sein risikoarmer Ansatz schnell aus der Mode. 2018 war eine andere Geschichte. So viele von uns sahen die Krypto-Gewinne in Verluste umschlagen, und die Aufmerksamkeit verschob sich zurück zu Stabilität und Historie. Ich bin eigentlich froh, ihn zu kopieren — ich suche gerade wirklich nach Konsistenz und Stabilität."},
        {"type": "h2", "text": "Das Portfolio im Allgemeinen"},
        {"type": "p", "text": "Im Moment läuft es, denke ich, gut. Mein Risikoscore sinkt, ebenso wie mein maximaler jährlicher Drawdown — es wird stabiler und beginnt, nach oben zu drehen :)"},
        {"type": "p", "text": "Ich verschiebe weiterhin mein Vermögen von den riskanteren Tradern in meinem Portfolio zu den risikoärmeren. Das fühlt sich immer noch seltsam an, da die riskanteren alle anderen übertroffen haben, aber es ist Teil des Plans, also bleibe ich dabei. Alles in allem gefällt mir, wie die Dinge im Moment laufen."},
        {"type": "h2", "text": "Danke an Lloyd Bazaar!"},
        {"type": "p", "text": "Ich habe diese Woche eine sehr nette Nachricht bekommen, denn anscheinend hat ein anderer YouTuber namens Lloyd Bazzar, der einen Kanal namens Financial Freedom 101 hat, mich auf seinem Kanal erwähnt. Danke Lloyd!"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-04-apr-2019 ----
updates["copy-trading-update-04-apr-2019"] = {
    "slug": "copy-trading-update-04-april-2019",
    "meta_description": "Copy Trading Update — 04. April 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 04. April 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · April 2019",
    "h1": "Copy Trading Update — 04. April 2019",
    "content_blocks": [
        {"type": "h2", "text": "4. April 2019 Mein Portfolio hat einen Risikoscore von 2! Zum ersten Mal ist mein Risikoscore tatsächlich auf 2 von 10 gesunken. Das ist fantastisch :) Mein ganzes Ziel ist es gerade, ein stabiles, risikoarmes Copy-Trading-Portfolio aufzubauen, und es funktioniert."},
        {"type": "p", "text": "Nun, ich kopiere 5 verschiedene Trader, also handeln sie alle unterschiedlich. Das bedeutet, dass sie wahrscheinlich nicht alle zur gleichen Zeit genau die gleichen Handelsentscheidungen treffen. Das hat zu einem viel diversifizierteren Portfolio geführt. Meine Eier sind nicht alle in einem Korb, also ist es unwahrscheinlich, dass alle gleichzeitig 'falsch liegen'..."},
        {"type": "p", "text": "Dazu kommt, dass sie alle selbst risikoarme Trader sind. Es ist also wie zwei Schichten Risikofokus. Da sind meine Trader selbst, die alle gutes Risikomanagement anwenden und primär darauf abzielen, ihr Kapital zu erhalten. Sie sind alle historisch profitabel und haben nachgewiesene Erfolgsbilanzen."},
        {"type": "p", "text": "Dann bin da ich, der all diese risikoarmen Leute in sein Portfolio packt, Diversifikation hinzufügt und einen 15% Copy Stop Loss auf jeden von ihnen anwendet. Alles in allem ist es ein gutes System, das sicherstellen soll, dass das Geld, das ich bei eToro einzahle:"},
        {"type": "p", "text": "A: So sicher wie möglich ist (es ist unwahrscheinlich, dass sie auf riesige Verlustserien geraten)."},
        {"type": "p", "text": "B: In Zukunft profitabel eingesetzt wird."},
        {"type": "p", "text": "Ausgezeichnet :) Es ist das Gegenmittel zur wilden Fahrt und den großen Schwankungen der Boom-Bust-Trading-Mentalität. Mal sehen, wie es läuft. Mein Ziel ist immer noch, ein Portfolio aufzubauen, in das ich gerne $20.000 stecken würde. Das ist für mich SEHR viel Geld, also muss ich so sicher wie möglich sein, dass es sicher wäre. Meine Nerven könnten es nicht anders verkraften..."},
        {"type": "h2", "text": "Wie läuft das Portfolio?"},
        {"type": "h3", "text": "Citadelpoint liegt immer noch vorne!"},
        {"type": "p", "text": "Citadelpoint dominiert weiterhin die Gewinne in meinem Portfolio und macht Profite als gäbe es kein Morgen. Er schneidet Verlierer früh ab, nimmt die Gewinne gut mit und macht das regelmäßig. Er ist gerade wie eine Gelddruckmaschine, mit vielen kleinen Gewinnen."},
        {"type": "p", "text": "Sein Risikoprofil ist immer noch höher als das, was ich für mein Portfolio anstrebe, und ich habe den Betrag, mit dem ich ihn kopiere, reduziert. Ich hoffe aber, dass er weiterhin sicher handelt, denn es wäre sehr schade, ihn als einen meiner Trader zu verlieren."},
        {"type": "p", "text": "Er hat darüber gesprochen, möglicherweise Teil des Popular-Investor-Programms auf eToro zu werden, was toll wäre, aber wir werden sehen, ob das klappt. Ich glaube, er arbeitet in der Finanzbranche, also könnte es davon abhängen, was sein Arbeitgeber sagt..."},
        {"type": "p", "text": "Der Beitritt zum PI-Programm würde seinen Handel auf bestimmte Weise einschränken — weniger erlaubter Hebel, kleinere Handelsgrößen empfohlen. Das will er vielleicht nicht, aber für mich als Kopierer wäre es sehr willkommen, da es sein Risikoprofil deutlich senken würde. Wir werden sehen..."},
        {"type": "h3", "text": "Chocowin, mein Aktien-Trader"},
        {"type": "p", "text": "Chocowin hat in letzter Zeit auch sehr gut abgeschnitten. Er hat kürzlich alle seine Trades gestoppt und viel mehr Geld auf sein Konto eingezahlt. Das lag am Popular-Investor-Programm — er ist gerade vom 'Rising Star' zum 'Champion' Level Investor aufgestiegen."},
        {"type": "p", "text": "Das Popular-Investor-Programm verlangt, dass man einen bestimmten Betrag auf dem eigenen Handelskonto hat, um die nächste Stufe zu erreichen, also hat Chocowin alle seine Trades geschlossen, das erforderliche Geld eingezahlt und wieder angefangen zu handeln, damit wir alle saubere Kopien von ihm haben."},
        {"type": "p", "text": "Ich habe auch versucht, den Anteil meines Portfolios, der Chocowin kopiert, zu reduzieren, wegen seines höheren Risikoprofils. Bisher habe ich $30 an Gewinn, den er mir eingebracht hat, abgezogen und zu meinen risikoärmeren Tradern hinzugefügt. Er hat einfach sehr gut performt. Zwischen ihm und Citadelpoint habe ich bisher $80 aus ihren Kopien entfernt und den anderen hinzugefügt. Das klingt vielleicht nicht viel, aber als Anteil der $200, mit denen ich jeden von ihnen kopiere, ist es eine Menge."},
        {"type": "h3", "text": "Wie geht es Alnayef?"},
        {"type": "p", "text": "Ungefähr gleich wirklich. Mittlerweile haben aber einige seiner offenen Trades angefangen, sich in die richtige Richtung zu bewegen. Das ist ein gutes Zeichen, aber ich bin immer noch sehr besorgt darüber, wie lange er seine Verlust-Trades offen hält. Es ist toll, geduldig zu sein, aber die Gebühren werden immer höher und das frisst langsam die Gewinne auf, die er gemacht hat. Er hat immer noch Trades offen seit November letzten Jahres..."},
        {"type": "h3", "text": "Der 'Neue' Berrau — wie handelt er?"},
        {"type": "p", "text": "Er ist derzeit über 1% im Plus und handelt sehr gut. Es gab einige beängstigende Momente, als er einen Trade eröffnete, der sich schnell gegen ihn wendete. Er hat es aber gut gemeistert und Verkaufspositionen im selben Asset eröffnet, um die Verluste zu stoppen. Es ist am Ende gut ausgegangen, da die gewinnenden Verkaufstrades die verlierenden Kauftrades ausgeglichen haben und er am Ende im Gewinn gelandet ist. Es ist gut zu sehen, dass jemand weiß, was zu tun ist, wenn die Dinge gegen einen laufen."},
        {"type": "p", "text": "Man sagt, selbst die besten Trader wählen nur 50% der Zeit die richtigen Trades. Die Kunst liegt anscheinend darin, Verlierer schnell abzuschneiden und Gewinner laufen zu lassen. Das scheint er bisher zu können, was toll zu sehen ist."},
        {"type": "h3", "text": "Olivier Danvel — weiterhin konsistentes, risikomanagiertes Trading?"},
        {"type": "p", "text": "Ja. Langsam und stetig gewinnende Trades. Es gibt große Wartephasen, in denen er auf die richtigen Einstiegspunkte für neue Trades wartet, aber das ist gut. Es passt zum Plan... Ich bin zufrieden damit, mich einfach zurückzulehnen und ihn handeln zu lassen."},
        {"type": "h2", "text": "Was ist mein nächster Schritt für das Portfolio?"},
        {"type": "p", "text": "Ich könnte eine neue Person hinzufügen, wenn ich mehr Geld bekomme, um das Portfolio weiter auszubalancieren und meine Exposure gegenüber den riskanteren Tradern zu reduzieren. Dafür muss ich aber warten, bis ich mehr Geld habe. Ich werde definitiv Harshsmith kopieren, aber ich brauche dafür extra $460, was etwas dauern könnte. Hoffentlich nicht zu lange :)"},
        {"type": "p", "text": "Ich bin dabei, einige Videos zu machen, in denen ich Top-Trader auf eToro interviewe und ihnen allen die gleichen Fragen stelle... Ich versuche gerade, mit einigen der großen Namen auf der Seite in Kontakt zu treten. Wenn du einen der Trader kennst, die ich am Ende des Videos erwähne, sag mir bitte Bescheid oder lass sie wissen, dass ich versuche, sie zu erreichen :)"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-16-apr-2019 ----
updates["copy-trading-update-16-apr-2019"] = {
    "slug": "copy-trading-update-16-april-2019",
    "meta_description": "Copy Trading Update — 16. April 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 16. April 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · April 2019",
    "h1": "Copy Trading Update — 16. April 2019",
    "content_blocks": [
        {"type": "p", "text": "16. April 2019 Also im Grunde ist mein Portfolio stetig gestiegen und ich bin bisher bei 1,45% Gewinn für den Monat. Wie schön :)"},
        {"type": "h2", "text": "Welcher Trader gewinnt?"},
        {"type": "p", "text": "Es ist immer noch Citadelpoint. Er gewinnt immer noch, nimmt regelmäßig Gewinne mit und ist immer noch mein bester Verdiener. Ich kopiere ihn derzeit mit etwa 11% meines Portfolios — weniger als Berrau, oder Olivier Danvel, oder Alnayef. Die Leute fragen mich, warum das so ist..."},
        {"type": "h2", "text": "Warum nicht Citadelpoint mit mehr kopieren?"},
        {"type": "p", "text": "Es ist eine Frage des Risikos. Ich weiß, er ist gerade der klare Gewinner, aber ich bin immer noch sehr vorsichtig damit, seinen Kopierbetrag zu erhöhen. Wenn überhaupt, plane ich immer noch, meine Kopie von ihm proportional weiter zu reduzieren. Bin ich verrückt? Ich denke nicht. Obwohl er absolut großartig performt hat und ich wirklich hoffe, dass es weitergeht, habe ich immer noch Bedenken. Seine Handelsgrößen können immer noch viel zu groß sein für meinen Geschmack. Manchmal geht er einfach 'all in' und setzt alle Mittel, die ich bei ihm kopiert habe, auf einen einzigen Trade. \"Gut\" magst du sagen. \"Der Mann gewinnt — lass ihn dir große Gewinne einbringen!\""},
        {"type": "p", "text": "Ich verstehe dieses Denken, wirklich. Glaub mir, ich würde mir nichts mehr wünschen als massive Gewinne, riesige grüne Balken in meinen Statistiken und eine Million Kopierer. Aber das Risiko ist auch sehr real. Wenn einer dieser großen Trades richtig schiefgeht, könnte es mich sehr viel kosten."},
        {"type": "p", "text": "\"Im Leben geht es darum, Risiken einzugehen\" höre ich dich sagen... Auch wahr, aber das ist nicht die Art von Portfolio, die ich aufbauen will. Ich versuche, eines zu bauen, in das ich viel mehr Geld stecken kann. Ein Portfolio, bei dem $20.000 so sicher wären, dass ich nicht den ganzen Tag jeden Tag zuschauen muss... Und mit diesem Ziel ist Citadelpoint als Trader immer noch eine ziemliche Unbekannte."},
        {"type": "p", "text": "Ich hoffe wirklich, dass er weiter gewinnt. Es war fantastisch zuzusehen, wie die Gewinne täglich wachsen :) Fan-tas-tisch."},
        {"type": "h2", "text": "Wie handelt Chocowin?"},
        {"type": "p", "text": "Sehr gut sogar. Er ist bei 11,8% meines Portfolios, da ich ihn immer noch als einen der risikoreicheren Trader in meinem Portfolio sehe. Trotzdem ist er mein zweitprofitabelster Trader im Moment. Er hat viele kleine Trades gemacht und großartige konsistente Renditen geliefert."},
        {"type": "p", "text": "Er hat auch zugestimmt, in meinem kommenden Video dabei zu sein, in dem ich verschiedene Popular Investors von eToro interviewe :) Ich freue mich darauf..."},
        {"type": "h2", "text": "Alnayef und seine langfristigen Forex-Trades"},
        {"type": "p", "text": "Alnayef hält immer noch all diese langfristigen Forex-Positionen... Die AUD/USD-Position, die so stark verlor, ist jetzt näher am Gewinn. Es war trotzdem ein langer Hold, und die Gebühren sind gestiegen. Ich hoffe, das markiert den Beginn einer kleinen Wende für Alnayef."},
        {"type": "p", "text": "Wenn ich mir seine Trades ansehe, scheinen sie sich alle ziemlich im Gleichschritt zu bewegen. Er scheint die makroökonomische Situation analysiert und entsprechend eine Reihe von Positionen eröffnet zu haben. Obwohl seine Positionen vielfältig sind, scheinen sie sich alle in eine ähnliche Richtung zu bewegen. Das sagt mir, dass er eine Gesamtansicht der wirtschaftlichen Situation hat und weiß, welche Forex-Paare er im Lichte dessen handeln muss, was er als Nächstes erwartet."},
        {"type": "p", "text": "Das ist sehr clever. Im letzten Video habe ich einen Link zu einer Anton-Kriel-Videoserie in der Beschreibung gepostet. Das war eine tolle Serie, die die Grundlagen der makroökonomischen Faktoren behandelte, die den Devisenhandel beeinflussen. Ich würde es sehr empfehlen, wenn du dich für Forex-Trading interessierst. Wirklich hilfreicher Stoff."},
        {"type": "p", "text": "Die Gebühren auf Alnayefs Trades sind für seine langfristigen Positionen immer noch sehr hoch. Aber die kürzerfristigen Trades haben tatsächlich ein sehr vernünftiges Verhältnis von Gebühren zu Gewinnen. Ich hoffe, er kann diese langfristigen Trades schließen und zu kürzerem Trading übergehen und die Dinge etwas umkehren. Wir werden sehen."},
        {"type": "h2", "text": "Olivier Danvel — sind alle seine Statistiken noch grün?"},
        {"type": "p", "text": "Ja, sind sie :) Er hatte in letzter Zeit eine etwas ruhigere Phase, aber es ist alles noch profitabel. Im Moment hat er ein paar Öl-'Verkauf'-Trades offen, aber sonst nichts. Ich denke, er wartet wie üblich auf die richtigen Einstiegspunkte, also mache ich mir keine Sorgen über seine mangelnde Aktivität. Ich vertraue ihm mittlerweile irgendwie, die richtigen Entscheidungen zu treffen. Sehr schön :)"},
        {"type": "h2", "text": "Berrau und Trades, die gegen ihn laufen"},
        {"type": "p", "text": "Berrau hat derzeit eine offene AUD/USD-Position, die ziemlich stark im Verlust ist. In letzter Zeit war er etwas volatiler mit Gewinnen, dann Verlusten, dann Gewinnen, dann Verlusten usw. Wenn Trades gegen ihn gelaufen sind, hat er aber nicht panisch reagiert. Stattdessen hat er Positionen im selben Paar in die entgegengesetzte Richtung eröffnet. Wenn eine gewinnt, verliert die andere, aber es ist ein großartiger Weg, keine weiteren Verluste zu machen, während man herausfindet, was der Markt tut."},
        {"type": "p", "text": "Es ist sozusagen wie ein riesiger 'Pause'-Knopf in seinem Trading. Es ist eine gute Idee, und bisher hat es für ihn funktioniert."},
        {"type": "p", "text": "Mehrmals hat er einen Trade eröffnet, der gegen ihn gelaufen ist. An diesem Punkt hat er konsequent gute Strategien angewandt, um seinen potenziellen Verlust mit Gegengeschäften zu begrenzen. Am Ende hat er jedes Mal Gewinn gemacht, und das ist sehr beruhigend. Man sagt, selbst die besten Trader liegen nur 50% der Zeit richtig. Den Unterschied macht, wie ein Trader reagiert, wenn etwas gewinnt und wenn etwas verliert. Bisher scheint Berrau einen kühlen Kopf und funktionierende Strategien zu haben."},
        {"type": "h2", "text": "Welche anderen Trader möchte ich kopieren?"},
        {"type": "p", "text": "Ich habe mir Kela-Leo angesehen, der eine Reihe von Assets handelt, darunter Rohstoffe und Forex. Das Problem ist, dass er gerade mitten in einem komplizierten Gold-Trade steckt. Ich würde mich da lieber raushalten ehrlich gesagt. Das Problem ist, dass ich ihn entweder mit offenen Trades kopieren kann (dann bin ich in diesem Gold-Trade dabei). Oder ich kann nur neue Trades kopieren."},
        {"type": "p", "text": "Das Problem dabei ist, dass er einige Gold-Trades eröffnet hat, die angefangen haben zu verlieren. Um dem entgegenzuwirken und weitere Verluste zu stoppen, hat er Gegengeschäfte eröffnet (Käufe statt Verkäufe). Das hat den gleichen Effekt, die Verlust-Trades auszugleichen. Aber wenn ich nur neue Trades kopiere, bekomme ich nur die neuen 'Gegengeschäfte'."},
        {"type": "p", "text": "Für ihn sind die Käufe und Verkäufe bei Gold Teil seiner Gesamtstrategie. Sie gleichen sich gegenseitig aus und stellen sicher, dass er kein Geld verliert. Wenn ich nur die neuen Kauftrades oder nur die neuen Verkaufstrades nehme, bin ich in einer riskanten Situation... Seine Strategie funktioniert als Ganzes. So handelt er. Wenn ich nur einen Teil seiner Trades nehme, bin ich nicht unter dem Schutz seiner vollständigen Gold-Strategie. Ich könnte potenziell Verluste machen, während er gewinn-/verlustneutral bleibt."},
        {"type": "p", "text": "Der Gedanke gefällt mir nicht. Also kann ich ihn gerade weder mit noch ohne offene Trades kopieren. Ich werde weiter nachdenken und beobachten, wohin er damit geht. Ich plane immer noch, ihn zu kopieren, vielleicht nur zu einem besseren Zeitpunkt, wenn Gold sich etwas mehr für eine Richtung entschieden hat."},
        {"type": "h3", "text": "Harshsmith?"},
        {"type": "p", "text": "Ja, ich plane immer noch, Harshsmith zu kopieren, aber ich brauche mehr Mittel dafür. Dieser Mindestkopierbetrag von $1 bedeutet, dass ich mindestens $460 brauche, um alle seine neuen Trades mitzunehmen. Ich habe noch keine $460, also muss ich warten. Vorerst muss mein Geld für mich arbeiten, also lasse ich Kela-Leo ran. Mal sehen, was passiert..."},
        {"type": "risk_warning"}
    ]
}

# Save first half and build second half in part 2
with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_part1.json', 'w', encoding='utf-8') as f:
    json.dump({"faq": output["faq"], "contact": output["contact"], "updates_part1": updates}, f, ensure_ascii=False, indent=2)

print(f"Part 1 saved with {len(updates)} update posts so far")
print("Keys:", sorted(updates.keys()))
