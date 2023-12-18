from fastapi import APIRouter
from googletrans import Translator
import json
from fastapi.encoders import jsonable_encoder
import pycaption
from pydantic import BaseModel, Field
import re
import traceback
from typing import Any, Callable, Dict, Optional

from ..config import *
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task import Result, Task


async def translate_caption(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    await publish_progress(task=task, progress=0)

    srt = task.context["text"]
    captions = pycaption.SRTReader().read(srt)
    # webvtt = pycaption.WebVTTWriter().write(captions)
    languages = captions.get_languages()

    sentences = _harvest_sentences(captions)
    # targetLanguage = context().languages.target
    targetLanguage = "de"
    for sentence in sentences:
        sentence.text[targetLanguage] = _translate_text(
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

    value = _construct_answer(
        r,
        context=task.context,
    )

    await publish_progress(task=task, progress=100)

    return await publish_result(
        task=task,
        result=Result(uid_task=task.uid, value=value),
    )


class Sentence(BaseModel):
    # whole sentence (value) on the language (key)
    text: dict = Field(default={})
    # node start (key) and count of chunks this harvested sentence in the node (value)
    chunks: dict = Field(default={})


def _translate_text(text: str, targetLanguage: str):
    translator = Translator()
    translated = translator.translate(text, dest=targetLanguage)

    return translated.text


def _harvest_sentences(captions):
    languages = captions.get_languages()
    language = languages[0]

    cl = captions.get_captions(language)
    sentences = []
    sentence = Sentence(text={language: ""})
    for caption in cl:
        start = caption.start
        for node in caption.nodes:
            prepared = _prepare_line(node.content)
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


def _prepare_line(s: str):
    s = s.strip() if s else ""
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


def _construct_answer(
    result: dict,
    context: Dict[str, Any],
    error: Optional[Exception] = None,
):
    o = {}

    if result:
        o["result"] = result

    if error:
        logger.error(error)
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    if include_context_in_answer:
        o["context"] = context

    return o
