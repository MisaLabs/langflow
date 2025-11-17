from langchain_openai import ChatOpenAI

from langflow.base.models.model import LCModelComponent
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs.inputs import BoolInput, StrInput
from langflow.io import MessageInput, MultilineInput, SecretStrInput, SliderInput

DEFAULT_OPENAI_API_URL = "https://api.openai.com/v1"


class MisaLabsLLMComponent(LCModelComponent):
    display_name = "MisaLabsLLM"
    description = "MisaLabsLLM MisaCore"
    documentation: str = "https://docs.langflow.org/components-models"
    icon = "MisaLabs"
    category = "models"
    priority = 0  # Set priority to 0 to make it appear first

    inputs = [
        StrInput(
            name="model_name",
            display_name="Model Name",
            value="gpt-4o",
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
                "The base URL of the OpenAI Compatible API. Default " + DEFAULT_OPENAI_API_URL + "."
                "You can change this to use other APIs like OpenAI-compatible endpoints."
            ),
            value=DEFAULT_OPENAI_API_URL,
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

        # Always pass temperature - the API will handle it appropriately
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            streaming=stream,
            api_key=self.api_key or "dummy",
            base_url=self.base_url or "https://api.openai.com/v1",
        )
