from copy import deepcopy
from typing import Any, Callable, List, Tuple

import ui


def get_input(
    query_string: str = None,
    choices: List = None,
    out_type: type = str,
    conditions: Tuple[Callable[..., Any], str] = None  # pylint: disable=bad-whitespace
) -> Any:
    """
    Gets user input and coerces it into the type provided.
    Note that query_string can be a format string and will be evaluated before this function is entered
    function, when the calling variables are out of scope
    If nothing is entered, we will keep looping. If the user wants to stop entering data, they can enter 'quit'
    """
    while True:
        if not choices:
            user_data = ui.ask_string(query_string) if query_string else ui.read_input()
        else:
            user_data = ui.ask_choice(query_string or '', deepcopy(choices))
        if not user_data:
            ui.error('Nothing entered')
            continue
        if user_data.lower() == 'quit':
            raise ValueError
        try:
            typed_data = out_type(user_data)
        except (TypeError, ValueError):
            ui.error(f'Unable to coerce string into {out_type}')
            continue
        if conditions:
            if not conditions[0](typed_data):
                ui.error(conditions[1])
                continue
        return typed_data
