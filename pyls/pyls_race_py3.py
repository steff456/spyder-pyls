import trio


def async_race(impls, **kwargs):
    """Create  the race between rope and jedi using async functions."""
    # pylint: disable=syntax-error
    async def race(impls):
        send_channel, receive_channel = trio.open_memory_channel(0)

        # pylint: disable=syntax-error
        async def _apply(impl):
            return impl, impl.function(**kwargs)

        # pylint: disable=syntax-error
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
