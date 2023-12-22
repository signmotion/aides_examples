import json
import logging
from pydantic import BaseModel
from typing import Any, Dict, List, Set, Union


logger = logging.getLogger("uvicorn.error") or logging.root


def short_json(
    o: Union[BaseModel, Dict[str, Any], List[Any], Set[Any], str, int, float, None],
    slice_dict_to_length: int = 12,
    slice_list_to_length: int = 4,
    slice_str_to_length: int = 120,
    include: Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None] = None,
    exclude: Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None] = None,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
    exclude_none: bool = True,
) -> Union[Dict[str, Any], List[Any], Set[Any], str, int, float, None]:
    """
    Truncate the values into JSON, exclude unused, empty or default values.

    Args:

        include: Field(s) to include in the JSON output. Can take either a string or set of strings.
        exclude: Field(s) to exclude from the JSON output. Can take either a string or set of strings.
        exclude_unset: Whether to exclude fields that have not been explicitly set.
        exclude_defaults: Whether to exclude fields that have the default value.
        exclude_none: Whether to exclude fields that have a value of `None`.

    Returns:
        A short JSON string representation.
    """

    d: Union[Dict[str, Any], List[Any], Set[Any], str, int, float, None]
    if isinstance(o, BaseModel):
        d = o.model_dump(
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    elif isinstance(o, str):
        try:
            d = json.loads(o)
        except Exception as _:
            d = o
    else:
        d = o

    if isinstance(d, str):
        if slice_str_to_length > 0 and len(d) > slice_str_to_length:
            d = f"{d[:slice_str_to_length]}..."
        return d

    if isinstance(d, dict):
        d = list(d.items())
        if slice_dict_to_length > 0 and len(d) > slice_dict_to_length:
            d = d[slice(slice_dict_to_length)]
            d.append(("...", "..."))
        return dict((k, short_json(v)) for k, v in d)

    if isinstance(d, list):
        d = _sliced(d, slice_list_to_length)
        return [short_json(v) for v in d]

    if isinstance(d, set):
        d = _sliced(d, slice_list_to_length)
        return set([short_json(v) for v in d])

    return d


def _sliced(v: Union[List[Any], Set[Any]], limit: int) -> List[Any]:
    r: List[Any] = v if isinstance(v, list) else list(v)
    if limit > 0 and len(v) > limit:
        r = r[slice(limit)]
        r.append("...")

    return r
