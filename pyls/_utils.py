# Copyright 2017 Palantir Technologies, Inc.
import functools
import inspect
import logging
import os
import threading
import trio
import sys

log = logging.getLogger(__name__)
PY3 = sys.version[0] == '3'


def debounce(interval_s, keyed_by=None):
    """Debounce calls to this function until interval_s seconds have passed."""
    def wrapper(func):
        timers = {}
        lock = threading.Lock()

        @functools.wraps(func)
        def debounced(*args, **kwargs):
            call_args = inspect.getcallargs(func, *args, **kwargs)
            key = call_args[keyed_by] if keyed_by else None

            def run():
                with lock:
                    del timers[key]
                return func(*args, **kwargs)

            with lock:
                old_timer = timers.get(key)
                if old_timer:
                    old_timer.cancel()

                timer = threading.Timer(interval_s, run)
                timers[key] = timer
                timer.start()
        return debounced
    return wrapper


def find_parents(root, path, names):
    """Find files matching the given names relative to the given path.

    Args:
        path (str): The file path to start searching up from.
        names (List[str]): The file/directory names to look for.
        root (str): The directory at which to stop recursing upwards.

    Note:
        The path MUST be within the root.
    """
    if not root:
        return []

    if not os.path.commonprefix((root, path)):
        log.warning("Path %s not in %s", path, root)
        return []

    # Split the relative by directory, generate all the parent directories, then check each of them.
    # This avoids running a loop that has different base-cases for unix/windows
    # e.g. /a/b and /a/b/c/d/e.py -> ['/a/b', 'c', 'd']
    dirs = [root] + os.path.relpath(os.path.dirname(path), root).split(os.path.sep)

    # Search each of /a/b/c, /a/b, /a
    while dirs:
        search_dir = os.path.join(*dirs)
        existing = list(filter(os.path.exists, [os.path.join(search_dir, n) for n in names]))
        if existing:
            return existing
        dirs.pop()

    # Otherwise nothing
    return []


def list_to_string(value):
    return ",".join(value) if isinstance(value, list) else value


def merge_dicts(dict_a, dict_b):
    """Recursively merge dictionary b into dictionary a.

    If override_nones is True, then
    """
    def _merge_dicts_(a, b):
        for key in set(a.keys()).union(b.keys()):
            if key in a and key in b:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    yield (key, dict(_merge_dicts_(a[key], b[key])))
                elif b[key] is not None:
                    yield (key, b[key])
                else:
                    yield (key, a[key])
            elif key in a:
                yield (key, a[key])
            elif b[key] is not None:
                yield (key, b[key])
    return dict(_merge_dicts_(dict_a, dict_b))


def format_docstring(contents):
    """Python doc strings come in a number of formats, but LSP wants markdown.

    Until we can find a fast enough way of discovering and parsing each format,
    we can do a little better by at least preserving indentation.
    """
    contents = contents.replace('\t', u'\u00A0' * 4)
    contents = contents.replace('  ', u'\u00A0' * 2)
    contents = contents.replace('*', '\\*')
    return contents


def clip_column(column, lines, line_number):
    # Normalise the position as per the LSP that accepts character positions > line length
    # https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md#position
    max_column = len(lines[line_number].rstrip('\r\n')) if len(lines) > line_number else 0
    return min(column, max_column)


if os.name == 'nt':
    import ctypes

    kernel32 = ctypes.windll.kernel32
    PROCESS_QUERY_INFROMATION = 0x1000

    def is_process_alive(pid):
        """Check whether the process with the given pid is still alive.

        Running `os.kill()` on Windows always exits the process, so it can't be used to check for an alive process.
        see: https://docs.python.org/3/library/os.html?highlight=os%20kill#os.kill

        Hence ctypes is used to check for the process directly via windows API avoiding any other 3rd-party dependency.

        Args:
            pid (int): process ID

        Returns:
            bool: False if the process is not alive or don't have permission to check, True otherwise.
        """
        process = kernel32.OpenProcess(PROCESS_QUERY_INFROMATION, 0, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        return False

else:
    import errno

    def is_process_alive(pid):
        """Check whether the process with the given pid is still alive.

        Args:
            pid (int): process ID

        Returns:
            bool: False if the process is not alive or don't have permission to check, True otherwise.
        """
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True


def race_hooks(hook_caller, **kwargs):
    """Given a pluggy hook spec, execute impls in parallel returning the first non-None result.

    Note this does not support a lot of pluggy functionality, e.g. hook wrappers.
    """
    impls = hook_caller._nonwrappers + hook_caller._wrappers
    log.debug("Racing hook impls for hook %s: %s", hook_caller, impls)

    if not impls:
        return None

    first_impl, result = async_race(impls, **kwargs)
    log.debug("Hook from plugin %s returned: %s", first_impl.plugin_name,
              result)
    return result


def async_race(impls, **kwargs):
    """Create the race between rope and jedi using async functions."""
    if PY3:
        async def race(impls):
            send_channel, receive_channel = trio.open_memory_channel(0)

            async def _apply(impl):
                return impl, impl.function(**kwargs)

            async def jockey(impl):
                if impl.plugin_name == 'rope_completion':
                    await trio.sleep(0.1)
                await send_channel.send(await _apply(impl))

            async with trio.open_nursery() as nursery:
                for impl in impls:
                    nursery.start_soon(jockey, impl)

                winner = await receive_channel.receive()
                if winner is not None or winner is []:
                    nursery.cancel_scope.cancel()
                    return winner
        return trio.run(race, impls)
    else:
        return None
