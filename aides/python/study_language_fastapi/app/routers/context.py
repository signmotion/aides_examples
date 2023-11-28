from pydantic.dataclasses import dataclass
from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
import textwrap

from ..internal.config import *


router = APIRouter()


class Languages(BaseModel):
    native: str = Field(
        default="",
        title="Native Language",
        description="The native language of Learner in alpha-2 ISO standard.",
    )
    target: str = Field(
        default="",
        title="Target Language",
        description="The target language of Learner in alpha-2 ISO standard.",
    )


class Context(BaseModel):
    languages: Languages = Field(
        default=Languages(),
        title="Languages",
        description="The native and target languages.",
    )
    text: str = Field(
        default="",
        title="Text",
        description="The text for processing.",
    )


_ctx: Context = Context()


test_context = {
    "languages": {"native": "en", "target": "uk"},
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
    _ctx = test_context
    print("Initialized the test context.")


@router.get("/context")
def context():
    print("ctx", _ctx)
    return _ctx


@router.get("/schema")
def schema():
    return Context.schema_json()


@router.get("/context/{hid}")
def value(hid: str):
    return _ctx[hid] if hid in _ctx else None


# the context's setters section


@router.put("/languages/native", status_code=201)
def languages_native(value: str = Body(embed=True)):
    print(f"set native language {value}")
    _ctx.languages.native = value


@router.put("/languages/target", status_code=201)
def languages_target(value: str = Body(embed=True)):
    print(f"set native language {value}")
    _ctx.languages.target = value


@router.put("/text", status_code=201)
def text(value: str = Body(embed=True)):
    print(f"set text {textwrap.shorten(value, 60)}")
    _ctx.text = value
