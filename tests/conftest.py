import builtins
import glob
import os
import sys

import pytest

from xonsh.built_ins import (
    ensure_list_of_strs,
    XonshSession,
    pathsearch,
    globsearch,
    regexsearch,
    list_of_strs_or_callables,
    list_of_list_of_strs_outer_product,
    call_macro,
    enter_macro,
    path_literal,
    _BuiltIns,
)
from xonsh.execer import Execer
from xonsh.jobs import tasks
from xonsh.events import events
from xonsh.parser import Parser
from xonsh.platform import ON_WINDOWS
from xonsh.built_ins import load_builtins

from tools import DummyShell, sp, DummyCommandsCache, DummyEnv, DummyHistory


@pytest.fixture
def source_path():
    """Get the xonsh source path."""
    pwd = os.path.dirname(__file__)
    return os.path.dirname(pwd)


@pytest.fixture
def xonsh_session(monkeypatch):
    session = XonshSession()
    monkeypatch.setattr(builtins, '__xonsh__', session, raising=False)
    return session


@pytest.fixture(scope='session')
def xonsh_parser():
    """Get the a reusable parser for Execer."""
    return Parser()


@pytest.fixture
def xonsh_execer(xonsh_session, xonsh_parser, monkeypatch):
    """Initiate the Execer with a mocked nop `load_builtins`"""

    # Make sure Execer will act normally inside tests (like in test_imphooks.py)
    _load_builtins, _parser_new = load_builtins.__code__, Parser.__new__
    load_builtins.__code__ = (lambda *args, **kwargs: None).__code__
    Parser.__new__ = lambda *args, **kwargs: xonsh_parser
    execer = Execer(unload=False)
    load_builtins.__code__, Parser.__new__ = _load_builtins, _parser_new
    xonsh_session.execer = execer
    return execer


@pytest.fixture
def monkeypatch_stderr(monkeypatch):
    """Monkeypath sys.stderr with no ResourceWarning."""
    with open(os.devnull, "w") as fd:
        monkeypatch.setattr(sys, "stderr", fd)
        yield


@pytest.fixture
def xonsh_events():
    yield events
    for name, oldevent in vars(events).items():
        # Heavily based on transmogrification
        species = oldevent.species
        newevent = events._mkevent(name, species, species.__doc__)
        setattr(events, name, newevent)


@pytest.fixture
def xonsh_builtins(xonsh_session, xonsh_execer, xonsh_events, monkeypatch):
    """Mock out most of the builtins xonsh attributes."""
    xonsh_session.env = DummyEnv()
    if ON_WINDOWS:
        xonsh_session.env["PATHEXT"] = [".EXE", ".BAT", ".CMD"]
    xonsh_session.shell = DummyShell()
    xonsh_session.help = lambda x: x
    xonsh_session.glob = glob.glob
    xonsh_session.exit = False
    xonsh_session.superhelp = lambda x: x
    xonsh_session.pathsearch = pathsearch
    xonsh_session.globsearch = globsearch
    xonsh_session.regexsearch = regexsearch
    xonsh_session.regexpath = lambda x: []
    xonsh_session.expand_path = lambda x: x
    xonsh_session.subproc_captured = sp
    xonsh_session.subproc_uncaptured = sp
    xonsh_session.stdout_uncaptured = None
    xonsh_session.stderr_uncaptured = None
    xonsh_session.ensure_list_of_strs = ensure_list_of_strs
    xonsh_session.commands_cache = DummyCommandsCache()
    xonsh_session.all_jobs = {}
    xonsh_session.list_of_strs_or_callables = list_of_strs_or_callables
    xonsh_session.list_of_list_of_strs_outer_product = (
        list_of_list_of_strs_outer_product
    )
    xonsh_session.history = DummyHistory()
    xonsh_session.subproc_captured_stdout = sp
    xonsh_session.subproc_captured_inject = sp
    xonsh_session.subproc_captured_object = sp
    xonsh_session.subproc_captured_hiddenobject = sp
    xonsh_session.enter_macro = enter_macro
    xonsh_session.completers = None
    xonsh_session.call_macro = call_macro
    xonsh_session.enter_macro = enter_macro
    xonsh_session.path_literal = path_literal
    xonsh_session.builtins = _BuiltIns(execer=xonsh_execer)
    monkeypatch.setattr(builtins, 'evalx', eval, raising=False)
    monkeypatch.setattr(builtins, 'execx', None, raising=False)
    monkeypatch.setattr(builtins, 'compilex', None, raising=False)
    monkeypatch.setattr(builtins, 'aliases', {}, raising=False)
    # Unlike all the other stuff, this has to refer to the "real" one because all modules that would
    # be firing events on the global instance.
    builtins.events = xonsh_events
    yield builtins
    tasks.clear()  # must to this to enable resetting all_jobs


def pytest_configure(config):
    """Abort test run if --flake8 requested, since it would hang on parser_test.py"""
    if config.getoption('--flake8', ''):
        pytest.exit("pytest-flake8 no longer supported, use flake8 instead.")
