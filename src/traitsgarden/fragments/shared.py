"""Shared functions and wrappers between fragments."""

def dropdown_options_input(get_options):
    """From an iterable, generate dropdown menu options,
    including custom input values.
    """
    def wrapper(search_value, input_value):
        if not search_value:
            search_value = ''
        result = get_options(search_value, input_value)
        options = list(result)
        if search_value:  ## Include the user input
            options = [search_value] + options
        if input_value:  ## Keep the input after selected
            options = [input_value] + options
        return options
    return wrapper
