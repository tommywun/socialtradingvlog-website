#!/usr/bin/env python3
"""Build the complete Spanish translation JSON file."""
import json

# Load the skeleton with FAQ and Contact already translated
with open("/Users/thomaswest/socialtradingvlog-website/tools/translations/updates_faq_contact_es.json", "r") as f:
    data = json.load(f)

# Build all 27 update posts translated to Spanish
updates = {}

# ============================================================
# POST 1: social-trading-update-jun-2017
# ============================================================
updates["social-trading-update-jun-2017"] = {
    "slug": "actualizacion-copy-trading-jun-2017",
    "meta_description": "Actualizacion de copy trading — Junio 2017. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — Junio 2017 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Junio 2017",
    "h1": "Actualizacion de Copy Trading — Junio 2017",
    "content_blocks": [
        {"type": "p", "text": "21 de junio de 2017 Social Trading Vlog Bueno, esto fue en 2017, cuando todavia hacia trading manual y las criptomonedas estaban en escena. Estaba pasando por una pesadilla intentando mantener mi posicion en Ethereum... Ojala simplemente hubiera esperado 5 meses :) Las cosas se ven muy claras en retrospectiva."},
        {"type": "h3", "text": "¿Quieres ver mi perfil?"},
        {"type": "p", "text": "Ver mi perfil"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 2: copy-trading-update-28-nov-2017
# ============================================================
updates["copy-trading-update-28-nov-2017"] = {
    "slug": "actualizacion-copy-trading-28-nov-2017",
    "meta_description": "Actualizacion de copy trading — 28 Nov 2017. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 28 Nov 2017 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Noviembre 2017",
    "h1": "Actualizacion de Copy Trading — 28 Nov 2017",
    "content_blocks": [
        {"type": "h3", "text": "Echa un vistazo a mi perfil..."},
        {"type": "p", "text": "Espero que me este yendo bien :) Puedes verlo aqui. El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Mi perfil actual en eToro"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 3: copy-trading-update-jul-2018
# ============================================================
updates["copy-trading-update-jul-2018"] = {
    "slug": "actualizacion-copy-trading-jul-2018",
    "meta_description": "Actualizacion de copy trading — Julio 2018. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — Julio 2018 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Julio 2018",
    "h1": "Actualizacion de Copy Trading — Julio 2018",
    "content_blocks": [
        {"type": "p", "text": "9 de julio de 2018 Social Trading Vlog Todavia en Italia, aqui va otra breve actualizacion sobre mi copy trading en eToro. Las cosas van muy lentas y basicamente estoy esperando y esperando. He copiado a un nuevo trader y veremos como va."},
        {"type": "p", "text": "Tambien hablo sobre esta pagina web y por que he empezado a construirla. ¡Gracias por verlo!"},
        {"type": "p", "text": "Si quieres ver mi perfil o portafolio en eToro puedes hacer clic aqui. El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "h3", "text": "¿Quieres ver mi portafolio?"},
        {"type": "p", "text": "¡Espero que me este yendo bien hoy! Echa un vistazo a mi portafolio :)"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Haz clic aqui"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 4: copy-trading-update-23-aug-2018
# ============================================================
updates["copy-trading-update-23-aug-2018"] = {
    "slug": "actualizacion-copy-trading-23-ago-2018",
    "meta_description": "Actualizacion de copy trading — 23 Ago 2018. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 23 Ago 2018 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Agosto 2018",
    "h1": "Actualizacion de Copy Trading — 23 Ago 2018",
    "content_blocks": [
        {"type": "p", "text": "23 de agosto de 2018 Social Trading Vlog Aqui esta mi ultima actualizacion de copy trading sobre mis aventuras en eToro. En esta, hablo de por que he dejado de copiar a uno de los traders y tambien comento sobre los demas que sigo copiando."},
        {"type": "p", "text": "Han sido unos meses dificiles, y han estado perdiendo dinero constantemente, asi que estoy empezando a pensar en buscar nuevos traders."},
        {"type": "p", "text": "Tambien hablo de como funcionan los pagos de afiliados con eToro y como los han cambiado recientemente, aparentemente para cumplir con las nuevas regulaciones europeas ESMA."},
        {"type": "p", "text": "Es muy frustrante cuando haces copy trading y las personas que copias simplemente siguen perdiendo cada vez mas dinero lentamente. Siempre quiero aguantar y esperar a que recuperen las perdidas, pero a veces simplemente tienes que decir 'basta' y parar la copia, asumir las perdidas y buscar gente nueva."},
        {"type": "p", "text": "Grabe este video en Malta otra vez, en el piso de mi hermano. Mis disculpas por todo el sudor :) Hace mucho calor en Malta durante agosto..."},
        {"type": "h3", "text": "¿Quieres ver como me va?"},
        {"type": "p", "text": "Mis estadisticas en eToro"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 5: copy-trading-update-25-nov-2018
# ============================================================
updates["copy-trading-update-25-nov-2018"] = {
    "slug": "actualizacion-copy-trading-25-nov-2018",
    "meta_description": "Actualizacion de copy trading — 25 Nov 2018. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 25 Nov 2018 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Noviembre 2018",
    "h1": "Actualizacion de Copy Trading — 25 Nov 2018",
    "content_blocks": [
        {"type": "p", "text": "El 'Copy Stop Loss' es una forma de establecer automaticamente cuanto dinero estas dispuesto a perder con cada trader que copias, para que el sistema pueda detener automaticamente la copia si alguna vez se alcanza esa cantidad."},
        {"type": "p", "text": "Tambien hablo de los otros traders en mi portafolio, de como he bajado mis expectativas de ganancias despues de los dias locos de las criptos en 2017, y de por que a veces creo que los traders que copiamos necesitan un poco mas de empatia y posiblemente espacio para pensar del que les damos..."},
        {"type": "p", "text": "Se que puede parecer que les estoy dejando escapar, pero de verdad, ¿te imaginas el tiempo y la energia que les debe costar a estos chicos y chicas responder a todos los comentarios y preguntas que reciben?"},
        {"type": "p", "text": "Podria explicar por que, despues de convertirse en 'PI' (Popular Investor - las personas que podemos copiar en eToro), muchos traders de repente registran una caida en su rendimiento y grandes cambios en su estilo de trading. Quizas simplemente necesitamos dejarlos tranquilos para que sigan haciendo lo que estaban haciendo :) No estoy seguro..."},
        {"type": "p", "text": "Parte de ser PI en eToro es que tienes que comunicarte con las personas que te copian. Hasta cierto punto, esta en las reglas. Pero aun asi, si lo que queremos son resultados, quizas eToro podria darles un boton opcional de 'Silenciar' :)"},
        {"type": "h3", "text": "¿Quieres ver como me va ahora?"},
        {"type": "p", "text": "Consulta mi perfil y estadisticas"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 6: copy-trading-update-14-dec-2018
# ============================================================
updates["copy-trading-update-14-dec-2018"] = {
    "slug": "actualizacion-copy-trading-14-dic-2018",
    "meta_description": "Actualizacion de copy trading — 14 Dic 2018. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 14 Dic 2018 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Diciembre 2018",
    "h1": "Actualizacion de Copy Trading — 14 Dic 2018",
    "content_blocks": [
        {"type": "p", "text": "Repaso las paginas de estadisticas de cada uno y muestro un poco del historial de operaciones de cada uno para hacerme una idea de su metodologia y rendimiento. Todas las copias son nuevas, asi que es pronto con cada uno de ellos, y estoy observando como les va."},
        {"type": "p", "text": "Durante 2018, fui mucho mas pasivo ya que no queria cerrar mis copias y fijar las perdidas de todas esas criptomonedas que estuvieron perdiendo dinero todo el ano. Pero finalmente, esas copias se cerraron, y ahora estoy mucho mas activo de nuevo, buscando los mejores traders para copiar en mi nuevo portafolio."},
        {"type": "h3", "text": "¿Quieres ver como me va ahora?"},
        {"type": "p", "text": "Mis estadisticas y portafolio actual"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 7: copy-trading-update-11-jan-2019
# ============================================================
updates["copy-trading-update-11-jan-2019"] = {
    "slug": "actualizacion-copy-trading-11-ene-2019",
    "meta_description": "Actualizacion de copy trading — 11 Ene 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 11 Ene 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Enero 2019",
    "h1": "Actualizacion de Copy Trading — 11 Ene 2019",
    "content_blocks": [
        {"type": "p", "text": "Aqui esta mi perfil en eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Todo trading implica riesgo. Solo arriesga capital que estes dispuesto a perder. El rendimiento pasado no es indicativo de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversion."},
        {"type": "p", "text": "Primero, deje de copiar a mi trader de criptomonedas \"SaveTheAnimals\" porque todo estaba bastante plano por ahora, y creo que el dinero se puede usar mejor en otro sitio. Aunque sigo buscando traders de criptomonedas para copiar, ya que creo que el futuro de las criptos va a seguir siendo enorme."},
        {"type": "p", "text": "Tambien hablo de \"ChineseTiger\" - un trader que copie muy recientemente y que ha estado haciendo operaciones muy arriesgadas. He dejado de copiarlo ya que perdio mas del 10% de lo que inverti con el en solo un par de dias, y su gestion de riesgo parecia practicamente inexistente. No es lo que quiero para el portafolio - mucho riesgo y grandes fluctuaciones ya no son para mi. Comento sus graficos, y como si parece haber cierta logica detras de sus operaciones perdedoras, pero simplemente no es el estilo de trading que busco - demasiado arriesgado para mi."},
        {"type": "p", "text": "Tambien hablo de como algo parece estar mal con las estadisticas. No estoy seguro de que esta pasando, pero parecen estar equivocadas en bastantes casos. eToro me dijo que les avisara si encontraba algun error, asi que les he pasado mis dudas y hasta ahora no me han respondido. Mi copia de DazPanda tambien muestra estadisticas poco realistas, cosa que le he preguntado a DazPanda y el tambien lo ha notado. Veremos que pasa. Todavia no entiendo del todo como calculan las estadisticas de trading - es muy dificil ver que esta pasando realmente ahi."},
        {"type": "p", "text": "Tambien he copiado al trader 'Chocowin' ya que habia vuelto a analizar sus estadisticas recientemente y he decidido darle una oportunidad..."},
        {"type": "h3", "text": "¿Quieres ver como me va?"},
        {"type": "p", "text": "Puedes ver mis estadisticas aqui :) El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Mis estadisticas..."},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 8: copy-trading-update-13-jan-2019
# ============================================================
updates["copy-trading-update-13-jan-2019"] = {
    "slug": "actualizacion-copy-trading-13-ene-2019",
    "meta_description": "Actualizacion de copy trading — 13 Ene 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 13 Ene 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Enero 2019",
    "h1": "Actualizacion de Copy Trading — 13 Ene 2019",
    "content_blocks": [
        {"type": "p", "text": "13 de enero de 2019 Social Trading Vlog He copiado a dos nuevos traders - uno especializado en Forex y el otro en una variedad de activos, pero principalmente en acciones (renta variable)."},
        {"type": "p", "text": "Aqui esta mi perfil en eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Todo trading implica riesgo. Solo arriesga capital que estes dispuesto a perder. El rendimiento pasado no es indicativo de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversion."},
        {"type": "h3", "text": "¿Por que los copie?"},
        {"type": "p", "text": "Bueno, Citadelpoint simplemente parece saber de lo que habla. Es un tipo muy cualificado con los numeros, y de hecho trabaja en la industria del trading - he leido uno de sus articulos academicos y era extremadamente inteligente. Se que no tiene mucho historial de trading en eToro, pero quiero darle una oportunidad y ver como va..."},
        {"type": "p", "text": "Chocowin si tiene un historial demostrado - de hecho habia revisado su perfil hace unos meses y no lo copie, pero despues de volver a analizar todo, he decidido copiarlo y observar su progreso. Opera principalmente con acciones, pero no se limita a ellas - tambien hay indices y materias primas en su portafolio de vez en cuando y parece entender como estan vinculados todos los activos ('correlaciones'), lo que deberia permitirle sacar provecho de diferentes condiciones del mercado, ya que si un activo no rinde bien, sabra a cual otro cambiar para generar beneficios. ¡Veremos!"},
        {"type": "p", "text": "Durante un tiempo, he estado evitando los traders de acciones porque me preocupaba la estrategia de comprar y mantener que muchos traders usaban en 2017... ¿que pasa si la caida que tanta gente predice realmente ocurre? - no quiero un portafolio lleno de traders que simplemente esperan y esperan y pierden todo mi dinero. Asi que he estado buscando a alguien que tenga exposicion a acciones, pero que tambien parezca capaz de cortar perdidas y cambiar a otras clases de activos si el contexto del mercado cambia y surge la necesidad. Espero que Chocowin sea ese tipo."},
        {"type": "h3", "text": "¿Quieres ver como me va hoy?"},
        {"type": "p", "text": "Mira mis estadisticas y rendimiento actuales aqui... El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Echa un vistazo"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 9: copy-trading-update-29-jan-2019
# ============================================================
updates["copy-trading-update-29-jan-2019"] = {
    "slug": "actualizacion-copy-trading-29-ene-2019",
    "meta_description": "Actualizacion de copy trading — 29 Ene 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 29 Ene 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Enero 2019",
    "h1": "Actualizacion de Copy Trading — 29 Ene 2019",
    "content_blocks": [
        {"type": "p", "text": "29 de enero de 2019 Social Trading Vlog Aqui va otra actualizacion sobre mis aventuras de copy trading en eToro. En esta, presento a un nuevo trader en el portafolio - Olivier Danvel."},
        {"type": "p", "text": "Aqui esta mi perfil en eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Es un trader de muy bajo riesgo con algunos anos de historial y sin perdidas mensuales en sus estadisticas. Nunca habia visto eso - normalmente, hay bastantes perdidas cuando miras las estadisticas de alguien a lo largo de 3 anos, pero no es el caso con Olivier."},
        {"type": "p", "text": "Aparentemente habia mantenido su perfil privado hasta hace poco (le pregunte por que nunca lo habia visto en la plataforma antes) y ahora que es visible, creo que los copiadores empezaran a llegar. Opera principalmente en forex, y dedica mucho mas tiempo del que he visto nunca esperando los puntos de entrada correctos en las operaciones - es cauteloso y paciente - dos cualidades muy admirables en un trader para mi a estas alturas."},
        {"type": "p", "text": "Cada vez mas, me estoy decantando por elegir traders mas seguros y de menor riesgo para intentar mantener las cosas lo mas estables posible. Eso significa esperar menores beneficios, pero siendo honesto, buscar grandes ganancias nunca me ha dado buenos resultados..."},
        {"type": "p", "text": "Todo trading implica riesgo. Solo arriesga capital que estes dispuesto a perder. El rendimiento pasado no es indicativo de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversion."},
        {"type": "h3", "text": "¿Quieres ver mis estadisticas?"},
        {"type": "p", "text": "Mi perfil"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 10: copy-trading-update-03-feb-2019
# ============================================================
updates["copy-trading-update-03-feb-2019"] = {
    "slug": "actualizacion-copy-trading-03-feb-2019",
    "meta_description": "Actualizacion de copy trading — 03 Feb 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 03 Feb 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Febrero 2019",
    "h1": "Actualizacion de Copy Trading — 03 Feb 2019",
    "content_blocks": [
        {"type": "p", "text": "3 de febrero de 2019 Social Trading Vlog ¡Mi ultima actualizacion de copy trading! Es domingo por la noche, los mercados abriran de nuevo en unas seis horas, y ya casi es hora de otra semana de trading."},
        {"type": "p", "text": "Aqui esta mi perfil en eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Todo trading implica riesgo. Solo arriesga capital que estes dispuesto a perder. El rendimiento pasado no es indicativo de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversion."},
        {"type": "h3", "text": "Entonces, ¿que ha estado pasando?"},
        {"type": "p", "text": "Ha sido un comienzo de mes un poco dificil, con 'DazPanda' - una adicion muy reciente al portafolio, haciendome perder alrededor del 1% del valor total de mi portafolio en cuestion de dias... No ha ido bien. Otro trader, Manusabrina, tambien ha tenido un rendimiento bastante malo, y empiezo a preguntarme si es hora de cerrar estas dos copias."},
        {"type": "p", "text": "Acaba de haber una gran decision y cambio de sentimiento en torno a los tipos de interes en Estados Unidos, y se que eso puede tener un gran impacto en como opera todo el mundo, asi que por el momento estoy esperando un poco para ver si estos dos traders pueden aprovechar cualquier cambio de tendencia que la nueva informacion sobre tipos de interes pueda causar..."},
        {"type": "h3", "text": "¿Como esta cambiando el portafolio?"},
        {"type": "p", "text": "Los demas en el portafolio han estado operando bien, con la mayoria de ellos teniendo puntuaciones de riesgo y volatilidad (oscilaciones arriba y abajo) mas bajas que DazPanda y Manusabrina. Estoy investigando otros traders para copiar, y en mi busqueda, he vuelto a mirar a algunos de los traders mas antiguos - los que estaban en lo mas alto y eran populares cuando empece a usar eToro en 2016. Cuando la fiebre cripto de 2017 se apodero de todo, estos traders mas estables fueron olvidados ya que todos (incluido yo) vimos los enormes beneficios generados por los traders de criptomonedas y nos subimos al carro."},
        {"type": "p", "text": "Ahora sin embargo, he vuelto a buscar especificamente a personas de bajo riesgo para copiar y Berrau es sin duda uno que tengo en el radar. Tambien he vuelto a mirar a CatyFX, a quien de hecho copie durante un breve periodo en 2017 antes de parar la copia para meter mis fondos en las criptomonedas... El otro trader que estoy mirando, y que realmente quiero copiar, es Harshsmith, que opera principalmente con acciones, pero segun dice, esta preparado para posibles caidas, y parece aplicar muy buenas reglas de gestion de riesgo a su trading y portafolio. Tambien me gustaria ver si los nuevos movimientos de tipos de interes en America pueden ser aprovechados por alguien como el..."},
        {"type": "p", "text": "Los tres tienen drawdowns muy bajos, dentro de mi limite aproximado del 15%, lo cual es genial. Harshsmith parece mi candidato mas probable, aunque copiarlo haria un poco mas dificil que la gente me copie a mi debido a la regla de tamano minimo de operacion en el copy trading. Lo explicare en otro video ya que es un poco complicado. Todavia lo estoy pensando. Como trader, creo que es una buena eleccion."},
        {"type": "h3", "text": "¿Quieres ver mi rendimiento actual?"},
        {"type": "p", "text": "Mi rendimiento"},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 11: copy-trading-update-07-feb-2019
# ============================================================
updates["copy-trading-update-07-feb-2019"] = {
    "slug": "actualizacion-copy-trading-07-feb-2019",
    "meta_description": "Actualizacion de copy trading — 07 Feb 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 07 Feb 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Febrero 2019",
    "h1": "Actualizacion de Copy Trading — 07 Feb 2019",
    "content_blocks": [
        {"type": "p", "text": "7 de febrero de 2019 Social Trading Vlog Ha sido una semana dura con uno de mis traders alcanzando su Stop Loss, y yo teniendo que cerrar manualmente a otro..."},
        {"type": "p", "text": "Aqui esta mi perfil en eToro: https://etoro.tw/2rcYYm0"},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Todo trading implica riesgo. Solo arriesga capital que estes dispuesto a perder. El rendimiento pasado no es indicativo de resultados futuros. Este contenido es solo para fines educativos y no es asesoramiento de inversion."},
        {"type": "h2", "text": "Se activo un Copy Stop Loss..."},
        {"type": "p", "text": "¡El trader 'DazPanda' ha sido eliminado de mi portafolio! De hecho, activo mi copy stop loss, que es una funcion disenada para detener automaticamente tu copia de un trader si alguna vez pierde una cantidad de dinero predefinida. Cuando vi que el Copy Stop Loss se habia activado, senti que me estaba perdiendo algo, pero en general es algo bueno, ya que esta en linea con mis ideas de gestion de riesgo."},
        {"type": "p", "text": "Otro trader, 'Manusabrina', tambien ha salido del portafolio, aunque yo pare esa copia manualmente ya que su puntuacion de riesgo tambien era demasiado alta, y realmente quiero un portafolio mas estable."},
        {"type": "h3", "text": "Lo que hice despues"},
        {"type": "p", "text": "Despues de eso copie y luego deje de copiar a 'Berrau' y 'Harshsmith' - fue un poco de panico ya que solo queria reutilizar el dinero de las copias detenidas de DazPanda y Manusabrina lo mas rapido posible. El panico nunca es bueno sin embargo, asi que simplemente reinverti los fondos en mis traders existentes y me tomare un tiempo para pensar a quien copiar a continuacion."},
        {"type": "p", "text": "Repaso los otros traders del portafolio, hablando de los problemas actuales de Aimstrader, y por que estoy esperando a ver que pasa."},
        {"type": "h3", "text": "Problemas con las estadisticas"},
        {"type": "p", "text": "He estado escuchando que la gente tiene problemas y preocupaciones con las estadisticas en eToro y ha habido mucha confusion sobre que estadisticas son correctas y por que hay ciertas contradicciones y resultados diferentes. Siendo honesto, todavia no estoy seguro de que esta pasando, pero ahora estoy comparando el grafico normal de estadisticas de trading con las operaciones cerradas en la seccion de 'historial' del portafolio. Tambien estoy intentando cruzar eso con el grafico de cada trader para obtener una imagen completa. Os contare como va."},
        {"type": "p", "text": "Tambien estoy buscando un buen trader de materias primas de bajo riesgo, asi que si conoces alguno, ¡dimelo!"},
        {"type": "h3", "text": "Ver mi rendimiento actual"},
        {"type": "p", "text": "¿Como me va hoy? Descubrelo aqui."},
        {"type": "p", "text": "El Copy Trading no constituye asesoramiento de inversion. El valor de tus inversiones puede subir o bajar. Tu capital esta en riesgo."},
        {"type": "p", "text": "Mis estadisticas..."},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 12: copy-trading-update-14-feb-2019
# ============================================================
updates["copy-trading-update-14-feb-2019"] = {
    "slug": "actualizacion-copy-trading-14-feb-2019",
    "meta_description": "Actualizacion de copy trading — 14 Feb 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 14 Feb 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Febrero 2019",
    "h1": "Actualizacion de Copy Trading — 14 Feb 2019",
    "content_blocks": [
        {"type": "h2", "text": "14 de febrero de 2019 Una semana preocupante... Esta semana ha sido un poco inquietante por culpa de uno de mis traders - 'Citadelpoint', que ha estado subiendo y bajando toda la semana..."},
        {"type": "p", "text": "Estaba vendiendo USD/SEK en una operacion usando el 100% del dinero que inverti con el, con apalancamiento. La operacion fue en la direccion equivocada y perdio mas del 3% del valor de mi portafolio total en solo 3 dias... Aterrador. Y a medida que mis estadisticas caian, la gente que me copiaba tambien huyo."},
        {"type": "h3", "text": "¿Seguire copiando a Citadelpoint?"},
        {"type": "p", "text": "Si creo que Citadelpoint es un tipo muy listo - tiene un doctorado de Cambridge donde trabajo en pronostico de volatilidad de riesgo. Pero esta semana dio miedo. Su puntuacion de riesgo salto a 8 de 10. Al final tenia razon sobre la direccion del activo, pero su forma de operar es simplemente demasiado arriesgada para mi portafolio actual."},
        {"type": "p", "text": "Asi que... actualmente estoy intentando decidir si mantenerlo en el portafolio o no. Su drawdown maximo anual ya ha superado el maximo del 15% que busco en las personas que copio... No es buena senal. Entonces, para poder seguir copiandolo (creo que tiene talento) pero estar menos expuesto a su nuevo comportamiento mas arriesgado, he reducido la proporcion del portafolio que le copia."},
        {"type": "h2", "text": "¿Como van los otros traders en mi portafolio?"},
        {"type": "p", "text": "Es una cifra muy significativa, pero no estoy muy seguro de que hacer con el todavia - lo vigilare de cerca por ahora y reducire mi exposicion a el en el portafolio."},
        {"type": "p", "text": "Tambien me han dicho que puede que no tenga que pagar comisiones debido a tener una 'cuenta islamica' aunque tendria que verificarlo."},
        {"type": "h3", "text": "Parece estar operando al reves"},
        {"type": "p", "text": "Creo que si hubiera abierto todas sus operaciones recientes al reves (por ejemplo comprando en vez de vendiendo, o vendiendo en vez de comprando) habria ganado un monton de dinero. Pero asi son las cosas - no puedo microgestionar sus operaciones, y estos tipos no parecen adaptarse a las condiciones cambiantes del mercado tan rapido, asi que supongo que seguira con su estrategia actual en el futuro previsible. Seguire observando y vere como va en las proximas semanas."},
        {"type": "h2", "text": "Mi portafolio en general"},
        {"type": "p", "text": "La mayoria de mis traders operan en Forex, esperando capitalizar los movimientos en los mercados que ocurren constantemente y potencialmente manteniendose alejados de cualquier caida importante en las acciones si llegara a ocurrir."},
        {"type": "h3", "text": "Ser Popular Investor"},
        {"type": "p", "text": "Ahora que soy Popular Investor en eToro, estoy empezando a pensar en como subir los niveles del sistema de estrellas PI. Eso significaria tener 20.000 euros en mi cuenta de trading y en ese punto, definitivamente querria estar copiando traders con un fuerte enfoque de bajo riesgo. Esa preocupacion esta influyendo realmente en todas mis decisiones sobre a quien copiar ahora. Una cosa es arriesgar 500 euros (aunque ni siquiera quiero arriesgar eso demasiado) pero arriesgar 20.000 euros es otro nivel de riesgo completamente diferente..."},
        {"type": "p", "text": "Asi que realmente estoy intentando construir un portafolio rentable y de muy bajo riesgo. Veremos como va."},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 13: copy-trading-update-20-feb-2019
# ============================================================
updates["copy-trading-update-20-feb-2019"] = {
    "slug": "actualizacion-copy-trading-20-feb-2019",
    "meta_description": "Actualizacion de copy trading — 20 Feb 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 20 Feb 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Febrero 2019",
    "h1": "Actualizacion de Copy Trading — 20 Feb 2019",
    "content_blocks": [
        {"type": "p", "text": "20 de febrero de 2019 Bienvenidos a mi ultima actualizacion de Copy Trading, donde repaso mi portafolio y veo como va todo..."},
        {"type": "h2", "text": "Aimstrader"},
        {"type": "p", "text": "Lo ha estado haciendo bastante mal la verdad, abriendo varios cortos en indices cuando deberian ser compras y abriendo compras cuando deberian ser cortos... Aparentemente en enero se habia fijado unas directrices estrictas de gestion de riesgo, pero parece estar saltandoselas. No es genial si es verdad."},
        {"type": "p", "text": "Entonces, ¿hay buenas razones para las operaciones que esta haciendo? Creo que si - esta buscando correcciones basadas en grandes movimientos de precio recientes, pero parece estar errando el timing y luego manteniendo operaciones perdedoras mas tiempo del que probablemente deberia."},
        {"type": "p", "text": "Cuando miro los graficos de los activos con los que opera, puedo aplicar un analisis tecnico basico y ver que hay fuertes lineas de soporte y resistencia alrededor de donde sus activos estan cotizando actualmente. Basicamente, creo que puedo ver por que esta haciendo lo que hace, pero no le esta yendo bien y muchos de sus copiadores estan preocupados..."},
        {"type": "p", "text": "Aunque Aimstrader me ha estado haciendo perder dinero, los otros traders de mi portafolio han estado cubriendo el hueco."},
        {"type": "h2", "text": "Citadelpoint"},
        {"type": "p", "text": "Lo ha estado haciendo mucho mejor esta semana. Se acabaron los grandes movimientos arriesgados - he reducido la cantidad que lo copio y ha estado funcionando ultimamente."},
        {"type": "p", "text": "Esta usando cantidades mas pequenas de su cuenta total y haciendo operaciones a mas corto plazo, tomando pequenos bocados del mercado. Son buenas noticias en general por ahora..."},
        {"type": "h2", "text": "Chocowin"},
        {"type": "p", "text": "Beneficiandose de la reciente subida de las acciones, a Chocowin le esta yendo bien aunque no se que haria si llegara un mercado bajista. Tendremos que esperar y ver."},
        {"type": "h2", "text": "Alnayef"},
        {"type": "p", "text": "Ha estado haciendo muchas operaciones pequenas ultimamente, lo cual es bueno de ver - a veces me pregunto si simplemente ha desaparecido... Parece desvanecerse a veces, y nadie esta muy seguro de a donde fue ni que esta pasando. Siempre parece reaparecer sin embargo y pasa por un periodo de operar mucho mas frecuentemente antes de volver a quedarse en silencio."},
        {"type": "p", "text": "Algunas de sus operaciones llevan abiertas mucho tiempo y sigue manteniendolas abiertas esperando a que se pongan en verde. Sigue siendo un problema que estoy vigilando. No quiero dejar de copiarlo por ahora ya que creo que sigue siendo de bajo riesgo y potencialmente rentable en el futuro."},
        {"type": "h2", "text": "Olivier Danvel"},
        {"type": "p", "text": "Ha estado haciendo lo que esperaba de el. Operaciones pequenas, esperando lo que el considera los mejores puntos de entrada (periodos con muy poca actividad). Lo dijo desde el principio, asi que lo esperaba."},
        {"type": "p", "text": "La primera operacion que hizo fue del 3%, que esta dentro de sus directrices de gestion de riesgo. Su objetivo declarado es alrededor del 1% de beneficio al mes, y hasta ahora parece ir en buen camino. Es una de las personas que copio con la mayor proporcion de mis fondos."},
        {"type": "h2", "text": "Analisisciclico"},
        {"type": "p", "text": "Esta en negativo este mes hasta ahora, pero sigue manteniendo su enfoque de gestion de dinero de bajo riesgo. Sus operaciones rondan el 2-3% del tamano de su cuenta como se esperaba. Me quedo con el - no hay nada que dispare alarmas por ahora, asi que le dejare seguir con sus metodos."},
        {"type": "h3", "text": "¿Trajo Olivier Danvel sus estadisticas de otra plataforma?"},
        {"type": "p", "text": "Se lo pregunte directamente ya que escuche que podria haberlo hecho y dio una respuesta algo enigmatica, pero basicamente parecio decir que no, que ha estado en eToro todo el tiempo y que de alguna manera estaba oculto. No estoy seguro, pero tengo que tomar lo que dice al pie de la letra..."},
        {"type": "h3", "text": "Aimstrader ha estado recibiendo muchas criticas por su trading..."},
        {"type": "p", "text": "Ultimamente he sentido un poco de lastima por Aimstrader. La parte 'social' de eToro a veces puede ser bastante dura, pero con rumores sin fundamento volando de que perdio 2 cuentas de trading anteriores en eToro, han sido tiempos dificiles para el... Espero que consiga darle la vuelta a todo."},
        {"type": "h3", "text": "¿Viene un mercado bajista?"},
        {"type": "p", "text": "Podria ser - hay mucha gente hablando de ello como posibilidad, y algunos incluso como probabilidad. Esa es una de las razones por las que me alejo de las acciones ahora mismo - no estoy seguro de lo rapido que reaccionarian todos si las cosas empeoran... Podria ser que Aimstrader realmente este esperando el mercado bajista y este quedandose en el lado equivocado de las operaciones un poco mas ahora debido a eso. No estoy seguro..."},
        {"type": "h3", "text": "Ser Popular Investor"},
        {"type": "p", "text": "Estoy pensando en hacer algunos videos sobre como es ser popular investor en eToro ya que me parece muy interesante, asi que quizas a otras personas les guste. Tambien me gustaria hacer algunos videos sobre ser afiliado, asi que veremos que pasa con eso."},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# ============================================================
# POST 14: copy-trading-update-01-mar-2019
# ============================================================
updates["copy-trading-update-01-mar-2019"] = {
    "slug": "actualizacion-copy-trading-01-mar-2019",
    "meta_description": "Actualizacion de copy trading — 01 Mar 2019. Documentacion honesta de mi experiencia usando la funcion de copy trading de eToro.",
    "title": "Actualizacion de Copy Trading — 01 Mar 2019 | SocialTradingVlog",
    "article_tag": "Actualizacion del portafolio · Marzo 2019",
    "h1": "Actualizacion de Copy Trading — 01 Mar 2019",
    "content_blocks": [
        {"type": "p", "text": "1 de marzo de 2019 ¿Cual de estos traders es demasiado arriesgado?"},
        {"type": "p", "text": "Mirando mi portafolio, hay unos cuantos traders claramente de mayor riesgo ahi dentro, y empiezo a preguntarme si quizas el riesgo que conllevan no vale la pena por la recompensa..."},
        {"type": "p", "text": "Pero, ¿por que seria asi? Seguramente el riesgo va con la recompensa, asi que cuanto mayores sean las recompensas que busco, mayor riesgo deberia estar dispuesto a aceptar. Eso tambien es cierto. Un trader como Citadelpoint solo esta en mi portafolio porque parece muy versado en los mercados, un tipo educado con tecnicas de analisis solidas y un historial de analisis de riesgo en la Universidad de Cambridge. Esta en el portafolio por buenas razones (creo*). Pero, ¿deberia mantenerlo?"},
        {"type": "h2", "text": "Las consideraciones del Popular Investor"},
        {"type": "p", "text": "Esto suena mas a una decision empresarial que a una decision de trading, y realmente lo es... Poco despues de convertirme en Popular Investor en eToro, me di cuenta de que potencialmente podria ganar mucho mas dinero siendo Popular Investor y teniendo muchos activos bajo gestion que con mi trading real. ¿Por que?"},
        {"type": "p", "text": "Bueno, digamos que pudiera hacer un 2% al mes (que es una tasa de retorno muy muy alta comparada con los estandares de la industria para vehiculos de inversion). ¿Cuanto dinero necesitaria tener en mi cuenta de trading para que un 2% de beneficio igualara $1000/mes?"},
        {"type": "p", "text": "2% de $10,000 = $200"},
        {"type": "p", "text": "2% de $20,000 = $400"},
        {"type": "p", "text": "2% de $40,000 = $800"},
        {"type": "p", "text": "2% de $50,000 = $1000"},
        {"type": "p", "text": "Entonces, si ganara un 2% cada mes, y esperara retirar continuamente ese 2% para vivir de el, necesitaria tener $50,000 en mi cuenta de trading. Eso es MUCHO dinero..."},
        {"type": "h2", "text": "¿De que otra forma podria ganar ese dinero con el programa PI de eToro?"},
        {"type": "p", "text": "Bueno, si puedo alcanzar el nivel de estrella roja 'Champion' en el Programa de Popular Investors de eToro, recibire $1000 al mes directamente de eToro."},
        {"type": "p", "text": "Un minimo de $5000 en mi cuenta de trading, y un minimo de 10 copiadores que, en conjunto, hayan invertido $150,000 conmigo."},
        {"type": "p", "text": "No digo que sea facil conseguir esos copiadores, con esa cantidad de activos bajo gestion... Pero probablemente es mas probable que conseguir de alguna manera $50,000 para poner en mi cuenta de trading. Asi que al instante, mi forma de pensar cambia... Y de repente me pregunto si estos traders arriesgados estan potencialmente espantando a los copiadores con sus drawdowns."},
        {"type": "p", "text": "La verdad es que probablemente deberia estar mas preocupado por esos drawdowns para mi propio portafolio y objetivos de copy trading. Pero parece que la avaricia me ciega un poco todavia, asi que me expongo a mayor riesgo buscando mayores pagos y frecuentemente me sale mal. Las esperanzas de ganar mas dinero siendo PI (avaricia realmente) estan de hecho superando y anulando la avaricia que me lleva a tomar malas decisiones de riesgo sobre a quien copiar :) Es un poco un acto de equilibrio, y no estoy seguro de donde se asentara todavia."},
        {"type": "h2", "text": "Preocupandose por las estadisticas de trading"},
        {"type": "p", "text": "De repente estoy mucho mas preocupado por mis estadisticas como resultado de todo esto. La consistencia es ahora lo que busco. En 2017, me conformaba con un drawdown del 30% un mes si creia que subiria un 60% al mes siguiente. Mis estadisticas no eran importantes de la misma manera."},
        {"type": "p", "text": "En general queria 'grandes victorias' en lugar de un crecimiento constante mas pequeno. Obviamente, ¡no queria ver un drawdown del 30% nunca! PERO, mi enfoque estaba mucho mas en las grandes victorias entonces, asi que mientras creyera que en general los traders que estaba copiando, o mis propias operaciones saldrian ganadoras, no me importaba como se veian mis estadisticas en el camino."},
        {"type": "h3", "text": "¿Estoy asumiendo muy poco riesgo? ¿O preocupandome demasiado con las estadisticas de trading?"},
        {"type": "p", "text": "¿Se puede estar demasiado enfocado en las estadisticas de trading? Algunas personas se han quejado de algunos de los PIs en eToro recientemente diciendo que estan demasiado preocupados por sus estadisticas. ¿Es posible? ¿Puedes preocuparte demasiado por tus estadisticas? Al fin y al cabo, asi es como medimos a quien deberiamos copiar. Todos estamos aqui para ganar dinero, asi que ¿por que no estariamos enormemente preocupados por como le ha ido a un trader hasta ahora..."},
        {"type": "p", "text": "Es cierto que unas estadisticas verdes, solidas y consistentes son nuestra mejor carta de presentacion y publicidad como PIs. Sin embargo, tambien podria ser cierto que si nos estamos perdiendo operaciones y no tomando ciertos riesgos, podria ser que ya no estemos operando de forma natural. Y eso podria significar que estamos alterando nuestro propio sistema de trading, lo que al final nos causara problemas."},
        {"type": "p", "text": "Eso obviamente es diferente para mi ya que solo hago copy trading. Pero incluso en mi caso, ¿estoy alterando mi sistema de eleccion de traders hasta el punto de que podria convertirse en un problema real? No estoy seguro todavia - ya vere. Pero empiezo a pensar mas como un 'gestor de fondos de copia' que otra cosa. No estoy seguro de que pensar de eso todavia. Es interesante seguro. Y emocionante :) Veremos como va."},
        {"type": "p", "text": "Se que cuando se trato de invertir el dinero de mis padres en eToro, al instante elegi la estrategia de bajo riesgo. La conservacion del capital fue mi preocupacion principal al instante. Tomaria mucho menos riesgo con su dinero que con el mio. Y de hecho, su cuenta genero mucho mas beneficio que la mia. Eso tambien me hizo pensar... ¡Quizas deberia seguir mi propio consejo!"},
        {"type": "h2", "text": "Entonces... ¿Deberian salir un par de traders del portafolio?"},
        {"type": "p", "text": "Estoy considerando seriamente sacar a un par de traders de mi portafolio - aimstrader y Citadelpoint. Ahora bien, Citadelpoint es de hecho el trader con mejor rendimiento en mi portafolio. Pero tambien es con diferencia el mas arriesgado... ¿Lo mantengo por los beneficios potenciales? ¿O me deshago de el por las posibles perdidas que tambien podria provocar si las cosas van mal?"},
        {"type": "p", "text": "Esa seria una gran solucion, pero desafortunadamente no tengo suficiente dinero adicional para anadir a mi portafolio. Necesitaria anadir mucho mas dinero del que tengo para que Citadelpoint representara alrededor del 3% de mi portafolio. Creo que con un 3% de mi portafolio, me sentiria seguro copiandolo con mis objetivos de riesgo actuales... Pero simplemente no tengo fondos suficientes para reestructurar mi portafolio de esa manera. No por ahora al menos."},
        {"type": "p", "text": "No estoy seguro de que hare... Pero me inclino hacia la idea de que dejarlo seria la decision mas sabia."},
        {"type": "risk_warning", "text": "Reminder Past performance is not an indication of future results. 51% of retail investor accounts lose money when trading CFDs with eToro. Your capital is at risk. This is not investment advice."}
    ]
}

# Write the first part - we'll add the rest in the next script
data["updates"] = updates

with open("/Users/thomaswest/socialtradingvlog-website/tools/translations/updates_faq_contact_es.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Written {len(updates)} posts so far")
