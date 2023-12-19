from deep_translator import GoogleTranslator
from fastapi.encoders import jsonable_encoder
import json
import pycaption
import re
import traceback
from typing import Any, Callable, Dict, List, Optional

from .sentence import Sentence

from ...config import *
from ...context import Context
from ...packages.aide_server.src.aide_server.log import logger
from ...packages.aide_server.src.aide_server.task import Result, Task
from ...packages.short_json.src.short_json.short_json import short_json


async def translate_caption(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")
    logger.info(f"Running `{short_json(task)}`...")

    await publish_progress(task=task, progress=0)

    r = None
    error = None
    try:
        r = await _translate_caption(
            task,
            publish_progress=publish_progress,
        )
    except Exception as ex:
        error = ex

    value = _construct_answer(
        r,  # type: ignore[override]
        context=task.context,
        error=error,  # type: ignore[override]
    )

    await publish_progress(task=task, progress=100)

    return await publish_result(
        task=task,
        result=Result(uid_task=task.uid, value=value),
    )


async def _translate_caption(
    task: Task,
    publish_progress: Callable,
) -> Dict[str, Any]:
    context = Context.model_validate(task.context)

    captions = pycaption.SRTReader().read(context.text)

    # webvtt = pycaption.WebVTTWriter().write(captions)
    languages = captions.get_languages()

    sentences = _harvest_sentences(captions)

    targetLanguage = context.languages.target
    logger.info(f"Target language: `{targetLanguage}`")
    for i, sentence in enumerate(sentences):
        sentence.text[targetLanguage] = _translate_text(
            list(sentence.text.values())[0],
            targetLanguage=targetLanguage,
        )

        progress = round(100 * i / (len(sentences) + 1), 2)
        logger.info(f"{i} {progress}% {sentence}")
        await publish_progress(task=task, progress=progress)

    r = {
        "sentences_count": len(sentences),
        "sentences": jsonable_encoder(sentences),
        "languages": languages,
        # "raw": captions,
    }

    with open("app/data/translated.json", "w", encoding="utf-8") as file:
        # json.dump(r, file)
        json.dump(r, file, ensure_ascii=False)

    return r


def _translate_text(text: str, targetLanguage: str):
    return GoogleTranslator(target=targetLanguage).translate(text)


def _harvest_sentences(captions):
    languages = captions.get_languages()
    language = languages[0]

    cl = captions.get_captions(language)
    sentences: List[Sentence] = []
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
) -> Dict[str, Any]:
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
