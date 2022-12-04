import subprocess
import textwrap
import webbrowser
import openai
from flox import Flox


def get_model_name(model_name: str) -> str:
    """
    Returns a valid model name. If model_name is not valid, it defaults to text-ada-001
    :param model_name: model name to input
    :return: model name if valid
    """
    return model_name if model_name in ["text-ada-001", "text-babbage-001", "text-curie-001",
                                        "text-davinci-003"] else "text-ada-001"


def open_openai_site() -> None:
    """
    Opens the OpenAI API key site in the browser
    """
    webbrowser.open("https://beta.openai.com/account/api-keys")


def get_temperature(temperature: str) -> float:
    """
    Returns a temperature between 0.1 and 1.0
    :param temperature: temperature to check
    :return: valid temperature
    """
    if float(temperature) < 0.1:
        return 0.1
    elif float(temperature) > 1.0:
        return 1.0
    else:
        return float(temperature)


def get_max_tokens(max_tokens: str, model_name: str) -> int:
    """
    Returns a valid number of tokens for the given model
    :param max_tokens: max_tokens to check
    :param model_name: model to check
    :return: valid max_tokens
    """
    big_models = ["text-davinci-003"]
    if int(max_tokens) < 10:
        return 10
    elif int(max_tokens) > 2048 and model_name not in big_models:
        return 2048
    elif int(max_tokens) > 4000:
        return 4000
    else:
        return int(max_tokens)


class OpenAI(Flox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Warning: Changing the level to debug will print your API key in cleartext into the log file as Flox then dumps
        # the whole query and the whole settings of the plugin into the log file!
        self.logger_level("info")

    def openai_request(self, input_query: str) -> str:
        """
        Performs the actual request to OpenAI with the parameters in the plugin settings
        :param input_query: query to give to the model
        :return: Response from OpenAI
        """
        openai.api_key = self.settings.get("OPENAI_KEY")
        model_name = get_model_name(self.settings.get("OPENAI_MODEL"))
        max_tokens = get_max_tokens(self.settings.get("OPENAI_MAX_TOKENS"), model_name)
        temperature = get_temperature(self.settings.get("OPENAI_TEMPERATURE"))
        completion = openai.Completion.create(
            model=model_name,
            prompt=input_query,
            max_tokens=max_tokens,
            temperature=temperature
        )
        result = completion.choices[0].text.replace("\n", "")
        return result

    def query(self, query: str) -> None:
        """
        Entry into the FlowLauncher Query
        :param query: query from FlowLauncher
        """
        if self.settings.get("OPENAI_KEY") == "EDIT_ME":
            self.add_item(
                title="Edit your OpenAI Key in the settings of this plugin",
                subtitle="Press Enter to launch the OpenAI API key website",
                IcoPath="Images/logo.png",
                method="open_openai_site"
            )
        elif query.split(" ")[-1] == "x":
            result = self.openai_request(query[:-2])
            self.add_item(
                title=textwrap.shorten(result, width=200, placeholder="..."),
                subtitle="Press Enter to copy the whole text into your clipboard!",
                IcoPath="Images/logo.png",
                method="copy",
                parameters=[result],
            )
        else:
            self.add_item(
                title="Waiting for x to send",
                subtitle="This is done to limit requests to the OpenAI API",
                IcoPath="Images/logo.png"
            )

    def copy(self, params: str) -> None:
        """
        Copies the given params (i.e. the result from OpenAI) into the clipboard and displays a windows toast notification
        :param params: result from OpenAI to copy
        """
        subprocess.check_call(f"echo {params}|clip", shell=True)
        self.show_msg(title="Successfully copied the text into the clipboard", sub_title="")
