import json

data = {}

data["faq"] = {
    "slug": "perguntas-frequentes",
    "meta_description": "Perguntas frequentes sobre copy trading e eToro — e gratuito, quais sao as taxas, por que promovo o eToro e mais.",
    "title": "Perguntas Frequentes | SocialTradingVlog",
    "article_tag": "FAQ",
    "h1": "Perguntas Frequentes",
    "article_meta": "Esta secao cresce com o tempo a medida que novas perguntas surgem.",
    "questions": [
        {
            "question": "Por que voce promove o eToro?",
            "answer": "E a melhor plataforma de trading social que encontrei ate agora. Uso desde 2016 e e onde documento minha propria experiencia com copy trading. Tenho uma relacao de afiliado com o eToro — se voce se cadastrar pelo meu link, posso receber uma comissao sem custo extra pra voce. Essa relacao nao muda o que escrevo nem como relato minha experiencia."
        },
        {
            "question": "O copy trading e gratuito?",
            "answer": "Sim. Ha taxas associadas a operacoes em todas as corretoras — incluindo o eToro — mas copiar as operacoes de outro investidor e gratuito. Voce nao precisa pagar nenhum tipo de comissao a pessoa que esta copiando. Eles investem com o proprio dinheiro; sua conta simplesmente copia automaticamente todas as operacoes deles. A pessoa que voce copia recebe incentivos do eToro — quanto mais pessoas copiam e mais dinheiro e copiado, mais o eToro paga a eles. Eles ganham com a situacao, so que nao diretamente de voce."
        },
        {
            "question": "Quais sao as taxas no eToro?",
            "answer": "Ha algumas para ficar atento:<ul><li><strong>Taxas de spread</strong> — embutidas em cada operacao. Quando voce abre uma operacao, vai notar que ela ja comeca com um pequeno prejuizo. Isso e a taxa de spread. Conforme o ativo se move a seu favor, voce recupera e depois entra em lucro.</li><li><strong>Taxa de saque</strong> — o eToro cobra uma taxa fixa quando voce retira dinheiro da plataforma.</li><li><strong>Conversao de moeda</strong> — como tudo no eToro e em USD, se voce depositar ou sacar em outra moeda, uma taxa de cambio sera aplicada.</li><li><strong>Taxas overnight/fim de semana</strong> — se voce mantiver posicoes alavancadas durante a noite, pode haver taxas adicionais. Se estiver usando o copy trading com posicoes sem alavancagem, isso e menos preocupante.</li></ul>"
        },
        {
            "question": "Preciso ter experiencia em trading?",
            "answer": "Nao — esse e justamente o objetivo do copy trading. A ideia toda e que voce pode se beneficiar da experiencia de pessoas que sabem o que estao fazendo, sem precisar se tornar um especialista. Voce ainda precisa escolher com cuidado quem copiar e entender os riscos envolvidos, mas nao precisa saber ler graficos ou analisar mercados."
        },
        {
            "question": "Posso perder dinheiro?",
            "answer": "Sim. O copy trading nao elimina o risco — ainda e um investimento. Se a pessoa que voce esta copiando tiver prejuizos, voce tambem tera. So invista dinheiro que voce pode se dar ao luxo de perder. Leia o artigo <a href=\"copy-trading-returns.html\">Quanto Voce Pode Ganhar?</a> para uma visao realista de risco e retorno."
        },
        {
            "question": "O eToro e regulamentado?",
            "answer": "Sim. O eToro e regulamentado por diversas autoridades financeiras, incluindo a FCA (Reino Unido), CySEC (Chipre) e ASIC (Australia). Regulamentacao significa que ha supervisao e responsabilidade legal. Leia meu artigo completo <a href=\"etoro-scam.html\">O eToro e Golpe?</a> para saber mais sobre isso."
        },
        {
            "question": "Como comeco a fazer copy trading?",
            "answer": "Os passos basicos sao: abrir uma conta no eToro, verificar sua identidade, depositar fundos, navegar pela secao 'Copiar Pessoas', escolher alguem cujas estatisticas voce goste, definir o valor da copia e clicar em copiar. O <a href=\"copy-trading.html\">Guia de Copy Trading</a> cobre isso em mais detalhes."
        }
    ],
    "sidebar_h3": "Pronto para experimentar o copy trading?",
    "sidebar_p": "Aqui esta o meu link de afiliado eToro para comecar.",
    "sidebar_nav_h4": "Guias uteis"
}

data["contact"] = {
    "slug": "contacto",
    "meta_description": "Entre em contato com o Social Trading Vlog — perguntas sobre copy trading, eToro ou o site.",
    "title": "Contacto | SocialTradingVlog",
    "article_tag": "Contactar",
    "h1": "Contacto",
    "intro": "Tem alguma pergunta sobre copy trading, eToro ou algo no site? Fique a vontade para entrar em contato. Por favor, note que nao sou consultor financeiro e nao posso dar conselhos de investimento — mas fico feliz em responder perguntas sobre como a plataforma funciona ou compartilhar minha experiencia.",
    "form_labels": {
        "name": "O seu nome",
        "name_placeholder": "ex. Maria Silva",
        "email": "Endereco de e-mail",
        "email_placeholder": "voce@exemplo.com",
        "message": "Mensagem",
        "message_placeholder": "A sua pergunta ou mensagem...",
        "submit": "Enviar mensagem"
    },
    "reminder_title": "Lembrete",
    "reminder_text": "Este site e apenas para fins educativos e informativos. Nada aqui constitui aconselhamento financeiro ou de investimento. 51% das contas de investidores de varejo perdem dinheiro ao negociar CFDs com a eToro. Seu capital esta em risco."
}

with open('/Users/thomaswest/socialtradingvlog-website/tools/translations/_pt_part1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Part 1 written successfully")
print(f"FAQ questions: {len(data['faq']['questions'])}")
