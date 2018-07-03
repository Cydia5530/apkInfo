import asyncio
from pyppeteer import launch


async def main():
    browser = await launch(headless=False)  #headless=False,devtools=True
    page = await  browser.newPage()
    await page.setViewport({'width': 1200, 'height': 768})
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
    await asyncio.sleep(3)
    ps = await browser.pages()
    loginPage= [pg for pg in ps if  "login" in pg.url][0]
    if loginPage is not None:
        print("从首页跳转，代码可以实现打开、点击、跳转")
    await loginPage.setViewport({'width': 1024, 'height': 768})

# 账号、密码登录（这里设置成读取配置文件吧）
    #loginType = input("您选择哪种登录方式 1：账号密码登录；2：动态验证码登录\n")
    loginType = "1"
    if loginType == "1":
        print("进入账号密码登录")
        await loginPage.type("#userName", "15011245637")
        await loginPage.type("#pwd","woailn123")
        await loginPage.click("#yzm")
        print("请自行完成登录")
    elif loginType == "2":
        print("动态验证码登录")
        await loginPage.click("li.phone_login")
        await loginPage.type("#reg_mobile", "15011245637")
        print("请自行完成登录")
    else:
        print("只能选择 1 或者 2\n")
    while True:
        #await asyncio.sleep(0.1)
        ps = await browser.pages()
        MemberPage = [pg for pg in ps if "member" in pg.url]
        if MemberPage:
            print(MemberPage[0].url)
            await  MemberPage[0].close()
            break
        await asyncio.sleep(0.1)


    await page.goto("https://store.lining.com/shop/goods-493477.html")
    await page.bringToFront()
    await asyncio.sleep(0.1)

    #hand = await page.J("#thumblist>li.thumbimgchecked.tb-selected>a")
    selectColorElement = await page.xpath("// *[ @ id = 'thumblist'] / li[2] / a") ##这个xpath对李宁商品是通用的
    await selectColorElement[0].click()  #选择点击不同款式
    await asyncio.sleep(1)
    sizeList = await page.JJ("div.size-layer")  #获取所有的尺寸
    print(len(sizeList))
    data = []
    for s in sizeList:
        #await s.click()  #事实证明，这里的 div 节点是可以点击的
        eleValue = await s.xpath(".//input/@value")     # 前边加点是从当前节点作为根节点开始搜索，否则是从整个页面搜索
        eleAmount = await s.xpath(".//input/@enablesaleamount")

        if eleValue and eleAmount:

            eleValue = await page.evaluate('(element) => element.textContent', eleValue[0])
            eleAmount = await page.evaluate('(element) => element.textContent', eleAmount[0])
            data.append((eleValue, eleAmount, s))
            print("{} 号还有 {}双".format(eleValue, eleAmount) )   #这里直接用a
    data.sort(key=lambda x: x[1], reverse=True)  #直接打印 print(data.sort())会打印无，因为排序这个函数返回的是空值
    #选择剩余数量最多的那个鞋号点击（后期可以做用户自定义鞋号）

    await data[0][2].click()
    await asyncio.sleep(0.1)
    await page.click("#addtonowcart")
    #速度太快，需要睡会
    await asyncio.sleep(1)
    subButton = await page.xpath("// *[ @ id = 'id_action_submit'] / input")
    await asyncio.sleep(0.6)
    if subButton:
        print("点击提交")
        await subButton[0].click()

    await asyncio.sleep(1000)

    await page.setRequestInterception(False)
    await page.close()
    await browser.close()

#


async def request_check(req):
    #print(req.url)
    if req.resourceType == "image":
        #await req.abort()
        await req.continue_()
    #if "yzmImages" in req.url:
    #    print("验证码url "+ req.url)
    #    #global URL
    #    #URL= req.url
    else:
        #print("###真正加载的url "+ req.url)
        await req.continue_()

asyncio.get_event_loop().run_until_complete(main())

#获取选定元素的文本内容
# tem = await page.J("li.phone_login")
# title = await page.evaluate('(element) => element.textContent', tem)

#移动到屏幕可见位置
    #curr = await page.querySelectorEval("li.phone_login","(elem) => elem.scrollIntoView()")



