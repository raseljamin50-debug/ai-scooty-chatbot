"""
Builds data/knowledge.json  (the chatbot's internal knowledge base).

Run:   python tools/build_dataset.py

How to edit the knowledge:
  * change an answer      -> edit the "answer" text of an intent below
  * add more paraphrases  -> add more lines to that intent's "cores" list
  * add a new question    -> copy one intent block and give it a new "id"
Then run this file again. Every intent must end up with at least 50 paraphrases,
otherwise this script stops with an error.
"""
import json
from pathlib import Path

MIN_PARAPHRASES = 50

# Each core is expanded with these prefixes -> 5 x cores = paraphrases
PREFIXES = ["", "please ", "hi, ", "excuse me, ", "just curious, "]

INTENTS = [
    # ------------------------------------------------------------------ product
    {
        "id": "what_is_ai_scooty",
        "question": "What is AI Scooty?",
        "answer": (
            "AI Scooty is a solar-powered scooty sold in Bangladesh. It runs on solar power "
            "and can also be charged with electric current when the weather is bad. "
            "It was founded by Md Rasel."
        ),
        "must_include": ["solar"],
        "strong": [],
        "cores": [
            "what is ai scooty", "what is an ai scooty", "tell me about ai scooty",
            "explain ai scooty", "what does ai scooty do", "what kind of vehicle is ai scooty",
            "what exactly is this product", "give me an overview of ai scooty",
            "describe ai scooty", "what are you selling", "what is this scooty about",
            "introduce ai scooty", "what is the ai scooty product", "i want to know about ai scooty",
            "what is the idea behind ai scooty", "what is this company selling",
            "can you give details about ai scooty", "what is this scooter",
        ],
    },
    {
        "id": "founder",
        "question": "Who is the founder of AI Scooty?",
        "answer": "The founder of AI Scooty is Md Rasel.",
        "must_include": ["rasel"],
        "strong": ["found", "ceo"],
        "cores": [
            "who is the founder of ai scooty", "who founded ai scooty", "who is the founder",
            "founder name", "who started ai scooty", "who created ai scooty",
            "who invented ai scooty", "who is the owner of ai scooty", "who is the ceo of ai scooty",
            "who is behind ai scooty", "who is the person that built ai scooty",
            "who made this scooty", "name of the founder of ai scooty", "who is the creator of ai scooty",
            "tell me the founder name", "who is md rasel", "tell me about md rasel",
            "who is the man behind this scooty", "who established ai scooty",
        ],
    },
    {
        "id": "founder_origin",
        "question": "Where was the founder born and where is he originally from?",
        "answer": "The founder, Md Rasel, was born in Bangladesh. He is Bangladeshi by origin.",
        "must_include": ["bangladesh"],
        "strong": ["born", "nationality", "origin"],
        "cores": [
            "where was the founder born", "where is the founder of ai scooty from",
            "where was md rasel born", "what is the founder birthplace", "which country is the founder from",
            "what is the nationality of the founder", "is the founder bangladeshi",
            "where does the founder originally come from", "where is md rasel originally from",
            "what is the origin of the founder", "in which country was the founder born",
            "founder place of birth", "what is the founder home country", "is md rasel from bangladesh",
            "where is the founder from originally", "what is the birth country of md rasel",
            "which country does the founder belong to", "where did the founder come from",
        ],
    },
    {
        "id": "exclusive_rights",
        "question": "Who can work on AI Scooty in Bangladesh?",
        "answer": (
            "A paper about AI Scooty has been published by the founder. Under that paper, "
            "only Md Rasel can work on AI Scooty in Bangladesh."
        ),
        "must_include": ["rasel", "paper"],
        "strong": ["paper", "right", "exclusive"],
        "cores": [
            "who can work on ai scooty in bangladesh", "is there a paper published about ai scooty",
            "is ai scooty backed by a research paper", "who has the rights to ai scooty in bangladesh",
            "can anyone else work on ai scooty in bangladesh", "why only md rasel can work on ai scooty",
            "who is allowed to operate ai scooty in bangladesh", "does the founder have a published paper",
            "is there an exclusive right for ai scooty in bangladesh",
            "under whose paper does ai scooty work in bangladesh",
            "who holds the authority for ai scooty in bangladesh",
            "can other companies sell ai scooty in bangladesh", "is ai scooty based on a published paper",
            "what is the paper related to ai scooty", "is md rasel the only person allowed to work on ai scooty",
            "who has the exclusive right in bangladesh", "can another company work on ai scooty",
        ],
    },
    # ------------------------------------------------------------------ power
    {
        "id": "solar_power",
        "question": "Does AI Scooty run on solar power / without electricity?",
        "answer": (
            "Yes. AI Scooty runs on solar power, so it does not need electricity to run. "
            "If the sun is not available, it can be charged with electric current."
        ),
        "must_include": ["solar"],
        "strong": ["solar", "panel"],
        "cores": [
            "does ai scooty run on solar power", "is ai scooty solar powered",
            "can ai scooty run without electricity", "does it work without electric power",
            "how does ai scooty run", "what powers ai scooty", "what is the power source of ai scooty",
            "does ai scooty need electricity to run", "can the scooty run on solar energy",
            "how is ai scooty powered", "does it use solar panels", "will it work without grid power",
            "can i ride ai scooty without electricity", "what energy does ai scooty use",
            "is it a solar scooty", "does the scooty work with solar", "is it powered by the sun",
        ],
    },
    {
        "id": "bad_weather_charging",
        "question": "What if there is no sun or the weather is bad?",
        "answer": (
            "If the sun is not available or the weather is bad, AI Scooty can be charged "
            "with electric current and keep running."
        ),
        "must_include": ["electric"],
        "strong": ["sun", "sunlight", "cloudy", "plug", "mains"],
        "require_any": ["sun", "cloudy", "bad", "charge", "plug", "current", "electric", "solar", "backup", "mains"],
        "cores": [
            "what if there is no sun", "what happens when the weather is bad",
            "how do you charge ai scooty on a cloudy day", "can ai scooty be charged with electricity",
            "how to charge ai scooty", "what if the sun is not available",
            "does it work on cloudy days", "can i charge ai scooty from the mains",
            "how can the scooty run when there is no sunlight",
            "what is the backup when solar does not work", "can it be charged by electric current",
            "how do i charge it in bad weather", "how to charge when sunlight is low",
            "can i plug in ai scooty for charging", "is there another way to charge besides solar",
            "what if solar power is not enough", "what if the weather is cloudy",
        ],
    },
    {
        "id": "scooty_to_scooty",
        "question": "Can one AI Scooty charge another AI Scooty?",
        "answer": (
            "Yes. AI Scooty units can share charge with each other. If one scooty is well "
            "charged and another has low charge, they can distribute power between themselves."
        ),
        "must_include": ["charge"],
        "strong": ["share", "sharing", "distribute", "transfer"],
        "cores": [
            "can one ai scooty charge another", "can scooties share charge with each other",
            "can two scooties share power", "what if one scooty has low charge and another is charged",
            "can i give power from one scooty to another", "can scooties distribute power between themselves",
            "is power sharing possible between scooties", "does ai scooty support charge sharing",
            "can a charged scooty help a low charge scooty", "can scooty to scooty charging be done",
            "how does charge sharing between scooties work", "can scooties transfer power to each other",
            "can a scooty charge another scooty", "can i charge a scooty from another scooty",
            "what if my scooty has low charge and another has charge",
            "can scooties exchange power", "do scooties share electricity with each other",
        ],
    },
    {
        "id": "rain",
        "question": "Can AI Scooty run in the rain?",
        "answer": "Yes, AI Scooty can run in the rain.",
        "must_include": ["rain"],
        "strong": ["rain"],
        "require_any": ["rain"],
        "cores": [
            "can ai scooty run in the rain", "does it work in rain", "is ai scooty rain proof",
            "can i ride ai scooty when it is raining", "will it stop working in rainy weather",
            "does rain affect ai scooty", "can it move on a rainy day", "does ai scooty work during monsoon",
            "what happens if it rains", "is ai scooty usable in rainy season",
            "can it run when it is raining outside", "does the scooty work in wet weather",
            "will ai scooty work on rainy days", "can i drive it in the rain",
            "is it ok to use ai scooty in rain", "can the scooty be used when it rains",
        ],
    },
    # ------------------------------------------------------------------ price / buying
    {
        "id": "cost",
        "question": "How much does AI Scooty cost?",
        "answer": (
            "The initial cost of AI Scooty is BDT 200,000 (2 lakh taka). "
            "To buy one, an initial bank draft of BDT 120,000 is required."
        ),
        "must_include": ["200,000"],
        "strong": ["cost", "price"],
        "cores": [
            "how much does ai scooty cost", "what is the price of ai scooty", "what is the initial cost",
            "how much money is needed for ai scooty", "what is the total cost of the scooty",
            "how expensive is ai scooty", "price in bangladeshi taka", "what is the rate of ai scooty",
            "how much do i have to pay for ai scooty", "cost of ai scooty in bdt",
            "ai scooty price in bangladesh", "what will be the initial investment",
            "how many taka does ai scooty cost", "tell me the price", "is the ai scooty expensive",
            "what is the price tag", "how much is one ai scooty",
        ],
    },
    {
        "id": "how_to_buy",
        "question": "How can I buy AI Scooty? Who is eligible?",
        "answer": (
            "To buy an AI Scooty, you must make an initial bank draft of BDT 120,000. "
            "You must be located in Dhaka City and have a valid trade license for the business you run. "
            "You also need to provide the owner's NID and the other required documents."
        ),
        "must_include": ["120,000", "dhaka"],
        "strong": ["eligible", "eligibility", "process", "procedure"],
        "cores": [
            "how can i buy ai scooty", "how to purchase ai scooty", "what is the process to buy ai scooty",
            "what do i need to buy an ai scooty", "who can buy ai scooty",
            "what are the requirements to buy ai scooty", "am i eligible to buy ai scooty",
            "what are the eligibility conditions", "i want to buy ai scooty what should i do",
            "how do i get an ai scooty", "what is the buying procedure", "how to order ai scooty",
            "what are the conditions for purchasing", "what is required to purchase",
            "how can i become a buyer of ai scooty", "i want to purchase ai scooty",
            "what are the steps to buy ai scooty",
        ],
    },
    {
        "id": "bank_draft",
        "question": "How much is the bank draft?",
        "answer": (
            "To buy an AI Scooty you must first make a bank draft of BDT 120,000 "
            "(one lakh twenty thousand taka)."
        ),
        "must_include": ["120,000"],
        "strong": ["draft", "advance", "upfront", "deposit"],
        "cores": [
            "how much is the bank draft", "what is the bank draft amount",
            "how much bank draft do i need to make", "is a bank draft required",
            "do i need to submit a bank draft", "what is the initial payment to buy",
            "how much should i pay first", "what is the advance payment",
            "how much money do i pay upfront", "what is the initial bank draft amount for ai scooty",
            "how much is the down payment", "what payment is needed to start buying",
            "do i have to pay by bank draft", "what is the first payment for purchasing",
            "how much is the initial deposit", "what is the bank draft for ai scooty",
            "how much do i need to deposit to buy",
        ],
    },
    {
        "id": "dhaka_only",
        "question": "Can I buy AI Scooty outside Dhaka?",
        "answer": "The buyer must be located within Dhaka City.",
        "must_include": ["dhaka"],
        "strong": ["dhaka", "outside", "district", "city"],
        "cores": [
            "can i buy ai scooty outside dhaka", "must i be in dhaka to buy", "is ai scooty available only in dhaka",
            "do you sell in other cities", "which areas is ai scooty sold in", "where can i buy ai scooty",
            "is the buyer required to be in dhaka city", "is it available outside dhaka",
            "can someone from chittagong buy ai scooty", "what location is required for buying",
            "do i have to live in dhaka to buy", "does the business need to be inside dhaka city",
            "where is ai scooty available in bangladesh", "is ai scooty sold in other districts",
            "what is the area restriction for buyers", "does the buyer have to be from dhaka",
            "is it sold in dhaka city only",
        ],
    },
    {
        "id": "trade_license",
        "question": "Do I need a trade license?",
        "answer": (
            "Yes. You need a valid trade license for the business you will run with AI Scooty."
        ),
        "must_include": ["trade license"],
        "strong": ["license"],
        "cores": [
            "do i need a trade license", "is a trade license required to buy", "what license is needed",
            "is a business license required", "do i need a business trade license to buy ai scooty",
            "can i buy without a trade license", "what is the trade license requirement",
            "which license do i need to purchase", "must my business have a trade license",
            "is trade licence mandatory", "do i need a licence for my business",
            "what kind of trade license is required", "is a valid trade license needed for purchase",
            "trade licence needed or not", "is a trade license compulsory",
            "do you need my trade license",
        ],
    },
    {
        "id": "documents",
        "question": "What documents are required to buy?",
        "answer": (
            "To buy an AI Scooty you need to provide your business trade license, "
            "the owner's NID, and the other required documents."
        ),
        "must_include": ["nid", "trade license"],
        "strong": ["document", "nid", "identification"],
        "cores": [
            "what documents are required to buy ai scooty", "what papers do i need", "is nid required",
            "do i need national id card", "what documents do i have to submit", "do i need the owner nid",
            "which documents are needed for purchase", "what paperwork is required",
            "list of required documents", "what other documents are needed", "do you need my nid",
            "what identification is required", "what do i have to bring to buy",
            "do i need to provide nid and trade license", "what are the document requirements",
            "whose nid is required", "what documents does the owner need",
        ],
    },
    # ------------------------------------------------------------------ support / bot
    {
        "id": "customer_support",
        "question": "How can I talk to customer support?",
        "answer": "To talk to our customer support team directly, please call: {support_phone}",
        "use_llm": False,
        "must_include": [],
        "strong": ["support", "contact", "agent", "human", "phone", "complain", "complaint"],
        "cores": [
            "i want to talk to customer support", "how can i contact customer service",
            "what is the customer support phone number", "give me the support number",
            "i want to speak to a human", "how do i call your team", "contact number please",
            "can i talk to an agent", "customer care number", "how can i reach you",
            "i need to speak with someone", "phone number of customer support",
            "how to get in touch with support", "i want to complain",
            "i have a problem and need help from your team", "can i call you",
            "i want to speak with a real person",
        ],
    },
    {
        "id": "bot_identity",
        "question": "Who are you?",
        "answer": (
            "I am the AI Scooty Assistant, a chatbot that answers questions about AI Scooty."
        ),
        "use_llm": False,
        "must_include": [],
        "strong": ["bot", "robot", "yourself"],
        "cores": [
            "who are you", "what are you", "are you a bot", "are you a robot", "what is your name",
            "are you human", "who am i talking to", "are you an ai", "what should i call you",
            "introduce yourself", "tell me about yourself", "are you a real person",
            "which assistant is this", "what is this chatbot", "are you a chatbot",
            "is this a bot", "who is this",
        ],
    },
    {
        "id": "capabilities",
        "question": "What can you help me with?",
        "answer": (
            "I can answer questions about AI Scooty: what it is, who founded it, how it is "
            "powered (solar and electric charging), whether it runs in the rain, charge sharing "
            "between scooties, the price, and how to buy (bank draft, Dhaka City, trade license "
            "and documents). For anything else, you can call our customer support: {support_phone}"
        ),
        "use_llm": False,
        "must_include": [],
        "strong": [],
        "cores": [
            "what can you do", "what can you help me with", "how can you help me",
            "what questions can you answer", "what do you know", "what topics can you help with",
            "help", "how can you assist me", "what information do you have", "what can i ask you",
            "list the things you can answer", "what are you able to answer",
            "show me what you can do", "can you help me", "i need help",
            "what are your features", "what can i ask",
        ],
    },
    {
        "id": "language",
        "question": "Do you speak Bangla?",
        "answer": (
            "At the moment this assistant chats in English only. Bangla is not available yet."
        ),
        "use_llm": False,
        "must_include": [],
        "strong": ["bengali", "bangla", "language"],
        "cores": [
            "do you speak bangla", "can i chat in bangla", "is bengali supported",
            "do you support bangla language", "can you answer in bengali", "which languages do you support",
            "can you talk in bangla", "is there a bangla version", "can i ask in bengali",
            "do you understand bangla", "what language do you speak", "is the chatbot available in bangla",
            "will you support bangla in future", "english or bangla", "can i speak in bangla with you",
            "do you know bengali", "is there bangla support",
        ],
    },
]


# More natural wording people use. Add your own lines here whenever the bot misses a question.
EXTRA_CORES = {
    "what_is_ai_scooty": [
        "what is ai scooty all about", "what is this", "what do you sell", "what is your product",
        "what is ai scooty exactly", "what does this company do",
    ],
    "founder": [
        "name of the owner please", "who owns ai scooty", "who is the owner",
        "who founded this company", "who started this company", "who owns this company",
        "who is the person behind this company", "who is the founder of this company",
        "founder of this company", "who runs ai scooty",
    ],
    "founder_origin": [
        "is the founder a local person from bd", "is the founder from bd", "where does md rasel come from",
        "is md rasel bangladeshi", "is the founder a bangladeshi", "is md rasel a bangladeshi citizen",
        "is rasel from bangladesh", "where was he born", "where is he from", "where is he originally from",
        "which country is md rasel from",
    ],
    "exclusive_rights": [
        "can only rasel work on this in bangladesh", "can only md rasel work on ai scooty",
        "is there any published paper", "who is allowed to work on ai scooty in bangladesh",
        "who has the authority over ai scooty in bangladesh", "has the founder published a paper",
        "can anyone else sell ai scooty", "who has the rights in bangladesh",
    ],
    "solar_power": [
        "will it run without power supply", "can it run without a power supply", "does it run without a charger",
        "does it run on solar", "can it work without electricity", "is the scooty solar",
        "does it need electricity", "does it need petrol or electricity", "is it electric or solar",
        "does it need fuel", "does it run on petrol",
    ],
    "bad_weather_charging": [
        "can i charge it from a wall socket", "can i charge it at home", "can i charge it from a power socket", "can i charge it with a charger",
        "what if the sun is not out", "what if there is no sunshine", "what happens when it is not sunny",
        "what if the sun does not come out", "how do i charge it when the weather is bad",
        "what if it is cloudy", "what if there is no sun today", "how to charge with current",
    ],
    "scooty_to_scooty": [
        "can two scooties share power with each other", "can scooties help each other with charge",
        "can i charge one scooty from another scooty", "do scooties share charge",
    ],
    "rain": [
        "will rain damage it", "is rain a problem for ai scooty", "can rain stop the scooty",
        "does it work in the rain", "can i use it when it rains", "can i ride it in rain",
        "is it ok in the rain", "does it work when it is raining",
    ],
    "cost": [
        "is it cheap", "what is the cost of one unit", "how much money do i need", "is it affordable",
        "what is the price", "how much does it cost", "what is the cost", "how much is it",
        "how much does it cost in bangladesh", "what is the price in taka", "how much for one scooty",
    ],
    "how_to_buy": [
        "how to get ai scooty", "how do i get one", "i want to get ai scooty", "how can i own an ai scooty",
        "how do i buy one", "how do i buy it", "how can i buy one", "how do i purchase one",
        "where do i start to buy", "who is eligible to buy", "who is eligible", "how to buy",
        "how can i purchase it", "what do i need to buy it",
    ],
    "bank_draft": [
        "how much money should i put in the draft", "what is the amount of draft", "how much should the draft be",
        "what is the advance payment", "how much is the advance", "how much to pay in advance",
        "how much do i pay first", "what is the booking amount", "how much is the initial payment",
    ],
    "dhaka_only": [
        "can i buy from chittagong", "can i buy from sylhet", "can i buy from outside dhaka city",
        "do i have to be in dhaka", "is it only for dhaka", "do you sell outside dhaka",
        "can i buy if i live outside dhaka",
    ],
    "trade_license": [
        "is a license required for my shop", "do i need a license for my shop", "do i need a license for my business",
        "is trade licence needed", "do i need a trade licence", "do i need trade license to buy",
        "is a licence required", "is license needed for buying",
    ],
    "documents": [
        "which documents do i need to submit", "what documents are needed", "do i need nid",
        "is national id needed", "what do i need to submit", "what papers are needed to buy",
    ],
    "customer_support": [
        "i want to speak to someone from your company", "i want to speak to a person from your team", "how can i reach customer service",
        "give me your phone number", "what is your phone number", "your contact number",
        "how can i call you", "i want to call customer support", "support phone number",
        "i want to talk to someone", "talk to a person",
    ],
    "bot_identity": [
        "are you a machine", "are you a computer program", "are you a virtual assistant",
        "who are you", "what is your name", "are you a person", "who am i chatting with",
    ],
    "capabilities": [
        "what can you tell me", "what do you have information on", "what do you know about ai scooty",
        "what can i ask you", "what do you do", "what can you answer", "how can you help",
    ],
    "language": [
        "can i write in bengali", "can i type in bangla", "do you reply in bangla",
        "do you speak bangla", "can you speak bengali", "bangla please", "can we talk in bangla",
    ],
}

# ---------------------------------------------------------------- small talk
# These are written out explicitly (so we still get 50+ variations each).
GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hi there",
             "hello there", "hey there", "greetings", "assalamu alaikum", "salam", "namaste",
             "howdy", "hiya"]
GREETING_SUFFIX = ["", " scooty", " ai scooty", " team", " assistant", " bot"]

THANKS = ["thanks", "thank you", "thank you so much", "thanks a lot", "many thanks", "thx",
          "ok thanks", "okay thank you", "great thanks", "thanks for the help",
          "that helps thank you", "appreciate it", "awesome thanks", "cool thanks",
          "perfect thank you", "ok", "okay", "alright", "got it", "fine"]
THANKS_SUFFIX = ["", " assistant", " team"]

BYES = ["bye", "goodbye", "see you", "see you later", "take care", "good night",
        "talk to you later", "ok bye", "bye bye", "i am done", "that is all",
        "that is all for now", "have a nice day", "see you soon", "farewell"]
BYE_SUFFIX = ["", " assistant", " team", " thanks"]


def combine(a_list, b_list):
    return [(a + b).strip() for a in a_list for b in b_list]


SMALLTALK = [
    {
        "id": "greeting",
        "question": "Hello",
        "answer": "Hello! Welcome to AI Scooty. Ask me anything about AI Scooty.",
        "use_llm": False, "must_include": [], "strong": [],
        "paraphrases": combine(GREETINGS, GREETING_SUFFIX),
    },
    {
        "id": "thanks",
        "question": "Thank you",
        "answer": "You're welcome! Let me know if you have any other question about AI Scooty.",
        "use_llm": False, "must_include": [], "strong": [],
        "paraphrases": combine(THANKS, THANKS_SUFFIX),
    },
    {
        "id": "goodbye",
        "question": "Goodbye",
        "answer": "Goodbye! Thank you for your interest in AI Scooty.",
        "use_llm": False, "must_include": [], "strong": [],
        "paraphrases": combine(BYES, BYE_SUFFIX),
    },
]


def build():
    intents = []
    for item in INTENTS:
        paras = []
        for core in item["cores"] + EXTRA_CORES.get(item["id"], []):
            for prefix in PREFIXES:
                paras.append((prefix + core).strip())
        entry = {k: v for k, v in item.items() if k != "cores"}
        entry["paraphrases"] = sorted(set(paras))
        entry.setdefault("use_llm", True)
        intents.append(entry)
    for item in SMALLTALK:
        item = dict(item)
        item["paraphrases"] = sorted(set(item["paraphrases"]))
        intents.append(item)

    for entry in intents:
        n = len(entry["paraphrases"])
        if n < MIN_PARAPHRASES:
            raise SystemExit(f"Intent '{entry['id']}' has only {n} paraphrases (need {MIN_PARAPHRASES}+).")

    data = {"brand": "AI Scooty", "version": 1, "intents": intents}
    out = Path(__file__).resolve().parent.parent / "data" / "knowledge.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    for entry in intents:
        print(f"  {entry['id']:<22} {len(entry['paraphrases'])} paraphrases")


if __name__ == "__main__":
    build()
