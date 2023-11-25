from fastapi import FastAPI
from fastapi.responses import FileResponse
import g4f
from pathlib import Path
from dotenv import load_dotenv
import os
import traceback


# ! See conventions in README.md.
# See the descriptions for the functions in the project `auction_ebay_fast_api`.


is_production = False
use_test_context = True

include_context_in_response = True
include_original_response_in_response = True

load_dotenv(dotenv_path=Path(".env" if is_production else ".wip.env"))
EBAY_OAUTH_APP_TOKEN = os.getenv('EBAY_OAUTH_APP_TOKEN')


app = FastAPI(title="Study Language Aide")


# gpt4free
g4f.debug.logging = True
g4f.check_version = False
print(g4f.version)
print(g4f.Provider.Ails.params)


# the aide character section


@app.get("/about")
def root_about():
    return "The aide for studying language."


@app.get("/tags")
def tags():
    return ["english", "language", "learning", "study", "teach", "ukrainian"]


@app.get("/")
def root():
    return root_about()


# the abilities section


@app.get("phrasal-verbs-about")
def phrasal_verbs_about():
    return "Extracts phrasal verbs from [text] and translates these verbs."


@app.get("phrasal-verbs-tags")
def phrasal_verbs_tags():
    return ["extract", "phrasal verbs", "translate"]


@app.get("/phrasal-verbs")
def phrasal_verbs():
    result = None
    error = None
    try:
        # automatic selection of provider
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": "Tell me a story in 12 words limit."
            }],
        )
        print(response)
        result = response

    except Exception as ex:
        error = ex

    return enrich_response(result, error)


def enrich_response(result: dict, error: Exception):
    o = {}
    if result:
        o["result"] = result

    if error:
        print(f"!) {error}")
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    if include_context_in_response:
        o["context"] = ctx

    if include_original_response_in_response:
        o["original_response"] = result

    return o


@app.get("/phrasal-verbs-demo")
def phrasal_verbs_demo():
    return {
        "result": {
            "draft (cards)": "вибирати (карти)",
            "come up with": "придумати",
            "pull away": "відволікати",
        },
        "context": ctx,
    }


# the context section


ctx = {}


test_context = {
    "languages": ["en", "uk"],
    "text": """
When plans are overrated

Benjamin Keep
https://benjaminkeep.com/numot-and-drafting/?ref=avoiding-folly-newsletter

The Magic streamer Kenji "Numot the Nummy" Egashira does something unusual. He doesn't make guides to help people understand the new Magic cards. And he doesn't read guides to help understand the new cards.

Lost? Magic is a popular strategy game where players draft cards into decks and use these decks to compete with each other. Each card is a little bit different and cards interact with other cards in interesting ways.

An entire new set of cards comes out every few months. And, to prepare for the next couple of months of play, content creators create draft guides, which detail the new cards in the set and make predictions about which cards will be good, which will be bad, and which will work well together. And Magic players spend hours reading draft guides to understand these new cards.

People love these things. And Kenji hates them. Yet Kenji is one of the most experienced and best drafters around. This incongruity should cause players who want to learn the game to pause.

Can a draft guide be useful? Yes. Are some guides better than others? Yes. But the relevant question is: is reading a draft guide before the set comes out worth it?

How does Kenji learn the new set? Well... he plays it when it comes out. And, as he plays, he figures things out. Going into the set, Kenji has a disadvantage. He hasn't seen the cards and doesn't have time to read them all as he plays. And he doesn't know what the main deck-building strategies will be.

Players who have previewed the cards and read draft guides, by contrast, know what the cards should do. It seems like they would have a leg up on Kenji from the get-go. That's only true, however, if the draft guide makes accurate predictions about the format that couldn't be made without the draft guide.

But players who have previewed the cards and read draft guides also enter with a disadvantage, albeit a different kind of disadvantage. They enter with certain expectations. Some cards seem good in isolation, but don't work out well in practice. Some cards seem bad in isolation, but over-perform expectations. Prior knowledge about the set helps, but, like all prior knowledge, it can also hinder players from seeing novel interactions because their expectations get in the way.

I am glossing over a pretty important point here. Kenji has a distinct advantage that other, less experienced players do not have: he's played a LOT of Magic. Thus, there's a different kind of prior knowledge at work. Even a rank amateur player like myself knows basically what a new set will look like: there will be counter spells, burn spells, a board-wipe or two, some color-fixing, and invariably a high-cost, high power-and-toughness green creature that gains its controller life when it enters the battlefield.

Does a draft guide provide meaningful value? For very new players, I can see it helping. And for the first couple of drafts, having some familiarity with the cards is probably an advantage. But three drafts in? I doubt it matters. The actual game-play, in context, provides far more relevant and memorable information.

You could argue that draft guides aren't really there to teach people the format, despite that being the explicit rationale for their existence. Draft guides serve other social purposes. As content anchors, they bring in a lot of people to the podcast or channel. Draft guides are also just a way of getting excited about the new set.

But it's hard for me not to think of the draft guide as, fundamentally, a misdirection. People demand a product that they think will help them learn something or help them accomplish some goal. But the product itself pulls them away from the key skill.

From time to time, Youtubers ask me to help them come up with a study plan for something they're working on: a hard, standardized test or a professional certification. It's a reasonable request. But is the value of creating a study guide – especially one that is plotted out months into the future – worth it? I highly doubt it.

The whole point of learning something is that you don't know what will happen next – what you will find, what you will forget, what you will struggle with. It's far more important to make good decisions about studying in the moment. If you're three weeks into studying for a big test, what use is the study plan? The most relevant information is what you understand right now.
""",
}


if use_test_context:
    ctx = test_context
    print("Initialized the test context.")


@app.get("/context")
def context():
    print("ctx", ctx)
    return ctx


@app.get("/schema")
def schema():
    return {
        "type": "object",
        "properties": {
            "languages": {
                "type": "array",
                "about": "Languages for studying in alpha-2 ISO standard: first is non-native, second is native for learner."
            },
            "text": {
                "type": "string",
                "about": "Text for processing."
            },
        },
        "required": ["languages", "text"]
    }


@app.get("/context/{hid}")
def value(hid: str):
    return ctx[hid] if hid in ctx else None


# the context's setters section


@app.post("/languages/{first}/{second}")
def languages(first: str, second: str): ctx["languages"] = [first, second]


@app.post("/text/{v}")
def text(v: str): ctx["text"] = v
