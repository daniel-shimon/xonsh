import pytest

from tests.tools import skip_if_on_windows, skip_if_on_darwin

from xonsh.completers.bash import complete_from_bash
from xonsh.parsers.completion_context import CompletionContext, CommandContext, CommandArg


@skip_if_on_darwin
@skip_if_on_windows
@pytest.mark.parametrize("command_context, completions", (
        (CommandContext(args=(CommandArg("bash"),), arg_index=1, prefix="--deb"), {"--debug ", "--debugger "}),
))
def test_bash_completer(command_context, completions):
    bash_completions, prefix = complete_from_bash(CompletionContext(command_context))
    assert bash_completions == completions

