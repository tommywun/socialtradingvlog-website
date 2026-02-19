#!/usr/bin/env python3
"""Build part 2 of French translation — updates 14-27."""
import json

with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_fr_part1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def rw():
    return {"type": "risk_warning", "text": "Rappel Les performances passees ne sont pas une indication des resultats futurs. 51% des comptes d'investisseurs particuliers perdent de l'argent lorsqu'ils negocient des CFD avec eToro. Votre capital est a risque. Ceci n'est pas un conseil en investissement."}

# -------------------------------------------------------
# 14. copy-trading-update-01-mar-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-01-mar-2019"] = {
    "slug": "mise-a-jour-copy-trading-01-mars-2019",
    "meta_description": "Mise a jour copy trading — 01 mars 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 01 Mars 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Mars 2019",
    "h1": "Mise a jour Copy Trading — 01 Mars 2019",
    "content_blocks": [
        {"type": "p", "text": "1er mars 2019 Lequel de ces traders est trop risque ?"},
        {"type": "p", "text": "En regardant mon portefeuille, il y a quelques traders clairement plus risques la-dedans, et je commence a me demander si le risque qu'ils representent ne vaut pas la recompense..."},
        {"type": "p", "text": "Mais pourquoi ca ? Apres tout, le risque va de pair avec la recompense, donc plus les gains que je recherche sont eleves, plus le risque que je devrais etre pret a accepter est eleve. C'est aussi vrai. Un trader comme Citadelpoint n'est dans mon portefeuille que parce qu'il semble bien maitriser les marches, c'est un gars instruit avec de bonnes techniques d'analyse et un historique d'analyse du risque a l'Universite de Cambridge. Il est dans le portefeuille pour de bonnes raisons (je pense*). Mais devrais-je le garder ?"},
        {"type": "h2", "text": "Les considerations du Popular Investor"},
        {"type": "p", "text": "Ca ressemble plus a une decision commerciale qu'a une decision de trading, et c'est vraiment le cas... Peu apres etre devenu Popular Investor sur eToro, j'ai calcule que je pourrais potentiellement gagner beaucoup plus d'argent en etant Popular Investor avec beaucoup d'actifs sous gestion que par mon trading reel. Pourquoi ?"},
        {"type": "p", "text": "Eh bien, disons que je pourrais faire 2% par mois (ce qui est un taux de rendement tres tres eleve compare aux standards de l'industrie pour les vehicules d'investissement). De combien aurais-je besoin dans mon compte de trading pour que 2% de profit equivalent a $1000/mois ?"},
        {"type": "p", "text": "2% de $10 000 = $200"},
        {"type": "p", "text": "2% de $20 000 = $400"},
        {"type": "p", "text": "2% de $40 000 = $800"},
        {"type": "p", "text": "2% de $50 000 = $1000"},
        {"type": "p", "text": "Donc, si je faisais 2% chaque mois, et esperais retirer continuellement ces 2% pour en vivre, il me faudrait $50 000 dans mon compte de trading. C'est ENORMEMENT d'argent..."},
        {"type": "h2", "text": "Comment d'autre pourrais-je gagner cet argent avec le programme PI d'eToro ?"},
        {"type": "p", "text": "Eh bien, si j'arrive au niveau etoile rouge 'Champion' du programme Popular Investor d'eToro, je recevrai $1000 par mois directement d'eToro."},
        {"type": "p", "text": "Un minimum de $5000 dans mon compte de trading, et un minimum de 10 copieurs qui, ensemble, ont investi $150 000 avec moi."},
        {"type": "p", "text": "Maintenant je ne dis pas que c'est facile d'obtenir ces copieurs, avec ce montant d'actifs sous gestion... Mais c'est probablement plus probable que de trouver d'une facon ou d'une autre $50 000 a mettre dans mon compte de trading. Donc immediatement, ma facon de penser change... Et soudain je me demande si ces traders risques effraient potentiellement les copieurs avec leurs drawdowns."},
        {"type": "p", "text": "La verite, c'est que je devrais potentiellement etre plus inquiet de ces drawdowns pour mon propre portefeuille et mes objectifs de copy trading. Mais je semble etre encore un peu aveugle par la cupidite, donc je m'expose a plus de risque en quete de gains plus eleves et ca se retourne souvent contre moi. Les espoirs de gagner plus d'argent en tant que PI (la cupidite vraiment) l'emportent en fait sur la cupidite qui me pousse a prendre de mauvaises decisions de risque dans le choix de qui copier. C'est un peu un exercice d'equilibre, et je ne suis pas sur de la ou ca va se stabiliser."},
        {"type": "h2", "text": "S'inquieter des statistiques de trading"},
        {"type": "p", "text": "Je suis soudainement beaucoup plus soucieux de mes statistiques a cause de tout ca. La regularite est maintenant ce que je recherche. En 2017, j'acceptais un drawdown de 30% un mois si je croyais que ca remonterait de 60% le mois suivant. Mes statistiques n'etaient pas importantes de la meme facon."},
        {"type": "p", "text": "Dans l'ensemble je voulais des 'gros gains' plutot qu'une croissance plus petite mais reguliere. Evidemment, je ne voulais jamais voir un drawdown de 30% ! MAIS, mon focus etait beaucoup plus sur les gros gains a l'epoque, donc tant que je croyais que globalement les traders que je copiais, ou mes propres trades sortiraient gagnants, je ne me souciais pas de l'apparence de mes statistiques en cours de route."},
        {"type": "h3", "text": "Est-ce que je prends trop peu de risques ? Ou est-ce que je me preoccupe trop des statistiques de trading ?"},
        {"type": "p", "text": "Peut-on etre trop concentre sur ses statistiques de trading ? Certaines personnes se sont plaintes de certains PIs sur eToro recemment, disant qu'ils sont trop soucieux de leurs statistiques. Est-ce possible ? Peut-on etre trop preoccupe par ses stats ? Apres tout, c'est comme ca qu'on mesure qui on devrait copier. On est tous la pour gagner de l'argent, alors pourquoi ne serions-nous pas enormement soucieux des performances passees d'un trader..."},
        {"type": "p", "text": "C'est vrai que des statistiques vertes solides et regulieres sont notre meilleure carte de visite et publicite en tant que PIs. Il est aussi possible cependant que si on rate des trades et qu'on ne prend pas certains risques, on ne trade peut-etre plus de facon naturelle. Et ca pourrait signifier qu'on perturbe notre propre systeme de trading, ce qui finira par nous causer des problemes."},
        {"type": "p", "text": "C'est evidemment different pour moi car je fais juste du copy trading. Mais meme dans mon cas, est-ce que je modifie mon systeme de choix de traders au point ou ca pourrait devenir un vrai probleme ? Je ne suis pas encore sur — on verra. Mais je commence a penser davantage comme un 'gestionnaire de fonds de copie' qu'autre chose. Je ne sais pas encore quoi en penser. C'est interessant, c'est sur. Et excitant ! On verra comment ca se passe."},
        {"type": "p", "text": "Je sais que quand il s'est agi d'investir l'argent de mes parents sur eToro, j'ai immediatement choisi la strategie a faible risque. La conservation du capital etait ma preoccupation premiere instantanement. Je prendrais beaucoup moins de risques avec leur argent qu'avec le mien. Et en fait, leur compte a fait beaucoup plus de profit que le mien. Ca m'a aussi fait reflechir... Peut-etre que je devrais suivre mes propres conseils !"},
        {"type": "h2", "text": "Alors... Faut-il retirer quelques traders du portefeuille ?"},
        {"type": "p", "text": "J'envisage serieusement de retirer quelques traders de mon portefeuille — aimstrader et Citadelpoint. Maintenant, Citadelpoint est en fait le trader le plus performant de mon portefeuille. Mais il est aussi de loin le plus risque... Est-ce que je le garde pour les profits potentiels ? Ou est-ce que je m'en debarrasse a cause des pertes potentielles qu'il pourrait aussi engendrer si les choses tournent mal ?"},
        {"type": "p", "text": "Ce serait une bonne solution, mais malheureusement je n'ai pas assez d'argent supplementaire a ajouter a mon portefeuille. Il me faudrait ajouter beaucoup plus d'argent que ce que j'ai pour que Citadelpoint represente environ 3% de mon portefeuille. Je pense qu'a 3% de mon portefeuille, je me sentirais en securite en le copiant avec mes objectifs de risque actuels... Mais je n'ai tout simplement pas assez de fonds pour restructurer mon portefeuille de cette facon. Pas pour le moment en tout cas."},
        {"type": "p", "text": "Je ne sais pas ce que je vais faire... Mais je penche vers l'idee que le retirer serait le choix le plus sage."},
        rw()
    ]
}

# -------------------------------------------------------
# 15. copy-trading-update-13-mar-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-13-mar-2019"] = {
    "slug": "mise-a-jour-copy-trading-13-mars-2019",
    "meta_description": "Mise a jour copy trading — 13 mars 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 13 Mars 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Mars 2019",
    "h1": "Mise a jour Copy Trading — 13 Mars 2019",
    "content_blocks": [
        {"type": "h2", "text": "13 mars 2019 Les traders les plus risques gagnent toujours dans mon portefeuille... Donc les deux traders les plus risques de mon portefeuille — Citadelpoint et Aimstrader, me rapportent ENCORE le plus d'argent, meme si j'ai reduit mes copies avec eux et que je les copie maintenant avec des proportions plus faibles de mon portefeuille que les autres traders..."},
        {"type": "h2", "text": "Alnayef garde toujours des trades ouverts tres longtemps..."},
        {"type": "p", "text": "Vous vous souvenez peut-etre de comment j'ai parle du trader Alnayef dans mon portefeuille. C'est celui qui garde des trades ouverts tres longtemps et qui commence a accumuler beaucoup de frais. Eh bien, il le fait toujours."},
        {"type": "p", "text": "Je pense qu'il ouvre peut-etre des trades et attend ensuite aussi longtemps que necessaire jusqu'a ce que le trade passe au vert. Ca semble correct, mais ca cause beaucoup de frais overnight et weekend car il utilise l'effet de levier sur ses trades, donc les frais s'appliquent."},
        {"type": "p", "text": "Ca pourrait etre lie au fait qu'il a un compte 'islamique' — il n'a pas a payer les frais mais moi si. C'est encore juste une rumeur cependant, je n'ai pas encore examine ce qu'un compte 'islamique' implique reellement. J'imagine qu'eToro a trouve un autre moyen de gagner de l'argent sur les personnes ayant ces comptes dits 'islamiques', donc il y a peut-etre d'autres frais qui lui sont factures et pas a moi."},
        {"type": "p", "text": "Je ne suis pas sur... Je reste avec lui pour le moment quand meme. J'espere que quelque chose va changer, et que ces trades vont passer au vert ou qu'il commence a faire de nouveaux trades gagnants."},
        {"type": "h2", "text": "Aimstrader"},
        {"type": "h2", "text": "Que faire de l'argent que j'utilisais pour copier Aimstrader ?"},
        {"type": "p", "text": "J'allais copier un nouveau trader appele 'Harshsmith'. Je surveille ses performances depuis un moment et c'est l'un des traders qui m'interesse le plus. Mais il y a un probleme avec l'argent dont j'aurais besoin pour le copier."},
        {"type": "p", "text": "Ca a a voir avec les restrictions de 'taille minimale de trade' pour le copy trading sur eToro."},
        {"type": "h3", "text": "Quelle est la taille minimale de trade ?"},
        {"type": "p", "text": "La taille minimale de trade est le plus petit montant que vous pouvez utiliser dans un trade. En copy trading, ca fonctionne tres differemment du trading manuel normal (ou vous tradez vous-meme)."},
        {"type": "p", "text": "eToro a fixe des tailles minimales de trade standard pour toutes les differentes classes d'actifs qu'on peut trader sur leur site. Si vous allez dans leur section d'aide et tapez 'taille minimale de trade', vous verrez la liste et tous les details pour les actions, ETFs, cryptos, indices, matieres premieres etc."},
        {"type": "p", "text": "Avec le copy trading, ca fonctionne un peu differemment. Quand vous copiez quelqu'un, quand il fait un trade, vous faites un trade. Disons qu'il utilise 10% de son argent total pour un trade Apple. Vous, en tant que copieur, utiliserez 10% DE L'ARGENT QUE VOUS L'AVEZ COPIE AVEC pour le meme trade Apple."},
        {"type": "p", "text": "S'il a achete, vous avez achete, s'il a utilise l'effet de levier (ou non), vous aussi. La difference se situe dans l'argent reellement utilise pour le trade. Ca fonctionne en pourcentage."},
        {"type": "p", "text": "Quand il fait un nouveau trade, eToro essaie d'ouvrir le meme trade pour vous — c'est la beaute de copier des traders. C'est automatique. Mais si le trade essaie de s'ouvrir, et que le trade resultant dans votre compte serait inferieur a $1, alors il n'ouvrira tout simplement pas ce trade pour vous. La taille minimale de trade pour les trades copies est de $1."},
        {"type": "h3", "text": "Un exemple rapide..."},
        {"type": "p", "text": "Vous copiez le Trader A"},
        {"type": "p", "text": "Le Trader A achete des actions Apple avec 0,3% de l'argent total de son compte."},
        {"type": "p", "text": "Vous avez copie le trader A avec le montant minimum de copie de $200 (au moment de cet article)."},
        {"type": "p", "text": "eToro essaie d'ouvrir une copie exacte du trade Apple pour vous. Acheter des actions Apple, en utilisant 0,3% des $200 que vous avez copies avec le Trader A."},
        {"type": "p", "text": "0,3% de $200 = 60 cents. C'est en dessous de $1, donc le trade ne s'ouvrira pas..."},
        {"type": "h2", "text": "Est-ce le probleme pour copier les trades de Harshsmith ?"},
        {"type": "p", "text": "Oui. Il a dit precedemment que le minimum qu'il utilisera jamais pour faire un nouveau trade est 0,24% de la taille de son compte. Donc si je le copie avec seulement $200, comme vous l'avez vu dans l'exemple precedent, je ne pourrai pas copier tous ses futures trades. Tout trade en dessous de 0,5% qu'il ouvrira a l'avenir, je ne pourrai pas le copier..."},
        {"type": "p", "text": "0,5% de $200 = $1 (le minimum pour ouvrir un trade copie)"},
        {"type": "p", "text": "Donc, j'ai fait les calculs et determine que j'aurais besoin de copier Harshsmith avec $460 pour m'assurer que meme s'il fait un trade a l'avenir avec 0,24% de la taille totale de son compte, j'ouvrirai quand meme automatiquement ce trade car il sera au-dessus de $1."},
        {"type": "p", "text": "Pour l'instant, je n'ai pas les moyens de le copier avec autant, donc je ne peux pas le copier encore. C'est dommage vraiment, mais les maths sont les maths et on ne peut pas les contredire !"},
        {"type": "p", "text": "Je veux definitivement le copier a l'avenir car il maintient des scores de risque tres bas (actuellement 1 sur 10 possibles !). Il trade des actions, mais semble planifier a l'avance en cas d'arrivee d'un marche baissier. Son drawdown maximum annuel est sous ma cible de 15%, et c'est un trader tres actif et apparemment competent."},
        {"type": "h2", "text": "Et les autres traders de mon portefeuille ?"},
        {"type": "p", "text": "Ils avancent tranquillement, et en general gagnent lentement de l'argent. Mon attention est vraiment sur ce qu'il faut faire des plus risques et comment aborder le probleme du reequilibrage du portefeuille alors que je n'ai pas la possibilite d'ajouter plus d'argent a mon compte. Je ne peux juste pas le faire vraiment, donc pour l'instant, je vais devoir attendre et voir."},
        {"type": "p", "text": "Croisons les doigts pour les prochaines semaines. Mon Copy Stop Loss de 15% est toujours en place pour chacun des traders que je copie. Ca signifie que meme s'ils commencent a perdre de facon catastrophique, la copie sera simplement coupee automatiquement. Ce ne serait quand meme pas une super situation, donc j'espere qu'ils pourront rester prudents jusqu'a ce que je puisse ajouter plus de fonds..."},
        rw()
    ]
}

# -------------------------------------------------------
# 16. copy-trading-update-26-mar-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-26-mar-2019"] = {
    "slug": "mise-a-jour-copy-trading-26-mars-2019",
    "meta_description": "Mise a jour copy trading — 26 mars 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 26 Mars 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Mars 2019",
    "h1": "Mise a jour Copy Trading — 26 Mars 2019",
    "content_blocks": [
        {"type": "h2", "text": "26 mars 2019 J'ai encore change l'un de mes traders ! J'ai remplace Analisisciclico par Berrau. Donc Berrau est dedans, et Analisisciclico est sorti..."},
        {"type": "p", "text": "Ces deux traders ont a peu pres les memes scores de risque et se concentrent sur le trading forex. Des deux, je peux simplement voir plus d'historique pour Berrau, donc c'est un choix plus sur. Je pourrai copier Analisisciclico a nouveau a l'avenir quand j'aurai plus d'argent, mais pour l'instant, je pars avec Berrau."},
        {"type": "h2", "text": "Comment vont les autres traders ?"},
        {"type": "p", "text": "Citadelpoint est toujours largement en tete, me rapportant le plus d'argent. Recemment, sa gestion du risque a ete excellente ; un levier plus faible, en evitant les gros evenements d'actualite, en prenant des profits regulierement et en coupant les perdants."},
        {"type": "p", "text": "J'ai en fait retire de l'argent de ma copie avec lui chaque fois qu'il fait $10 de nouveau profit, puis j'ajoute ces profits a mes autres traders a plus faible risque. Ca semble tres contre-intuitif car c'est comme punir le meilleur performer, mais il y a une raison derriere ca... Ca fait partie de ma strategie a faible risque donc je continue pour le moment."},
        {"type": "p", "text": "L'objectif est toujours de reduire l'exposition de mon portefeuille a lui, pour que si son comportement risque tourne mal un jour, je ne sois pas trop touche. Pourvu que sa serie de victoires continue cependant ! C'est incroyable."},
        {"type": "h2", "text": "Chocowin trade aussi magnifiquement"},
        {"type": "p", "text": "Chocowin a aussi trade exceptionnellement bien, faisant des profits reguliers et tradant une gamme de classes d'actifs. Il a saisi les opportunites au fur et a mesure que le marche les presentait, ce qui est super. Je suis toujours impressionne par la facon dont certains traders semblent comprendre comment les actifs sont correles."},
        {"type": "p", "text": "Ils peuvent passer des matieres premieres aux actions, au forex, en comprenant les liens entre tout, et en utilisant leur comprehension pour generer des idees de trades rentables. C'est impressionnant, et bon a voir."},
        {"type": "h2", "text": "Olivier Danvel est-il toujours dans le vert ?"},
        {"type": "p", "text": "Oui ! Il a fait environ 1% ce mois-ci, ce qui est en gros son objectif mensuel. Olivier prend toujours son temps avec ses points d'entree — il ne se precipite pas dans les trades. Il est tout en timing et exposition limitee de ce que je peux voir jusqu'ici."},
        {"type": "p", "text": "Il utilise une petite proportion de la taille de son compte pour chaque trade, entre dans les trades progressivement, et semble avoir des objectifs de sortie definis aussi. Ce sont tous des facteurs qui l'aident a garder ses scores de risque vraiment bas."},
        {"type": "p", "text": "Il s'en sort bien, et sa regularite est toujours tres rassurante. Les marches sont volatils, le trading est risque, mais M. Danvel semble avoir trouve une methode pour naviguer a travers tout ca de facon assez stable. Excellent."},
        {"type": "h2", "text": "Alnayef est-il toujours inquietant ?"},
        {"type": "p", "text": "Oui — il garde toujours des trades tres anciens ouverts — les maintenant ouverts jusqu'a ce qu'ils passent au vert. Les frais s'accumulent et les trades ne sont pas encore rentables. Je pense qu'il a ete un peu malchanceux recemment, car beaucoup des trades qu'il a ouverts se sont retournes contre lui. Le probleme c'est qu'il garde les trades perdants ouverts, immobilisant le capital que j'ai utilise pour le copier."},
        {"type": "p", "text": "A terme, je vois ca arriver au point ou tout l'argent que j'ai investi avec lui est immobilise dans des trades perdants. Jusqu'a present, il avait des fonds supplementaires disponibles pour faire quelques petits trades rentables en parallele..."},
        {"type": "p", "text": "Le moment approche cependant ou il n'aura plus de fonds supplementaires pour trader, car tout est immobilise. Ca ne serait pas une super situation du tout, car il ne resterait pas vraiment de marge de manoeuvre. Tres frustrant... Je le copie toujours, mais il y a de plus en plus de commentaires questionnant pourquoi, vu ses performances recentes. Je vais encore attendre un peu plus longtemps..."},
        {"type": "h2", "text": "Comment va le nouveau trader Berrau ?"},
        {"type": "p", "text": "C'est une de ces situations difficiles ou vous copiez un nouveau trader juste au moment ou il commence a perdre. C'est difficile psychologiquement quand on voit des resultats rouges plutot que verts, mais ce n'est pas toujours la meilleure indication de ce qui se passe..."},
        {"type": "p", "text": "Si je regarde Alnayef par exemple, son profit pour moi etait beaucoup plus eleve, et a considerablement baisse ces dernieres semaines. Si je combine l'argent qu'il m'a perdu avec les frais qu'il m'a engendres, je pense que Berrau s'en sort en fait encore mieux qu'Alnayef. Mais quand on voit du vert, meme s'il est moins vert qu'avant, c'est toujours psychologiquement plus facile que n'importe quelle quantite de rouge."},
        {"type": "p", "text": "Ce n'est pas un super indicateur de comment tout le monde s'en sort comparativement cependant. Je reste avec Berrau, et je lui donne le temps et l'espace de montrer ce dont il est capable. C'est en fait l'un des premiers Popular Investors que j'ai vus sur eToro quand j'ai rejoint en 2016."},
        {"type": "p", "text": "A l'epoque, il etait la superstar de la plateforme, mais au milieu du grand huit / de la fusee du boom crypto de 2017, son approche a faible risque est rapidement passee de mode. 2018 a ete une autre histoire. Beaucoup d'entre nous ont vu ces gains crypto se transformer en pertes, et l'attention s'est reportee sur la stabilite et l'historique. Je suis en fait content de le copier — je cherche vraiment la regularite et la stabilite en ce moment."},
        {"type": "h2", "text": "Le portefeuille en general"},
        {"type": "p", "text": "Pour l'instant, ca va bien je pense. Mon score de risque baisse, tout comme mon drawdown maximum annuel — ca se stabilise et ca commence a remonter !"},
        {"type": "p", "text": "Je continue de deplacer mes actifs des traders les plus risques de mon portefeuille vers les gars a plus faible risque. Ca fait toujours bizarre, car les gars plus risques surperforment tous les autres, mais ca fait partie du plan donc je m'y tiens. Dans l'ensemble, j'aime bien la direction que prennent les choses en ce moment."},
        {"type": "h2", "text": "Merci a Lloyd Bazaar !"},
        {"type": "p", "text": "J'ai eu une tres bonne nouvelle cette semaine car il semble qu'un autre youtubeur appele Lloyd Bazaar, qui a une chaine appelee Financial Freedom 101, m'a mentionne sur sa chaine. Merci Lloyd !"},
        rw()
    ]
}

# -------------------------------------------------------
# 17. copy-trading-update-04-apr-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-04-apr-2019"] = {
    "slug": "mise-a-jour-copy-trading-04-avril-2019",
    "meta_description": "Mise a jour copy trading — 04 avril 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 04 Avr 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Avril 2019",
    "h1": "Mise a jour Copy Trading — 04 Avr 2019",
    "content_blocks": [
        {"type": "h2", "text": "4 avril 2019 J'ai un score de risque de 2 dans mon portefeuille ! Pour la premiere fois, mon score de risque est effectivement descendu a 2 sur 10. C'est fantastique ! Mon objectif actuel est de creer un portefeuille de copy trading stable et a faible risque, et ca marche."},
        {"type": "p", "text": "Eh bien, je copie 5 traders differents, donc ils tradent tous differemment pour commencer. Ca signifie qu'ils ne prennent probablement pas exactement les memes decisions de trading au meme moment. Ca a conduit a un portefeuille beaucoup plus diversifie. Tous mes oeufs ne sont pas dans le meme panier, donc il est peu probable qu'ils se trompent tous en meme temps..."},
        {"type": "p", "text": "En plus de ca, ils sont tous eux-memes des traders a faible risque. Donc c'est comme avoir deux couches d'accent sur le faible risque. Il y a mes traders eux-memes, qui appliquent tous une bonne gestion du risque et visent d'abord a preserver leur capital. Ils sont tous historiquement rentables, avec des bilans prouves."},
        {"type": "p", "text": "Ensuite il y a moi, mettant tous ces gars a faible risque dans mon portefeuille, ajoutant de la diversification, et appliquant un Copy Stop Loss de 15% a chacun d'eux. Dans l'ensemble, c'est un bon systeme, concu pour s'assurer que l'argent que je mets dans eToro va etre :"},
        {"type": "p", "text": "A : Aussi sur que possible (il est peu probable qu'ils entrent dans de grosses series de pertes)."},
        {"type": "p", "text": "B : Utilise de maniere rentable a l'avenir."},
        {"type": "p", "text": "Excellent ! C'est l'antidote aux montagnes russes et aux grosses fluctuations de la mentalite boom-crash du trading. Voyons ce que ca donne. Mon objectif est toujours de construire un portefeuille dans lequel je serais heureux de mettre $20 000. C'est ENORMEMENT d'argent pour moi, donc je dois m'assurer autant que possible que ce serait sur. Mes nerfs ne supporteraient pas autre chose..."},
        {"type": "h2", "text": "Comment va le portefeuille ?"},
        {"type": "h3", "text": "Citadelpoint est toujours en tete !"},
        {"type": "p", "text": "Citadelpoint continue de dominer les gains dans mon portefeuille, faisant des profits comme si c'etait le dernier jour. Il coupe les perdants tot, prend bien les profits sur les gagnants, et le fait regulierement. C'est comme une machine a argent en ce moment, avec plein de gains incrementaux."},
        {"type": "p", "text": "Son profil de risque est toujours plus eleve que ce que je vise dans mon portefeuille, et j'ai reduit le montant que je copie avec lui. J'espere cependant qu'il continuera a trader prudemment, car ce serait vraiment dommage de le perdre comme l'un de mes traders."},
        {"type": "p", "text": "Il a parle de peut-etre rejoindre le programme Popular Investor sur eToro, ce qui serait super, mais on verra si ca se concretise. Je crois qu'il travaille dans le secteur financier donc ca pourrait dependre de ce que disent ses employeurs vraiment..."},
        {"type": "p", "text": "Rejoindre le programme PI restreindrait son trading de certaines manieres — un levier plus faible autorise, des tailles de trade plus petites encouragees. Il pourrait ne pas vouloir ces choses, mais elles seraient certainement les bienvenues pour moi en tant que copieur, car ca reduirait son profil de risque significativement. On verra..."},
        {"type": "h3", "text": "Chocowin, mon trader d'actions"},
        {"type": "p", "text": "Chocowin s'en est aussi tres bien sorti recemment. Il a recemment arrete tous ses trades et ajoute beaucoup plus d'argent a son compte. C'etait a cause du programme Popular Investor — il vient de passer du niveau 'Rising Star' au niveau 'Champion'."},
        {"type": "p", "text": "Le programme Popular Investor exige d'avoir un certain montant d'argent dans votre propre compte de trading pour acceder au niveau suivant, donc Chocowin a ferme tous ses trades, ajoute l'argent requis, et a recommence a trader pour qu'on ait tous des copies propres de lui."},
        {"type": "p", "text": "J'ai essaye de reduire la part de mon portefeuille qui copie Chocowin aussi, a cause de son profil de risque plus eleve. Jusqu'ici, j'ai pris $30 de profit qu'il m'a genere, et je les ai ajoutes a mes traders a plus faible risque. Il s'en sort juste tres bien. Entre lui et Citadelpoint, j'ai retire $80 de leurs copies jusqu'ici et je les ai ajoutes aux autres gars. Ca peut ne pas sembler beaucoup, mais en proportion des $200 que je copie chacun d'eux avec, c'est beaucoup."},
        {"type": "h3", "text": "Comment va Alnayef ?"},
        {"type": "p", "text": "A peu pres pareil vraiment. A ce stade cependant, certains de ses trades ouverts ont commence a bouger dans la bonne direction. C'est bon signe, mais je suis toujours vraiment preoccupe par la duree pendant laquelle il garde ses trades perdants ouverts. C'est bien d'etre patient, mais les frais continuent d'augmenter et ca commence a vraiment grignoter les profits qu'il m'a rapportes. Il a encore des trades ouverts depuis novembre dernier..."},
        {"type": "h3", "text": "Le 'nouveau' Berrau — comment trade-t-il ?"},
        {"type": "p", "text": "Il est actuellement en hausse de plus de 1%, et trade tres bien. Il y a eu des moments effrayants ou il a ouvert un trade qui s'est rapidement retourne contre lui. Il a bien gere ca cependant, ouvrant des ventes sur le meme actif pour stopper les pertes. Ca s'est bien termine au final avec les trades de vente gagnants couvrant les trades d'achat perdants et il a fini en profit. C'est bon de voir que quelqu'un sait quoi faire quand les choses tournent mal."},
        {"type": "p", "text": "On dit que meme les meilleurs traders ne choisissent les bons trades que 50% du temps. Le talent, apparemment, c'est de savoir couper les perdants vite et laisser les gagnants courir. Il semble capable de faire ca jusqu'ici, ce qui est super a voir."},
        {"type": "h3", "text": "Olivier Danvel — toujours un trading regulier et bien gere ?"},
        {"type": "p", "text": "Oui. Des trades lentement et regulierement gagnants. Il y a de longues periodes d'attente ou il attend les bons points d'entree pour de nouveaux trades, mais c'est tres bien. Ca correspond au plan... Je suis content de simplement m'asseoir et le laisser trader."},
        {"type": "h2", "text": "Quel est mon prochain mouvement pour le portefeuille ?"},
        {"type": "p", "text": "Je pourrais ajouter une nouvelle personne quand j'aurai plus d'argent pour reequilibrer davantage le portefeuille et reduire mon exposition aux gars plus risques. Je dois attendre d'avoir plus d'argent pour ca cependant. Je copierai definitivement Harshsmith, mais j'aurai besoin de $460 supplementaires pour ca, ce qui pourrait prendre un moment. Esperons pas trop longtemps !"},
        {"type": "p", "text": "Je suis en train de faire des videos ou j'interviewe les meilleurs traders sur eToro, en leur posant a tous les memes questions... J'essaie actuellement de contacter certains des grands noms du site. Si vous connaissez l'un des traders que je mentionne a la fin de la video, faites-le moi savoir, ou dites-leur que j'essaie de les contacter !"},
        rw()
    ]
}

# -------------------------------------------------------
# 18. copy-trading-update-16-apr-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-16-apr-2019"] = {
    "slug": "mise-a-jour-copy-trading-16-avril-2019",
    "meta_description": "Mise a jour copy trading — 16 avril 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 16 Avr 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Avril 2019",
    "h1": "Mise a jour Copy Trading — 16 Avr 2019",
    "content_blocks": [
        {"type": "p", "text": "16 avril 2019 Social Trading Vlog En gros, mon portefeuille a augmente regulierement et je suis a 1,45% de profit pour le mois jusqu'ici. Comme c'est agreable !"},
        {"type": "h2", "text": "Quel trader est en tete ?"},
        {"type": "p", "text": "C'est toujours Citadelpoint. Il gagne toujours, prend des profits regulierement et reste mon plus gros rapporteur. Je le copie actuellement avec environ 11% de mon portefeuille — moins que Berrau, ou Olivier Danvel, ou Alnayef. Les gens me demandent pourquoi..."},
        {"type": "h2", "text": "Pourquoi ne pas copier Citadelpoint avec plus ?"},
        {"type": "p", "text": "C'est une question de risque. Je sais qu'il est le grand gagnant en ce moment, mais je reste tres prudent quant a augmenter son montant de copie. Au contraire, je prevois encore de reduire proportionnellement ma copie de lui. Suis-je fou ? Je ne pense pas. Meme s'il a ete absolument magnifique, et j'espere vraiment que ca continue, j'ai encore des inquietudes. Ses tailles de trade peuvent etre encore beaucoup trop grosses pour mon confort. Parfois il mise tout et met tous les fonds que j'ai copies avec lui sur un seul trade. \"Bien\" direz-vous. \"Le gars gagne — laissez-le vous faire de gros gains !\""},
        {"type": "p", "text": "Je comprends ce raisonnement, vraiment. Croyez-moi, j'aimerais rien de plus que de faire des gains massifs, afficher d'enormes barres vertes dans mes stats et avoir un million de copieurs. Mais le risque est aussi tres reel. Si l'un de ces gros trades tourne vraiment mal, ca pourrait me couter enormement."},
        {"type": "p", "text": "\"La vie, c'est prendre des risques\" j'entends dire... Aussi vrai, mais ce n'est pas le type de portefeuille que j'essaie de construire. J'essaie d'en construire un ou je pourrais mettre beaucoup plus d'argent. Un portefeuille ou $20 000 seraient tellement en securite que je n'aurais pas besoin de surveiller toute la journee... Et avec cet objectif, Citadelpoint est encore une quantite un peu inconnue en tant que trader."},
        {"type": "p", "text": "J'espere vraiment qu'il continuera a gagner cependant. Ca a ete fantastique de regarder les profits croitre au quotidien ! Fan-tas-tique."},
        {"type": "h2", "text": "Comment trade Chocowin ?"},
        {"type": "p", "text": "Tres bien en effet. Il est a 11,8% de mon portefeuille car je le considere toujours comme l'un des traders a plus haut risque de mon portefeuille. Malgre ca cependant, il est mon deuxieme trader le plus rentable en ce moment. Il a fait plein de petits trades et a fourni d'excellents rendements reguliers."},
        {"type": "p", "text": "Il a aussi accepte de participer a ma prochaine video ou j'interviewe une serie de Popular Investors d'eToro ! J'ai hate..."},
        {"type": "h2", "text": "Alnayef et ses trades forex a long terme"},
        {"type": "p", "text": "Alnayef garde toujours toutes ces positions forex a long terme... Le trade AUD/USD qui perdait si mal est revenu plus pres du profit maintenant. Ca a quand meme ete une longue attente, et les frais ont augmente. J'espere que ca marque le debut d'un revirement pour Alnayef vraiment."},
        {"type": "p", "text": "Quand je regarde ses trades, ils semblent tous bouger plus ou moins de concert. Il semble avoir analyse la situation macro-economique et ouvert une serie de positions en consequence. Bien que ses positions soient variees, elles semblent toutes bouger dans une direction similaire. Ca me dit qu'il a une vision globale de la situation economique et sait quelles paires forex trader a la lumiere de ce qu'il pense qu'il va se passer ensuite."},
        {"type": "p", "text": "C'est tres intelligent de pouvoir faire ca. Dans la derniere video, j'ai mis un lien en description vers une serie de videos d'Anton Kreil. C'etait un ensemble de videos incroyable, passant en revue les fondamentaux des facteurs macro-economiques qui affectent le trading forex. Je recommande vivement de la regarder si vous etes interesse par le trading Forex. Vraiment utile."},
        {"type": "p", "text": "Les frais sur les trades d'Alnayef sont toujours vraiment eleves pour ses positions a long terme. Mais les trades a plus court terme ont en fait un ratio frais/profits tres raisonnable. J'espere qu'il pourra fermer ces trades a long terme et se mettre a du trading a plus court terme pour renverser la situation un peu. On verra."},
        {"type": "h2", "text": "Olivier Danvel — ses stats sont-elles toujours vertes ?"},
        {"type": "p", "text": "Oui ! Il a connu une periode un peu calme recemment, mais c'est toujours rentable. En ce moment, il a quelques trades de vente de petrole ouverts, mais rien d'autre. Je pense qu'il attend les bons points d'entree comme d'habitude donc je ne suis pas inquiet de son manque d'activite. Je lui fais en quelque sorte confiance pour prendre les bonnes decisions a ce stade. Tres bien !"},
        {"type": "h2", "text": "Berrau et les trades qui se retournent contre lui"},
        {"type": "p", "text": "Donc Berrau a actuellement une position ouverte sur AUD/USD qui est en perte assez importante. Recemment il a ete un peu plus volatil avec des gains, puis des pertes, puis des gains, puis des pertes etc. Quand des trades se sont retournes contre lui cependant, il n'a pas panique. Au lieu de ca, il a ouvert des positions sur la meme paire dans la direction opposee. Si l'une gagne, l'autre perd, mais c'est un excellent moyen de ne pas accumuler plus de pertes pendant qu'on essaie de comprendre ce que fait le marche."},
        {"type": "p", "text": "C'est un peu comme appuyer sur un gros bouton 'pause' dans son trading. C'est une bonne idee, et jusqu'ici ca a marche pour lui."},
        {"type": "p", "text": "Plusieurs fois il a ouvert un trade, et ca s'est retourne contre lui. A chaque fois, il a systematiquement applique de bonnes strategies pour limiter sa perte potentielle avec des contre-trades. Il a en fait fini en profit a chaque fois, et c'est tres rassurant. On dit que meme les meilleurs traders n'ont raison que 50% du temps. Ce qui fait la difference, c'est comment un trader reagit quand quelque chose gagne et quand quelque chose perd. Jusqu'ici Berrau semble avoir la tete froide et des strategies qui fonctionnent."},
        {"type": "h2", "text": "Quels autres traders est-ce que j'envisage de copier ?"},
        {"type": "p", "text": "J'ai regarde Kela-Leo qui trade une gamme d'actifs incluant les matieres premieres et le forex. Le probleme c'est qu'il est au milieu d'un trade complique sur l'or en ce moment. Je prefere rester en dehors pour etre honnete. Le probleme c'est que je peux soit le copier avec les trades ouverts (auquel cas je suis dans ce trade or). Soit je peux copier seulement les nouveaux trades."},
        {"type": "p", "text": "Le probleme avec ca c'est qu'il a ouvert des trades sur l'or qui ont commence a perdre. Pour contrer ca et arreter plus de pertes, il a ouvert des contre-trades (des achats au lieu de ventes). Ca a le meme effet d'annuler les trades perdants. Mais si je ne copie que les nouveaux trades, je n'aurai que les nouveaux 'contre-trades'."},
        {"type": "p", "text": "Pour lui, les achats et ventes sur l'or font partie de sa strategie globale. Ils se compensent mutuellement et s'assurent qu'il ne perd pas d'argent. Si je ne prends qu'une partie de ses trades, je ne suis pas protege par sa strategie complete autour de l'or. Je pourrais potentiellement faire des pertes la ou lui reste neutre en termes de profit/perte."},
        {"type": "p", "text": "Ca ne me plait pas. Donc je ne peux pas copier avec ou sans trades ouverts en ce moment. J'y reflechirai plus et je verrai ou il va avec tout ca. Je prevois toujours de le copier, peut-etre juste a un meilleur moment, quand l'or aura choisi une direction un peu plus clairement."},
        {"type": "h3", "text": "Harshsmith ?"},
        {"type": "p", "text": "Oui, je prevois toujours de copier Harshsmith mais j'ai besoin de plus de fonds pour le faire. Ce montant minimum de copy trading de $1 signifie que j'ai besoin d'au moins $460 pour capter tous ses nouveaux trades. Je n'ai pas $460 encore, donc je vais devoir attendre. Pour l'instant j'ai besoin que mon argent travaille pour moi, donc je vais laisser sa chance a Kela-Leo. On verra ce qui se passe..."},
        rw()
    ]
}

# -------------------------------------------------------
# 19. copy-trading-update-23-apr-2019
# -------------------------------------------------------
data["updates"]["copy-trading-update-23-apr-2019"] = {
    "slug": "mise-a-jour-copy-trading-23-avril-2019",
    "meta_description": "Mise a jour copy trading — 23 avril 2019. Documentation honnete de mon experience avec la fonction copy trading d'eToro.",
    "title": "Mise a jour Copy Trading — 23 Avr 2019 | SocialTradingVlog",
    "article_tag": "Mise a jour du portefeuille · Avril 2019",
    "h1": "Mise a jour Copy Trading — 23 Avr 2019",
    "content_blocks": [
        {"type": "h2", "text": "23 avril 2019 Social Trading Vlog Copy trading et panique... Donc l'un de mes traders a pris des risques plus gros que ce avec quoi je suis a l'aise, et l'essentiel de cette mise a jour concerne ca vraiment..."},
        {"type": "p", "text": "C'est Citadelpoint. Eh oui — la superstar de mon portefeuille qui engrangeait les profits a tour de bras. Il a perdu environ un tiers de tous les profits qu'il m'a rapportes en un jour."},
        {"type": "h2", "text": "Alors que s'est-il passe ?"},
        {"type": "p", "text": "Ca se resume essentiellement a un trade specifique qu'il a fait. C'est un trade forex — Achat AUD/USD. Ca veut dire qu'il pense que le Dollar australien (AUD) va se renforcer face au Dollar americain (USD). Mais ca n'a pas ete le cas."},
        {"type": "img_grid", "images": [{"src": "../images/Screenshot-2019-08-28-at-22.22.52.png", "alt": "Capture d'ecran du portefeuille de copy trading eToro montrant la position problematique — Avril 2019"}, {"src": "../images/Screenshot-2019-08-28-at-22.35.30.png", "alt": "Capture d'ecran detail du trade eToro — Mise a jour avril 2019"}]},
        {"type": "p", "text": "Il a baisse, et baisse vite. Le probleme c'est qu'il n'a pas ouvert 'un trade banal'. Il a utilise presque tout l'argent qu'il avait sur son compte pour ce seul trade. Et ensuite il a fait un autre petit trade sur la meme paire forex... Donc maintenant, il utilise 100% de l'argent que j'ai investi avec lui sur ce seul trade. Et ca va contre lui rapidement."},
        {"type": "h2", "text": "Alors que faire maintenant ?"},
        {"type": "p", "text": "C'est une tres bonne question, et une a laquelle j'ai essaye de repondre. Des que j'ai vu le trade ouvert j'ai pense \"Oh oh... Peut-etre que je devrais fermer celui-la.\" Mais je ne l'ai pas fait. J'aurais voulu maintenant, mais je l'ai laisse ouvert."},
        {"type": "p", "text": "\"Non.\" J'ai pense \"Je ne veux pas juste micro-gerer son trading — je dois pouvoir lui faire confiance sinon ca ne sera pas du tout passif.\""},
        {"type": "p", "text": "Bon, c'est vrai — a quoi bon le copy trading si on doit quand meme constamment surveiller ? Mais d'un autre cote, peut-etre qu'il a simplement des objectifs differents des miens. Peut-etre que garder un faible risque ne lui importe pas vraiment. Peut-etre qu'il prefere miser gros et gagner gros..."},
        {"type": "p", "text": "Oh oh... Ensuite il a en fait poste a propos de ce trade exact sur son fil. Il savait que certains de nous copieurs pourrions paniquer alors il a expose ses raisons pour que tout le monde les voie. C'est un gars intelligent, et ses raisons semblent solides, mais il a aussi clairement dit qu'il garderait le trade pour l'instant."},
        {"type": "p", "text": "Il a souligne qu'il etait pret a perdre le meme montant encore avant de le fermer (si j'ai bien compris)."},
        {"type": "h2", "text": "Va-t-il declencher mon Copy Stop Loss ?"},
        {"type": "p", "text": "C'est mon inquietude. J'ai mis un Copy Stop Loss serre sur toutes les personnes que je copie dans mon portefeuille. En gros, mon copy stop loss dit a eToro \"S'ils perdent jamais ce montant d'argent, arretez la copie automatiquement\". J'ai fixe ce CSL a 15% pour tous mes traders. Donc, s'il chute de 15% par rapport a son plus haut historique (le profit le plus eleve qu'il m'a jamais rapporte), ca se declenchera. Si ca se declenche, la copie sera arretee automatiquement, et je ne pourrai plus le copier."},
        {"type": "h3", "text": "Pourquoi ne pourrai-je plus le copier ?"},
        {"type": "p", "text": "Citadelpoint ne fait pas partie du \"Programme Popular Investor\" sur eToro. C'est quand les gens sont approuves par eToro... Ils suivent les regles d'eToro, et sont eligibles pour etre copies par d'autres et gagner de l'argent grace a ca."},
        {"type": "p", "text": "Citadelpoint ne veut pas faire partie de ce programme. Il l'a dit explicitement car son employeur actuel ne le permet pas. Si vous n'etes pas dans le programme Popular Investor, un petit nombre de personnes PEUT quand meme vous copier."},
        {"type": "p", "text": "Mais c'est un tres petit nombre — vingt ou trente environ. Et il y a BEAUCOUP de gens qui veulent actuellement le copier. Donc, si mon Copy Stop Loss se declenche, et que j'arrete de le copier, quelqu'un d'autre prendra ma place, et je ne pourrai plus revenir..."},
        {"type": "h2", "text": "Alors quel est le plan maintenant ?"},
        {"type": "p", "text": "Je sais depuis un moment que Citadelpoint est plus risque que les autres dans mon portefeuille. C'est pourquoi je le copie actuellement avec environ 11% de mon portefeuille plutot que les 24% avec lesquels Berrau ou Olivier Danvel sont copies."},
        {"type": "p", "text": "C'est quelque chose qui me preoccupe depuis un moment. Mais, cela dit, c'est aussi Citadelpoint qui fait la plus grosse part des profits pour moi. Il a trade comme un champion — comme une machine. Mais j'ai pense depuis un moment que si je veux garder un portefeuille vraiment sur, je dois reduire son allocation."},
        {"type": "p", "text": "Je pense que s'il etait a environ 5% de la taille totale de mon portefeuille, ce serait un scenario risque/recompense equitable. Il faudrait que je mette plus d'argent dans mon compte pour faire ca cependant. Et je n'ai tout simplement pas l'argent a ajouter en ce moment, donc 11% c'est a peu pres le plus bas possible..."},
        {"type": "p", "text": "Souvenez-vous — le minimum avec lequel je peux copier un trader est de $200. Donc il me faudrait ajouter assez d'argent a mon compte pour que $200 represente 5% du total. C'est plus d'argent que ce que j'ai actuellement — et ca perturbe mon profil de risque."},
        {"type": "h2", "text": "L'avenir de ce trade forex"},
        {"type": "p", "text": "J'ai fait un peu d'analyse technique, et je peux voir les niveaux de support juste en dessous de la ou il se trouve actuellement. Tant qu'il reste au-dessus, je ne paniquerai pas trop plus. Mais s'il tombe a travers ces niveaux de support (les creux precedents) alors je pourrais potentiellement faire face a des pertes beaucoup plus grandes, et possiblement au declenchement du CSL. On verra."},
        {"type": "img_grid", "images": [{"src": "../images/Screenshot-2019-08-28-at-22.49.24.png", "alt": "Capture d'ecran analyse de trade forex eToro — Avril 2019"}, {"src": "../images/Screenshot-2019-08-28-at-23.08.23.png", "alt": "Evaluation du risque du portefeuille eToro et trades ouverts — Avril 2019"}]},
        {"type": "p", "text": "Je ne veux vraiment pas le perdre du portefeuille. Mais je ne changerai pas mon Copy Stop Loss pour que ca arrive. J'ai deja fait ca — baisser mon stop loss de plus en plus sur un trade perdant. Ca n'a pas marche a l'epoque, et j'ai regrette de ne pas avoir pris les pertes plus petites plus tot."},
        {"type": "p", "text": "Donc c'est ce que je ferai maintenant — s'il declenche mon Copy Stop Loss, tant pis. Ce sera tres dommage, car je pense qu'il est tres talentueux, mais j'accepterai et j'avancerai."},
        {"type": "h2", "text": "Comment vont les autres traders ?"},
        {"type": "p", "text": "Honnetement, j'ai ete dans une telle panique a propos de la situation avec Citadelpoint que j'ai largement ignore les hauts et bas relativement mineurs des autres. Ils vont bien. Olivier Danvel a actuellement quelques trades qui vont contre lui, et il est actuellement en baisse de 0,5% pour le mois."},
        {"type": "p", "text": "Ca m'inquieterait normalement, mais la situation avec Citadelpoint rend ca assez insignifiant. Je crois qu'Olivier va se rattraper, et il reste encore une semaine en avril, donc je ne suis pas trop inquiet."},
        {"type": "p", "text": "Tous les regards sont sur ce trade AUD/USD pour l'instant — s'il chute encore, je pourrais voir ce stop loss se declencher et perdre mon meilleur joueur. On attend et on verra !"},
        rw()
    ]
}

# Write the intermediate state
with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_fr_part2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Part 2 written with {len(data['updates'])} updates so far")
