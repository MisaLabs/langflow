from typing import Any
from urllib.parse import urljoin

from langchain_openai import ChatOpenAI
from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, StrInput
from lfx.io import DropdownInput, MessageInput, MultilineInput, SecretStrInput, SliderInput
from lfx.log.logger import logger
from lfx.schema.dotdict import dotdict
from lfx.utils.util import transform_localhost_url


class LanguageModelComponent(LCModelComponent):
    display_name = "MisaLabs LLM"
    description = "MisaLabs LLM MisaCore"
    documentation: str = "https://docs.langflow.org/components-models"
    icon = "brain-circuit"
    category = "models"
    priority = 0  # Set priority to 0 to make it appear first

    inputs = [
        StrInput(
            name="model_name",
            display_name="Model Name",
            value="meta-llama/Llama-3.1-8B-Instruct",
            info="Enter the model name manually", 
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="API key if needed",
            required=False,
            show=True,
            real_time_refresh=True,
        ),
        StrInput(
            name="base_url",
            display_name="API Base URL",
            info=(
                "The base URL of the OpenAI Compatible API. Defaults to https://api.openai.com/v1. "
                "You can change this to use other APIs like OpenAI-compatible endpoints."
            ),
            value="https://api.openai.com/v1",
            show=True,
            advanced=True,
            required=False,
        ),
        MessageInput(
            name="input_value",
            display_name="Input",
            info="The input text to send to the model",
        ),
        MultilineInput(
            name="system_message",
            display_name="System Message",
            info="A system message that helps set the behavior of the assistant",
            advanced=False,
        ),
        BoolInput(
            name="stream",
            display_name="Stream",
            info="Whether to stream the response",
            value=False,
            advanced=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            info="Controls randomness in responses",
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            advanced=True,
        ),
    ]

    def build_model(self) -> LanguageModel:
        model_name = self.model_name
        temperature = self.temperature
        stream = self.stream

        if not self.api_key:
          self.api_key = "nokey"

        # Always pass temperature - the API will handle it appropriately
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            streaming=stream,
            api_key=self.api_key,
            base_url=self.base_url or "https://api.openai.com/v1",
        )

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None) -> dotdict:
        # Using StrInput for model_name, so just set a default value
        build_config["model_name"]["value"] = "gpt-4o"
        build_config["api_key"]["display_name"] = "API Key"
        build_config["api_key"]["show"] = True
        build_config["base_url"]["show"] = True
        build_config["project_id"]["show"] = False
        return build_config
