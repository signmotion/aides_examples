from gpt4all import GPT4All, pyllmodel
import logging
from pydantic import Field
import sys
from typing import Any, Iterable, Optional, Union

logger = logging.getLogger(__name__)


def printing_response_callback(token_id: int, token_text: str) -> bool:
    sys.stdout.write(token_text)
    sys.stdout.flush()

    return True


class AideLlm:
    def __init__(
        self,
        model_name: str,
        model_path: str,
        verbose: bool = False,
    ):
        self.model_name = model_name
        self.model_path = model_path

        self._li(f"Connecting to model `{model_path}`...")
        try:
            self.model = GPT4All(
                model_name,
                model_path=model_path,
                allow_download=False,
                verbose=verbose,
            )
        except Exception as ex:
            self._le(ex)
            raise ex

        self._li(f"Connected to model `{model_path}`.")

    model_name: str = Field(
        ...,
        title="Model Name",
        description="The filename of LLM model.",
    )

    model_path: str = Field(
        ...,
        title="Model Path",
        description="The path to LLM model without filename.",
    )

    verbose: bool = Field(
        ...,
        title="Verbose",
        description="Verbose mode when `true`.",
    )

    model: GPT4All = Field(
        ...,
        title="Model",
        description="The initiated LLM model.",
    )

    def generate(
        self,
        prompt: str,
        max_tokens: int = 60,
        temp: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.4,
        repeat_penalty: float = 1.18,
        repeat_last_n: int = 64,
        n_batch: int = 8,
        n_predict: Optional[int] = None,
        streaming: bool = True,
        response_callback: Union[pyllmodel.ResponseCallbackType, None] = None,
    ) -> Union[str, Iterable[str]]:
        """
        Generate outputs from the `model`.

        See `GPT4All.generate()` for details.
        """

        callback = response_callback
        if not callback:
            callback = (
                printing_response_callback
                if self.verbose
                else pyllmodel.empty_response_callback
            )

        return self.model.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temp,
            top_k=top_k,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            repeat_last_n=repeat_last_n,
            n_batch=n_batch,
            n_predict=n_predict,
            streaming=streaming,
            callback=callback,
        )

    def _li(self, v: Any):
        if self.verbose:
            logger.info(v)

    def _le(self, v: Any):
        if self.verbose:
            logger.error(v)
