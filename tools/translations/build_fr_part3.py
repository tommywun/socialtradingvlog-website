#!/usr/bin/env python3
"""Build part 3 of French translation — updates 20-27."""
import json

with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_fr_part2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def rw():
    return {"type": "risk_warning", "text": "Rappel Les performances passees ne sont pas une indication des resultats futurs. 51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils negocient des CFD avec eToro. Votre capital est a risque. Ceci n'est pas un conseil en investissement."}

# -------------------------------------------------------
# 20. copy-trading-update-30-apr-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-30-apr-2019"] = {
    "slug": "mise-a-jour-copy-trading-30-avril-2019",
    "meta_description": "Mise a jour copy trading — 30 avril 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 30 Avr 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Avril 2019",
    "h1": "Mise a jour Copy Trading — 30 Avr 2019",
    "content_blocks": [
        {"type": "h2", "text": "30 avril 2019 Social Trading Vlog Il a declenche mon Copy Stop Loss... Vous vous souvenez dans la derniere mise a jour, quand je parlais de Citadelpoint ? C'etait le trader le plus performant de mon portefeuille. Pendant des semaines, il n'avait apporte qu'excitation et solides gains verts. Et puis le trade risque sur AUD/USD."},
        {"type": "p", "text": "Eh bien ca a empire la nuit apres que j'ai enregistre cette derniere video. Les marches ont bouge contre lui de facon assez dramatique. Le lendemain, quand je me suis reveille, il avait disparu du portefeuille."},
        {"type": "img_grid", "images": [{"src": "../images/Screenshot-2019-08-29-at-15.14.01.png", "alt": "Portefeuille eToro apres le declenchement du copy stop loss — Avril 2019"}, {"src": "../images/Screenshot-2019-08-29-at-16.15.16.png", "alt": "Trade eToro ferme automatiquement apres le copy stop loss — Avril 2019"}]},
        {"type": "p", "text": "Ca a pris un moment pour comprendre ce qui s'etait passe..."},
        {"type": "p", "text": "Pendant la nuit, le trade avait subi de lourdes pertes alors que le Dollar americain se renforcait face au Dollar australien. Quelque part au milieu de la nuit, mon copy stop loss s'est declenche et le trade et toute la copie ont ete fermes."},
        {"type": "p", "text": "C'est vraiment dommage — je prenais vraiment plaisir a le regarder trader. Et je prenais vraiment plaisir aux profits !"},
        {"type": "h2", "text": "Qu'aurais-je pu faire pour le garder dans mon portefeuille ?"},
        {"type": "p", "text": "Pas grand-chose vraiment... J'aurais pu faire deux choses :"},
        {"type": "h3", "text": "A : Annuler ce trade sur AUD/USD manuellement."},
        {"type": "p", "text": "Ca aurait pu etre fait. J'aurais simplement du aller dans mon portefeuille et cliquer sur le nom de Citadelpoint. De la, j'aurais pu voir tous les trades que je copie via lui."},
        {"type": "p", "text": "Il y a un 'X' rouge a droite de chacun des trades copies. J'aurais pu cliquer dessus et le fermer manuellement. Mais alors, si je commence a faire ca, y a-t-il un interet a appeler ca du copy trading ? Ou est-ce du trading partiellement copie, partiellement manuel... Est-ce que je veux devoir faire ca indefiniment ?"},
        {"type": "p", "text": "Et si j'avais ferme le trade et qu'ensuite ca s'etait bien passe ? Qu'auraient dit mes copieurs alors ? \"Tom, on t'aime bien, mais arrete de toucher aux copies manuellement !\" Si j'avais gagne, j'aurais ete plutot malin. Si j'avais perdu cependant, j'aurais trahi la confiance de tout le monde. Pas une super idee..."},
        {"type": "h3", "text": "B : Augmenter mon Copy Stop Loss."},
        {"type": "p", "text": "J'aurais pu aller dans mon portefeuille, cliquer sur la petite icone d'engrenage a droite et faire des changements. Mon Copy Stop Loss (CSL) est actuellement fixe a 85% pour tous mes traders. Aurais-je du augmenter le montant que je suis pret a perdre avec Citadelpoint ?"},
        {"type": "p", "text": "Peut-etre que j'aurais pu le mettre a 80% (ce qui signifie que je risquerais 20% de l'argent investi avec lui.) Et pourquoi pas 75% ou meme 70% ? De combien aurais-je du modifier le stop loss pour survivre aux drawdowns potentiels..."},
        {"type": "p", "text": "Et est-ce que ce serait juste envers toutes les autres personnes que je copie ? Ca signifierait que je donne a la personne la plus risquee plus de marge qu'aux personnes plus sures pour perdre mon argent."},
        {"type": "p", "text": "Aucune de ces options ne semble etre un super plan..."},
        {"type": "h2", "text": "Il est parti, et c'est comme ca — quels traders restent ?"},
        {"type": "p", "text": "Chocowin, Alnayef, Berrau, Olivier Danvel, et Kela-Leo sont maintenant les traders que je copie..."},
        {"type": "p", "text": "Entre eux, ils tradent principalement le forex, un peu d'actions, et un tout petit peu d'or. Alors comment vont-ils tous..."},
        {"type": "p", "text": "Honnetement, je pense que je le reduirais a environ 5% du portefeuille si je pouvais. Je le ferais pour les memes raisons que j'aurais reduit Citadelpoint. Son risque est juste trop eleve pour le portefeuille que j'essaie de construire..."},
        {"type": "p", "text": "Il s'en est tres bien sorti cependant. Il trade frequemment et avec succes, et engrange les profits."},
        {"type": "p", "text": "Donc, avec le meme mouvement de l'actif, ses pertes restent minimales. Mieux..."},
        {"type": "p", "text": "Il a aussi fait pas mal de petits trades gagnants recemment, ce qui est bon a voir. Il avait en gros disparu pendant un moment, donc un signe d'activite est le bienvenu. J'attends de voir ce qui se passe ensuite avec lui."},
        {"type": "h2", "text": "Comment trade Berrau ?"},
        {"type": "p", "text": "Plutot bien. Il est en hausse de 2,65% jusqu'ici pour avril, ce qui est super. Il n'a pas beaucoup de trades ouverts en ce moment — juste un petit trade Ripple (XRP) qui perd un peu. 2,65% c'est beaucoup de profit pour quelqu'un dont le risque est aussi bas que celui de Berrau. Il s'en sort bien !"},
        {"type": "img_grid", "images": [{"src": "../images/Screenshot-2019-08-29-at-16.32.21.png", "alt": "Performance de trading de Berrau sur eToro — fin avril 2019"}, {"src": "../images/Screenshot-2019-08-29-at-16.48.28.png", "alt": "Statistiques de copy trading de Berrau sur eToro — fin avril 2019"}]},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Maintenant, Olivier est connu pour ses resultats a faible risque et sa mer de vert. Jusqu'ici, il a ete tres regulier. Ce mois-ci est le premier, meme petit signe d'une approche legerement plus risquee. Apres avoir ouvert un trade forex, ca s'est retourne contre lui. Ca arrive a tout le monde... Sa methode pour gerer ca etait quelque chose appele le 'cost averaging' (*je pense !)"},
        {"type": "p", "text": "Ca signifie que lorsque le trade va contre vous et que le prix baisse, vous continuez a ouvrir de petites nouvelles positions a intervalles."},
        {"type": "p", "text": "Les positions sont dans la meme direction — tous des 'achats' dans ce cas."},
        {"type": "p", "text": "L'idee est de se retrouver avec un prix d'achat moyen plus bas (quand on prend la moyenne de tous les prix d'ouverture.)"},
        {"type": "p", "text": "C'est une tactique utilisee par beaucoup de traders qui s'y connaissent. A terme, quand le trade touche le fond et que l'actif change de direction, ca devrait payer assez vite. Plus le prix d'achat moyen est bas, mieux c'est."},
        {"type": "p", "text": "C'est apparemment ce qu'Olivier faisait, et maintenant le trade s'est retourne et il est en voie de revenir au vert."},
        {"type": "p", "text": "C'etait une plus grande amplitude que ce a quoi j'etais habitue de sa part cependant."},
        {"type": "p", "text": "C'est un trader a faible risque — sous mon drawdown maximum annuel de 15% avec de faibles scores de risque actuels. Je ne pense pas qu'il fasse quoi que ce soit de fou, donc j'aurai le temps de voir comment il s'en sort !"},
        rw()
    ]
}

# -------------------------------------------------------
# 21. copy-trading-update-07-may-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-07-may-2019"] = {
    "slug": "mise-a-jour-copy-trading-07-mai-2019",
    "meta_description": "Mise a jour copy trading — 07 mai 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 07 Mai 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Mai 2019",
    "h1": "Mise a jour Copy Trading — 07 Mai 2019",
    "content_blocks": [
        {"type": "h2", "text": "7 mai 2019 Social Trading Vlog Quel trader d'actions garder ?"},
        {"type": "p", "text": "Donc la question principale de cette mise a jour est de savoir si j'echange mon trader d'actions actuel pour un nouveau. En ce moment, je copie Chocowin pour mes actions. Il s'en sort bien, mais son profil de risque est un peu eleve pour mes objectifs."},
        {"type": "p", "text": "Je surveille un trader appele 'Harshsmith' depuis un moment maintenant. Ses scores de risque sont plus bas, ses performances sont bonnes, et je pense a passer a lui. Mais d'abord, je reviens sur quelques sondages de mes videos precedentes..."},
        {"type": "h2", "text": "Resultats des sondages sur quels traders copier"},
        {"type": "p", "text": "Recemment, j'ai publie quelques-unes de ces videos \"Copieriez-vous ce trader\". C'est un bon moyen de passer en revue les suggestions de mes spectateurs et aussi de laisser tout le monde donner son avis. Les sondages sont vraiment utiles pour ca, car ils permettent aux futurs spectateurs de voir comment les autres pensent..."},
        {"type": "p", "text": "Voici les resultats :"},
        {"type": "p", "text": "1. VIDEO : \"Copieriez-vous Berrau\" Oui : 54% Le mettre en watchlist pour le moment : 21% Non, il est trop ennuyeux : 18% Non, il est trop risque : 5%"},
        {"type": "img", "src": "../images/Berrau-closed-trades-may-07-2019-eToro-2400x1300.png", "alt": "Trades clotures de Berrau sur eToro — 7 mai 2019"},
        {"type": "p", "text": "2. VIDEO : \"Copieriez-vous LoydBazaar\" OUI : 40% Le mettre en watchlist pour le moment : 37% Pas sur : 15% Non : 6%"},
        {"type": "p", "text": "3. VIDEO : \"Copieriez-vous Kela-Leo\" Oui : 53% Le mettre en watchlist pour le moment : 12% Pas sur : 20% Non : 14%"},
        {"type": "p", "text": "Maintenant, je sais que ce n'est pas scientifique ! J'ai pose des questions legerement differentes et donne des options differentes pour les reponses. Prenez ca comme une indication approximative et un peu d'amusement... Faites toujours vos propres recherches avant de decider qui copier !"},
        {"type": "h2", "text": "Retour a Harshsmith VS Chocowin"},
        {"type": "p", "text": "Donc, comme je disais, je regarde a changer le trader d'actions que je copie dans mon portefeuille. Pourquoi ?"},
        {"type": "p", "text": "Chocowin a tres bien fait pour moi, mais compare a Harshsmith, il est a haut risque. Mon objectif est d'avoir un portefeuille a faible risque. J'ai mis en place quelques regles informelles pour atteindre cet objectif."},
        {"type": "p", "text": "L'une d'elles concerne le 'Max Drawdown'. C'est une metrique dans les statistiques d'eToro qui mesure le drawdown maximum de chaque trader au cours de la derniere annee. Le 'drawdown' peut presque etre assimile a une 'serie de pertes'."},
        {"type": "p", "text": "Ca decrit essentiellement la plus grande perte que vous avez faite avant de recommencer a gagner. C'est comme regarder un creux dans vos profits — jusqu'ou le trader a-t-il laisse descendre avant de redresser la barre."},
        {"type": "p", "text": "Je l'utilise pour avoir une idee approximative de si un trader est susceptible de declencher mon Copy Stop Loss de 15%. Je fixe mon Copy Stop Loss (CSL) a 15% pour chaque trader que je copie afin de ne pas risquer trop de mon capital. Mais j'essaie aussi de choisir des traders dont l'historique montre qu'ils sont peu susceptibles de declencher mon CSL."},
        {"type": "p", "text": "Je ne veux pas fixer un stop loss aussi serre pour le voir declenche constamment. Ca n'aurait aucun sens. Donc je surveille leurs statistiques..."},
        {"type": "h2", "text": "Scores de risque et drawdown maximum annuel de Chocowin"},
        {"type": "p", "text": "Ici vous pouvez voir les scores de risque de Chocowin pour les douze derniers mois ainsi que les statistiques de Max Drawdown. Si vous les comparez a ceux de Harshsmith (montres ci-dessous), vous verrez que les scores de risque sont plus eleves tout au long de l'annee."},
        {"type": "img", "src": "../images/Chocowin-risk-scores-max-yearly-drawdown-May-2019-1024x657.png", "alt": "Scores de risque et drawdown maximum annuel de Chocowin sur eToro — Mai 2019"},
        {"type": "p", "text": "Sous le graphique en barres, vous pouvez voir la section Max Drawdown. Le nombre a droite de la case montre le drawdown maximum annuel. Comme vous pouvez le voir, celui de Chocowin est au-dessus de ma cible de 15%, alors que celui de Harshsmith est bien en dessous..."},
        {"type": "h2", "text": "Scores de risque et drawdown maximum annuel de Harshsmith"},
        {"type": "p", "text": "Ca semble etrange d'arreter de copier un trader qui m'a fait de bons profits. Mais tout est question de croissance durable et a faible volatilite a l'avenir. C'est mon objectif principal. Si je mettais $20 000 dans mon compte de trading eToro, quels traders voudrais-je voir trader avec mon argent ?"},
        {"type": "img", "src": "../images/Harshsmith-risk-scores-max-yerly-drawdonw-may-2019-1024x657.png", "alt": "Scores de risque et drawdown maximum annuel de Harshsmith sur eToro — Mai 2019"},
        {"type": "p", "text": "Les deux tradent des actions, les deux sont historiquement rentables. L'un est statistiquement moins risque que l'autre. Que feriez-vous ? J'ai demande aux spectateurs, et je verrai ce que dit la sagesse de la foule. Je penche vers l'arret de Chocowin et la copie de Harshsmith cependant."},
        {"type": "p", "text": "Je ne veux pas trop d'exposition aux actions car la volatilite semble etre une nouvelle norme, et je dois surveiller mon risque. D'ou mon penchant pour ne garder qu'un seul trader d'actions dans mon portefeuille."},
        {"type": "h2", "text": "Comment vont les autres traders ?"},
        {"type": "h3", "text": "Alnayef"},
        {"type": "p", "text": "Il est a peu pres au meme niveau que dans la derniere mise a jour. Pas grand-chose n'a bouge vraiment... Il y a beaucoup de rouge."},
        {"type": "img", "src": "../images/Alnayef-open-trade-may-07-2019-eToro-2400x1300.png", "alt": "Trades ouverts d'Alnayef visibles dans le portefeuille eToro — 7 mai 2019"},
        {"type": "p", "text": "Alnayef n'a pas fait grand-chose. Il a encore beaucoup de trades legerement perdants ouverts, et il semble juste les laisser la. Il attend qu'ils passent au vert je pense. Je ne sais pas combien de temps ca prendra. Pour l'instant, je vais juste continuer a le laisser et surveiller. Esperons que les choses s'ameliorent."},
        {"type": "p", "text": "Il ne prend pas de risques massifs, et ne fait rien d'insense. Il est juste du mauvais cote de beaucoup de trades — mais pas assez gravement pour paniquer. Il y a juste un sentiment persistant qu'il est dans une sorte de serie de pertes lente."},
        {"type": "h3", "text": "Berrau"},
        {"type": "p", "text": "Il s'en est tres bien sorti. Des gains lents et reguliers — faisant environ 0,25% sur chaque trade gagnant, avec une serie de gagnants recemment."},
        {"type": "p", "text": "Ses scores de risque et son drawdown maximum sont toujours bas, et il semble etre sur la bonne voie en ce moment. Tous les deux jours environ, il ouvre un nouveau trade. Quand il gagne un quart de pourcent, il le ferme et prend le profit. Simple et propre."},
        {"type": "p", "text": "Quand je l'ai copie pour la premiere fois, beaucoup de ses trades allaient contre lui. Il arrivait quand meme a s'en sortir avec profit. Recemment cependant, tous ses nouveaux trades semblent aller dans son sens. Pourvu que ca dure !"},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Il est a peu pres au meme niveau aussi. Il a eu un peu de drawdown a la fin du mois dernier, mais a reussi a se retourner pour finir en profit. Il a toujours 100% de mois verts dans ses statistiques. Je suis satisfait d'Olivier, et je vais le laisser la pour faire son travail !"},
        {"type": "h3", "text": "Kela-Leo"},
        {"type": "p", "text": "Kela-Leo est juste monte un peu, puis descendu un peu, puis monte un peu tout le mois. Mes profits de la copie n'ont pas vraiment bouge, donc il n'y a pas grand-chose a dire ! Encore une fois, j'attends et je surveille..."},
        rw()
    ]
}

# -------------------------------------------------------
# 22. copy-trading-update-16-may-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-16-may-2019"] = {
    "slug": "mise-a-jour-copy-trading-16-mai-2019",
    "meta_description": "Mise a jour copy trading — 16 mai 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 16 Mai 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Mai 2019",
    "h1": "Mise a jour Copy Trading — 16 Mai 2019",
    "content_blocks": [
        {"type": "h2", "text": "16 mai 2019 Social Trading Vlog Quel trader a gagne dans le sondage de la semaine derniere ? La semaine derniere, j'ai dit que je pensais echanger l'un des traders que je copie pour un nouveau. Je pensais arreter ma copie de Chocowin et commencer une nouvelle copie de Harshsmith. Ils tradent tous les deux des actions, mais le profil de risque de Harshsmith est plus en phase avec mes objectifs de faible risque."},
        {"type": "p", "text": "J'ai mis un sondage dans ma derniere video pour voir comment vous, les spectateurs, pensiez. Voici les resultats :"},
        {"type": "p", "text": "\"Remplacer Chocowin par Harshsmith ?\""},
        {"type": "p", "text": "'Garder les deux dans le portefeuille' : 56% 'Oui - Prendre Harshsmith a la place' : 32% 'Non - Garder seulement Chocowin' : 7% 'Pas sur' : 2%"},
        {"type": "p", "text": "J'ai laisse la video la pour que vous puissiez voir mon raisonnement si vous ne l'avez pas encore regardee... Alors, qu'ai-je fait ?"},
        {"type": "p", "text": "J'ai arrete de copier Chocowin, et j'ai commence a copier Harshsmith. De facon realiste, je ne veux pas trop d'exposition aux actions en ce moment. Je m'inquiete d'un retournement majeur, donc limiter mon exposition me rend moins nerveux pour le moment. Harshsmith utilise ce qu'on appelle un systeme de portefeuille 'Long/Short'. Ca signifie qu'il parie que certains actifs vont monter, et d'autres pourraient baisser."},
        {"type": "h2", "text": "Strategie de couverture Long/Short"},
        {"type": "p", "text": "C'est une strategie de 'couverture' — un moyen de rendre votre portefeuille statistiquement plus sur. Un moyen de s'assurer que si les marches plongent soudainement, vous pouvez quand meme en profiter. Ou au moins ne pas perdre autant d'argent que si vous etiez juste 'long' (acheteur) sur tout. Il se prepare essentiellement a une correction majeure. Tant que je sais qu'il surveille, je peux me detendre un peu."},
        {"type": "p", "text": "Si vous regardez son portefeuille, vous remarquerez qu'il utilise de petites proportions de son capital total sur chaque trade. Il trade toutes sortes d'actions, et il en achete certaines et en vend d'autres. Je lui ai demande quel etait son plan, et il a dit que son portefeuille est 'Net Short'."},
        {"type": "p", "text": "Ca signifie que bien qu'il achete et vende des actifs, globalement plus de son argent est dans des trades de vente (Short) que des trades d'achat (Long)."},
        {"type": "p", "text": "Il a aussi dit qu'il est short sur des actions a 'High Beta'. Les actions 'High Beta' sont celles qui sont traditionnellement plus volatiles que la moyenne du marche. Donc, il a choisi celles qu'il pense reagiraient le plus radicalement en cas de retournement soudain, et il les 'shorte'. Il a pris toutes ces mesures pour essayer de faire deux choses :"},
        {"type": "p", "text": "1. Stabiliser son portefeuille en periodes de volatilite accrue."},
        {"type": "p", "text": "2. Positionner son portefeuille pour faire des profits si les marches corrigent a la baisse."},
        {"type": "p", "text": "Avec des scores de risque et un drawdown maximum clairement plus bas, j'ai senti que le changement de traders etait la chose prudente a faire."},
        {"type": "h2", "text": "Un grand merci a Chocowin !"},
        {"type": "p", "text": "Meme si j'ai arrete de copier Chocowin, j'aimerais lui dire un grand MERCI. J'ai ferme la copie en bon profit, ce qui est un super resultat. Il m'a fait de tres bons rendements, donc je voulais juste dire merci, et lui souhaiter tout le meilleur ! Merci Chocowin !"},
        {"type": "h2", "text": "Comment Alnayef trade-t-il ?"},
        {"type": "p", "text": "Honnetement, ses frais commencent a m'inquieter un peu. Il a eu pas mal de trades qui se sont retournes contre lui, et ils perdent actuellement de l'argent. Il ne les a pas fermes cependant. Il a maintenant un portefeuille presque entierement compose de trades ouverts dans le rouge. Le truc c'est qu'il les a ouverts depuis tres longtemps."},
        {"type": "img_grid", "images": [{"src": "../images/Alnayef-open-trades-etoro-may-14-2019-2400x1300.png", "alt": "Trades ouverts d'Alnayef sur eToro — 14 mai 2019"}, {"src": "../images/alnayef-fees-on-trades-may-2019-2400x1300.png", "alt": "Frais de trading d'Alnayef sur les copies eToro — Mai 2019"}]},
        {"type": "p", "text": "Et les trades utilisent l'effet de levier."},
        {"type": "p", "text": "Maintenant, quand vous utilisez l'effet de levier sur un trade, vous encourez de minuscules 'frais overnight' et 'frais weekend'. Pour chaque jour ou le trade est ouvert, les frais s'appliquent. Ce sont de minuscules frais, mais sur un tres long delai, ils peuvent vraiment s'accumuler."},
        {"type": "p", "text": "C'est ce qui se passe avec Alnayef. Des frais sont a prevoir, et Alnayef a toujours utilise l'effet de levier. C'est juste qu'il a garde certains ouverts pendant tellement de mois maintenant que les frais sont perceptibles."},
        {"type": "p", "text": "Et les trades perdants ouverts ne semblent pas pres de se retourner. Je garde un oeil dessus, car c'est maintenant un leger probleme sur mon radar. On verra."},
        {"type": "h2", "text": "Berrau — Frais faibles et trading regulier"},
        {"type": "p", "text": "Berrau s'en sort bien. Il a ferme ce trade Ripple (XRP) en profit, et il en a ferme un autre depuis. Il avance regulierement, et heureusement a aussi genere des frais extremement faibles. Bien."},
        {"type": "h2", "text": "Olivier Danvel"},
        {"type": "p", "text": "Olivier a un trade forex qui s'est retourne contre lui (dans le rouge) ces derniers jours. Il semble employer une strategie de 'cost averaging' pour repondre a cette situation."},
        {"type": "img", "src": "../images/Olivier-Danvel-cost-averaging-forex-may-2019-2400x1264.png", "alt": "Strategie de cost averaging forex d'Olivier Danvel sur eToro — Mai 2019"},
        {"type": "p", "text": "Dans ce cas, le 'cost averaging' signifie qu'il continue d'acheter de petits lots supplementaires de la meme paire forex a mesure que le prix baisse."},
        {"type": "p", "text": "De cette facon, son prix d'achat moyen baisse de plus en plus."},
        {"type": "p", "text": "En ce moment, sa position est une position 'achat'. Il attend que la paire forex monte en valeur pour pouvoir gagner de l'argent. Puisqu'il a fait baisser son prix d'achat moyen, ca a change le prix auquel il sera en profit. L'ensemble du trade deviendra rentable meme si les premiers lots qu'il a achetes sont encore dans le rouge."},
        {"type": "p", "text": "On verra comment ca se passe. J'ai confiance en Olivier cependant — on n'obtient pas autant de mois verts d'affilee sans talent..."},
        {"type": "h2", "text": "Harshsmith — Le copy trading a commence"},
        {"type": "p", "text": "La copie de Harshsmith vient d'etre ouverte, et il y a des trades d'actions, quelques trades de matieres premieres, et des cryptos. La plus grande proportion est de loin dans les actions cependant, car c'est son focus principal. Je vais laisser et surveiller — esperons que tout se passe bien !"},
        {"type": "img", "src": "../images/HArsmith-open-trades-etoro-14-May-2019-2400x1300.png", "alt": "Trades ouverts de Harshsmith sur eToro apres le debut de la copie — 14 mai 2019"},
        {"type": "h2", "text": "Kela-Leo"},
        {"type": "h2", "text": "Mon portefeuille a faible risque"},
        {"type": "p", "text": "Tous les traders que je copie sont maintenant des traders 'a faible risque'. Tous leurs scores de risque sont du cote tres bas. Ils sont tous en dessous de mon drawdown maximum annuel cible de 15%. Voyons ce qui se passe. C'est un peu un jeu d'attente maintenant. Faible risque et un portefeuille a faible volatilite signifie que les choses se passent plus lentement et regulierement. Ca vaut pour les profits comme pour les pertes... Mon score de risque est officiellement descendu a 1 sur 10 cette semaine ! Bien."},
        {"type": "h2", "text": "Je veux faire du copy trading de cryptos"},
        {"type": "p", "text": "Etant donne que les cryptomonnaies ont connu une sorte de hausse recemment, je leur porte a nouveau attention. J'adorerais trouver un bon trader de cryptos a copier sur eToro, mais j'ai du mal avec ca."},
        {"type": "img", "src": "../images/bitcoin-logo.jpg", "alt": "Logo Bitcoin — consideration du copy trading de cryptomonnaies sur eToro"},
        {"type": "p", "text": "Tous ceux qui tradent des cryptos semblent etre soit :"},
        {"type": "p", "text": "A : Tres nouveaux, donc je ne peux pas voir assez d'historique de trading."},
        {"type": "p", "text": "B : Tradant aussi beaucoup d'actions (ce dont je ne veux pas plus d'exposition en ce moment)."},
        {"type": "p", "text": "En consequence, j'ai largement rate les mouvements recents a la hausse. Ca a ete frustrant pour etre honnete. Je suis presque tente de demander aux gens qui me copient s'ils accepteraient que je fasse du HODL manuellement. Je n'en suis pas encore la cependant. J'aimerais toujours vraiment trouver un bon trader crypto, donc je demande aux spectateurs des suggestions."},
        {"type": "p", "text": "J'ai besoin de quelqu'un avec un historique prouve. Quelqu'un sous mon drawdown maximum annuel de 15%, avec des scores de risque bas. Il y a ceux qui disent que c'est impossible sur le marche crypto. Je ne vois pas pourquoi... Si l'actif est volatil, il suffit d'utiliser de plus petites proportions du portefeuille. Eviter l'effet de levier. Mettre des stop loss. Ca devrait etre possible ! On verra quelles suggestions me reviennent !"},
        rw()
    ]
}

# -------------------------------------------------------
# 23. copy-trading-update-04-jun-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-04-jun-2019"] = {
    "slug": "mise-a-jour-copy-trading-04-juin-2019",
    "meta_description": "Mise a jour copy trading — 04 juin 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 04 Juin 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Juin 2019",
    "h1": "Mise a jour Copy Trading — 04 Juin 2019",
    "content_blocks": [
        {"type": "h2", "text": "4 juin 2019 Social Trading Vlog J'ai ete promu au niveau 'Rising Star' du Popular Investor !"},
        {"type": "p", "text": "J'ai l'etoile jaune d'eToro, et je suis maintenant un 'Rising Star' dans leur programme PI. Super. Alors comment c'est arrive ?"},
        {"type": "img_grid", "images": [{"src": "../images/eToro-Yellow-Star-Popular-Investor-Program.png", "alt": "Etoile jaune eToro indiquant le niveau Rising Star dans le programme Popular Investor"}, {"src": "../images/Etoro-Red-star-champion-popular-investor.png", "alt": "Etoile rouge eToro pour le niveau Champion du Popular Investor — le palier suivant"}]},
        {"type": "p", "text": "Eh bien, dans le cadre du programme Popular Investor d'eToro, je peux monter dans les niveaux et obtenir de meilleurs avantages. N'importe qui rejoint le programme peut le faire. L'inscription est simple — jetez un oeil a cette page ci-dessus, et elle expliquera tout."},
        {"type": "p", "text": "En gros, j'ai reussi a atteindre $40K d'AUM (actifs sous gestion) et j'avais rempli toutes les autres conditions. Des que c'etait le cas, j'ai ete promu au niveau suivant."},
        {"type": "h2", "text": "L'etoile jaune montre que vous etes un PI de niveau 'Rising Star'. Quels avantages ai-je ?"},
        {"type": "p", "text": "Eh bien, je vais maintenant recevoir un paiement de $500 directement d'eToro chaque mois, tant que je reste a ce niveau. C'est super !"},
        {"type": "p", "text": "Je ne suis plus non plus facture de frais de retrait quand je retire de l'argent d'eToro. Tres bien..."},
        {"type": "h2", "text": "Peut-on perdre son etoile ?"},
        {"type": "p", "text": "Je ne suis pas encore sur, mais je pense que oui. Je dois rester au-dessus du niveau requis pour garder mon statut actuel, ou monter davantage pour atteindre le suivant."},
        {"type": "h2", "text": "Quel est le prochain niveau de Popular Investor ?"},
        {"type": "p", "text": "Le prochain niveau serait l'etoile rouge — le Popular Investor de niveau 'Champion'."},
        {"type": "h2", "text": "Une fois au niveau 'Champion' vous aurez une etoile rouge. Retour a mes aventures de Copy Trading"},
        {"type": "p", "text": "Les choses vont plutot bien dans le portefeuille en fait. Je vais les passer en revue et parler de ce qui s'est passe."},
        {"type": "p", "text": "Je suis un peu inquiet des frais d'Alnayef, et Berrau vient d'entrer dans un trade forex un peu effrayant. Kela-Leo semble toujours monter un peu, baisser un peu. Les autres sont a peu pres les memes que la derniere fois..."},
        {"type": "h2", "text": "Alnayef et ses frais de trading"},
        {"type": "p", "text": "Le truc avec Alnayef c'est qu'il ne paie peut-etre pas de frais overnight et weekend. J'entends dire que les comptes 'islamiques' sur eToro sont exemptes de ces frais pour des raisons religieuses."},
        {"type": "img", "src": "../images/Fees-page-on-eToro.png", "alt": "Page des frais eToro montrant les frais de trading overnight et weekend expliques"},
        {"type": "p", "text": "Mais les personnes sans compte islamique qui copient ces traders ne sont pas exemptees. Ca a cree une situation un peu difficile autour de la rentabilite a ce que je vois. Maintenant il y a peut-etre d'autres frais que les gens avec compte islamique paient et pas moi."},
        {"type": "p", "text": "Je ne suis pas sur si ca s'equilibre sur le long terme, et tout est juste nomme differemment. Ca se peut — les entreprises veulent toujours faire leurs profits..."},
        {"type": "p", "text": "Mais, de ce que je vois, il n'y a pas de facteur temps dans les trades d'Alnayef, alors que l'horloge tourne pour moi."},
        {"type": "h2", "text": "Que sont les frais overnight et weekend ?"},
        {"type": "p", "text": "Au cas ou vous ne savez pas ce que sont les frais overnight et weekend, je vais expliquer brievement. (Voici la page eToro) Quand vous faites un trade :"},
        {"type": "p", "text": "Vous serez facture des frais overnight pour chaque jour ou vous gardez ce trade ouvert d'un jour a l'autre."},
        {"type": "p", "text": "Les frais 'weekend' sont simplement plusieurs 'frais overnight' additionnes pour couvrir le weekend."},
        {"type": "p", "text": "Ce sont de petits montants — calcules en fonction du nombre d'unites de l'actif que vous detenez. Avec le temps cependant, ces petits frais peuvent commencer a s'accumuler... Si vous les payez, ca vous rend tres conscient du temps. Combien de temps allez-vous garder ce trade ouvert ?"},
        {"type": "h3", "text": "Est-ce que ca vaut le coup avec ces frais qui s'accumulent ?"},
        {"type": "p", "text": "Si vous ne payez pas ces frais, toute votre attitude envers le temps change. Qu'importe combien de temps le trade reste ouvert ? Il perd peut-etre maintenant, mais dans quelques mois il se retournera et je serai en profit. Ou est le probleme ?"},
        {"type": "p", "text": "Le probleme c'est que je vous copie, et vous ne payez pas ces frais, mais moi si. Donc, quand vous pensez a quel profit vous allez faire, vous ne tenez pas compte de ces frais."},
        {"type": "p", "text": "Moi cependant, je paie ces frais. Donc vous pouvez dire \"Regardez j'ai fait du profit\" quand vous fermez le trade, et moi je peux etre en perte. Pour le meme trade. Pas terrible."},
        {"type": "h2", "text": "Vais-je continuer a copier les trades d'Alnayef ?"},
        {"type": "p", "text": "Pour l'instant, oui. Par le passe, les frais sur chaque trade n'ont represente qu'une tres petite proportion du trade global. C'est seulement maintenant que le probleme commence a etre perceptible."},
        {"type": "p", "text": "Il s'est retrouve pris dans des trades qui vont a contre-courant des tendances du marche. Il voit une devise se renforcer, et elle s'est en fait affaiblie."},
        {"type": "p", "text": "Les marches forex semblent etre mus par de grands facteurs macro-economiques. Ca signifie que certaines tendances peuvent durer assez longtemps. Tant que cette tendance dure, et qu'Alnayef est du mauvais cote, les trades resteront ouverts. Ca signifie que les frais se sont accumules et representent maintenant une proportion perceptible de ces trades specifiques."},
        {"type": "p", "text": "Mais je vais continuer a le copier. Il a ete un bon trader, regulier et a faible risque, donc je vais attendre et voir comment les choses evoluent. Je surveille de plus en plus pres cependant."},
        {"type": "h2", "text": "Comment Olivier Danvel s'en est-il sorti avec le cost averaging ?"},
        {"type": "p", "text": "Tres bien ! Si vous vous souvenez, la derniere fois, j'ai parle de comment Olivier achetait plusieurs lots sur la meme paire forex."},
        {"type": "p", "text": "Sa strategie a paye et il a termine mai en bon profit."},
        {"type": "p", "text": "Olivier a garde sa serie ininterrompue de statistiques vertes. C'est tres impressionnant !"},
        {"type": "h2", "text": "Le trade forex delicat de Berrau"},
        {"type": "p", "text": "Berrau s'en est bien sorti, mais il a baisse en profit ce mois-ci. C'est du a un trade forex specifique sur la paire AUD/USD. Il a ouvert un trade 'Vente' sur la paire. Malheureusement, le Dollar australien (AUD) a en fait commence a se renforcer face au Dollar americain (USD). Donc, il a commence a perdre de l'argent..."},
        {"type": "img", "src": "../images/Berrau-short-term-AUDUSD-trades-june-2019-2400x1150.png", "alt": "Trades forex a court terme AUD/USD de Berrau ouverts sur eToro — Juin 2019"},
        {"type": "p", "text": "Il a garde le trade ouvert, et il a continue a baisser, mais tout n'est pas perdu !"},
        {"type": "p", "text": "Il a aussi fait des trades d'achat et de vente a plus court terme sur l'AUD/USD qui lui ont rapporte des profits."},
        {"type": "p", "text": "Je vais continuer a surveiller et voir comment il gere ce drawdown sur ce trade specifique. Et si ca atteint 100% de perte (sur ce trade) ? Va-t-il etendre le stop loss au-dela de 100% ou le fermer ? Je ne sais pas, donc j'attends de voir quelle decision il prend."},
        {"type": "p", "text": "A part ca, il s'en sort bien. Je suis toujours tres interesse de voir comment les traders que je copie gerent les situations adverses / inattendues. Pour etre honnete, je suis toujours soit en train de gagner soit de perdre confiance en eux."},
        {"type": "p", "text": "Je cherche des personnes ou je peux simplement arreter de regarder par moments, en leur faisant confiance pour prendre la bonne decision. Voyons comment ca tourne..."},
        {"type": "h2", "text": "Kela-Leo — Comment trade-t-il ?"},
        {"type": "p", "text": "Encore une fois, Kela-Leo n'a pas fait grand-chose. Il est monte un peu, puis descendu un peu, puis monte un peu, descendu un peu. Pas grand-chose a signaler."},
        {"type": "p", "text": "Il a trade, mais les gains et les pertes s'equilibrent a peu pres. Son risque est toujours faible — il est toujours en ligne avec mes objectifs de risque pour le portefeuille. J'attends simplement, vraiment, pour voir ce qu'il fait."},
        {"type": "h3", "text": "Couverture au sein du portefeuille"},
        {"type": "p", "text": "J'ai en fait une situation etrange avec Kela-Leo et certains de mes autres traders. Certains achetent GBP/USD, et d'autres vendent ! Ca se produit avec quelques paires forex differentes en ce moment. Certains de mes traders parient contre certains de mes autres traders."},
        {"type": "p", "text": "C'est un peu bizarre a regarder, mais ca garde aussi le portefeuille assez sur d'une certaine maniere. S'ils tradaient tous le meme actif dans la meme direction, je pourrais etre expose a trop de risque... Ce serait comme avoir trop d'oeufs dans le meme panier. Au moins de cette facon, mon exposition au risque est reduite. Esperons que les maths fonctionnent a la fin, et que j'en sorte en profit !"},
        {"type": "h2", "text": "Harshsmith et le trade Baidu"},
        {"type": "p", "text": "Donc, juste apres avoir commence a copier Harshsmith, une entreprise dans laquelle il est investi appelee Baidu a eu son rapport de resultats. Les resultats ont ete inferieurs aux attentes, et l'action a chute. C'est juste un mauvais timing. Donc la semaine derniere, Harshsmith etait en baisse de plus, mais ca revient lentement."},
        {"type": "img", "src": "../images/Harshsmith-losing-baidu-trade-june-2019-2400x1300.png", "alt": "Trade perdant de Harshsmith sur Baidu visible dans le portefeuille eToro — Juin 2019"},
        {"type": "p", "text": "Pour l'instant, beaucoup de trades sont encore dans le rouge, mais ils bougent dans la bonne direction."},
        {"type": "p", "text": "Il n'utilise qu'une petite proportion de la taille de son compte pour chaque trade cependant, donc dans l'ensemble ca n'a pas fait une enorme difference..."},
        {"type": "p", "text": "Il n'est en baisse que d'une fraction meme si ce trade a l'air vraiment mauvais. Son systeme de portefeuille long/short signifie qu'il est couvert contre les grands mouvements du marche. Si certains baissent, d'autres montent et vice versa. Equilibrer ca et s'assurer que c'est globalement rentable, c'est son talent."},
        {"type": "p", "text": "Bien sur, je vais attendre et regarder comment il retourne la situation. Je suis content de copier enfin Harshsmith ! Ca a pris un moment pour reunir les fonds a cause du probleme de taille minimale de trade !"},
        rw()
    ]
}

# -------------------------------------------------------
# 24. copy-trading-update-15-jun-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-15-jun-2019"] = {
    "slug": "mise-a-jour-copy-trading-15-juin-2019",
    "meta_description": "Mise a jour copy trading — 15 juin 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 15 Juin 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Juin 2019",
    "h1": "Mise a jour Copy Trading — 15 Juin 2019",
    "content_blocks": [
        {"type": "h2", "text": "15 juin 2019 Social Trading Vlog Copy Trading / Decentralisation / Gestion de l'argent"},
        {"type": "p", "text": "J'ai aide mon frere a faire des videos sur le sujet de la 'decentralisation' recemment."},
        {"type": "img", "src": "../images/Last-Train-To-Utopia-youtube-channel-2400x1300.png", "alt": "Chaine YouTube Last Train to Utopia — mise a jour du vlog de copy trading"},
        {"type": "p", "text": "C'est un sujet fascinant, qui eclaire beaucoup sur l'origine du Bitcoin."},
        {"type": "p", "text": "Ca explique aussi pourquoi ils ont cree les cryptomonnaies — ce que leurs createurs esperaient accomplir."},
        {"type": "p", "text": "J'allais mettre les videos sur ma chaine, mais vraiment, ca a plus de sens sur la sienne. Au fil du temps, il en fera plus, donc si ca vous interesse, allez voir."},
        {"type": "h2", "text": "Donner de l'argent"},
        {"type": "p", "text": "Je parle aussi de mon plan provisoire de donner 10% de certains de mes gains..."},
        {"type": "img", "src": "../images/monopoly-man-1500x1300.jpg", "alt": "Monsieur Monopoly — illustrant les concepts de gestion d'argent et de richesse"},
        {"type": "p", "text": "Plus precisement, tout ce que je gagne du programme Popular Investors d'eToro."},
        {"type": "p", "text": "Maintenant, je ne sais pas si je vais m'y tenir — c'est juste une idee, mais je vais essayer."},
        {"type": "p", "text": "Pour l'instant, j'ai tres peu d'argent. Je suis habitue a avoir peu d'argent, et a juste survivre. Mais j'ai connu beaucoup de gens riches, et j'ai vu certains des pieges associes. Il semble assez facile de finir riche et de se demander pourquoi on n'est pas si heureux."},
        {"type": "p", "text": "D'apres ce que je vois, les gens heureux sont ceux qui arrivent a aider les autres meme d'une petite facon. Les personnes les plus sages que j'ai ecoutees autour de l'argent en parlent assez souvent. Je l'ai aussi entendu discute dans diverses cultures anciennes et modernes. Il semble que tant que vous pouvez continuer a donner, vous avez de meilleures chances de rester heureux."},
        {"type": "p", "text": "C'est probablement parce qu'il y a de la joie associee a votre succes, plutot que juste la peur de le perdre. Ca semble etre un gros piege dans lequel beaucoup tombent. J'entends beaucoup parler de comment gagner de l'argent. Mais j'aimerais aussi savoir comment on peut bien vivre quand on en a !"},
        {"type": "p", "text": "En tout cas — c'est l'idee. On verra comment ca se passe..."},
        {"type": "h2", "text": "Mise a jour du portefeuille de Copy Trading"},
        {"type": "p", "text": "Le portefeuille se porte bien. Si bien qu'il n'y a pas grand-chose a dire depuis la derniere fois vraiment."},
        {"type": "img", "src": "../images/My-Copy-Trading-Portfolio-June-15-2019-2400x1300.png", "alt": "Vue d'ensemble du portefeuille de copy trading eToro complet — 15 juin 2019"},
        {"type": "p", "text": "Les frais croissants d'Alnayef et son manque de changement signifient que je suis maintenant officiellement inquiet."},
        {"type": "p", "text": "Je vais reduire le montant que je copie avec lui et equilibrer avec Kela-Leo."},
        {"type": "p", "text": "Je vais ajouter plus d'argent (quand je l'aurai) a Harshsmith, Berrau et Olivier Danvel. J'aimerais avoir environ 24% de mon portefeuille sur chacun d'eux (environ 72% au total)."},
        {"type": "p", "text": "Ensuite Kela-Leo et Alnayef peuvent constituer possiblement les autres 28% entre eux. On verra..."},
        {"type": "h2", "text": "Berrau et le trade forex AUD/USD"},
        {"type": "p", "text": "Berrau a eu un moment un peu turbulent, apres qu'un trade forex sur AUD/USD se soit retourne contre lui. Il a bien reagi cependant, en utilisant le 'cost averaging' pour faire baisser son prix d'achat moyen global."},
        {"type": "img_grid", "images": [{"src": "../images/AUD-USD-Forex-trade-June-2019-Berrau.png", "alt": "Position de trade forex AUD/USD de Berrau sur eToro — Juin 2019"}, {"src": "../images/Berrau-eToro-June-2019-profit-statistics-15-June-2019-1024x551.png", "alt": "Statistiques de profit de Berrau sur eToro — 15 juin 2019"}]},
        {"type": "p", "text": "Quand la paire est allee dans son sens, il a pu sortir plus vite, et en profit ! Bravo !"},
        {"type": "p", "text": "Il s'en sort tres bien pour le mois, a 1,57% de profit jusqu'ici. Il fait vraiment du bon travail, et je suis vraiment content."},
        {"type": "p", "text": "Je vais ajouter plus d'argent a ma copie de Berrau des que j'en aurai."},
        {"type": "p", "text": "Ce n'etait pas la premiere fois que Berrau se trouvait dans un trade forex qui allait contre lui. Il en a eu quelques-uns maintenant, et a chaque fois il a utilise des techniques sages pour s'en sortir."},
        {"type": "p", "text": "Quand un trade va trop loin contre Berrau, il ouvre souvent une position dans la direction opposee comme couverture. Si son trade de 'vente' perd trop, il ouvre souvent un trade d''achat' pour le meme montant sur le meme instrument."},
        {"type": "p", "text": "L'effet est que quand l'un baisse, l'autre monte de la meme valeur, donc le profit reste statique. Les gains annulent parfaitement les pertes. Quand les choses se calment, il commence a utiliser le cost averaging ou des trades plus petits pour sortir de la position. Ca a marche a chaque fois jusqu'ici. Le resultat est que j'etais moins inquiet quand j'ai vu le trade aller dans le mauvais sens cette fois. Je l'ai deja vu avant, et il l'a bien gere."},
        {"type": "h2", "text": "Comment va Olivier ? Toujours dans le vert ?"},
        {"type": "p", "text": "Oui. Toujours dans le vert, et ca va bien."},
        {"type": "img", "src": "../images/Olivier-eToro-0.45-May-14-2019-2400x1300.png", "alt": "Compte eToro d'Olivier Danvel montrant un gain de 0,45% — Mai 2019"},
        {"type": "p", "text": "Il a regulierement pris de petits montants du marche pour moi. Du travail regulier et encourageant !"},
        {"type": "p", "text": "Il a actuellement fait un peu moins d'un demi-pourcent jusqu'ici en juin."},
        {"type": "p", "text": "Je vais ajouter plus d'argent a ma copie d'Olivier aussi. Il correspond a mon objectif global... \"Qui va me rapporter de l'argent regulierement, meme lentement, avec un risque tres faible de perdre mon argent.\" Ca semble simple, mais vous seriez surpris de voir combien cette question est difficile a repondre."},
        {"type": "h2", "text": "Alnayef et mes inquietudes sur les frais"},
        {"type": "p", "text": "Les frais sur ma copie d'Alnayef representent maintenant plus de 50% du profit qu'il m'a genere sur toute la duree de la copie."},
        {"type": "img", "src": "../images/My-copy-trading-portfolio-Alnayef-fees-june-2019-1600x822.png", "alt": "Portefeuille de copy trading eToro montrant la repartition des frais d'Alnayef — Juin 2019"},
        {"type": "p", "text": "C'est trop pour moi."},
        {"type": "p", "text": "J'ai aborde les inquietudes sur les frais avec Alnayef dans ma derniere mise a jour de copy trading."},
        {"type": "p", "text": "La situation ne semble pas se corriger d'elle-meme. Les trades perdants ouverts continuent de baisser, et les frais augmentent."},
        {"type": "p", "text": "Je vais quand meme continuer a le copier pour voir ce qui se passe, mais pour l'instant mon sentiment est negatif sur la copie. C'est dommage car je pense qu'il est talentueux, et il s'en sortait vraiment bien pour moi."},
        {"type": "p", "text": "Je ne vais pas ajouter plus de fonds a ma copie de lui cependant — je vais les ajouter a Berrau, Olivier, et Harshsmith."},
        {"type": "h2", "text": "Kela-Leo et un possible marche haussier de l'or"},
        {"type": "p", "text": "Kela-Leo a maintenu ouvertes quelques positions de 'vente' sur l'or. Ca aurait du sens dans certains cas, sauf qu'il semble qu'une nouvelle hausse de l'or pourrait etre en train de commencer. Ce n'est pas tres bon. Il est en baisse de 1,79% jusqu'ici pour le mois, et ma copie de lui continue d'aller dans le mauvais sens."},
        {"type": "p", "text": "Son risque est toujours faible, et il n'a pas perdu tant que ca pour etre honnete. Je pense que je l'ai peut-etre copie a un moment malheureux ou les choses ne semblent pas aller dans son sens. Je vais quand meme continuer a attendre et voir. S'il perdait enormement, je serais plus inquiet, mais pour l'instant, ce sont tous des mouvements relativement faibles."},
        {"type": "h2", "text": "Harshsmith — Rien a signaler."},
        {"type": "p", "text": "Si peu a change qu'il n'y a pas grand-chose a dire sur ma copie de Harshsmith. Il n'a pas vraiment gagne ou perdu beaucoup. Juste la, stable, toujours en legere perte, mais rien de trop inquietant. J'attends et on verra !"},
        rw()
    ]
}

# -------------------------------------------------------
# 25. copy-trading-update-23-jul-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-23-jul-2019"] = {
    "slug": "mise-a-jour-copy-trading-23-juillet-2019",
    "meta_description": "Mise a jour copy trading — 23 juill. 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 23 Juil 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Juillet 2019",
    "h1": "Mise a jour Copy Trading — 23 Juil 2019",
    "content_blocks": [
        {"type": "h2", "text": "23 juillet 2019 Social Trading Vlog 3 commentaires Mon portefeuille de Copy Trading est stable... C'est un peu une facon de voir le verre a moitie plein, mais il faut se concentrer sur le positif ! Jusqu'ici ce mois-ci, je suis en baisse de 0,5% MAIS c'est encore mieux que ce que 3 des traders de mon portefeuille ont fait sur la meme periode..."},
        {"type": "h2", "text": "Un bel exemple de diversification"},
        {"type": "p", "text": "Je ne fais pas de trading manuel, je fais du copy trading, et je copie plusieurs personnes dans mon portefeuille. Ca me donne une diversification beaucoup plus grande que si je faisais juste du trading manuel, car des traders divers menent a des trades divers. Plus c'est diversifie, plus c'est sur..."},
        {"type": "p", "text": "Je copie six traders differents, donc mes oeufs ne sont pas tous dans le meme panier. Trois de mes traders — Harshsmith, Alnayef, et Kela-Leo — ont eu des mois negatifs, mais j'ai ete protege de la pleine force de leurs pertes car j'ai d'autres traders qui s'en sont bien sortis."},
        {"type": "h2", "text": "Ce ne sont quand meme pas des profits, Tom..."},
        {"type": "p", "text": "Maintenant, je sais que ce n'est pas ideal de voir des pertes ou que ce soit, mais revenons a l'idee du verre a moitie plein — c'est bon de voir les benefices de ma diversification en action. (Il faut prendre les victoires la ou on peut parfois...) Ca peut etre vraiment frustrant de regarder les traders qu'on copie perdre de l'argent. La tentation de devenir un trader de banquette arriere pour eux est vraiment assez forte parfois !"},
        {"type": "p", "text": "J'ai du controler l'envie de laisser des commentaires sur leurs murs et 'gentiment' attirer leur attention sur les pertes qu'ils font. Mais ca ne sert a rien, et ils sont deja probablement tres conscients et font de leur mieux pour rectifier la situation. Ils ont plus a perdre que moi — ces etoiles de Popular Investor sont difficiles a obtenir. La derniere chose qu'ils veulent c'est un exode massif de copieurs, donc je suis sur qu'ils font ce qu'ils peuvent..."},
        {"type": "h2", "text": "Alors quels traders gagnent ?"},
        {"type": "h3", "text": "M. Berrau"},
        {"type": "p", "text": "Berrau est clairement le premier en ce moment. Il a une serie ininterrompue de mois verts remontant au milieu de l'annee derniere. Il a choisi regulierement et de maniere constante la bonne direction dans divers trades forex AUD/USD. Parfois il achete, parfois il vend, mais il a eu raison de maniere presque solide depuis plus d'un mois. C'est un grand soulagement."},
        {"type": "p", "text": "Quand je l'ai copie pour la premiere fois, il y a eu quelques cas ou il a trade dans la mauvaise direction (achetant quand le prix baissait, ou vendant quand le prix montait). Mais il a ete en plein dans le mille recemment. Grace a lui, les baisses de certains des autres traders que je copie ne m'ont pas trop affecte. Merci Berrau !"},
        {"type": "h3", "text": "Olivier Danvel"},
        {"type": "p", "text": "Toujours dans le vert, toujours regulierement gagnant, il a trade le forex de maniere constante et rentable comme d'habitude. Je n'ai pas grand-chose de plus a dire sinon \"Quel soulagement\" !"},
        {"type": "p", "text": "La majorite de mon argent est repartie entre la copie d'Olivier, Berrau et Harshsmith. Environ 75% de mon portefeuille est reparti entre ces trois traders. Alnayef, Kela-Leo et maintenant GrePod representent les autres 25% entre eux."},
        {"type": "h2", "text": "Et les autres ?"},
        {"type": "h3", "text": "Alnayef — tous mes fonds immobilises"},
        {"type": "p", "text": "J'aimerais en fait reduire encore plus ma copie d'Alnayef a ce stade, mais on ne peut retirer des fonds d'une copie que s'ils ne sont pas utilises dans des trades actifs... (J'ai fait une video a ce sujet sur ma chaine)."},
        {"type": "p", "text": "Pour le moment, a moins d'arreter de le copier, je dois laisser les fonds qu'il utilise deja la ou ils sont."},
        {"type": "p", "text": "Je cherche activement des remplacants pour Alnayef, et pour remplir une place de copy trading supplementaire maintenant. J'ai cherche, mais trouver des traders avec des profils a faible risque, des rendements reguliers sur une periode historique assez longue (peut-etre 2 ans) est assez difficile. Je vais continuer jusqu'a en trouver d'autres... Les frais d'Alnayef sont excessifs maintenant, du fait qu'il a garde certains trades ouverts pendant 8 mois a ce stade."},
        {"type": "p", "text": "Maintenant c'est bien, mais ils accumulent des frais, et les frais sont a seulement deux dollars du profit qu'il m'a rapporte jusqu'ici. Donc, a ce stade, apres une copie de 8 mois, il m'a rapporte $2. C'est juste trop peu. Et les trades ouverts immobilisent mon argent qui pourrait potentiellement etre mieux utilise ailleurs. Il y a des 'couts d'opportunite' impliques."},
        {"type": "h3", "text": "Kela-Leo ne bouge pas vraiment"},
        {"type": "p", "text": "Il n'y a pas grand-chose de plus a dire que le titre sur celui-ci. Kela-Leo continue de faire de petits gains ici et la, et quelques pertes mineures. Le probleme c'est qu'il a fait de si grosses pertes sur quelques trades d'or (proportionnellement) que je ne sais pas combien de temps il faudra pour regagner des profits au rythme ou il va. Pour l'instant, je le laisse dans le portefeuille et je lui souhaite le meilleur, mais je cherche activement de nouveaux traders. Je cherche toujours en fait, mais le besoin est plus evident en ce moment."},
        {"type": "h2", "text": "3 commentaires sur \"Mise a jour Copy Trading — eToro — 24/Juillet/2019\""},
        {"type": "p", "text": "Bonjour je m'appelle Angga d'Indonesie, en Asie du Sud-Est. Mon anglais n'est pas tres bon mais j'essaie de comprendre ce que vous dites sur YouTube. Je fais aussi du copy trading sur eToro depuis environ 1 mois. Je copie Berrau aussi, et une autre personne que j'ai choisie personnellement. Mais j'ai une question pour vous. J'investis $300 USD chacun... mais pourquoi les PI n'utilisent que $2-5 USD de mon argent... pourquoi pas tout l'argent que je leur ai donne... ? Merci pour votre reponse..."},
        {"type": "p", "text": "Ca depend du style du trader vraiment. Tres peu de traders utiliseront tout votre argent dans des trades actifs. Ils essaient de garder leurs 'scores de risque' bas, et une des facons de le faire est de n'utiliser que de petits pourcentages de la taille totale de leur compte dans des trades actifs. Certains en utilisent plus que d'autres, et il se peut qu'en ce moment, ils ne veulent risquer que cette somme de leur propre argent. Rappelez-vous, ils tradent reellement avec leur propre argent — vous copiez simplement exactement ce qu'ils font."},
        {"type": "p", "text": "Je sais que ca peut etre frustrant, et parfois je voudrais qu'ils utilisent plus de mon argent dans des trades actifs, mais j'ai abandonné ce genre de pensee maintenant. En fait, je regarde simplement leurs scores de risque, leurs statistiques de drawdown annuel, et leur rentabilite historique. Si j'aime ce que je vois, je les copie et je les laisse se soucier de leur style de trading et de combien d'argent ils utilisent. S'ils peuvent me faire un pourcentage dont je suis satisfait, tout en maintenant un score de risque avec lequel je suis a l'aise, alors c'est super. Leurs methodes pour atteindre ces resultats leur appartiennent."},
        {"type": "p", "text": "L'autre chose que ca pourrait potentiellement etre c'est que vous pourriez manquer certains de leurs trades ouverts car vous ne les copiez pas avec assez d'argent. J'ai fait une video a ce sujet — les tailles minimales de trade en copy trading — vous pouvez la trouver sur YouTube. Pour verifier si ca se produit, allez simplement voir leur portefeuille sur leur page de profil et voyez quels trades ils ont actuellement ouverts. Puis allez dans votre propre portefeuille, et voyez votre copie d'eux. Verifiez que tous les trades qu'ils ont ouverts, vous les avez aussi ouverts via votre copie. Vous pouvez aussi verifier la section 'historique' de leur portefeuille et de votre copie pour voir si vous aviez aussi tous les trades passes... Je vous conseille de regarder cette video que j'ai faite sur les tailles minimales de trade en copy trading pour comprendre ce que je veux dire. La voici : https://www.youtube.com/watch?v=BSxCSZHx5kI"},
        {"type": "p", "text": "D'accord, je vois. Merci beaucoup pour votre reponse monsieur. C'est tres bien explique. Je vais aller voir votre video, le lien ci-dessus. Merci, et ravi de vous connaitre monsieur. J'espere qu'on gagnera des dollars sur eToro. J'ai copie avec juste $600 USD... et desole pour mon mauvais anglais..."},
        {"type": "p", "text": "Les commentaires sont fermes."},
        rw()
    ]
}

# -------------------------------------------------------
# 26. copy-trading-update-02-aug-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-02-aug-2019"] = {
    "slug": "mise-a-jour-copy-trading-02-aout-2019",
    "meta_description": "Mise a jour copy trading — 02 aout 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 02 Aout 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Aout 2019",
    "h1": "Mise a jour Copy Trading — 02 Aout 2019",
    "content_blocks": [
        {"type": "h2", "text": "3 aout 2019 Social Trading Vlog 3 commentaires Les montagnes russes du trading... Ca a ete une semaine folle ! L'election de Boris Johnson au Royaume-Uni a fait chuter la Livre Sterling comme une pierre face au USD. La Reserve Federale americaine a baisse les taux d'interet, et la volatilite est montee en fleche pendant un moment. Ca a ete une semaine de chocs vraiment..."},
        {"type": "h2", "text": "Harshsmith trade comme un champion"},
        {"type": "p", "text": "La semaine derniere, il etait le trader le plus en baisse de mon portefeuille. Cette semaine, c'est la superstar, et il est maintenant le deuxieme meilleur performer de tous mes traders. C'est un exploit incroyable. Il a fait environ 5% la semaine derniere, avec le tournant venu au moment de l'annonce de la Fed sur les taux."},
        {"type": "p", "text": "C'etait incroyable a regarder en fait. J'etais la, assis, ecoutant les nouvelles de la Fed en ligne, colle a mon ecran a surveiller mon portefeuille. Au moment ou la nouvelle est tombee, j'ai regarde le profit de Harshsmith commencer a changer. Il a monte rapidement sur les 30 minutes suivantes environ, et dans les jours qui ont suivi, ca n'a fait que gagner. Excellent."},
        {"type": "p", "text": "Je suis sur qu'il doit y avoir eu d'autres traders du 'mauvais cote' de cette nouvelle. Ca a du etre difficile... Mais heureusement, notre homme Harshsmith etait bien prepare et positionne avant l'annonce."},
        {"type": "h3", "text": "Premiere rentabilite depuis que j'ai commence a le copier"},
        {"type": "p", "text": "C'est en fait la premiere fois qu'il est en profit depuis que j'ai commence a copier ses trades il y a 2 mois. Juste apres l'avoir copie, un gros trade qu'il avait ouvert sur Baidu a beaucoup baisse apres un mauvais rapport de resultats. Depuis, c'est reste constamment dans le rouge, et ca baissait lentement de plus en plus."},
        {"type": "p", "text": "C'est une chose difficile a endurer. Vous regardez, et attendez, et voyez de plus en plus de rouge. Ce n'est pas amusant. Mais c'est un analyste et trader competent, donc j'ai tenu bon et j'ai simplement attendu que sa strategie paie. C'est mon seul trader d'actions, et ce sont des temps etranges pour les actions. Je pense que tout le monde anticipe un crash tout en voyant les marches rallier vers des sommets historiques. De quel cote faites-vous votre pari ?"},
        {"type": "p", "text": "Pour l'instant, la strategie 'Net Short' de Harshsmith semble bien marcher. 'Net Short' signifie simplement qu'il a globalement plus de trades de 'vente' ouverts que de trades d'achat'. Maintenant, bien que ce soit vrai, il a aussi fait des gains significatifs sur ses trades d'achat. Donc, dans un rallye de marche, meme s'il est net short, il a reussi a controler ses pertes — les compensant avec des gains sur les achats. Beau travail ! Il represente actuellement environ 14% de la taille globale de mon portefeuille."},
        {"type": "h2", "text": "Berrau trade-t-il toujours comme un boeuf ?"},
        {"type": "p", "text": "Utilisation etrange de cette expression, mais quand on y pense, ca a du sens. Un boeuf est lent, regulier, fiable, et fait le travail. C'est a peu pres ce qu'a ete Berrau recemment."},
        {"type": "p", "text": "Il fait encore de petits gains tous les 2 ou 3 jours. C'est presque comme une horloge en ce moment. Il y a un trade gagnant, puis une pause d'un jour, puis un autre trade gagnant, puis une autre pause, puis etc. Il a ete vraiment regulier, et c'est le trader le plus performant de mon portefeuille. Excellent. Il represente aussi actuellement environ 24% de mon portefeuille global."},
        {"type": "h2", "text": "Ou est passe Alnayef ??"},
        {"type": "p", "text": "J'ai arrete ma copie d'Alnayef. C'est vraiment dommage, car il etait l'un de mes traders les plus forts... Mais il y a eu des mois d'inactivite basique et d'absence de communication. En meme temps, il avait tous ces trades a effet de levier ouverts — certains depuis environ 8 mois — tous accumulant des frais, et juste la, baissant lentement de plus en plus."},
        {"type": "p", "text": "Devrais-je etre plus patient ? C'est possible. Je veux dire, beaucoup des instruments qu'il trade sont a ou pres de niveaux de support historiques. Ca suggererait qu'un retournement a la hausse pourrait etre imminent et que ce n'est pas le moment d'arreter la copie. Mais il y a aussi les couts d'opportunite — mon argent pourrait-il etre utilise plus efficacement ailleurs ? Je le pense en ce moment. J'ai attendu 8 mois que certains de ces trades soient fermes et l'argent utilise ailleurs. Ca n'a pas ete le cas. Les trades ont juste ete laisses la, indefiniment. Les frais ont augmente. Tous les fonds disponibles ont ete utilises dans de nouveaux trades perdants ouverts, et a ce stade la copie est juste bloquee."},
        {"type": "p", "text": "Il n'y a plus de fonds disponibles pour ouvrir de nouveaux trades pour compenser les pertes. Donc j'ai juste regarde ca baisser lentement (et recemment plus rapidement). C'est vraiment dommage. Je me demande encore si arreter la copie etait la bonne decision, mais pour l'instant, c'est la ou j'en suis. On verra a l'avenir."},
        {"type": "h2", "text": "Comment va mon nouveau trader ?"},
        {"type": "p", "text": "Malheur a moi... Tres peu de temps apres avoir copie mon dernier trader — Gianluca Conte, il a ouvert des trades a plus haut risque qui se sont ensuite rapidement retournes contre lui et ont perdu beaucoup d'argent... Pas bon. Il a perdu, en 3 jours, autant qu'Alnayef a perdu au cours des trois derniers mois. Trop risque."},
        {"type": "h3", "text": "Etait-ce une erreur de le copier ?"},
        {"type": "p", "text": "Non, je pense toujours qu'au vu de ses statistiques recentes (2 dernieres annees) et de ses scores de risque sur la derniere annee, c'etait un bon choix. Ce qui n'etait pas un bon choix, c'est que je l'ai copie avec un peu trop de mes fonds. J'aurais du m'en tenir au minimum... Je ne l'ai pas fait. Le petit joueur en moi etait la. J'ai un peu lance les des, et je l'ai copie avec environ 14% de mon portefeuille au lieu des 6% minimum avec lesquels j'aurais du commencer. Mon erreur."},
        {"type": "p", "text": "Avec les gros drawdowns que je pouvais voir dans ses stats de 2018, j'aurais du etre plus prudent. C'est la a voir... Il s'en est bien sorti. Il semble avoir reduit son risque. Les choses ont ete stables ces deux dernieres annees. Mais QUAND MEME, les preuves etaient la de sa prise de risque precedente, et j'aurais du rester aussi prudent que possible."},
        {"type": "h3", "text": "Et maintenant avec lui ?"},
        {"type": "p", "text": "Le trade perdant majeur qu'il a ouvert est pres des creux historiques et des niveaux de support. Je pense qu'il s'attend a ce qu'il atteigne ce creux historique et rebondisse a la hausse... Il l'a dit sur son fil, et les graphiques confirment son analyse. On verra. Deux choses peuvent arriver :"},
        {"type": "p", "text": "1. Le trade atteint le niveau de support et rebondit a la hausse et recupere les pertes."},
        {"type": "p", "text": "2. Le trade casse le support, et on verra comment il gere ca. Fermerait-il le trade pour sortir ? Ou le garderait-il ouvert en continuant a perdre ?"},
        {"type": "p", "text": "Je ne sais pas encore — j'ai lu des commentaires a son sujet et je vois des arguments pour les deux scenarios possibles. Je suis nerveux a ce sujet, mais on verra."},
        {"type": "p", "text": "Je retire une partie de l'argent que j'ai copie avec lui pour que ses futures tailles de trade soient plus petites. J'ajuste aussi mon Copy Stop Loss pour lui donner une marge equitable pour trader, tout en controlant mon risque. J'y travaille."},
        {"type": "h2", "text": "Olivier Danvel est-il toujours dans le vert ?"},
        {"type": "p", "text": "Oui ! C'etait tres serre cependant le dernier jour de juillet. Olivier etait implique dans un certain nombre de trades qui avaient beaucoup baisse a la fin du mois dernier. Alors que la GBP se faisait marteler par les nouvelles de Boris Johnson, ses trades passaient fortement dans le rouge. Ca avait vraiment l'air comme s'il allait terminer son premier mois dans le rouge..."},
        {"type": "p", "text": "Le dernier jour du mois, il y a eu un rebond a la hausse, et Olivier a ferme tous ses trades ouverts en perte, mais potentiellement une perte bien moindre que ce qu'elle aurait pu etre. Au moment ou les trades se sont fermes, ils semblaient repartir a la baisse."},
        {"type": "h3", "text": "La 'Fed' et la volatilite..."},
        {"type": "p", "text": "Ca a aussi coincide avec les nouvelles de la Fed sur les taux. Quand la Reserve Federale americaine (connue comme 'la Fed') publie des nouvelles sur ses plans pour les taux d'interet, tout devient fou."},
        {"type": "p", "text": "La volatilite explose a chaque nouvelle de la Fed, donc Olivier a sagement ferme tous les trades avant que cette nouvelle ne sorte. Garder des trades ouverts pendant la conference de presse de la Fed peut etre un gros pari etant donne la volatilite qui s'ensuit souvent. Donc je pense que c'etait un choix sage de la part de M. Danvel !"},
        {"type": "p", "text": "Ca a fait peur a beaucoup de gens, et il y avait des discussions pour savoir s'il avait ferme tous les trades juste pour que ses stats restent vertes pour le mois. Mais je pense que c'etait un choix tres sage. Il s'est retrouve du mauvais cote dans certains trades, et a reussi a bien controler ses pertes et pertes potentielles."},
        {"type": "p", "text": "Donc, Olivier a baisse dans mon portefeuille par rapport au mois dernier, mais il est toujours rentable et il a de nouveau des trades ouverts, donc on verra comment ca se passe ce mois-ci. Je copie toujours Olivier avec environ 24% de mon portefeuille global."},
        {"type": "p", "text": "Donc, Olivier, Harshsmith, et Berrau representent environ 72% de mon portefeuille global a eux trois. Bien."},
        {"type": "h2", "text": "Kela-Leo — comment va-t-il ?"},
        {"type": "p", "text": "Il a baisse un peu plus depuis la derniere video. Il applique toujours a peu pres la meme strategie, et malheureusement semble toujours incapable d'endiguer la lente baisse et les pertes qui augmentent lentement. Je ne suis pas sur de quoi dire a son sujet. Il ne fait toujours pas de pertes enormes — il ne fait pas de choses risquees. Il semble juste etre du mauvais cote des trades de maniere constante."},
        {"type": "p", "text": "Je ne suis pas sur si c'est peut-etre juste un tres mauvais timing... Il ne fait pas de choses stupides en fait. Tout a du sens — ca ne marche juste pas vraiment. J'attends toujours pour le moment..."},
        {"type": "h2", "text": "Le nouveau trader que j'ai copie"},
        {"type": "p", "text": "Donc, j'en ai copie un nouveau — mtsnom015. Elle a 7 ans d'experience selon sa bio. Les 3 dernieres annees de statistiques sont solides et a faible risque. Ses scores de risque sur la derniere annee sont bas, et ses drawdowns sont sous ma cible de 15% pour le drawdown maximum annuel."},
        {"type": "p", "text": "C'est une autre trader forex. (Je sais que j'ai beaucoup de traders Forex, mais je limite toujours mon exposition aux actions). Je l'ai copiee avec le minimum d'environ 6% du portefeuille !"},
        {"type": "p", "text": "Je n'ai pas copie les trades ouverts — voyons comment ca se passe."},
        {"type": "h2", "text": "3 commentaires sur \"Mise a jour Copy Trading — eToro — 02/Aout/2019\""},
        {"type": "p", "text": "Salut,"},
        {"type": "p", "text": "Comment compares-tu eToro a ZuluTrade ? J'adore toutes tes videos YouTube et je base toute ma strategie eToro en m'aidant de tes videos."},
        {"type": "p", "text": "Sachant que ZuluTrade est le plus gros site de trading social Forex, j'aimerais beaucoup savoir ce que tu en penses ?"},
        {"type": "p", "text": "Le nombre de personnes a copier sur ZuluTrade est bien plus important que sur eToro et leurs rendements sont bien meilleurs que ceux des meilleurs sur eToro."},
        {"type": "p", "text": "Yugal (Australie)"},
        {"type": "p", "text": "Salut, j'ai regarde ZuluTrade, mais je l'ai trouve beaucoup moins convivial et plus difficile a comprendre. Je devais choisir une plateforme sur laquelle me concentrer au debut, et j'ai choisi eToro. Tu es sur qu'il y a plus de traders forex la-bas ? Je pense qu'eToro est actuellement le leader mondial en matiere de trading social — je peux me tromper cependant, je vais re-regarder. Merci !"},
        {"type": "p", "text": "Bonjour,"},
        {"type": "p", "text": "Merci pour votre vblog, c'est interessant. J'ai lu beaucoup de regles sur les CFD et eToro, mais je ne comprends toujours pas : si je copie un autre trader avec $100 et qu'il investit dans des CFD, est-il possible que je puisse perdre plus d'argent que $100 ?"},
        {"type": "p", "text": "Les commentaires sont fermes."},
        rw()
    ]
}

# -------------------------------------------------------
# 27. copy-trading-update-24-aug-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-24-aug-2019"] = {
    "slug": "mise-a-jour-copy-trading-24-aout-2019",
    "meta_description": "Mise a jour copy trading — 24 aout 2019. Or, argent et decisions de portefeuille documentes honnetement.",
    "title": "Mise a jour Copy Trading — 24 Aout 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Aout 2019",
    "h1": "Mise a jour Copy Trading — 24 Aout 2019",
    "content_blocks": [
        {"type": "p", "text": "La mise a jour de cette semaine couvre mon portefeuille de copy trading sur eToro, avec un focus particulier sur les positions en or et argent et un bilan de la performance des personnes que je copie."},
        {"type": "img_grid", "images": [{"src": "../images/bag-of-gold.jpg", "alt": "Sac de pieces d'or representant l'or comme actif d'investissement"}, {"src": "../images/U.S-Silver-Eagle-1-ounce-coin.jpg", "alt": "Piece American Silver Eagle d'une once — investissement en argent"}]},
        {"type": "h2", "text": "Or et Argent"},
        {"type": "p", "text": "L'or a bien performe recemment, ce qui a eu un effet positif sur le portefeuille. Certaines des personnes que je copie ont des positions significatives dans les metaux precieux, et c'etait interessant de voir comment elles ont evolue. L'argent a aussi connu des mouvements — comme toujours, ces actifs peuvent etre volatils et bouger de facons difficiles a predire."},
        {"type": "h2", "text": "Reflexions sur l'allocation du portefeuille"},
        {"type": "p", "text": "J'ai reflechi a mon allocation globale — combien j'ai copie avec chaque personne sur eToro. L'equilibre entre ceux concentres sur les actions, ceux exposes aux matieres premieres, et ceux avec des positions crypto est quelque chose que je revois regulierement. Trouver le bon mix fait partie de ce que le copy trading exige — il faut quand meme penser a la diversification meme quand on ne fait pas les trades individuels soi-meme."},
        {"type": "img", "src": "../images/pie-chart-investments.jpg", "alt": "Diagramme circulaire illustrant l'allocation du portefeuille d'investissement entre differents actifs"},
        {"type": "h2", "text": "Ce que je surveille"},
        {"type": "p", "text": "Le contexte economique mondial a ete incertain, ce qui se reflete dans les marches. Je fais attention a comment les personnes que je copie reagissent a ca — tiennent-elles bon, ajustent-elles leurs positions, ou reagissent-elles au bruit a court terme ? Leur comportement dans les marches incertains en dit beaucoup sur leur approche."},
        {"type": "img_grid", "images": [{"src": "../images/Screenshot-2019-08-28-at-13.20.09.png", "alt": "Capture d'ecran du portefeuille de copy trading eToro — 28 aout 2019"}, {"src": "../images/Screenshot-2019-08-28-at-13.56.27.png", "alt": "Graphique de drawdown AUD/JPY sur eToro — Aout 2019"}]},
        rw()
    ]
}

# ============================================================
# WRITE FINAL FILE
# ============================================================
output_path = '/Users/thomaswest/socialtradingvlog-website/tools/translations/updates_faq_contact_fr.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Final file written to {output_path}")
print(f"Total updates: {len(data['updates'])}")
print(f"FAQ questions: {len(data['faq']['questions'])}")
print("All keys:", sorted(data['updates'].keys()))
