import asyncio


from pyppeteer import launch
from pyppeteer.frame_manager import Frame
from pyppeteer.page import Page

URL = ""



async def main():
    browser = await launch(headless=False)  #headless=False,devtools=True

    page = await  browser.newPage()

    await page.setViewport({'width': 1054, 'height': 768})
    await page.setRequestInterception(True)
    page.on("request", lambda req: asyncio.ensure_future(request_check(req)))
#李宁主界面
    response = await page.goto("http://lining.com", waitUntil='networkidle0')
    #response = await page.goto('data:text/html,hello')
    await page.bringToFront()
    #if response is not None:
    #    print(response.url)
    #    print(response.status)
    #    print(response.text())
    #里层用单引号、外层用双引号
    #links = await page.xpath("//a[contains(@class,'childA')]")

#在首页点击登录
    link = await page.frames[1].xpath("//a[@href='/shop/login.php']")
    task = await link[0].click()
##点击后新开一个网页，browser开始异步新建一个target然后绑定一个新的page，此时立即调用browser.pages()，可能因为page还没建立，
##检索不到这个最新的page，需要sleep 一会
    await asyncio.sleep(1)
    ps = await browser.pages()
    loginPage= [pg for pg in ps if  "login" in pg.url ][0]
    print("#######Got it " + loginPage.url)

    await asyncio.sleep(20)


#点击登录
    #page.setViewport({'width': 1920, 'height': 1080})
    response = await page.goto("https://store.lining.com/shop/login_ssl.php",waitUntil='documentloaded')
    if response is  None:
        print(response.url)
        print(response.status)
        print(await response.text())
    #print(page.viewport)
    print(await page.cookies())
    #tem = await page.J("input#userName.ipt_t.user_icon")

#账号、密码登录

    await page.click("li.phone_login")
    #await page.click("")
    await page.type("#reg_mobile","15011245637")

    await asyncio.sleep(10)
    await page.setRequestInterception(False)
    await page.close()
    await browser.close()

#登录界面
    #await page.goto("https://store.lining.com/shop/login_ssl.php")


async def request_check(req):
    print(req.url)
    if req.resourceType == "image":
        await req.abort()
    #if "yzmImages" in req.url:
    #    print("验证码url "+ req.url)
    #    #global URL
    #    #URL= req.url
    else:
        print("###真正加载的url "+ req.url)
        await req.continue_()

asyncio.get_event_loop().run_until_complete(main())

#获取选定元素的文本内容
# tem = await page.J("li.phone_login")
# title = await page.evaluate('(element) => element.textContent', tem)

#移动到屏幕可见位置
    #curr = await page.querySelectorEval("li.phone_login","(elem) => elem.scrollIntoView()")




