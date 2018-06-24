import asyncio
from pyppeteer import launch
from pyppeteer.frame_manager import Frame
from pyppeteer.page import Page





async def main():
    browser = await launch(headless=False)
    page = await  browser.newPage()
    await page.setRequestInterception(True)
    page.on("request", requestCheck)
#李宁主界面
    #await page.goto("http://lining.com")
    #await page.bringToFront()
    #里层用单引号、外层用双引号
    #links = await page.xpath("//a[contains(@class,'childA')]")

#在首页点击登录
    #link = await page.frames[1].xpath("//a[@href='/shop/login.php']")
    #task = await link[0].click()


#点击登录
    await page.goto("https://store.lining.com/shop/login_ssl.php")
    page.click()







    await browser.close()

#登录界面
    #await page.goto("https://store.lining.com/shop/login_ssl.php")


async def requestCheck(req):
    if req.resourceType in ['image', 'media']:
        await req.abort()
    else:
        await req.continue_()


asyncio.get_event_loop().run_until_complete(main())