from fastapi import APIRouter
import traceback
import pycaption
import re
from pydantic import BaseModel, Field


from ..internal.config import *
from .context import context


router = APIRouter()

# srt text format - see `data/a.srt`
# pycaption JSON format - see `data/a.json`


@router.get("translate-caption-about")
def translate_caption_about():
    return "Translates the caption and subtitle to other language."


@router.get("translate-caption-tags")
def translate_caption_tags():
    return ["caption", "subtitle", "translate"]


@router.get("/translate-caption")
def translate_caption():
    srt = context()["text"]
    captions = pycaption.SRTReader().read(srt)
    # webvtt = pycaption.WebVTTWriter().write(captions)
    languages = captions.get_languages()

    r = harvestSentences(captions)

    r = {
        "r_count": len(r),
        "r": r,
        "languages": languages,
        "raw": captions,
    }

    # TBD

    return construct_answer(r)


class Sentence(BaseModel):
    # whole sentence
    text: str = Field(default="")
    # node start (key) and count of chunks this harvested sentence in the node (value)
    chunks: dict = Field(default={})


def harvestSentences(captions):
    languages = captions.get_languages()
    captions = captions.get_captions(languages[0])

    sentences = []
    sentence = Sentence()
    for caption in captions:
        start = caption.start
        for node in caption.nodes:
            prepared = prepare_line(node.content)
            if prepared:
                sentence.text += f" {prepared}"
                sentence.chunks[start] = (
                    sentence.chunks[start] + 1 if start in sentence.chunks else 1
                )
                if prepared.endswith((".", "!", "?")):
                    if sentence.text:
                        sentence.text = sentence.text.strip()
                        sentences.append(sentence)
                    sentence = Sentence()

    return sentences


def prepare_line(s: str):
    None


def prepare_line(s: str):
    s = s.strip() if s else None
    if not s:
        return None

    # "- Abby, what is this?" -> "Abby, what is this?"
    if s.startswith("-"):
        s = s.replace("-", "", 1).strip()

    # "\"Pining for fun?\"" -> "Pining for fun?"
    # "Mr. \"I can't work nights. \"" -> "Mr. \"I can't work nights. \""
    if s.startswith('"') and s.endswith('"'):
        s = s.replace('"', "").strip()

    # "<i> I missed you guys.</i>" -> "I missed you guys."
    # "<i>" -> ""
    # "</i>" -> ""
    s = re.sub(r"<[^>]+>", "", s).strip()
    if not s:
        return None

    # "$2,000." -> ""
    t = re.sub(r"[\d,.\$]", "", s).strip()
    if not t:
        return None

    t = re.sub(r"[.!\?]", "", s).strip()
    if len(t) < 4:
        return None

    return s


def construct_answer(
    result: str,
    error: Exception = None,
):
    o = {}
    o["result"] = result

    if error:
        print(f"!) {error}")
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    if include_context_in_answer:
        o["context"] = context()

    return o
