from fastapi import FastAPI
from fastapi.responses import FileResponse
import g4f
from pathlib import Path
from dotenv import load_dotenv
import traceback
import re


# ! See conventions in README.md.
# See the descriptions for the functions in the project `auction_ebay_fast_api`.


is_production = False
use_test_context = True
fake_response = True

include_context_in_answer = True
include_original_response_in_answer = True

# The answer will be formatted to JSON.
map_answer = True

# The answer will be improved: without duplicates.
improve_answer = True


load_dotenv(dotenv_path=Path(".env" if is_production else ".wip.env"))


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
    text = test_context["text"]
    prompt = f"""
Write out all phrasal verbs from the text below with a translation into Ukrainian.
Phrasal verbs are a type of verb in English that consist of a verb and a preposition or an adverb, or both.
Wite down only phrasal verbs.
Take into account the context for the translation.
Don't repeat verbs if they have been written down before.

TEXT:

{text}
"""

    responseResult = None
    improvedResult = None
    mappedResult = None
    error = None
    try:
        # automatic selection of provider
        response = phrasal_verbs_demo_text()["result"] if fake_response else g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            ignored=["ChatAnywhere", "ChatBase", "ChatgptX"]
        )
        print(response)

        responseResult = response

        if improve_answer:
            improvedResult = improved(responseResult)
        if map_answer:
            mappedResult = mapped(
                improvedResult if improvedResult else improved(responseResult))

    except Exception as ex:
        error = ex

    return construct_answer(
        mappedResult=mappedResult,
        improvedResult=improvedResult,
        responseResult=responseResult,
        error=error)


# 1. make out (translation: зрозуміти)\n
# 2. read out (translation: прочитати)\n
# 3. come out (translation: вийти)\n
# ...
# 37. think of (translation: думати про)\n
# ...
def improved(text: str):
    r = []

    lines = text.split("\n")
    for line in lines:
        print(f"\n{line}")

        print("Removing numbering...")
        line = re.sub(r'\d+\.\s', '', line)
        print(line)

        print("Improving a format for translation...")
        line = re.sub("translation", "", line)
        print(line)
        line = re.sub(":", "", line)
        print(line)

        sl = line.split("(")
        print(sl)
        a = sl[0].strip()
        b = sl[1]
        b = re.sub("\)", "", b).strip()
        line = f"{a} - {b}"
        print(line)

        print("Removing non-phrasal verbs...")
        sa = a.split(" ")
        if len(sa) < 2:
            print(f"REMOVE {line}")
            line = None

        if line:
            r.append(line)

    print("Removing duplicates...")
    r = list(set(r))

    return "\n".join(r)


def mapped(improvedText: str):
    r = {}

    lines = improvedText.split("\n")
    for line in lines:
        sl = line.split(" - ")
        a = sl[0]
        b = sl[1]
        r[a] = b

    return r


def construct_answer(
        mappedResult: dict,
        improvedResult: dict,
        responseResult: dict,
        error: Exception,
):
    o = {}

    if mappedResult:
        o["mapped_result"] = mappedResult

    if improvedResult:
        o["improved_result"] = improvedResult

    if include_original_response_in_answer or (not mappedResult and not improvedResult):
        o["response_result"] = responseResult

    if error:
        print(f"!) {error}")
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    if include_context_in_answer:
        o["context"] = ctx

    return o


@app.get("/phrasal-verbs-demo-text")
def phrasal_verbs_demo_text():
    return {
        "result": "1. make out (translation: зрозуміти)\n2. read out (translation: прочитати)\n3. come out (translation: вийти)\n4. use up (translation: використовувати)\n5. work out (translation: розібратися)\n6. figure out (translation: з'ясувати)\n7. go into (translation: увійти)\n8. read up on (translation: почитати про)\n9. set in (translation: встановлювати)\n10. make predictions (translation: робити передбачення)\n11. be good (translation: бути хорошим)\n12. be bad (translation: бути поганим)\n13. work well together (translation: добре співпрацювати разом)\n14. spend hours (translation: проводити години)\n15. love (translation: любити)\n16. hate (translation: ненавидіти)\n17. cause to pause (translation: заставляти задуматися)\n18. be useful (translation: бути корисним)\n19. be better than (translation: бути кращим, ніж)\n20. be worth it (translation: бути вартим того)\n21. figure things out (translation: розібратися в чомусь)\n22. have a disadvantage (translation: мати недолік)\n23. see something out (translation: побачити щось до кінця)\n24. know what something should do (translation: знати, що має робити щось)\n25. have a leg up on (translation: мати перевагу над)\n26. make accurate predictions (translation: робити точні передбачення)\n27. hinder from (translation: заважати чому-небудь)\n28. gloss over (translation: пропустити, замовчати)\n29. have a distinct advantage (translation: мати виразну перевагу)\n30. play a lot of (translation: грати багато в)\n31. help (translation: допомагати)\n32. have some familiarity with (translation: мати певну знайомість з)\n33. matter (translation: мати значення)\n34. provide meaningful value (translation: надавати практичну цінність)\n35. bring in (translation: привертати)\n36. get excited about (translation: захоплюватися)\n37. think of (translation: думати про)\n38. demand (translation: вимагати)\n39. learn (translation: вчитися)\n40. accomplish (translation: досягати)\n41. pull away from (translation: відводити увагу від)\n42. ask for (translation: просити)\n43. come up with (translation: придумувати)\n44. work on (translation: працювати над)\n45. create (translation: створювати)\n46. plot out (translation: розробляти схему)\n47. doubt (translation: сумніватися)\n48. happen next (translation: трапитися далі)\n49. find (translation: знаходити)\n50. struggle with (translation: боротися з)\n51. make decisions (translation: приймати рішення)\n52. understand (translation: розуміти)",
        "context": ctx,
    }


@app.get("/phrasal-verbs-demo-json")
def phrasal_verbs_demo_json():
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
