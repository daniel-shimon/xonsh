"""
String literals tools.
These are used to post-process completions (see ``xonsh/completer.py`` ).
"""
import re
import typing as tp

import xonsh.platform as xp
import xonsh.lazyasd as xl


@xl.lazyobject
def SLASH():
    return xt.get_sep()


@xl.lazyobject
def PATTERN_NEED_QUOTES():
    pattern = r'\s`\$\{\}\,\*\(\)"\'\?&#'
    if xp.ON_WINDOWS:
        pattern += "%"
    pattern = "[" + pattern + "]" + r"|\band\b|\bor\b"
    return re.compile(pattern)


def _quote_to_use(x: str) -> str:
    single = "'"
    double = '"'
    if single in x and double not in x:
        return double
    else:
        return single


def escape_quote_completion(
    comp: str, opening_quote: str, closing_quote: str
) -> tp.Tuple[str, str, str]:
    """
    Escape and quote a completion if necessary.
    Returns the new (comp, opening_quote, closing_quote) - they might be the original ones.
    """
    if not opening_quote and re.search(PATTERN_NEED_QUOTES, comp):
        opening_quote = closing_quote = _quote_to_use(comp)
    
    if "\\" in comp:
        

    return comp, opening_quote, closing_quote
