import chardet
import textract
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from textract.exceptions import ExtensionNotSupported


def send_message(lesson_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"lesson_{lesson_id}", {"type": "message", "data": data}
    )


def extract_file_text(file: str) -> str:
    try:
        text = textract.process(file)
    except ExtensionNotSupported:
        try:
            rawdata = open(file, "rb").read()
            enc = chardet.detect(rawdata)
            with open(file, encoding=enc["encoding"]) as file:
                text = file.read()
        except Exception:
            return ""
    if type(text) is bytes:
        return text.decode()
    return text


def extract_term_and_definition(input_string):
    # Remove leading hyphen if it exists
    input_string = input_string.lstrip("-").strip()

    try:
        # Split the string on the colon
        parts = input_string.split(":")

        # If there's no colon, we return None for both term and definition
        if len(parts) == 1:
            return None, None

        # The term is the first part, and the definition is the join of the remaining parts
        term = parts[0].strip()
        definition = ":".join(parts[1:]).strip()

        return term, definition
    except Exception as e:
        # If an error occurs, we return the error message
        return str(e), None
