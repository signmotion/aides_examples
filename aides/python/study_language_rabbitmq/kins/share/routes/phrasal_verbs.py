import openai
import re
import traceback
from typing import Any, Callable, Dict, Optional

from ..config import *
from ..context import Context
from ..packages.aide_server.src.aide_server.log import logger
from ..packages.aide_server.src.aide_server.task import Result, Task


async def phrasal_verbs(
    task: Task,
    publish_progress: Callable,
    publish_result: Callable,
):
    logger.info(f"Running `{__name__}`...")

    await publish_progress(task=task, progress=0)

    count_request_errors = 0
    ignored_providers = [
        # confidently
        # "ChatAnywhere",
        # "ChatBase",
        # "ChatgptX",
        # "GptGo",
        # maybe
        # "GptForLove",
        # "Chatgpt4Online",
    ]

    mapped_result: Optional[Dict[str, Any]] = None
    response_result: Optional[Dict[str, Any]] = None
    improved_result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    while True:
        try:
            response_result = _queryChatGpt(Context.model_validate(task.context))

            if improve_answer:
                improved_result = _improve(response_result)  # type: ignore[override]

            if map_answer:
                mapped_result = _map(
                    improved_result if improved_result else _improve(response_result)  # type: ignore[override]
                )

            break

        except Exception as ex:
            # provider_error = get_provider_from_error(ex)
            # if provider_error:
            #     ignored_providers.append(provider_error)
            #     logger.info(f"Added `{provider_error}` to ignored list.")

            count_request_errors += 1
            logger.warn(
                f"ATTEMPT {count_request_errors} {ex} :: {traceback.format_exc()}"
            )
            error = ex
            if count_request_errors >= max_count_request_errors:
                break

    value = _construct_answer(
        mapped_result=mapped_result,
        improved_result=improved_result,
        raw_result=response_result if include_raw_response_in_answer else None,
        context=task.context if include_context_in_answer else None,
        error=error,
    )

    await publish_progress(task=task, progress=100)

    return await publish_result(
        task=task,
        result=Result(uid_task=task.uid, value=value),
    )


def _queryChatGpt(context: Context) -> Dict[str, Any]:
    if fake_response:
        return _phrasal_verbs_demo_text(Context.model_validate(context))["result"]

    openai.api_key = open_api_key
    response = openai.Completion.create(  # type: ignore
        engine="text-davinci-003",
        prompt=_prompt(context.text),
        temperature=0.0,
        max_tokens=300,
    )

    logger.info(response)

    return response.choices[0].text


def _prompt(text: str):
    return f"""
Write out all phrasal verbs from the text below with a translation into Ukrainian.
Phrasal verbs are a type of verb in English that consist of a verb and a preposition or an adverb, or both.
Wite down only phrasal verbs.
Take into account the context for the translation.
Don't repeat verbs if they have been written down before.

TEXT:

{text}
"""


def _get_provider_from_error(ex: Exception):
    splitted = f"{ex}".split(":")
    r = None
    if len(splitted) > 1:
        r = splitted[1].strip()
        if len(r.split(" ")) != 0 or r == "RetryProvider":
            r = None

    return r


# 1. make out (translation: зрозуміти)\n
# 2. read out (translation: прочитати)\n
# 3. come out (translation: вийти)\n
# ...
# 37. think of (translation: думати про)\n
# ...
def _improve(text: str) -> str:
    r = []
    lines = text.split("\n")
    for line in lines:
        try:
            line = _improve_line(line)
        except Exception as ex:
            logger.info(f"{line} :: {ex} :: {traceback.format_exc()}")
            # line = f"{line} :: {ex} :: {traceback.format_exc()}"

        if line:
            r.append(line)

    logger.info("Removing duplicates...")
    unique_r = []
    for line in r:
        if line not in unique_r:
            unique_r.append(line)

    return "\n".join(unique_r)


def _improve_line(line: str):
    logger.info(f"\n{line}")

    logger.info("Removing numbering...")
    line = re.sub(r"\d+\.\s*", "", line)

    logger.info("Improving a format for translation...")
    line = re.sub("translation", "", line)
    line = re.sub(":", "", line)

    a = ""
    b = ""

    # make out (: зрозуміти)
    try:
        a, b = line.split("(")
        a = a.strip()
        b = re.sub(")", "", b).strip()
        line = f"{a} - {b}"
    except Exception as ex:
        pass

    # Make out - Розібратися
    try:
        a, b = line.split(" - ")
        a = a.strip()
        line = f"{a} - {b}"
    except Exception as ex:
        pass

    logger.info("Removing non-phrasal verbs...")
    sa = a.split(" ")
    if len(sa) < 2:
        line = ""

    return line.lower() if line else line


def _map(improvedText: str) -> Dict[str, Any]:
    r = {}

    lines = improvedText.split("\n")
    for line in lines:
        a, b = line.split(" - ")
        r[a] = b

    return r


def _construct_answer(
    mapped_result: Optional[Dict[str, Any]] = None,
    improved_result: Optional[Dict[str, Any]] = None,
    raw_result: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
) -> Dict[str, Any]:
    o = {}

    if bool(mapped_result):
        o["mapped_result"] = mapped_result

    if bool(improved_result):
        o["improved_result"] = improved_result

    if bool(raw_result) or (not bool(mapped_result) and not bool(improved_result)):
        o["raw_result"] = raw_result

    if bool(context):
        o["context"] = context

    if error:
        logger.error(error)
        o["error"] = {
            "key": f"{error}",
            "traceback": f"{traceback.format_exc()}",
        }

    return o


def _phrasal_verbs_demo_text(context: Context) -> Dict[str, Any]:
    return {
        "result":
        # "1. make out (translation: зрозуміти)\n2. read out (translation: прочитати)\n3. come out (translation: вийти)\n4. use up (translation: використовувати)\n5. work out (translation: розібратися)\n6. figure out (translation: з'ясувати)\n7. go into (translation: увійти)\n8. read up on (translation: почитати про)\n9. set in (translation: встановлювати)\n10. make predictions (translation: робити передбачення)\n11. be good (translation: бути хорошим)\n12. be bad (translation: бути поганим)\n13. work well together (translation: добре співпрацювати разом)\n14. spend hours (translation: проводити години)\n15. love (translation: любити)\n16. hate (translation: ненавидіти)\n17. cause to pause (translation: заставляти задуматися)\n18. be useful (translation: бути корисним)\n19. be better than (translation: бути кращим, ніж)\n20. be worth it (translation: бути вартим того)\n21. figure things out (translation: розібратися в чомусь)\n22. have a disadvantage (translation: мати недолік)\n23. see something out (translation: побачити щось до кінця)\n24. know what something should do (translation: знати, що має робити щось)\n25. have a leg up on (translation: мати перевагу над)\n26. make accurate predictions (translation: робити точні передбачення)\n27. hinder from (translation: заважати чому-небудь)\n28. gloss over (translation: пропустити, замовчати)\n29. have a distinct advantage (translation: мати виразну перевагу)\n30. play a lot of (translation: грати багато в)\n31. help (translation: допомагати)\n32. have some familiarity with (translation: мати певну знайомість з)\n33. matter (translation: мати значення)\n34. provide meaningful value (translation: надавати практичну цінність)\n35. bring in (translation: привертати)\n36. get excited about (translation: захоплюватися)\n37. think of (translation: думати про)\n38. demand (translation: вимагати)\n39. learn (translation: вчитися)\n40. accomplish (translation: досягати)\n41. pull away from (translation: відводити увагу від)\n42. ask for (translation: просити)\n43. come up with (translation: придумувати)\n44. work on (translation: працювати над)\n45. create (translation: створювати)\n46. plot out (translation: розробляти схему)\n47. doubt (translation: сумніватися)\n48. happen next (translation: трапитися далі)\n49. find (translation: знаходити)\n50. struggle with (translation: боротися з)\n51. make decisions (translation: приймати рішення)\n52. understand (translation: розуміти)"
        "1. Take into account - Враховувати\n2. Write down - Записати\n3. Make out - Розібратися\n4. Read out - Вголос прочитати\n5. Work out - Розібратися (про щось)\n6. Come out - Вийти (про новий набір карт)\n7. Figure out - Розібратися\n8. Read up - Почитати про щось\n9. Love these things - Обожнювати це\n10. Hate them - Ненавидіти їх\n11. Paused - Зупинитись на мить\n12. Be worth it - Бути вартим\n13. Hinder from - Заважати\n14. Gloss over - Пропустити, не зупинятись\n15. Have a leg up on - Мати перевагу над\n16. Seem good - Здаватися хорошим\n17. Work out well - Вдалий результат\n18. Over-perform expectations - Перевиконувати очікування\n19. Get in the way - Заважати, стояти на шляху\n20. Look like - Виглядати як\n21. Provide meaningful value - Надавати суттєву користь\n22. Bring in - Привертати\n23. Pull away from - Відводити увагу від\n24. Come up with - Придумати\n25. Work on - Працювати над\n26. Plot out - Складати план\n27. Doubt it - Сумніватись в цьому\n28. Make good decisions - Приймати правильні рішення\n29. Studying in the moment - Вчитися в даний момент\n30. Understand right now - Розуміти зараз",
        "context": context.model_dump_json(),
    }


def _phrasal_verbs_demo_json(context: Context) -> Dict[str, Any]:
    return {
        "result": {
            "draft (cards)": "вибирати (карти)",
            "come up with": "придумати",
            "pull away": "відволікати",
        },
        "context": context.model_dump_json(),
    }
