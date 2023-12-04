from fastapi import APIRouter
import json
import traceback
from fastapi.encoders import jsonable_encoder
import pycaption
import re
from pydantic import BaseModel, Field
from googletrans import Translator

import app
from ..internal.config import *


router = APIRouter()

# srt text format - see `data/a.srt`
# pycaption JSON format - see `data/a.json`


@router.get("/translate-caption")
def translate_caption(
    summary="Translates the caption and subtitle to other language.",
    description="Return the translated caption and subtitle to other language.",
    tags=["caption", "subtitle", "translate"],
):
    srt = app().memo.context()["text"]
    captions = pycaption.SRTReader().read(srt)
    # webvtt = pycaption.WebVTTWriter().write(captions)
    languages = captions.get_languages()

    sentences = harvestSentences(captions)
    # targetLanguage = context().languages.target
    targetLanguage = "de"
    for sentence in sentences:
        sentence.text[targetLanguage] = translate_text(
            list(sentence.text.values())[0],
            targetLanguage=targetLanguage,
        )
        print(sentence)

    r = {
        "sentences_count": len(sentences),
        "sentences": jsonable_encoder(sentences),
        "languages": languages,
        # "raw": captions,
    }

    with open("app/data/translated.json", "w", encoding="utf-8") as file:
        # json.dump(r, file)
        json.dump(r, file, ensure_ascii=False)

    return construct_answer(r)


class Sentence(BaseModel):
    # whole sentence (value) on the language (key)
    text: dict = Field(default={})
    # node start (key) and count of chunks this harvested sentence in the node (value)
    chunks: dict = Field(default={})


def translate_text(text: str, targetLanguage: str):
    translator = Translator()
    translated = translator.translate(text, dest=targetLanguage)

    return translated.text


def harvestSentences(captions):
    languages = captions.get_languages()
    language = languages[0]

    cl = captions.get_captions(language)
    sentences = []
    sentence = Sentence(text={language: ""})
    for caption in cl:
        start = caption.start
        for node in caption.nodes:
            prepared = prepare_line(node.content)
            if prepared:
                sentence.text[language] += f" {prepared}"
                sentence.chunks[start] = (
                    sentence.chunks[start] + 1 if start in sentence.chunks else 1
                )
                if prepared.endswith((".", "!", "?")):
                    if sentence.text[language]:
                        sentence.text[language] = sentence.text[language].strip()
                        sentences.append(sentence)
                    sentence = Sentence(text={language: ""})

    # if the recent sentence without ".", "!" or "?"
    if sentence.text[language]:
        sentence.text[language] = sentence.text[language].strip()
        sentences.append(sentence)

    return sentences


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
        o["context"] = app().memo.context()

    return o
