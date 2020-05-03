import os


class style:
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"


def highlight_title(title):
    if os.name == "nt":
        return title

    return f"{color.CYAN}{style.BOLD}{style.UNDERLINE}{title}{style.END}"


def highlight_text(text):
    if os.name == "nt":
        return text

    return (text
            .replace("[", f"{style.BOLD}{color.BLUE}[")
            .replace("]", f"]{style.END}")
            .replace("(", f"{color.PURPLE}(")
            .replace(")", f"){style.END}"))
