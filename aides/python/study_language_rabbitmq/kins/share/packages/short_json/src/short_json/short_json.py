import json
from pydantic import BaseModel
import textwrap
from typing import Any, Dict, List, Set, Union


def short_json(
    o: Union[BaseModel, Dict[str, Any], List[Any], str],
    truncate_dict_to_length: int = 12,
    truncate_list_to_length: int = 4,
    truncate_str_to_length: int = 120,
    include: Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None] = None,
    exclude: Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None] = None,
    exclude_unset: bool = True,
    exclude_defaults: bool = False,
    exclude_none: bool = True,
) -> Dict[str, Any]:
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
    d = o
    if isinstance(o, BaseModel):
        d = o.model_dump(
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    elif isinstance(o, str):
        d = json.loads(o)

    # work with `dict`
    r: Dict[str, Any] = {}
    for k, v in d.items():  # type: ignore[override]
        if isinstance(v, dict):
            if truncate_dict_to_length > 0 and len(v) > truncate_dict_to_length:
                v = list(v.items())
                v = v[slice(truncate_dict_to_length)]
                v.append(("...", "..."))
                v = dict(v)
            r[k] = short_json(v)
        elif isinstance(v, list):
            if truncate_list_to_length > 0 and len(r[k]) > truncate_list_to_length:
                v = v[slice(truncate_list_to_length)]
                v.append("...")
            r[k] = short_json(v)
        elif isinstance(v, str):
            if truncate_str_to_length > 0 and len(v) > truncate_str_to_length:
                v = textwrap.shorten(
                    v,
                    width=truncate_str_to_length,
                    placeholder="...",
                )
            r[k] = v

    return r
