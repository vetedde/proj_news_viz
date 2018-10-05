from aiohttp import web
import asyncio
import random


async def handle(request):
    await asyncio.sleep(random.randint(0, 3))
    return web.Response(text="Hello, World!")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)
