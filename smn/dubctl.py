from aiofile import async_open


class DubsDataFile:
    def __init__(self, file: str = ".dubdata", amount: int = 24 * 7 * 3):
        self.file = file
        self.amount = amount
        self.data = []

    async def _post_init(self):
        data = []
        try:
            async with async_open(self.file, mode="r") as f:
                async for line in f:
                    data.append(line.rstrip("\n"))
        except FileNotFoundError:
            open(self.file, mode="w", encoding="utf-8").close()
        self.data = data

    async def update(self, link: str):
        if len(self.data) >= self.amount:
            del self.data[0]
        self.data.append(link)
        await self.save()

    async def save(self):
        async with async_open(self.file, mode="w") as f:
            await f.write("\n".join(self.data))
