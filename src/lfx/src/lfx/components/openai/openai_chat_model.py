from typing import Any

from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr

from lfx.base.models.model import LCModelComponent

# Removed unused constants as we are no longer using a predefined list of models.
# from lfx.base.models.openai_constants import OPENAI_CHAT_MODEL_NAMES, OPENAI_REASONING_MODEL_NAMES
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec

# Removed DropdownInput as it's replaced by StrInput.
from lfx.inputs.inputs import BoolInput, DictInput, IntInput, SecretStrInput, SliderInput, StrInput
from lfx.log.logger import logger


class OpenAIModelComponent(LCModelComponent):
    display_name = "OpenAI"
    description = "Generates text using OpenAI LLMs."
    icon = "OpenAI"
    name = "OpenAIModel"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="The maximum number of tokens to generate. Set to 0 for unlimited tokens.",
            range_spec=RangeSpec(min=0, max=128000),
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments to pass to the model.",
        ),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, it will output JSON regardless of passing a schema.",
        ),
        # ------------------- MAJOR CHANGE 1: Changed DropdownInput to StrInput -------------------
        # This allows for manual entry of any model name, such as "gemini-2.5-pro".
        StrInput(
            name="model_name",
            display_name="Model Name",
            advanced=False,
            info="Manually enter the model name, e.g., 'gpt-4o', 'gemini-2.5-pro', etc.",
            value="gpt-4o",  # Provide a common default value.
            required=True,
        ),
        # -----------------------------------------------------------------------------------------
        StrInput(
            name="openai_api_base",
            display_name="OpenAI API Base",
            advanced=True,
            info="The base URL of the OpenAI API. "
            "Defaults to https://api.openai.com/v1. "
            "You can change this to use other APIs like JinaChat, LocalAI and Prem.",
        ),
        SecretStrInput(
            name="api_key",
            display_name="OpenAI API Key",
            info="The OpenAI API Key to use for the OpenAI model.",
            advanced=False,
            value="OPENAI_API_KEY",
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            show=True,
        ),
        IntInput(
            name="seed",
            display_name="Seed",
            info="The seed controls the reproducibility of the job.",
            advanced=True,
            value=1,
        ),
        IntInput(
            name="max_retries",
            display_name="Max Retries",
            info="The maximum number of retries to make when generating.",
            advanced=True,
            value=5,
        ),
        IntInput(
            name="timeout",
            display_name="Timeout",
            info="The timeout for requests to OpenAI completion API.",
            advanced=True,
            value=700,
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        logger.debug(f"Executing request with model: {self.model_name}")
        # Handle api_key - it can be string or SecretStr
        api_key_value = None
        if self.api_key:
            logger.debug(f"API key type: {type(self.api_key)}, value: {self.api_key!r}")
            if isinstance(self.api_key, SecretStr):
                api_key_value = self.api_key.get_secret_value()
            else:
                api_key_value = str(self.api_key)
        logger.debug(f"Final api_key_value type: {type(api_key_value)}, value: {'***' if api_key_value else None}")

        # Handle model_kwargs and ensure api_key doesn't conflict
        model_kwargs = self.model_kwargs or {}
        # Remove api_key from model_kwargs if it exists to prevent conflicts
        if "api_key" in model_kwargs:
            logger.warning("api_key found in model_kwargs, removing to prevent conflicts")
            model_kwargs = dict(model_kwargs)  # Make a copy
            del model_kwargs["api_key"]

        parameters = {
            "api_key": api_key_value,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens or None,
            "model_kwargs": model_kwargs,
            "base_url": self.openai_api_base or "https://api.openai.com/v1",
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            # ------------------- MAJOR CHANGE 2: Removed conditional logic for parameters -------------------
            # Since we can't determine the model type from a manual string, we always pass these parameters.
            # The API endpoint is expected to either use them or ignore them if not supported.
            "temperature": self.temperature,
            "seed": self.seed,
            # ------------------------------------------------------------------------------------------------
        }

        output = ChatOpenAI(**parameters)
        if self.json_mode:
            output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e: Exception):
        """Get a message from an OpenAI exception.

        Args:
            e (Exception): The exception to get the message from.

        Returns:
            str: The message from the exception.
        """
        try:
            from openai import BadRequestError
        except ImportError:
            return None
        if isinstance(e, BadRequestError):
            message = e.body.get("message")
            if message:
                return message
        return None

    # ------------------- MAJOR CHANGE 3: Simplified update_build_config method -------------------
    # This method was used to dynamically show/hide UI fields based on the selected model.
    # Since the model is now a manual input, this dynamic logic is no longer reliable.
    # We remove it to ensure all fields remain visible by default.
    def update_build_config(self, build_config: dict, _field_value: Any, _field_name: str | None = None) -> dict:
        # No longer need to dynamically modify the config based on model_name.
        # Just return the original config.
        return build_config

    # ---------------------------------------------------------------------------------------------
