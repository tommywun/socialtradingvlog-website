#!/usr/bin/env python3
"""Part 2: Build remaining 9 update posts and merge into final JSON."""
import json

# Load part 1
with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_part1.json', 'r', encoding='utf-8') as f:
    part1 = json.load(f)

updates = part1["updates_part1"]

# ---- copy-trading-update-23-apr-2019 ----
updates["copy-trading-update-23-apr-2019"] = {
    "slug": "copy-trading-update-23-april-2019",
    "meta_description": "Copy Trading Update — 23. April 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 23. April 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · April 2019",
    "h1": "Copy Trading Update — 23. April 2019",
    "content_blocks": [
        {"type": "h2", "text": "23. April 2019 Copy Trading und Panik... Einer meiner Trader ist größere Risiken eingegangen als mir lieb ist, und dieses Update dreht sich eigentlich hauptsächlich darum..."},
        {"type": "p", "text": "Es ist Citadelpoint. Genau — der Superstar meines Portfolios, der massenhaft Gewinne eingefahren hat. Er hat an einem Tag etwa ein Drittel aller Gewinne verloren, die er mir eingebracht hat."},
        {"type": "h2", "text": "Was ist also passiert?"},
        {"type": "p", "text": "Es geht im Grunde um einen bestimmten Trade, den er gemacht hat. Es ist ein Forex-Trade — Kauf AUD/USD. Das bedeutet, er denkt, dass der Australische Dollar (AUD) gegenüber dem US-Dollar (USD) stärker wird. Das ist aber nicht passiert."},
        {"type": "img_grid", "images": [
            {"src": "../images/Screenshot-2019-08-28-at-22.22.52.png", "alt": "eToro Copy-Trading-Portfolio-Screenshot mit der problematischen Position — April 2019"},
            {"src": "../images/Screenshot-2019-08-28-at-22.35.30.png", "alt": "eToro Trade-Detail-Screenshot — April 2019 Update"}
        ]},
        {"type": "p", "text": "Er ist gefallen, und zwar schnell. Das Problem ist, dass er nicht einfach irgendeinen Trade eröffnet hat. Er hat fast sein gesamtes Kontogeld für diesen einen Trade verwendet. Und dann hat er noch einen kleinen Trade auf dasselbe Forex-Paar gemacht... Jetzt verwendet er 100% des Geldes, das ich bei ihm investiert habe, für diesen einen Trade. Und es läuft schnell gegen ihn."},
        {"type": "h2", "text": "Was mache ich jetzt?"},
        {"type": "p", "text": "Das ist eine wirklich gute Frage, und eine, die ich zu beantworten versuche. Sobald ich den Trade sah, dachte ich \"Oh nein... Vielleicht sollte ich den schließen.\" Aber das habe ich nicht. Ich wünschte jetzt, ich hätte es getan, aber ich habe ihn offen gelassen."},
        {"type": "p", "text": "\"Nein\", dachte ich, \"ich will nicht einfach sein Trading im Detail steuern — ich muss ihm vertrauen können, sonst ist das überhaupt nicht mehr passiv.\""},
        {"type": "p", "text": "Das stimmt alles — was bringt Copy Trading, wenn man trotzdem ständig zuschauen muss? Aber andererseits hat er vielleicht einfach andere Ziele als ich. Vielleicht ist ihm niedriges Risiko egal. Vielleicht setzt er lieber groß und gewinnt groß..."},
        {"type": "p", "text": "Uh oh... Dann hat er tatsächlich über genau diesen Trade in seinem Feed gepostet. Er wusste, dass einige von uns Kopierern paniken könnten, also hat er seine Gründe für alle sichtbar dargelegt. Er ist ein kluger Kopf, und seine Gründe scheinen schlüssig, aber er hat auch klargemacht, dass er vorerst am Trade festhält."},
        {"type": "p", "text": "Er wies darauf hin, dass er bereit ist, nochmal den gleichen Betrag zu verlieren, bevor er den Trade schließt (soweit ich es verstanden habe)."},
        {"type": "h2", "text": "Wird mein Copy Stop Loss ausgelöst?"},
        {"type": "p", "text": "Das ist meine Sorge. Ich habe einen engen Copy Stop Loss auf alle Leute gesetzt, die ich in meinem Portfolio kopiere. Im Grunde sagt mein Copy Stop Loss eToro: \"Wenn sie jemals so viel Geld verlieren, stoppe die Kopie automatisch\". Ich habe diesen CSL bei 15% für alle meine Trader gesetzt. Wenn er also 15% von seinem Allzeithoch (dem höchsten Gewinn, den er mir je eingebracht hat) fällt, wird er ausgelöst. Wenn er ausgelöst wird, wird die Kopie automatisch gestoppt, und ich kann ihn nicht mehr kopieren."},
        {"type": "h3", "text": "Warum kann ich ihn dann nicht mehr kopieren?"},
        {"type": "p", "text": "Citadelpoint ist nicht Teil des \"Popular-Investor-Programms\" auf eToro. Da werden Leute von eToro genehmigt... Sie folgen den Regeln von eToro und können von anderen kopiert und dafür bezahlt werden."},
        {"type": "p", "text": "Citadelpoint will nicht Teil dieses Programms sein. Er hat das ausdrücklich gesagt, da sein aktueller Arbeitgeber es nicht erlaubt. Wenn man nicht im Popular-Investor-Programm ist, können trotzdem eine kleine Anzahl von Leuten einen kopieren."},
        {"type": "p", "text": "Aber es ist eine sehr kleine Anzahl — zwanzig oder dreißig oder so. Und es gibt SEHR viele Leute, die ihn derzeit kopieren wollen. Wenn also mein Copy Stop Loss auslöst und ich aufhöre, ihn zu kopieren, nimmt jemand anderes meinen Platz ein, und ich komme nicht mehr rein..."},
        {"type": "h2", "text": "Was ist jetzt der Plan?"},
        {"type": "p", "text": "Ich weiß seit einer Weile, dass Citadelpoint riskanter ist als die anderen in meinem Portfolio. Deshalb kopiere ich ihn derzeit mit etwa 11% meines Portfolios statt der 24%, mit denen Berrau oder Olivier Danvel kopiert werden."},
        {"type": "p", "text": "Es war schon eine Weile ein Grund zur Sorge. Aber gleichzeitig war es auch Citadelpoint, der den Löwenanteil der Gewinne für mich gemacht hat. Er hat gehandelt wie ein Champion — wie eine Maschine. Aber ich denke schon seit einiger Zeit, dass ich, wenn ich ein wirklich sicheres Portfolio haben will, seinen Anteil reduzieren muss."},
        {"type": "p", "text": "Ich denke, wenn er bei etwa 5% meiner gesamten Portfoliogröße wäre, wäre es ein faires Risiko-Rendite-Szenario. Dafür müsste ich aber mehr Geld auf mein Konto einzahlen. Und ich habe gerade einfach nicht das Geld zum Nachschießen, also sind 11% ungefähr so niedrig wie es geht..."},
        {"type": "p", "text": "Denk dran — das Minimum, mit dem ich jeden Trader kopieren kann, ist $200. Ich müsste also genug Geld auf mein Konto einzahlen, dass $200 gleich 5% davon sind. Das ist mehr Geld, als ich derzeit habe — und es bringt mein Risikoprofil durcheinander."},
        {"type": "h2", "text": "Die Zukunft dieses Forex-Trades"},
        {"type": "p", "text": "Ich habe ein wenig technische Analyse gemacht, und ich kann die Unterstützungsniveaus knapp unter dem aktuellen Kurs sehen. Solange er über ihnen bleibt, werde ich nicht noch mehr in Panik geraten. Aber wenn er durch diese Unterstützungsniveaus (vorherige Tiefs) fällt, könnten möglicherweise viel größere Verluste drohen und möglicherweise der CSL ausgelöst werden. Wir werden sehen."},
        {"type": "img_grid", "images": [
            {"src": "../images/Screenshot-2019-08-28-at-22.49.24.png", "alt": "eToro Forex-Trade-Analyse-Screenshot — April 2019"},
            {"src": "../images/Screenshot-2019-08-28-at-23.08.23.png", "alt": "eToro Portfolio-Risikobewertung und offene Trades — April 2019"}
        ]},
        {"type": "p", "text": "Ich will ihn wirklich nicht aus dem Portfolio verlieren. Aber ich werde meinen Copy Stop Loss nicht ändern, damit das nicht passiert. Das habe ich schon mal gemacht — meinen Stop Loss bei einem verlierenden Trade immer weiter gesenkt. Das hat damals nicht funktioniert, und ich wünschte mir, ich hätte einfach die kleineren Verluste früher genommen."},
        {"type": "p", "text": "Also werde ich jetzt genau das tun — wenn er meinen Copy Stop Loss auslöst, dann ist es eben so. Es wäre sehr schade, da ich ihn für sehr talentiert halte, aber ich werde es akzeptieren und weitermachen."},
        {"type": "h2", "text": "Wie geht es den anderen Tradern?"},
        {"type": "p", "text": "Ehrlich gesagt war ich in solcher Panik wegen der Situation mit Citadelpoint, dass ich die relativ kleinen Auf- und Abschwünge der anderen weitgehend ignoriert habe. Es geht ihnen gut. Olivier Danvel hat derzeit ein paar Trades, die gegen ihn laufen, und er ist im Moment 0,5% im Minus für den Monat."},
        {"type": "p", "text": "Das würde mich normalerweise sorgen, aber die Citadelpoint-Situation lässt alles andere ziemlich nebensächlich erscheinen. Ich glaube, Olivier wird das aufholen, und es ist noch eine Woche im April übrig, also mache ich mir darüber nicht allzu große Sorgen."},
        {"type": "p", "text": "Es ist alles auf diesen AUD/USD-Trade gerichtet — wenn er noch weiter fällt, könnte mein Stop Loss ausgelöst werden und ich meinen Starspieler verlieren. Wir warten ab!"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-30-apr-2019 ----
updates["copy-trading-update-30-apr-2019"] = {
    "slug": "copy-trading-update-30-april-2019",
    "meta_description": "Copy Trading Update — 30. April 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 30. April 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · April 2019",
    "h1": "Copy Trading Update — 30. April 2019",
    "content_blocks": [
        {"type": "h2", "text": "30. April 2019 Er hat meinen Copy Stop Loss ausgelöst... Erinnerst du dich an das letzte Update, als ich über Citadelpoint gesprochen habe? Er war der am besten performende Trader in meinem Portfolio. Wochenlang hat er nichts als Aufregung und solide grüne Gewinne gebracht. Und dann der riskante AUD/USD-Trade."},
        {"type": "p", "text": "Nun, es wurde noch schlimmer in der Nacht, nachdem ich das letzte Video aufgenommen hatte. Die Märkte bewegten sich dramatisch gegen ihn. Am nächsten Tag, als ich aufwachte, war er aus dem Portfolio verschwunden."},
        {"type": "img_grid", "images": [
            {"src": "../images/Screenshot-2019-08-29-at-15.14.01.png", "alt": "eToro Portfolio nach Auslösung des Copy Stop Loss — April 2019"},
            {"src": "../images/Screenshot-2019-08-29-at-16.15.16.png", "alt": "eToro Trade automatisch geschlossen nach Copy Stop Loss — April 2019"}
        ]},
        {"type": "p", "text": "Es hat eine Weile gedauert, bis ich verstanden hatte, was passiert war..."},
        {"type": "p", "text": "Über Nacht hatte der Trade schwere Verluste erlitten, als der US-Dollar gegenüber dem Australischen Dollar stärker wurde. Irgendwann mitten in der Nacht wurde mein Copy Stop Loss ausgelöst und der Trade und die gesamte Kopie wurden geschlossen."},
        {"type": "p", "text": "Es ist wirklich schade — ich habe es wirklich genossen, ihm beim Handeln zuzuschauen. Und ich habe die Gewinne wirklich genossen!"},
        {"type": "h2", "text": "Was hätte ich tun können, um ihn im Portfolio zu behalten?"},
        {"type": "p", "text": "Nicht viel wirklich... Ich hätte ein paar Dinge tun können:"},
        {"type": "h3", "text": "A: Den AUD/USD-Trade manuell schließen."},
        {"type": "p", "text": "Das wäre möglich gewesen. Ich hätte einfach in mein Portfolio gehen und auf Citadelpoints Namen klicken müssen. Von dort aus hätte ich alle Trades sehen können, die ich gerade über ihn kopiere."},
        {"type": "p", "text": "Rechts neben jedem kopierten Trade gibt es ein rotes 'X'. Ich hätte darauf klicken und ihn manuell schließen können. Aber wenn ich das anfange, macht es dann noch Sinn, es Copy Trading zu nennen? Oder ist es Teil-Kopie-Teil-manuelles-Trading... Will ich das für immer machen müssen?"},
        {"type": "p", "text": "Und was, wenn ich den Trade geschlossen hätte und er dann gut gelaufen wäre? Was würden meine Kopierer sagen? \"Tom, wir mögen dich, aber hör auf, manuell an den Kopien herumzupfuschen!\" Wenn ich gewonnen hätte, wäre ich ziemlich clever gewesen. Wenn ich verloren hätte, hätte ich das Vertrauen aller verraten. Keine tolle Idee..."},
        {"type": "h3", "text": "B: Meinen Copy Stop Loss erhöhen."},
        {"type": "p", "text": "Ich hätte in mein Portfolio gehen, auf das kleine Zahnrad-Symbol rechts klicken und Änderungen vornehmen können. Mein Copy Stop Loss (CSL) steht derzeit bei 85% für alle meine Trader. Hätte ich den Betrag erhöhen sollen, den ich bereit bin, mit Citadelpoint zu verlieren?"},
        {"type": "p", "text": "Vielleicht hätte ich ihn auf 80% setzen können (was bedeutet, dass ich 20% des bei ihm investierten Geldes riskiere). Was ist mit 75% oder sogar 70%? Wie weit hätte ich den Stop Loss ändern sollen, um die möglichen Drawdowns zu überleben..."},
        {"type": "p", "text": "Und wäre das fair gegenüber all den anderen Leuten, die ich kopiere? Es würde bedeuten, dass ich der riskantesten Person mehr Spielraum gebe als den sichereren Leuten, um mein Geld zu verlieren."},
        {"type": "p", "text": "Keines klingt nach einem tollen Plan..."},
        {"type": "h2", "text": "Er ist weg, und das war's — welche Trader sind übrig?"},
        {"type": "p", "text": "Chocowin, Alnayef, Berrau, Olivier Danvel und Kela-Leo sind jetzt die Trader, die ich kopiere..."},
        {"type": "p", "text": "Zusammen handeln sie hauptsächlich Forex, ein wenig Aktien und ein kleines bisschen Gold. Wie geht es ihnen also..."},
        {"type": "p", "text": "Ehrlich gesagt denke ich, ich würde ihn auf etwa 5% des Portfolios reduzieren, wenn ich könnte. Aus den gleichen Gründen wie bei Citadelpoint. Sein Risiko ist einfach zu hoch für das Portfolio, das ich aufbauen will..."},
        {"type": "p", "text": "Er hat sich aber wirklich gut geschlagen. Häufiges und erfolgreiches Trading und gute Gewinne."},
        {"type": "p", "text": "So sind seine Verluste bei der gleichen Bewegung im Asset immer noch minimal. Besser..."},
        {"type": "p", "text": "Er hat auch in letzter Zeit einige kleine Gewinntrades gemacht, was gut zu sehen ist. Er war im Grunde eine Weile verschwunden, also ist jedes Zeichen von Aktivität sehr willkommen. Ich warte ab und sehe, was als Nächstes passiert."},
        {"type": "h2", "text": "Wie handelt Berrau?"},
        {"type": "p", "text": "Ziemlich gut. Er ist bisher bei 2,65% Gewinn für April, was großartig ist. Er hat nicht viele offene Trades — nur einen kleinen Ripple (XRP) Trade, der etwas verliert. 2,65% ist viel Gewinn bei jemandem, dessen Risiko so niedrig ist wie das von Berrau. Er macht sich gut :)"},
        {"type": "img_grid", "images": [
            {"src": "../images/Screenshot-2019-08-29-at-16.32.21.png", "alt": "Berrau Trading-Performance auf eToro — Ende April 2019"},
            {"src": "../images/Screenshot-2019-08-29-at-16.48.28.png", "alt": "Berrau eToro Copy-Trading-Statistiken — Ende April 2019"}
        ]},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Nun, Olivier ist bekannt für seine risikoarmen, durchgehend grünen Ergebnisse. Bisher war er sehr konstant. Dieser Monat zeigt zum ersten Mal ein kleines Zeichen eines etwas riskanteren Ansatzes. Nachdem er einen Forex-Trade eröffnet hatte, wendete er sich gegen ihn. Das passiert jedem... Seine Methode, damit umzugehen, war etwas, das 'Cost Averaging' genannt wird (*glaube ich!)"},
        {"type": "p", "text": "Das bedeutet, dass man, während der Trade gegen einen läuft und der Preis fällt, weiterhin in Abständen kleine neue Positionen eröffnet."},
        {"type": "p", "text": "Die Positionen gehen in die gleiche Richtung — in diesem Fall alles 'Käufe'."},
        {"type": "p", "text": "Die Idee ist, am Ende einen insgesamt niedrigeren Durchschnittskaufpreis zu haben (wenn man den Durchschnitt aller Eröffnungspreise nimmt)."},
        {"type": "p", "text": "Es ist eine Taktik, die von vielen erfahrenen Tradern verwendet wird. Wenn der Trade schließlich seinen Tiefpunkt erreicht und der Kurs die Richtung wechselt, sollte es sich ziemlich schnell auszahlen. Je niedriger der durchschnittliche Einstiegspreis, desto besser."},
        {"type": "p", "text": "Das scheint das zu sein, was Olivier gemacht hat, und jetzt hat sich der Trade gedreht und er ist auf dem Weg zurück ins Grüne."},
        {"type": "p", "text": "Es war allerdings ein größerer Schwung, als ich von ihm gewohnt war."},
        {"type": "p", "text": "Er ist ein risikoarmer Trader — unter meinem 15% maximalen jährlichen Drawdown mit niedrigen aktuellen Risikoscores. Ich denke nicht, dass er etwas Verrücktes tun wird, also habe ich Zeit zu sehen, wie er sich macht :)"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-07-may-2019 ----
updates["copy-trading-update-07-may-2019"] = {
    "slug": "copy-trading-update-07-mai-2019",
    "meta_description": "Copy Trading Update — 07. Mai 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 07. Mai 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Mai 2019",
    "h1": "Copy Trading Update — 07. Mai 2019",
    "content_blocks": [
        {"type": "h2", "text": "7. Mai 2019 Welchen Aktien-Trader behalte ich?"},
        {"type": "p", "text": "Die Hauptfrage in diesem Update ist, ob ich meinen aktuellen Aktien-Trader gegen einen neuen tausche. Im Moment kopiere ich Chocowin für Aktien. Er hat gut performt, aber sein Risikoprofil ist etwas zu hoch für meine Ziele."},
        {"type": "p", "text": "Ich beobachte einen Trader namens 'Harshsmith' schon seit einiger Zeit. Seine Risikoscores sind niedriger, seine Performance ist gut, und ich denke daran, zu ihm zu wechseln. Aber zuerst gehe ich einige der Umfragen aus meinen vorherigen Videos durch..."},
        {"type": "h2", "text": "Umfrageergebnisse, welche Trader man kopieren sollte"},
        {"type": "p", "text": "In letzter Zeit habe ich einige dieser \"Würdest du diesen Trader kopieren\"-Videos gemacht. Das war ein guter Weg, einige Vorschläge meiner Zuschauer durchzugehen und auch jeden seine Meinung sagen zu lassen. Umfragen sind dafür wirklich nützlich, da alle zukünftigen Zuschauer sehen können, wie andere Leute denken..."},
        {"type": "p", "text": "Also hier sind sie:"},
        {"type": "p", "text": "1. VIDEO: \"Würdest du Berrau kopieren?\" Ja: 54% Erstmal auf die Watchlist: 21% Nein, er ist zu langweilig: 18% Nein, er ist zu riskant: 5%"},
        {"type": "img", "src": "../images/Berrau-closed-trades-may-07-2019-eToro-2400x1300.png", "alt": "Berrau geschlossene Trades auf eToro — 7. Mai 2019"},
        {"type": "p", "text": "2. VIDEO: \"Würdest du LoydBazaar kopieren?\" JA: 40% Erstmal auf die Watchlist: 37% Nicht sicher: 15% Nein: 6%"},
        {"type": "p", "text": "3. VIDEO: \"Würdest du Kela-Leo kopieren?\" Ja: 53% Erstmal auf die Watchlist: 12% Nicht sicher: 20% Nein: 14%"},
        {"type": "p", "text": "Ich weiß, das ist nicht wissenschaftlich :) Ich habe leicht unterschiedliche Fragen gestellt und verschiedene Antwortmöglichkeiten gegeben. Also nimm das als grobe Orientierung und ein bisschen Spaß... Mach immer deine eigene Recherche, bevor du entscheidest, wen du kopierst!"},
        {"type": "h2", "text": "Zurück zu Harshsmith VS Chocowin"},
        {"type": "p", "text": "Also, wie ich sagte, ich schaue mir an, ob ich den Aktien-Trader in meinem Portfolio wechsle. Warum?"},
        {"type": "p", "text": "Chocowin hat sehr gut für mich performt, aber im Vergleich zu Harshsmith ist er hochriskant. Mein Ziel ist ein risikoarmes Portfolio. Ich habe einige informelle Mini-Regeln aufgestellt, um dieses Ziel zu erreichen."},
        {"type": "p", "text": "Eine davon betrifft den 'Max Drawdown'. Das ist eine Kennzahl in eToros Statistiken, die den maximalen Drawdown jedes Traders im letzten Jahr misst. 'Drawdown' kann fast mit einer 'Verlustserie' gleichgesetzt werden."},
        {"type": "p", "text": "Es beschreibt im Grunde den größten Verlust, den du gemacht hast, bevor du wieder angefangen hast, Gewinne zu machen. Es ist wie ein Blick auf eine Delle in deinen Gewinnen — wie tief hat der Trader es sinken lassen, bevor:"},
        {"type": "p", "text": "Ich benutze es, um eine grobe Vorstellung davon zu bekommen, ob ein Trader wahrscheinlich meinen 15% Copy Stop Loss auslöst. Ich setze meinen Copy Stop Loss (CSL) bei 15% für jeden Trader, den ich kopiere, damit ich nicht zu viel von meinem Kapital riskiere. Aber ich versuche auch, Trader auszuwählen, deren Geschichte zeigt, dass sie meinen CSL wahrscheinlich nicht auslösen werden."},
        {"type": "p", "text": "Ich will keinen so engen Stop Loss setzen, nur um ihn ständig ausgelöst zu bekommen. Das würde keinen Sinn machen. Also beobachte ich ihre Statistiken..."},
        {"type": "h2", "text": "Chocowins Risikoscores und maximaler jährlicher Drawdown"},
        {"type": "p", "text": "Hier siehst du Chocowins Risikoscores der letzten zwölf Monate sowie die Max-Drawdown-Statistiken. Wenn du sie mit Harshsmiths (unten gezeigt) vergleichst, wirst du sehen, dass die Risikoscores das ganze Jahr über höher sind."},
        {"type": "img", "src": "../images/Chocowin-risk-scores-max-yearly-drawdown-May-2019-1024x657.png", "alt": "Chocowins Risikoscores und maximaler jährlicher Drawdown auf eToro — Mai 2019"},
        {"type": "p", "text": "Unter dem Balkendiagramm siehst du den Max-Drawdown-Bereich. Die Zahl auf der rechten Seite des Kastens zeigt den jährlichen Max-Drawdown. Wie du sehen kannst, liegt Chocowins über meinem 15%-Ziel, während Harshsmiths deutlich darunter liegt..."},
        {"type": "h2", "text": "Harshsmiths Risikoscores und maximaler jährlicher Drawdown"},
        {"type": "p", "text": "Es scheint seltsam, einen Trader nicht mehr zu kopieren, der mir gute Gewinne eingebracht hat. Es geht aber um nachhaltiges, schwankungsarmes Wachstum in der Zukunft. Das ist mein primäres Ziel. Wenn ich $20.000 auf mein eToro-Handelskonto einzahle, welche Trader würde ich mit meinem Geld handeln lassen wollen?"},
        {"type": "img", "src": "../images/Harshsmith-risk-scores-max-yerly-drawdonw-may-2019-1024x657.png", "alt": "Harshsmiths Risikoscores und maximaler jährlicher Drawdown auf eToro — Mai 2019"},
        {"type": "p", "text": "Beide handeln Aktien, beide sind historisch profitabel. Einer ist statistisch weniger riskant als der andere. Was würdest du tun? Ich habe die Zuschauer gefragt und werde sehen, was die Weisheit der Masse sagt. Ich tendiere aber dazu, Chocowin fallen zu lassen und Harshsmith zu kopieren."},
        {"type": "p", "text": "Ich will nicht zu viel Aktien-Exposure, da Volatilität eine neue Norm zu sein scheint und ich auf mein Risiko achten muss. Daher tendiere ich dazu, nur einen Aktien-Trader in meinem Portfolio zu behalten."},
        {"type": "h2", "text": "Wie geht es den anderen Tradern?"},
        {"type": "h3", "text": "Alnayef"},
        {"type": "p", "text": "Er ist ziemlich auf dem gleichen Level wie beim letzten Update. Es hat sich nicht viel bewegt wirklich... Da ist viel Rot."},
        {"type": "img", "src": "../images/Alnayef-open-trade-may-07-2019-eToro-2400x1300.png", "alt": "Alnayef offene Trades im eToro-Portfolio — 7. Mai 2019"},
        {"type": "p", "text": "Alnayef hat nicht viel getan. Er hat immer noch viele leicht verlierende Trades offen, und er scheint sie einfach dort zu lassen. Er wartet, bis sie grün werden, denke ich. Ich bin mir nicht sicher, wie lange das dauern wird. Vorerst werde ich ihn einfach weiter beobachten. Hoffentlich dreht sich die Sache."},
        {"type": "p", "text": "Er geht keine massiven Risiken ein und macht nichts Leichtsinniges. Er ist einfach auf der falschen Seite vieler Trades — aber nicht ernst genug, um Panik auszulösen. Es gibt nur ein nagendes Gefühl, dass er sich auf einer langsamen Verlustserie befindet."},
        {"type": "h3", "text": "Berrau"},
        {"type": "p", "text": "Er hat sich sehr gut gemacht. Langsame, stetige Gewinne — etwa 0,25% pro Gewinntrade, mit einer Serie von Gewinnern in letzter Zeit."},
        {"type": "p", "text": "Seine Risikoscores und der maximale Drawdown sind immer noch niedrig, und er scheint im Moment auf einem guten Kurs zu sein. Alle paar Tage eröffnet er einen neuen Trade. Wenn er ein Viertelprozent gewinnt, schließt er ihn und nimmt den Gewinn mit. Einfach und sauber."},
        {"type": "p", "text": "Als ich ihn zuerst kopiert habe, liefen viele seiner Trades gegen ihn. Er hat es trotzdem geschafft, sich mit Gewinn herauszuhandeln. In letzter Zeit allerdings scheinen alle seine neuen Trades in seine Richtung zu laufen. Möge es so weitergehen!"},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Er ist ziemlich auf dem gleichen Level auch. Er hatte Ende letzten Monats einen kleinen Drawdown, hat es aber gedreht und den Monat im Plus beendet. Er hat immer noch 100% grüne Monatsstatistiken. Ich bin zufrieden mit Olivier und lasse ihn sein Ding machen!"},
        {"type": "h3", "text": "Kela-Leo"},
        {"type": "p", "text": "Kela-Leo ist den ganzen Monat einfach ein bisschen hoch, dann ein bisschen runter, dann wieder ein bisschen hoch gegangen. Meine Gewinne aus der Kopie haben sich nicht wirklich bewegt, also gibt es nicht viel zu sagen :) Auch hier werde ich abwarten und beobachten..."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-16-may-2019 ----
updates["copy-trading-update-16-may-2019"] = {
    "slug": "copy-trading-update-16-mai-2019",
    "meta_description": "Copy Trading Update — 16. Mai 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 16. Mai 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Mai 2019",
    "h1": "Copy Trading Update — 16. Mai 2019",
    "content_blocks": [
        {"type": "h2", "text": "16. Mai 2019 Welcher Trader hat bei der Umfrage letzte Woche gewonnen? Letzte Woche sagte ich, ich denke daran, einen der Trader, die ich kopiere, gegen einen neuen zu tauschen. Ich dachte daran, meine Kopie von Chocowin zu stoppen und eine neue Kopie von Harshsmith zu starten. Beide handeln Aktien, aber Harshsmiths Risikoprofil passt besser zu meinen Niedrigrisiko-Zielen."},
        {"type": "p", "text": "Ich habe in meinem letzten Video eine Umfrage gestellt, um zu sehen, wie ihr, die Zuschauer, denkt. Hier sind die Ergebnisse:"},
        {"type": "p", "text": "\"Chocowin gegen Harshsmith tauschen?\""},
        {"type": "p", "text": "'Beide im Portfolio behalten': 56% 'Ja — Harshsmith stattdessen nehmen': 32% 'Nein — Nur Chocowin behalten': 7% 'Nicht sicher': 2%"},
        {"type": "p", "text": "Ich habe das Video rechts stehen gelassen, damit du meine Überlegungen sehen kannst, falls du es noch nicht gesehen hast... Also, was habe ich gemacht?"},
        {"type": "p", "text": "Ich habe aufgehört, Chocowin zu kopieren, und angefangen, Harshsmith zu kopieren. Realistisch gesehen will ich im Moment nicht zu viel Aktien-Exposure. Ich mache mir Sorgen über einen großen Abschwung, also macht mich weniger Exposure gerade weniger nervös. Harshsmith betreibt ein sogenanntes 'Long/Short'-Portfoliosystem. Das bedeutet, er wettet darauf, dass einige Assets steigen und andere fallen werden."},
        {"type": "h2", "text": "Long/Short-Portfolio-Hedging-Strategie"},
        {"type": "p", "text": "Es ist eine 'Hedging'-Strategie — ein Weg, dein Portfolio statistisch sicherer zu machen. Ein Weg sicherzustellen, dass du, wenn die Märkte plötzlich abstürzen, trotzdem davon profitieren kannst. Oder zumindest nicht so viel Geld verlierst wie wenn du einfach alles 'long' (kaufen) hättest. Er bereitet sich im Grunde auf eine große Korrektur vor. Solange ich weiß, dass er aufpasst, kann ich mich ein wenig entspannen."},
        {"type": "p", "text": "Wenn du dir sein Portfolio ansiehst, wirst du bemerken, dass er kleine Anteile seines Gesamtkapitals pro Trade verwendet. Er handelt alle möglichen Aktien, und er kauft einige und verkauft andere. Ich habe ihn nach seinem Plan gefragt, und er sagte, sein Portfolio ist 'Net Short'."},
        {"type": "p", "text": "Das bedeutet, dass, obwohl er sowohl kauft als auch verkauft, insgesamt mehr seines Geldes in Verkauf-(Short-)Trades steckt als in Kauf-(Long-)Trades."},
        {"type": "p", "text": "Er sagte auch, dass er 'High Beta'-Aktien shortet. 'High Beta'-Aktien sind die Wertpapiere, die traditionell volatiler sind als der Marktdurchschnitt. Er hat also diejenigen ausgewählt, von denen er glaubt, dass sie bei einem plötzlichen Abschwung am radikalsten reagieren würden, und er 'shortet' sie. Er hat all diese Schritte unternommen, um zwei Dinge zu erreichen:"},
        {"type": "p", "text": "1. Sein Portfolio in Zeiten erhöhter Volatilität zu stabilisieren."},
        {"type": "p", "text": "2. Sein Portfolio so zu positionieren, dass es Gewinne macht, wenn die Märkte nach unten korrigieren."},
        {"type": "p", "text": "Mit deutlich niedrigeren Risikoscores und maximalem Drawdown fand ich, dass der Tausch der beiden Trader die vernünftige Entscheidung war."},
        {"type": "h2", "text": "Ein großes Dankeschön an Chocowin!"},
        {"type": "p", "text": "Auch wenn ich aufgehört habe, Chocowin zu kopieren, möchte ich ihm ein großes DANKE sagen. Ich habe die Kopie mit gutem Gewinn geschlossen, was ein tolles Ergebnis ist. Er hat mir wirklich schöne Renditen eingebracht, also wollte ich einfach danke sagen und ihm alles Gute wünschen :) Prost Chocowin!"},
        {"type": "h2", "text": "Wie hat Alnayef gehandelt?"},
        {"type": "p", "text": "Ehrlich gesagt machen mir seine Gebühren langsam Sorgen. Er hatte einige Trades, die gegen ihn gelaufen sind, und die verlieren derzeit Geld. Er hat sie aber nicht geschlossen. Er hat jetzt ein Portfolio, das fast voll mit offenen Trades im Minus ist. Das Problem ist, dass er sie sehr lange offen hat."},
        {"type": "img_grid", "images": [
            {"src": "../images/Alnayef-open-trades-etoro-may-14-2019-2400x1300.png", "alt": "Alnayef offene Trades auf eToro — 14. Mai 2019"},
            {"src": "../images/alnayef-fees-on-trades-may-2019-2400x1300.png", "alt": "Alnayef Handelsgebühren bei eToro Copy Trades — Mai 2019"}
        ]},
        {"type": "p", "text": "Und die Trades nutzen Hebel."},
        {"type": "p", "text": "Wenn du bei einem Trade Hebel einsetzt, fallen winzige 'Übernachtgebühren' und 'Wochenendgebühren' an. Für jeden Tag, den der Trade offen gehalten wird, werden die Gebühren berechnet. Es sind winzige Gebühren, aber über einen sehr langen Zeitraum können sie sich wirklich ansammeln."},
        {"type": "p", "text": "Das passiert gerade bei Alnayef. Gewisse Gebühren sind zu erwarten, und Alnayef hat immer Hebel benutzt. Es ist nur so, dass er einige Trades jetzt so viele Monate offen hat, dass die Gebühren spürbar sind."},
        {"type": "p", "text": "Und die verlierenden offenen Trades sehen nicht so aus, als würden sie sich bald drehen. Ich behalte es im Auge, da es jetzt ein leichtes Problem ist, das auf meinem Radar ist. Wir werden sehen."},
        {"type": "h2", "text": "Berrau — niedrige Gebühren und stetiges Trading"},
        {"type": "p", "text": "Berrau hat sich gut gemacht. Er hat den Ripple-(XRP-)Trade im Gewinn geschlossen und seitdem noch einen. Er bewegt sich stetig vorwärts und hat erfreulicherweise auch extrem niedrige Gebühren. Schön."},
        {"type": "h2", "text": "Olivier Danvel"},
        {"type": "p", "text": "Olivier hat einen Forex-Trade, der in den letzten Tagen gegen ihn gelaufen ist (im Minus). Er scheint eine 'Cost-Averaging'-Strategie anzuwenden, um auf diese Situation zu reagieren."},
        {"type": "img", "src": "../images/Olivier-Danvel-cost-averaging-forex-may-2019-2400x1264.png", "alt": "Olivier Danvel Cost-Averaging-Forex-Strategie auf eToro — Mai 2019"},
        {"type": "p", "text": "In diesem Fall bedeutet 'Cost Averaging', dass er weiterhin kleine zusätzliche Lots desselben Forex-Paares kauft, während der Preis fällt."},
        {"type": "p", "text": "Auf diese Weise wird sein durchschnittlicher Kaufpreis immer niedriger."},
        {"type": "p", "text": "Im Moment ist seine Position eine 'Kauf'-Position. Er wartet darauf, dass das Forex-Paar im Wert steigt, damit er Geld verdienen kann. Da er seinen durchschnittlichen Einstiegspreis gesenkt hat, hat sich der Preis geändert, ab dem er im Gewinn ist. Die Gesamtposition wird profitabel, noch während die ersten Lots, die er gekauft hat, im Minus sind."},
        {"type": "p", "text": "Wir werden sehen, wie es ausgeht. Ich habe aber Vertrauen in Olivier — so viele grüne Monate in Folge bekommt man nicht ohne Können..."},
        {"type": "h2", "text": "Harshsmith — Copy Trading hat begonnen"},
        {"type": "p", "text": "Die Kopie von Harshsmith ist gerade gestartet, und es gibt Aktien-Trades, einige Rohstoff-Trades und ein paar Krypto-Trades. Der bei Weitem größte Anteil liegt in Aktien, da das sein Hauptfokus ist. Ich werde es laufen lassen und beobachten — hoffentlich läuft alles gut :)"},
        {"type": "img", "src": "../images/HArsmith-open-trades-etoro-14-May-2019-2400x1300.png", "alt": "Harshsmith offene Trades auf eToro nach Start der Kopie — 14. Mai 2019"},
        {"type": "h2", "text": "Kela-Leo"},
        {"type": "h2", "text": "Mein risikoarmes Portfolio"},
        {"type": "p", "text": "Alle Trader, die ich kopiere, sind jetzt 'risikoarme' Trader. Alle ihre Risikoscores sind auf der sehr niedrigen Seite. Sie liegen alle unter meinem Ziel-Max-Drawdown von 15% pro Jahr. Mal sehen, was passiert. Es ist jetzt etwas ein Wartespiel. Niedriges Risiko und ein schwankungsarmes Portfolio bedeuten, dass die Dinge langsamer und stetiger passieren. Das gilt für Gewinne ebenso wie für Verluste... Mein Risikoscore ist diese Woche offiziell auf 1 von 10 gesunken :) Schön."},
        {"type": "h2", "text": "Ich will Kryptos per Copy Trading handeln"},
        {"type": "p", "text": "Angesichts dessen, dass Kryptowährungen zuletzt etwas im Aufwärtstrend waren, denke ich wieder über sie nach. Ich würde gerne einen guten Krypto-Trader zum Kopieren auf eToro finden, aber ich tue mich damit schwer."},
        {"type": "img", "src": "../images/bitcoin-logo.jpg", "alt": "Bitcoin-Logo — Überlegungen zum Kryptowährungs-Copy-Trading auf eToro"},
        {"type": "p", "text": "Jeder, der Kryptos handelt, scheint entweder:"},
        {"type": "p", "text": "A: Sehr neu zu sein, sodass ich keine lange genuge Handelshistorie sehen kann."},
        {"type": "p", "text": "B: Auch viele Aktien zu handeln (wozu ich gerade nicht mehr Exposure will)."},
        {"type": "p", "text": "Daher habe ich die jüngsten Aufwärtsbewegungen größtenteils verpasst. Das war ehrlich gesagt frustrierend. Ich bin fast versucht, die Leute, die mich kopieren, zu fragen, ob es ihnen etwas ausmachen würde, wenn ich manuell etwas HODLe. Soweit bin ich aber noch nicht. Ich würde immer noch gerne einen guten Krypto-Trader finden, also bitte ich die Zuschauer um Vorschläge."},
        {"type": "p", "text": "Ich brauche jemanden mit nachgewiesener Historie. Jemanden unter meinem 15% Max-Drawdown pro Jahr, mit niedrigen Risikoscores. Es gibt Leute, die sagen, das sei unmöglich auf dem Kryptomarkt. Ich sehe nicht warum... Wenn der Vermögenswert volatil ist, einfach kleinere Anteile des Portfolios verwenden. Hebel vermeiden. Stop Losses setzen. Das muss doch möglich sein! Wir werden sehen, welche Vorschläge zurückkommen :)"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-04-jun-2019 ----
updates["copy-trading-update-04-jun-2019"] = {
    "slug": "copy-trading-update-04-juni-2019",
    "meta_description": "Copy Trading Update — 04. Juni 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 04. Juni 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Juni 2019",
    "h1": "Copy Trading Update — 04. Juni 2019",
    "content_blocks": [
        {"type": "h2", "text": "4. Juni 2019 Ich wurde zum 'Rising Star' Level Popular Investor befördert :)"},
        {"type": "p", "text": "Ich habe den gelben Stern von eToro bekommen und bin jetzt ein 'Rising Star' in ihrem PI-Programm. Schön. Wie ist das passiert?"},
        {"type": "img_grid", "images": [
            {"src": "../images/eToro-Yellow-Star-Popular-Investor-Program.png", "alt": "eToro gelber Stern als Zeichen des Rising-Star-Levels im Popular-Investor-Programm"},
            {"src": "../images/Etoro-Red-star-champion-popular-investor.png", "alt": "eToro roter Stern für Champion-Level Popular Investor — die nächste Stufe"}
        ]},
        {"type": "p", "text": "Nun, als Teil des eToro Popular-Investor-Programms kann ich die Stufen aufsteigen und bessere Vorteile bekommen. Jeder, der dem Programm beitritt, kann das. Die Anmeldung ist einfach — schau dir einfach die oben gezeigte Seite an, und alles wird erklärt."},
        {"type": "p", "text": "Im Grunde habe ich es geschafft, $40K AUM (verwaltetes Vermögen) zu erreichen, und ich hatte alle anderen Anforderungen erfüllt. Sobald das der Fall war, wurde ich auf die nächste Stufe befördert."},
        {"type": "h2", "text": "Der gelbe Stern zeigt, dass du ein 'Rising Star' Level PI bist. Welche Vorteile bekomme ich?"},
        {"type": "p", "text": "Nun, ich bekomme jetzt jeden Monat eine Zahlung von $500 direkt von eToro, solange ich auf diesem Level bleibe. Das ist toll :)"},
        {"type": "p", "text": "Außerdem werden mir keine Auszahlungsgebühren berechnet, wenn ich Geld von eToro abhebe. Sehr schön..."},
        {"type": "h2", "text": "Kann man den Stern wieder verlieren?"},
        {"type": "p", "text": "Ich bin mir noch nicht sicher, aber ich glaube schon. Ich muss über dem erforderlichen Level bleiben, um meinen aktuellen Status zu behalten, oder weiter aufsteigen, um die nächste Stufe zu erreichen."},
        {"type": "h2", "text": "Was ist die nächste Stufe des Popular Investor?"},
        {"type": "p", "text": "Die nächste Stufe wäre der rote Stern — der 'Champion Level' Popular Investor."},
        {"type": "h2", "text": "Auf 'Champion'-Level hat man einen roten Stern. Zurück zu meinen Copy-Trading-Abenteuern"},
        {"type": "p", "text": "Im Portfolio läuft es tatsächlich ziemlich gut. Ich gehe die einzelnen Positionen durch und erzähle, was passiert ist."},
        {"type": "p", "text": "Ich mache mir ein bisschen Sorgen über Alnayefs Gebühren, und Berrau ist gerade in einen etwas beunruhigenden Forex-Trade eingestiegen. Kela-Leo scheint immer noch ein bisschen hoch, ein bisschen runter zu gehen. Die anderen sind ziemlich gleich wie beim letzten Mal..."},
        {"type": "h2", "text": "Alnayef und seine Handelsgebühren"},
        {"type": "p", "text": "Das Ding bei Alnayef ist, dass er möglicherweise keine Übernacht- und Wochenendgebühren zahlt. Ich höre Berichte, dass 'Islamische' Konten auf eToro aus religiösen Gründen von diesen Gebühren befreit sind."},
        {"type": "img", "src": "../images/Fees-page-on-eToro.png", "alt": "eToro Gebührenseite mit Erklärung der Übernacht- und Wochenendgebühren"},
        {"type": "p", "text": "Aber die Leute ohne islamisches Konto, die diese Trader kopieren, sind nicht befreit. Das hat eine schwierige Situation in Bezug auf die Rentabilität geschaffen, soweit ich sehen kann. Nun, es mag sein, dass den Inhabern islamischer Konten eine andere Gebühr berechnet wird, die mir nicht berechnet wird."},
        {"type": "p", "text": "Ich bin mir nicht sicher, ob es sich langfristig ausgleicht und alles nur anders benannt ist. Könnte gut sein — Unternehmen wollen immer ihre Gewinne machen..."},
        {"type": "p", "text": "Aber soweit ich sehen kann, gibt es bei Alnayefs Trades keinen Zeitfaktor, während bei mir die Uhr tickt."},
        {"type": "h2", "text": "Was sind Übernacht- und Wochenendgebühren?"},
        {"type": "p", "text": "Falls du nicht weißt, was Übernacht- und Wochenendgebühren sind, erkläre ich es kurz. (Hier ist die eToro-Seite) Wenn du einen Trade machst, entweder:"},
        {"type": "p", "text": "Dir werden Übernachtgebühren für jeden Tag berechnet, den du diesen Trade von einem Tag zum nächsten offen hast."},
        {"type": "p", "text": "'Wochenend'-Gebühren sind einfach mehrere 'Übernachtgebühren', die zusammengerechnet werden, um das Wochenende abzudecken."},
        {"type": "p", "text": "Es sind winzige Beträge — berechnet auf Basis der Anzahl der Einheiten des Assets, die du hältst. Im Laufe der Zeit können diese kleinen Gebühren sich aber ansammeln... Wenn du sie zahlst, macht dich das sehr zeitbewusst. Wie lange wirst du diesen Trade offen halten?"},
        {"type": "h3", "text": "Lohnt es sich bei diesen steigenden Gebühren?"},
        {"type": "p", "text": "Wenn du diese Gebühren nicht zahlst, ändert sich deine ganze Einstellung zur Zeit. Was macht es schon, wie lange der Trade offen bleibt? Er verliert vielleicht jetzt, aber in ein paar Monaten dreht er sich und ich bin im Gewinn. Was ist das Problem?"},
        {"type": "p", "text": "Das Problem ist, dass ich dich kopiere, und du zahlst diese Gebühren nicht, aber ich schon. Wenn du also überlegst, welchen Gewinn du machen wirst, berücksichtigst du diese Gebühren nicht."},
        {"type": "p", "text": "Ich aber zahle diese Gebühren. Also magst du sagen \"Schau, ich habe Gewinn gemacht\", wenn du den Trade schließt, und ich bin möglicherweise im Verlust. Für den gleichen Trade. Nicht so gut."},
        {"type": "h2", "text": "Werde ich Alnayefs Trades weiter kopieren?"},
        {"type": "p", "text": "Vorerst ja. In der Vergangenheit haben die Gebühren pro Trade nur einen sehr kleinen Anteil am Gesamttrade ausgemacht. Erst jetzt wird das Problem spürbar."},
        {"type": "p", "text": "Er hat sich in einigen Trades verfangen, die gegen Markttrends laufen. Er sieht eine Währung stärker werden, und sie wurde schwächer."},
        {"type": "p", "text": "Die Forex-Märkte scheinen von großen makroökonomischen Faktoren bewegt zu werden. Das bedeutet, dass manche Trends eine Weile anhalten können. Solange dieser Trend anhält und Alnayef auf der falschen Seite steht, bleiben die Trades offen. Das bedeutet, die Gebühren haben sich angesammelt und machen jetzt einen spürbaren Anteil dieser spezifischen Trades aus."},
        {"type": "p", "text": "Aber ich werde ihn weiter kopieren. Er war ein guter, konsistenter, risikoarmer Trader, also werde ich abwarten, wie sich die Dinge entwickeln. Ich beobachte aber immer genauer."},
        {"type": "h2", "text": "Wie lief es bei Olivier Danvel mit dem Cost Averaging?"},
        {"type": "p", "text": "Sehr gut! Erinnerst du dich, wie ich letztes Mal darüber gesprochen habe, dass Olivier mehrere Lots desselben Forex-Paares kaufte?"},
        {"type": "p", "text": "Seine Strategie hat sich ausgezahlt und er hat den Mai mit gutem Gewinn beendet."},
        {"type": "p", "text": "Olivier hat seine ununterbrochene Serie grüner Statistiken beibehalten. Sehr beeindruckend :)"},
        {"type": "h2", "text": "Berraus kniffliger Forex-Trade"},
        {"type": "p", "text": "Berrau hat sich gut geschlagen, aber er ist diesen Monat im Gewinn gefallen. Es liegt an einem bestimmten Forex-Trade auf dem AUD/USD-Paar. Er hat einen 'Verkauf'-Trade auf das Paar eröffnet. Leider hat der Australische Dollar (AUD) tatsächlich begonnen, gegenüber dem US-Dollar (USD) stärker zu werden. Also fing er an, Geld zu verlieren..."},
        {"type": "img", "src": "../images/Berrau-short-term-AUDUSD-trades-june-2019-2400x1150.png", "alt": "Berrau kurzfristige AUD/USD-Forex-Trades auf eToro — Juni 2019"},
        {"type": "p", "text": "Er hat den Trade offen gehalten, und er hat weiter verloren, aber noch ist nicht alles verloren!"},
        {"type": "p", "text": "Er hat auch kürzere Kauf- und Verkauf-Trades auf den AUD/USD gemacht, die ihm etwas Gewinn zurückgebracht haben."},
        {"type": "p", "text": "Ich werde weiter beobachten, wie er mit diesem Drawdown bei diesem spezifischen Trade umgeht. Was, wenn er 100% Verlust erreicht (bei diesem Trade)? Wird er den Stop Loss über 100% hinaus erweitern oder ihn schließen? Ich weiß es nicht, also warte ich ab, welche Entscheidung er trifft."},
        {"type": "p", "text": "Abgesehen davon hat er sich gut geschlagen. Ich bin immer sehr gespannt zu sehen, wie die Trader, die ich kopiere, mit widrigen / unerwarteten Situationen umgehen. Ehrlich gesagt gewinne oder verliere ich ständig Vertrauen in sie."},
        {"type": "p", "text": "Ich suche nach Leuten, bei denen ich zeitweise einfach aufhören kann zuzuschauen und darauf vertraue, dass sie die richtige Entscheidung treffen. Mal sehen, wie es ausgeht..."},
        {"type": "h2", "text": "Kela-Leo — Wie handelt er?"},
        {"type": "p", "text": "Wieder hat Kela-Leo nicht wirklich viel gemacht. Er ist ein bisschen hochgegangen, dann ein bisschen runter, dann ein bisschen hoch, runter. Nicht viel los."},
        {"type": "p", "text": "Er hat gehandelt, aber die Gewinne und Verluste gleichen sich ziemlich aus. Sein Risiko ist immer noch niedrig — er liegt immer noch im Rahmen meiner Risikoziele für das Portfolio. Ich warte einfach weiter ab und schaue, was er macht."},
        {"type": "h3", "text": "Hedging innerhalb des Portfolios"},
        {"type": "p", "text": "Ich habe tatsächlich eine seltsame Situation mit Kela-Leo und einigen meiner anderen Trader. Manche kaufen GBP/USD, und manche verkaufen :) Das passiert gerade bei einigen verschiedenen Forex-Paaren. Einige meiner Trader wetten gegen einige meiner anderen Trader."},
        {"type": "p", "text": "Etwas seltsam zu beobachten, aber es hält das Portfolio auf eine Art auch ziemlich sicher. Wenn sie alle das gleiche Asset in die gleiche Richtung handeln würden, wäre ich möglicherweise zu hohem Risiko ausgesetzt... Es wäre wie zu viele Eier in einem Korb. Zumindest auf diese Weise ist meine Risikoexposition verringert. Hoffentlich geht die Rechnung am Ende auf und ich komme im Gewinn raus :)"},
        {"type": "h2", "text": "Harshsmith und der Baidu-Trade"},
        {"type": "p", "text": "Also, kurz nachdem ich angefangen hatte, Harshsmith zu kopieren, hatte ein Unternehmen, in das er investiert hat — Baidu — seinen Ergebnisbericht. Die Ergebnisse verfehlten die Erwartungen, und die Aktie fiel. Es war einfach schlechtes Timing. Letzte Woche war Harshsmith also weiter im Minus, aber es erholt sich langsam."},
        {"type": "img", "src": "../images/Harshsmith-losing-baidu-trade-june-2019-2400x1300.png", "alt": "Harshsmith verlierender Baidu-Trade im eToro-Portfolio — Juni 2019"},
        {"type": "p", "text": "Im Moment sind viele der Trades noch im Minus, aber sie bewegen sich wieder in die richtige Richtung."},
        {"type": "p", "text": "Er verwendet pro Trade nur einen kleinen Anteil seiner Kontogröße, also hat es insgesamt keinen riesigen Unterschied gemacht..."},
        {"type": "p", "text": "Er ist nur einen Bruchteil im Minus, obwohl dieser Trade wirklich schlecht aussieht. Sein Long/Short-Portfoliosystem bedeutet, dass er gegen große Marktbewegungen abgesichert ist. Wenn einige fallen, steigen andere und umgekehrt. Das auszubalancieren und sicherzustellen, dass es insgesamt profitabel ist, ist seine Kompetenz."},
        {"type": "p", "text": "Ich werde natürlich abwarten und zusehen, wie er es dreht. Ich bin froh, endlich Harshsmith zu kopieren! Es hat eine Weile gedauert, die Mittel zusammenzubekommen wegen des Mindesthandelsgrößen-Problems :)"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-15-jun-2019 ----
updates["copy-trading-update-15-jun-2019"] = {
    "slug": "copy-trading-update-15-juni-2019",
    "meta_description": "Copy Trading Update — 15. Juni 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 15. Juni 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Juni 2019",
    "h1": "Copy Trading Update — 15. Juni 2019",
    "content_blocks": [
        {"type": "h2", "text": "15. Juni 2019 Copy Trading / Dezentralisierung / Geldmanagement"},
        {"type": "p", "text": "Ich habe meinem Bruder in letzter Zeit geholfen, einige Videos zum Thema 'Dezentralisierung' zu machen."},
        {"type": "img", "src": "../images/Last-Train-To-Utopia-youtube-channel-2400x1300.png", "alt": "Last Train to Utopia YouTube-Kanal — Copy-Trading-Vlog-Update"},
        {"type": "p", "text": "Es ist ein faszinierendes Thema und wirft viel Licht darauf, woher Bitcoin kommt."},
        {"type": "p", "text": "Es erklärt auch, warum sie Kryptowährungen geschaffen haben — was die Schöpfer damit erreichen wollten."},
        {"type": "p", "text": "Ich wollte die Videos auf meinem Kanal veröffentlichen, aber wirklich, es macht mehr Sinn auf seinem. Mit der Zeit wird er mehr machen, also wenn es dich interessiert, schau es dir an."},
        {"type": "h2", "text": "Geld verschenken"},
        {"type": "p", "text": "Ich gehe auch meinen vorläufigen Plan durch, 10% einiger meiner Einnahmen zu verschenken..."},
        {"type": "img", "src": "../images/monopoly-man-1500x1300.jpg", "alt": "Monopoly-Männchen — zur Veranschaulichung von Geldmanagement und Vermögenskonzepten"},
        {"type": "p", "text": "Genauer gesagt, alles was ich aus dem eToro Popular-Investors-Programm verdiene."},
        {"type": "p", "text": "Ich weiß nicht, ob ich das durchhalte — es ist nur ein Gedanke, aber ich werde es versuchen."},
        {"type": "p", "text": "Im Moment habe ich sehr wenig Geld. Ich bin es gewohnt, wenig Geld zu haben und irgendwie über die Runden zu kommen. Aber ich habe viele reiche Leute kennengelernt, und ich habe einige der damit verbundenen Fallen gesehen. Es scheint ziemlich leicht zu sein, reich zu werden und sich zu fragen, warum man nicht so glücklich ist."},
        {"type": "p", "text": "Soweit ich sehen kann, sind die glücklichen Menschen diejenigen, die es schaffen, anderen auf irgendeine kleine Weise zu helfen. Die weisesten Menschen, denen ich zum Thema Geld zugehört habe, sprechen ziemlich oft darüber. Ich habe es auch aus verschiedenen alten und modernen Kulturen gehört. Es scheint, dass man, solange man geben kann, eine bessere Chance hat, glücklich zu bleiben."},
        {"type": "p", "text": "Es liegt wahrscheinlich daran, dass Freude mit dem Erfolg verbunden ist, statt nur Angst, ihn zu verlieren. Das scheint eine große Falle zu sein, in die viele Leute tappen. Ich höre viel darüber, wie man Geld verdient. Aber ich würde auch gerne wissen, wie man wirklich gut damit leben kann :)"},
        {"type": "p", "text": "Wie auch immer — das ist die Idee. Wir werden sehen, wie es läuft..."},
        {"type": "h2", "text": "Zeit für das Copy-Trading-Portfolio-Update"},
        {"type": "p", "text": "Das Portfolio lief gut. So gut, dass es seit letztem Mal nicht viel zu sagen gibt."},
        {"type": "img", "src": "../images/My-Copy-Trading-Portfolio-June-15-2019-2400x1300.png", "alt": "Vollständige eToro Copy-Trading-Portfolio-Übersicht — 15. Juni 2019"},
        {"type": "p", "text": "Alnayefs steigende Gebühren und mangelnde Veränderung bedeuten, dass ich jetzt offiziell besorgt bin."},
        {"type": "p", "text": "Ich werde den Betrag reduzieren, mit dem ich ihn kopiere, und ihn und Kela-Leo gleichmäßiger machen."},
        {"type": "p", "text": "Ich werde mehr Geld (wenn ich es habe) zu Harshsmith, Berrau und Olivier Danvel hinzufügen. Ich hätte die gerne bei jeweils etwa 24% meines Portfolios (zusammen etwa 72%)."},
        {"type": "p", "text": "Dann können Kela-Leo und Alnayef möglicherweise die anderen 28% zwischen sich aufteilen. Wir werden sehen..."},
        {"type": "h2", "text": "Berrau und der AUD/USD-Forex-Trade"},
        {"type": "p", "text": "Berrau hatte eine etwas turbulente Zeit, nachdem ein Forex-Trade auf AUD/USD gegen ihn gelaufen war. Er hat aber gut reagiert und 'Cost Averaging' eingesetzt, um seinen durchschnittlichen Einstiegspreis zu senken."},
        {"type": "img_grid", "images": [
            {"src": "../images/AUD-USD-Forex-trade-June-2019-Berrau.png", "alt": "Berrau AUD/USD-Forex-Trade-Position auf eToro — Juni 2019"},
            {"src": "../images/Berrau-eToro-June-2019-profit-statistics-15-June-2019-1024x551.png", "alt": "Berraus eToro-Gewinnstatistiken — 15. Juni 2019"}
        ]},
        {"type": "p", "text": "Als das Paar in seine Richtung ging, konnte er schneller und im Gewinn aussteigen! Gute Arbeit :)"},
        {"type": "p", "text": "Er macht sich diesen Monat sehr gut, mit 1,57% Gewinn bisher. Er macht einfach einen tollen Job, und ich bin wirklich zufrieden."},
        {"type": "p", "text": "Ich werde mehr Geld zu meiner Kopie von Berrau hinzufügen, sobald ich es habe."},
        {"type": "p", "text": "Das war nicht das erste Mal, dass Berrau in einem Forex-Trade war, der gegen ihn lief. Er war schon in einigen drin, und jedes Mal hat er kluge Techniken eingesetzt, um sich herauszuhandeln."},
        {"type": "p", "text": "Wenn ein Trade zu weit gegen Berrau läuft, eröffnet er oft eine Position in die entgegengesetzte Richtung als Absicherung. Wenn sein 'Verkauf'-Trade zu viel verliert, eröffnet er oft einen 'Kauf'-Trade für den gleichen Betrag im gleichen Instrument."},
        {"type": "p", "text": "Der Effekt ist, dass, wenn einer fällt, der andere mit dem gleichen Wert steigt, sodass der Gewinn statisch bleibt. Die Gewinne gleichen die Verluste perfekt aus. Wenn sich die Lage beruhigt, fängt er an, Cost Averaging oder kleinere Trades zu nutzen, um sich aus der Position herauszuarbeiten. Es hat bisher jedes Mal funktioniert. Das Ergebnis ist, dass ich mir weniger Sorgen gemacht habe, als ich sah, dass der Trade diesmal in die falsche Richtung ging. Ich habe es schon mal gesehen, und er hat es gut gemeistert."},
        {"type": "h2", "text": "Wie geht es Olivier? Immer noch grün?"},
        {"type": "p", "text": "Ja. Immer noch grün und macht sich gut."},
        {"type": "img", "src": "../images/Olivier-eToro-0.45-May-14-2019-2400x1300.png", "alt": "Olivier Danvel eToro-Konto mit 0,45% Gewinn — Mai 2019"},
        {"type": "p", "text": "Er hat mir konsistent kleine Beträge aus dem Markt geholt. Stetig und ermutigend :)"},
        {"type": "p", "text": "Er hat derzeit knapp unter einem halben Prozent im Juni gemacht."},
        {"type": "p", "text": "Ich werde auch mehr Geld zu meiner Kopie von Olivier hinzufügen. Er passt zu meinem Gesamtziel... \"Wer wird mir stetig Geld verdienen, auch wenn es langsam geht, mit sehr geringem Risiko, mein Geld zu verlieren.\" Klingt einfach, aber du wärst überrascht, wie schwer diese Frage zu beantworten ist."},
        {"type": "h2", "text": "Alnayef und meine Gebührensorgen"},
        {"type": "p", "text": "Die Gebühren auf meine Kopie von Alnayef betragen jetzt über 50% des Gewinns, den er mir über die gesamte Kopierzeit eingebracht hat."},
        {"type": "img", "src": "../images/My-copy-trading-portfolio-Alnayef-fees-june-2019-1600x822.png", "alt": "eToro Copy-Trading-Portfolio mit Alnayef-Gebührenaufschlüsselung — Juni 2019"},
        {"type": "p", "text": "Das ist mir zu viel."},
        {"type": "p", "text": "Ich bin die Gebührenbedenken mit Alnayef in meinem letzten Copy-Trading-Update durchgegangen."},
        {"type": "p", "text": "Die Situation scheint sich nicht zu bessern. Die offenen Verlust-Trades ziehen weiter nach unten, und die Gebühren steigen."},
        {"type": "p", "text": "Ich werde ihn vorerst weiter kopieren, um zu sehen, was passiert, aber im Moment ist meine Einstellung zur Kopie negativ. Es ist schade, da ich ihn für talentiert halte und er mir wirklich gute Gewinne gebracht hat."},
        {"type": "p", "text": "Ich werde ihm aber keine weiteren Mittel zuweisen — die werden an Berrau, Olivier und Harshsmith gehen."},
        {"type": "h2", "text": "Kela-Leo und ein möglicher Gold-Bullenmarkt"},
        {"type": "p", "text": "Kela-Leo hat ein paar Gold-'Verkauf'-Positionen offen gehalten. Das würde in mancher Hinsicht Sinn machen, außer dass es so aussieht, als könnte ein neuer Gold-Bullenmarkt beginnen. Das ist nicht so gut. Er ist diesen Monat bisher 1,79% im Minus, und meine Kopie von ihm geht weiter in die falsche Richtung."},
        {"type": "p", "text": "Sein Risiko ist immer noch niedrig, und er hat ehrlich gesagt nicht so viel verloren. Ich glaube, ich habe ihn vielleicht einfach zu einem unglücklichen Zeitpunkt kopiert, als die Dinge nicht in seine Richtung laufen. Ich werde trotzdem abwarten. Wenn er stark verlieren würde, wäre ich besorgter, aber vorerst sind es alles relativ kleine Bewegungen."},
        {"type": "h2", "text": "Harshsmith — Nichts zu berichten."},
        {"type": "p", "text": "Es hat sich so wenig verändert, dass es nicht viel über meine Kopie von Harshsmith zu sagen gibt. Er hat nicht wirklich viel gewonnen oder verloren. Einfach da, stabil, immer noch mit leichtem Verlust, aber nichts allzu Besorgniserregendes. Ich warte ab :)"},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-23-jul-2019 ----
updates["copy-trading-update-23-jul-2019"] = {
    "slug": "copy-trading-update-23-juli-2019",
    "meta_description": "Copy Trading Update — 23. Juli 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 23. Juli 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · Juli 2019",
    "h1": "Copy Trading Update — 23. Juli 2019",
    "content_blocks": [
        {"type": "h2", "text": "23. Juli 2019 3 Kommentare Mein Copy-Trading-Portfolio ist stabil... Es ist eine etwas optimistische Sichtweise, aber man muss sich auf das Positive konzentrieren! Bisher bin ich diesen Monat 0,5% im Minus, ABER das ist immer noch besser als 3 der Trader in meinem Portfolio im gleichen Zeitraum performt haben..."},
        {"type": "h2", "text": "Ein schönes Stück Diversifikation"},
        {"type": "p", "text": "Ich handle nicht manuell, ich mache Copy Trading, und ich kopiere mehrere Personen in meinem Portfolio. Das gibt mir eine viel größere Diversifikation, als wenn ich nur manuell handeln würde, da diverse Trader zu diversen Trades führen. Je diverser, desto sicherer..."},
        {"type": "p", "text": "Ich kopiere sechs verschiedene Trader, also sind meine Eier nicht alle in einem Korb. Drei meiner Trader — Harshsmith, Alnayef und Kela-Leo — hatten negative Monate, aber ich war vor der vollen Wucht ihrer Verluste geschützt, da ich andere Trader habe, die gut performt haben."},
        {"type": "h2", "text": "Es sind aber trotzdem keine Gewinne, Tom..."},
        {"type": "p", "text": "Ich weiß, es ist nicht ideal, irgendwo Verluste zu sehen, aber zurück zur Sache mit den Silberstreifen — es ist gut, die Vorteile meiner Diversifikation in Aktion zu sehen. (Man muss sich die kleinen Siege manchmal nehmen...) Es kann wirklich frustrierend sein, den Tradern zuzusehen, die man kopiert, wenn sie Geld verlieren. Die Versuchung, ihnen als Beifahrer-Trader reinzureden, ist manchmal wirklich ziemlich stark :)"},
        {"type": "p", "text": "Ich musste den Drang unterdrücken, Kommentare auf ihren Pinnwänden zu hinterlassen und sie 'sanft' auf die Verluste aufmerksam zu machen. Aber das bringt nichts, und sie sind wahrscheinlich bereits sehr bewusst und tun ihr Bestes, um die Situation zu korrigieren. Sie haben mehr zu verlieren als ich — diese Popular-Investor-Sterne sind hart erkämpft. Das Letzte, was einer von ihnen will, ist ein massiver Exodus von Kopierern, also bin ich sicher, dass sie tun, was sie können..."},
        {"type": "h2", "text": "Welche Trader gewinnen also?"},
        {"type": "h3", "text": "Herr Berrau"},
        {"type": "p", "text": "Berrau ist im Moment der ziemlich klare Spitzenreiter. Er hat eine ununterbrochene Serie grüner Monate, die bis Mitte letzten Jahres zurückreicht. Er hat stetig und konsistent die richtige Richtung in verschiedenen AUD/USD-Forex-Trades gewählt. Manchmal kauft er, manchmal verkauft er, aber er hatte ziemlich durchgehend seit über einem Monat recht. Das ist eine große Erleichterung."},
        {"type": "p", "text": "Als ich ihn zuerst kopiert habe, gab es ein paar Fälle, wo er in die falsche Richtung gehandelt hat (gekauft, wenn der Preis fiel, oder verkauft, wenn der Preis stieg). Aber in letzter Zeit lag er goldrichtig. Dank ihm haben mich die Drawdowns einiger anderer Trader, die ich kopiere, nicht zu stark getroffen. Danke Berrau!"},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Immer noch grün, immer noch konsistent gewinnend, er hat wie üblich stetig und profitabel Forex gehandelt. Ich habe nicht viel mehr zu sagen als \"Was für eine Erleichterung\" :)"},
        {"type": "p", "text": "Der Großteil meines Geldes ist zwischen dem Kopieren von Olivier, Berrau und Harshsmith aufgeteilt. Etwa 75% meines Portfolios verteilen sich auf diese drei Trader. Alnayef, Kela-Leo und jetzt GrePod machen die anderen 25% zwischen sich aus."},
        {"type": "h2", "text": "Und die Übrigen?"},
        {"type": "h3", "text": "Alnayef — all meine Mittel gebunden"},
        {"type": "p", "text": "Ich würde meine Kopie von Alnayef an diesem Punkt sogar noch weiter reduzieren, aber man kann nur Mittel aus einer Kopie entfernen, die nicht in aktiven Trades verwendet werden... (Ich habe dazu ein Video auf meinem Kanal gemacht)."},
        {"type": "p", "text": "Im Moment muss ich, sofern ich ihn nicht entkopiere, die Mittel, die er bereits verwendet, dort lassen, wo sie sind."},
        {"type": "p", "text": "Ich suche aktiv nach Ersatz für Alnayef und um einen weiteren Copy-Trading-Platz zu füllen. Ich habe gesucht, aber Trader mit niedrigen Risikoprofilen, konsistenten Renditen über einen längeren historischen Zeitraum (vielleicht 2 Jahre) zu finden, ist ziemlich schwierig. Ich mache weiter, bis ich mehr finde... Alnayefs Gebühren sind mittlerweile übertrieben, da er einige Trades seit inzwischen 8 Monaten offen hat."},
        {"type": "p", "text": "Das ist an sich okay, aber sie sammeln Gebühren an, und die Gebühren sind nur zwei Dollar weniger als der Gewinn, den er mir bisher eingebracht hat. An diesem Punkt, nach einer 8-monatigen Kopie, hat er mir $2 verdient. Das ist einfach zu wenig. Und die offenen Trades binden mein Geld, das möglicherweise anderswo in besseren Positionen eingesetzt werden könnte. Es gibt 'Opportunitätskosten'."},
        {"type": "h3", "text": "Kela-Leo bewegt sich nicht wirklich"},
        {"type": "p", "text": "Es gibt nicht viel mehr zu sagen als die Überschrift hier. Kela-Leo macht weiterhin kleine Gewinne hier und da und einige kleinere Verluste. Das Problem ist, dass er bei einigen Gold-Trades (proportional) so große Verluste gemacht hat, dass ich nicht weiß, wie lange es dauern wird, bei seinem aktuellen Tempo einige Gewinne zurückzuholen. Vorerst lasse ich ihn im Portfolio und wünsche ihm das Beste, aber ich suche aktiv nach neuen Tradern. Eigentlich suche ich immer, aber die Notwendigkeit ist gerade offensichtlicher."},
        {"type": "h2", "text": "3 Gedanken zu \"Copy Trading Update — eToro — 24/Juli/2019\""},
        {"type": "p", "text": "Hallo, mein Name ist Angga aus Indonesien... Südostasien. Mein Englisch ist nicht so gut... aber ich versuche zu verstehen, was du auf YouTube sagst. Ich mache auch seit weniger als 1 Monat Copy Trading auf eToro. Ich kopiere auch Berrau... und eine weitere Person, die ich persönlich ausgewählt habe. Aber ich habe eine Frage an dich. Ich investiere jeweils $300 USD... aber warum geben sie (die PIs) nur $2-5 USD meines Geldes aus... warum nicht alles verwenden, was ich ihnen gebe...? Danke für die Antwort..."},
        {"type": "p", "text": "Das hängt wirklich vom Stil des Traders ab. Sehr wenige Trader werden dein gesamtes Geld in aktiven Trades verwenden. Sie versuchen, ihre 'Risikoscores' niedrig zu halten, und ein Weg dafür ist, nur kleine Prozentsätze ihrer Gesamtkontogröße in aktiven Trades einzusetzen. Manche nutzen mehr als andere, und es könnte sein, dass sie im Moment nur so viel von ihrem eigenen Geld riskieren wollen. Denk daran, sie handeln tatsächlich mit ihrem eigenen Geld — du kopierst nur genau das, was sie tun."},
        {"type": "p", "text": "Ich weiß, es kann frustrierend sein, und manchmal will ich auch, dass sie mehr von meinem Geld in aktiven Trades verwenden, aber ich habe diese Art zu denken eigentlich aufgegeben. Ich schaue mir einfach ihre Risikoscores an, ihre jährlichen Drawdown-Statistiken und ihre historische Profitabilität. Wenn mir gefällt, was ich sehe, kopiere ich sie und lasse sie sich um ihren Handelsstil kümmern und wie viel Geld sie einsetzen. Wenn sie mir einen Prozentsatz einbringen können, mit dem ich zufrieden bin, und dabei einen Risikoscore beibehalten, mit dem ich mich wohlfühle, dann ist das großartig. Ihre Methoden, diese Ergebnisse zu erzielen, sind ihre Sache."},
        {"type": "p", "text": "Das Einzige, was es noch sein könnte, ist, dass du möglicherweise einige ihrer offenen Trades verpasst, weil du sie nicht mit genug Geld kopierst. Ich habe ein Video dazu gemacht — die Mindesthandelsgrößen beim Copy Trading — du findest es auf YouTube. Um zu prüfen, ob das passiert, schau dir einfach ihr Portfolio auf ihrer Profilseite an und sieh, welche Trades sie derzeit offen haben. Dann geh zu deinem eigenen Portfolio und sieh dir deine Kopie von ihnen an. Überprüfe, ob du alle Trades, die sie offen haben, auch über deine Kopie offen hast. Du kannst auch den 'Verlauf'-Bereich ihres Portfolios und deiner Kopie überprüfen, um zu sehen, ob du auch alle vergangenen Trades hattest... Ich würde mir das Video über Mindesthandelsgrößen beim Copy Trading ansehen, um zu verstehen, was ich meine. Hier ist es: https://www.youtube.com/watch?v=BSxCSZHx5kI"},
        {"type": "p", "text": "Ok... verstehe... vielen Dank für deine Antwort... Das war eine sehr gute Erklärung... Ich werde mir dein Video ansehen... oben verlinkt. Danke... und freut mich, dich kennenzulernen... hoffen wir, dass wir ein paar Dollar bei eToro verdienen...? Ich kopiere mit ungefähr $600 USD... und sorry für mein schlechtes Englisch..."},
        {"type": "p", "text": "Kommentare sind geschlossen."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-02-aug-2019 ----
updates["copy-trading-update-02-aug-2019"] = {
    "slug": "copy-trading-update-02-august-2019",
    "meta_description": "Copy Trading Update — 02. August 2019. Ehrliche Dokumentation meiner Erfahrungen mit der Copy-Trading-Funktion von eToro.",
    "title": "Copy Trading Update — 02. Aug. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · August 2019",
    "h1": "Copy Trading Update — 02. Aug. 2019",
    "content_blocks": [
        {"type": "h2", "text": "3. August 2019 3 Kommentare Die Trading-Achterbahn... Es war eine verrückte Woche! Die Wahl von Boris Johnson in Großbritannien ließ das Britische Pfund gegenüber dem USD wie ein Stein fallen. Die US-Notenbank senkte die Zinsen, und die Volatilität ging für kurze Zeit durch die Decke. Es war wirklich eine Woche voller Schocks..."},
        {"type": "h2", "text": "Harshsmith handelt wie ein Champion"},
        {"type": "p", "text": "Letzte Woche war er der Trader mit dem größten Drawdown in meinem Portfolio. Diese Woche ist er der Superstar und jetzt der zweitbeste Performer unter all meinen Tradern. Das ist eine erstaunliche Leistung. Er hat in der letzten Woche etwa 5% gemacht, wobei die Wende kam, als die Fed-Zinsnachricht veröffentlicht wurde."},
        {"type": "p", "text": "Es war tatsächlich erstaunlich zuzusehen. Da saß ich, hörte online die Fed-Nachrichten, klebte an meinem Bildschirm und beobachtete mein Portfolio. In dem Moment, als die Nachricht herauskam, beobachtete ich, wie Harshsmiths Gewinn sich zu ändern begann. Er stieg in den nächsten 30 Minuten oder so rapide an, und in den Tagen seither hat er einfach weiter zugelegt. Ausgezeichnet."},
        {"type": "p", "text": "Ich bin sicher, es muss andere Trader auf der 'falschen Seite' dieser Nachricht gegeben haben. Das muss hart gewesen sein... Aber zum Glück war unser Mann Harshsmith gut vorbereitet und positioniert, als die Ankündigung kam."},
        {"type": "h3", "text": "Erste Profitabilität seit ich angefangen habe, ihn zu kopieren"},
        {"type": "p", "text": "Das ist tatsächlich das erste Mal, dass er im Gewinn ist, seit ich vor 2 Monaten angefangen habe, seine Trades zu kopieren. Kurz nachdem ich ihn kopiert hatte, verzeichnete ein großer Trade in Baidu nach einem schlechten Ergebnisbericht starke Verluste. Seitdem war er durchgehend im Minus und hat langsam weiter verloren."},
        {"type": "p", "text": "Das ist schwer, einfach auszusitzen. Man schaut zu, wartet und sieht immer mehr Rot. Das macht keinen Spaß. Aber er ist ein geschickter Analyst und Trader, also bin ich dabei geblieben und habe einfach gewartet, bis seine Strategie aufgeht. Er ist mein einziger Aktien-Trader, und das sind seltsame Zeiten für Aktien. Ich glaube, jeder erwartet einen Crash, während gleichzeitig die Märkte auf Allzeithochs steigen. Wohin platzierst du deine Wette?"},
        {"type": "p", "text": "Vorerst scheint Harshsmiths 'Net Short'-Strategie gut zu funktionieren. 'Net Short' bedeutet einfach, dass er insgesamt mehr 'Verkauf'-Trades offen hat als 'Kauf'-Trades. Obwohl das stimmt, hat er auch mit seinen Kauf-Trades erhebliche Gewinne erzielt. In einer Marktrallye, obwohl er net short ist, hat er es geschafft, seine Verluste zu kontrollieren — sie durch Gewinne bei den Käufen auszugleichen. Tolle Arbeit :) Er macht derzeit etwa 14% meiner gesamten Portfoliogröße aus."},
        {"type": "h2", "text": "Handelt Berrau immer noch wie ein Ochse?"},
        {"type": "p", "text": "Seltsame Verwendung dieses Ausdrucks, aber wenn man darüber nachdenkt, ergibt es Sinn. Ein Ochse ist langsam, stetig, zuverlässig und erledigt die Arbeit. Das beschreibt Berrau in letzter Zeit ziemlich gut."},
        {"type": "p", "text": "Er macht immer noch alle 2-3 Tage kleine Gewinne. Es ist im Moment ziemlich wie ein Uhrwerk. Es gibt einen Gewinntrade, dann eine Pause für einen Tag, und dann wieder einen Gewinntrade, und dann eine weitere Pause, und dann — usw. Er war wirklich konstant, und er ist der bestperformende Trader in meinem Portfolio. Ausgezeichnet. Er macht derzeit auch etwa 24% meines gesamten Portfolios aus."},
        {"type": "h2", "text": "Wo ist Alnayef hin??"},
        {"type": "p", "text": "Ich habe meine Kopie von Alnayef gestoppt. Es ist wirklich schade, denn er war einer meiner stärksten Trader... Aber es gab monatelange Inaktivität und keine Kommunikation. Gleichzeitig hatte er all diese gehebelten Trades offen — einige seit etwa 8 Monaten — die alle Gebühren ansammelten und einfach da saßen und langsam weiter verloren."},
        {"type": "p", "text": "Hätte ich einfach geduldiger sein sollen? Möglich. Viele der Instrumente, die er handelt, sind auf oder nahe historischen Unterstützungsniveaus. Das würde darauf hindeuten, dass eine Aufwärtswende bevorstehen könnte und jetzt nicht der richtige Zeitpunkt ist, die Kopie zu stoppen. Aber es gibt auch die Opportunitätskosten — könnte mein Geld effizienter anderswo eingesetzt werden? Ich denke gerade schon. Ich habe 8 Monate darauf gewartet, dass einige dieser Trades geschlossen werden und das Geld anderswo eingesetzt wird. Das ist nicht passiert. Die Trades lagen einfach da, endlos. Die Gebühren stiegen. Alle verfügbaren Mittel wurden in neue, verlierende offene Trades verwendet, und an diesem Punkt ist die Kopie einfach feststeckt."},
        {"type": "p", "text": "Es gibt keine weiteren verfügbaren Mittel, um neue Trades zu eröffnen und die Verluste auszugleichen. Also habe ich nur zugesehen, wie es langsam (und zuletzt schneller) weiter verlor. Es ist wirklich schade. Ich frage mich immer noch, ob das Stoppen der Kopie die richtige Entscheidung war, aber vorerst ist es so. Wir werden es in Zukunft sehen."},
        {"type": "h2", "text": "Wie hat sich mein neuer Trader gemacht?"},
        {"type": "p", "text": "Wehe mir... Sehr bald nachdem ich meinen neuesten Trader — Gianluca Conte — kopiert hatte, eröffnete er einige riskantere Trades, die sich dann prompt gegen ihn wendeten und viel Geld verloren... Nicht gut. Er hat in 3 Tagen so viel verloren wie Alnayef in den letzten drei Monaten. Zu riskant."},
        {"type": "h3", "text": "War es ein Fehler, ihn zu kopieren?"},
        {"type": "p", "text": "Nein, ich denke immer noch, dass es angesichts seiner jüngsten Statistiken (letzte 2 Jahre) und seiner Risikoscores im letzten Jahr ein guter Schritt war. Was kein guter Schritt war, ist, dass ich ihn mit etwas zu viel meiner Mittel kopiert habe. Ich hätte beim Minimum bleiben sollen... Das habe ich nicht. Der kleine Spieler in mir war da. Ich habe ein bisschen gewürfelt und ihn mit etwa 14% meines Portfolios kopiert statt den 6% Minimum, mit denen ich hätte starten sollen. Mein Fehler."},
        {"type": "p", "text": "Mit den großen Drawdowns, die in seinen 2018er Statistiken zu sehen waren, hätte ich mehr Vorsicht walten lassen sollen. Es war alles sichtbar... Er hat gut performt. Er scheint sein Risiko reduziert zu haben. Die Dinge waren in den letzten Jahren stabil. ABER TROTZDEM waren die Beweise für sein früheres Risikoverhalten da, und ich hätte so vorsichtig wie möglich bleiben sollen."},
        {"type": "h3", "text": "Was jetzt mit ihm?"},
        {"type": "p", "text": "Der große Verlust-Trade, den er offen hat, ist nahe historischen Tiefs und Unterstützungsniveaus. Ich denke, er erwartet, dass es dieses historische Tief erreicht und wieder nach oben springt... Er hat das in seinem Feed gesagt, und die Charts unterstützen seine Analyse. Wir werden sehen. Zwei Dinge könnten passieren:"},
        {"type": "p", "text": "1. Der Trade erreicht das Unterstützungsniveau, springt nach oben und holt die Verluste wieder auf."},
        {"type": "p", "text": "2. Der Trade bricht durch die Unterstützung, und wir sehen, wie gut er damit umgeht. Würde er den Trade schließen und aussteigen? Oder würde er ihn offen halten und weiter verlieren?"},
        {"type": "p", "text": "Ich weiß es noch nicht — ich habe Kommentare über ihn gelesen und sehe Hinweise für beide möglichen Szenarien. Ich bin nervös deswegen, aber wir werden sehen."},
        {"type": "p", "text": "Ich ziehe etwas von dem Geld ab, mit dem ich ihn kopiert habe, damit seine zukünftigen Handelsgrößen kleiner werden. Ich muss auch meinen Copy Stop Loss anpassen, um ihm fairen Raum zum Handeln zu geben und gleichzeitig mein Risiko zu kontrollieren. Ich arbeite daran."},
        {"type": "h2", "text": "Ist Olivier Danvel immer noch im Grünen?"},
        {"type": "p", "text": "Ja :) Es war aber am letzten Tag im Juli sehr knapp. Olivier war an einer Reihe von Trades beteiligt, die Ende letzten Monats stark verloren hatten. Als das Pfund durch die Boris-Johnson-Nachrichten schwer getroffen wurde, gingen seine Trades stark ins Minus. Es sah wirklich so aus, als würde er seinen ersten Monat im Minus beenden..."},
        {"type": "p", "text": "Am letzten Tag des Monats gab es einen Aufschwung, und Olivier schloss alle seine offenen Trades mit Verlust, aber möglicherweise viel weniger Verlust, als es hätte sein können. Zum Zeitpunkt der Schließung sah es so aus, als würden sie wieder nach unten gehen."},
        {"type": "h3", "text": "Die 'Fed' und Volatilität..."},
        {"type": "p", "text": "Es fiel auch mit den Fed-Zinsnachrichten zusammen. Wenn die US-Notenbank (bekannt als 'die Fed') Nachrichten über ihre Zinspläne veröffentlicht, dreht alles durch."},
        {"type": "p", "text": "Die Volatilität geht durch die Decke, wann immer es Nachrichten von der Fed gibt, also hat Olivier klugerweise alle Trades vor dieser Nachricht geschlossen. Trades während der Fed-Pressekonferenz offen zu halten kann ein großes Glücksspiel sein angesichts der Volatilität, die oft folgt. Ich denke, es war ein kluger Schritt von Herrn Danvel :)"},
        {"type": "p", "text": "Es hat viele Leute erschreckt, und es wurde darüber geredet, ob er alle Trades nur geschlossen hat, damit seine Statistiken für den Monat grün bleiben. Aber ich denke, es war ein sehr kluger Schritt. Er wurde bei einigen Trades auf dem falschen Fuß erwischt und hat seine Verluste und potenziellen Verluste gut kontrolliert."},
        {"type": "p", "text": "Also, Olivier hat in meinem Portfolio gegenüber dem letzten Monat verloren, aber er ist immer noch profitabel und hat wieder offene Trades, also werden wir sehen, wie es diesen Monat läuft. Ich kopiere Olivier immer noch mit etwa 24% meines gesamten Portfolios."},
        {"type": "p", "text": "Also machen Olivier, Harshsmith und Berrau zusammen etwa 72% meines gesamten Portfolios aus. Schön."},
        {"type": "h2", "text": "Kela-Leo — wie geht es ihm?"},
        {"type": "p", "text": "Er hat seit dem letzten Video etwas mehr verloren. Er wendet immer noch ungefähr die gleiche Strategie an und scheint leider immer noch nicht in der Lage zu sein, den langsamen Drawdown und die langsam steigenden Verluste zu stoppen. Ich bin mir nicht sicher, was ich über ihn sagen soll. Er macht immer noch keine riesigen Verluste — er macht nichts Riskantes. Er scheint nur durchgehend auf der falschen Seite der Trades zu stehen."},
        {"type": "p", "text": "Ich bin mir nicht sicher, ob es möglicherweise einfach sehr schlechtes Timing ist... Er macht eigentlich nichts Dummes. Alles ergibt Sinn — es funktioniert einfach nicht wirklich. Ich warte vorerst weiter ab..."},
        {"type": "h2", "text": "Der neue Trader, den ich kopiert habe"},
        {"type": "p", "text": "Also, ich habe einen neuen kopiert — mtsnom015. Sie hat laut ihrem Profil 7 Jahre Erfahrung. Die Statistiken der letzten 3 Jahre sind solide und risikoarm. Ihre Risikoscores im letzten Jahr sind niedrig, und ihre Drawdowns liegen unter meinem 15%-Ziel für den maximalen jährlichen Drawdown."},
        {"type": "p", "text": "Sie ist eine weitere Forex-Traderin. (Ich weiß, ich bin sehr Forex-lastig, aber ich begrenze immer noch meine Aktien-Exposure). Ich habe sie mit dem Minimum von etwa 6% des Portfolios kopiert :)"},
        {"type": "p", "text": "Ich habe keine offenen Trades kopiert — mal sehen, wie es läuft."},
        {"type": "h2", "text": "3 Gedanken zu \"Copy Trading Update — eToro — 02/Aug/2019\""},
        {"type": "p", "text": "Hey,"},
        {"type": "p", "text": "Wie vergleichst du eToro mit ZuluTrade? Ich liebe wirklich all deine YouTube-Videos und stütze meine gesamte eToro-Strategie auf Hilfe aus deinen Videos."},
        {"type": "p", "text": "Wenn man bedenkt, dass ZuluTrade die größte Forex-Social-Trading-Website ist, würde ich gerne wissen, was du denkst?"},
        {"type": "p", "text": "Die Anzahl der Leute zum Kopieren auf ZuluTrade ist viel größer als auf eToro und ihre Renditen sind viel, viel besser als die der Top-Leute auf eToro."},
        {"type": "p", "text": "Yugal (Australien)"},
        {"type": "p", "text": "Hallo, ich habe mir ZuluTrade angesehen, fand es aber viel weniger benutzerfreundlich und schwieriger zu verstehen. Ich musste mich zuerst auf eine Plattform konzentrieren, und ich habe mich für eToro entschieden. Bist du sicher, dass es dort mehr Forex-Trader gibt? Ich glaube, eToro ist derzeit der Weltmarktführer beim Social Trading — könnte mich aber irren, ich werde noch mal nachschauen. Danke!"},
        {"type": "p", "text": "Hallo,"},
        {"type": "p", "text": "Danke für deinen Vblog, er ist interessant. Ich habe viele Regeln über CFDs und eToro gelesen, aber ich verstehe immer noch nicht: Wenn ich einen anderen Trader mit $100 kopiere und er in CFDs investiert, ist es möglich, dass ich mehr als $100 verlieren kann?"},
        {"type": "p", "text": "Kommentare sind geschlossen."},
        {"type": "risk_warning"}
    ]
}

# ---- copy-trading-update-24-aug-2019 ----
updates["copy-trading-update-24-aug-2019"] = {
    "slug": "copy-trading-update-24-august-2019",
    "meta_description": "Copy Trading Update — 24. August 2019. Gold, Silber und Portfolio-Entscheidungen ehrlich dokumentiert.",
    "title": "Copy Trading Update — 24. Aug. 2019 | SocialTradingVlog",
    "article_tag": "Portfolio-Update · August 2019",
    "h1": "Copy Trading Update — 24. Aug. 2019",
    "content_blocks": [
        {"type": "p", "text": "Das Update dieser Woche behandelt mein Copy-Trading-Portfolio auf eToro, mit besonderem Fokus auf Gold- und Silber-Positionen und einem Überblick darüber, wie die Leute, die ich kopiere, performt haben."},
        {"type": "img_grid", "images": [
            {"src": "../images/bag-of-gold.jpg", "alt": "Beutel mit Goldmünzen als Darstellung von Gold als Anlage"},
            {"src": "../images/U.S-Silver-Eagle-1-ounce-coin.jpg", "alt": "American Silver Eagle Einunzen-Münze — Silberinvestition"}
        ]},
        {"type": "h2", "text": "Gold und Silber"},
        {"type": "p", "text": "Gold hat sich in letzter Zeit stark entwickelt, was sich positiv auf das Portfolio ausgewirkt hat. Einige der Leute, die ich kopiere, haben bedeutende Positionen in Edelmetallen, und es war interessant zu beobachten, wie sich diese bewegt haben. Silber hat ebenfalls Bewegung gezeigt — wie immer können diese Assets volatil sein und sich auf schwer vorhersagbare Weise bewegen."},
        {"type": "h2", "text": "Überlegungen zur Portfolio-Aufteilung"},
        {"type": "p", "text": "Ich habe über meine Gesamtaufteilung nachgedacht — wie viel ich bei jeder Person auf eToro kopiert habe. Das Gleichgewicht zwischen denjenigen, die sich auf Aktien konzentrieren, denjenigen mit Rohstoff-Exposure und denjenigen mit Krypto-Positionen ist etwas, das ich regelmäßig überprüfe. Diese Mischung richtig hinzubekommen ist Teil dessen, was Copy Trading erfordert — man muss immer noch über Diversifikation nachdenken, auch wenn man die einzelnen Trades nicht selbst macht."},
        {"type": "img", "src": "../images/pie-chart-investments.jpg", "alt": "Kreisdiagramm zur Darstellung der Investment-Portfolio-Aufteilung über verschiedene Assets"},
        {"type": "h2", "text": "Was ich beobachte"},
        {"type": "p", "text": "Der globale wirtschaftliche Hintergrund war unsicher, was sich in den Märkten widerspiegelt. Ich achte darauf, wie die Leute, die ich kopiere, darauf reagieren — bleiben sie standhaft, passen sie ihre Positionen an oder reagieren sie auf kurzfristiges Rauschen? Ihr Verhalten in unsicheren Märkten sagt viel über ihren Ansatz aus."},
        {"type": "img_grid", "images": [
            {"src": "../images/Screenshot-2019-08-28-at-13.20.09.png", "alt": "eToro Copy-Trading-Portfolio-Screenshot — 28. August 2019"},
            {"src": "../images/Screenshot-2019-08-28-at-13.56.27.png", "alt": "AUD/JPY Drawdown-Chart auf eToro — August 2019"}
        ]},
        {"type": "risk_warning"}
    ]
}

# Assemble final output
final = {
    "faq": part1["faq"],
    "contact": part1["contact"],
    "updates": updates
}

# Validate and write
output_path = '/Users/thomaswest/socialtradingvlog-website/tools/translations/updates_faq_contact_de.json'
json_str = json.dumps(final, ensure_ascii=False, indent=2)

# Quick validation
parsed = json.loads(json_str)
print(f"Valid JSON: True")
print(f"FAQ questions: {len(parsed['faq']['questions'])}")
print(f"Total update posts: {len(parsed['updates'])}")
print(f"Update post keys:")
for k in sorted(parsed['updates'].keys()):
    print(f"  {k}")

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(json_str)

print(f"\nFile written to: {output_path}")
print(f"File size: {len(json_str)} characters")

# Clean up temp files
import os
os.remove('/Users/thomaswest/socialtradingvlog-website/tools/translations/_part1.json')
print("Temp file cleaned up.")
