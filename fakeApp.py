import asyncio
from pyppeteer import launch


async def main():
    browser = await launch(headless=False)  #headless=False,devtools=True
    LoginPage = await  browser.newPage()
    await LoginPage.setViewport({'width': 1200, 'height': 768})
    response = await LoginPage.goto("https://www.appscan.io/login.html", waitUntil='documentloaded')
    await LoginPage.bringToFront()

    userName = await LoginPage.type("#email", "hnq@cert.org.cn")
    passWord = await LoginPage.type("#password","tw2LQE8L4t1VCD5M")

    await asyncio.sleep(100)

    await LoginPage.close()
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
