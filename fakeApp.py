import asyncio
from pyppeteer import launch
import time
import xlwt

##############//  关于此脚本的部分说明：//###################
#	1. 大多数时间，我们在等待浏览器加载、渲染数据；
#	2. 输入验证码登录的等待超时时间为 60s;
#	3. 正常网页的渲染等待超时时间为 30s;
#   4. 对于部分可能确实没有数据的网页，等待超时时间为 5s;（以上等待时间均可根据网速自行更改）
#   5. 对于搜索结果小于#20#个的情况，本脚本会崩掉（不要搜索太奇怪的信息）；
#   6. 如果可能，请先手动在盘古搜索，看下大致的结果；
#   7. env py3.6;
#   8. 需安装的包: pyppeteer, xlwt；
#   9. 具体情况，自行查看代码、注释、控制台打印信息。



######  欲抓取的内容, 请按照盘古搜索格式指定搜索内容
__wanted = "农行"     ## example: md5:"XXXX"

##### 欲抓取的字段
__wantedArrt = ["编号", "应用名", "包名", "MD5", "SHA1", "入库时间", "扫描时间", "版本",
                "大小", "签名", "签名MD5", "签名SHA1", "发布平台", "发布页面", "下载地址", "备注"]
#####  抓取的页数
pages = 2

##### 初识化 excel 头部和字体
workbook = xlwt.Workbook(encoding="utf8")
worksheet = workbook.add_sheet("盘古应用信息抓取", cell_overwrite_ok=True)
style = xlwt.XFStyle()     # 初始化样式
font = xlwt.Font()         # 为样式创建字体
font.name = 'Times New Roman'
font.height = 250
font.bold = True           # 黑体
#font.underline = True # 下划线
#font.italic = True # 斜体字
style.font = font # 设定样式
for i in range(len(__wantedArrt)):
    worksheet.write(0, i, __wantedArrt[i], style)

##### 全局行数记录
index = 1


##### 进入主函数
async def main():
    browser = await launch(headless=False)  #headless=False,devtools=True
    LoginPage = await  browser.newPage()
    await LoginPage.setViewport({'width': 1200, 'height': 768})
#####  登录界面
    await LoginPage.goto("https://www.appscan.io/login.html", waitUntil='documentloaded')
    await LoginPage.bringToFront()
    ##### 输入账号、密码
    await LoginPage.waitForSelector("#password")
    await LoginPage.type("#email", "hnqn")
    await LoginPage.type("#password", "twD5M")
    since = time.time()
#####  空转，等待用户成功输入验证码
    #while True:
    #    ps = await browser.pages()
    #    homePage = [pg for pg in ps if "home" in pg.url]     ####这里用waitfornagivatio吧
    #    if homePage:
    #        print(homePage[0].url)
    #        homePage = homePage[0]
    #        break
    #    await asyncio.sleep(0.1)
#### 等待用户输入正确的验证码，点击登录后，等待浏览器跳转，当前最大等待时间为60s。可根据网速、手速更改
    navi = LoginPage.waitForNavigation(timeout=60*1000)
    await navi
    time_elapsed = int(time.time() - since)
    print("\n######恭喜，您成功登陆了盘古系统, 用时{}s".format(time_elapsed))
    homePage = LoginPage

#### 进入进入home 页
    await homePage.waitForXPath('.//input[1]')      # 这里还是需要等待一下
    select = await homePage.xpath('.//input')
    await select[1].type(__wanted)                  # 输入搜索内容
    await homePage.waitForSelector(".search-btn", visible=True)
    await homePage.click(".search-btn")

    targeListPage = homePage
    targeUrlList = []
#####这里要不使用copy库，深度拷贝一个targePage出来备用，要不就是先把 targePage 当前页的所有用于跳转的 a @ href 取出来放进；
    ####放进任务队列里，挨个在新开的页面里读取，然后销毁页面
    curPage = targeListPage
    page = 1
    global pages
    while page <= pages:
        #### 这个等待可能有问题，对于一般应用检索应该没问题
        await curPage.waitForXPath("/ html / body / div / div[2] / div[6] / div[1] / div[2] / div[20]", visible=True)
        appList = await curPage.xpath("/ html / body / div / div[2] / div[6] / div[1] / div[2] / div")
        print("\n############ 进入第{}页 #############".format(page))
        appListLen = len(appList)
        if appListLen == 0:
            print("当前检索页未检索到任何应用")   #### 没有任何结果，准备退出
            await browser.close()
            return
        else:
            print("当前页面共检索到 " + str(appListLen-3) + "个应用")    #有三个div不是应用列表，第一个、第二个、最后一个div不是应用
        appListLen -= 1
        for i in range(2, appListLen):
            ##获取当前页面的所有app的跳转url
            targeApp = await appList[i].xpath(".// div[1] / dl / dt / a[1] ")
            targeAppUrl = await curPage.evaluate('(element) => element.href', targeApp[0])
            targeUrlList.append(targeAppUrl)
            print("\t当前页面的第 " + str(i - 1) + "个应用的跳转url为 " + targeAppUrl)

        #await curPage.waitForXPath(".//a[class='next-page']")      ####这个先保留，可能有用的着时候
        nextpages = await curPage.xpath(".//a[@class='next-page']")
        await nextpages[-1].click()                                ####   点击下一页
        page += 1
    print("\n成功扫描盘古应用共 {} 页，结束\n".format(pages))

    targeAppPage = await browser.newPage()
    await targeAppPage.setViewport({'width': 1200, 'height': 768})

    for targeUrl in targeUrlList:
        global index
        await targeAppPage.goto(targeUrl, waitUntil='documentloaded')

        #### 得等待一下这个表，第一次启动时，可能还没获取到
        await targeAppPage.waitForXPath('.//div[ @ id = "apk_base_info"] / div[1] / div[2] / table', visible=True)
        appInfo = await targeAppPage.xpath('.//div[ @ id = "apk_base_info"] / div[1] / div[2] / table / tbody / tr')
        print("当前获取到的应用信息为：")
        print(r"  应用基本信息为：")

        await targeAppPage.waitForXPath('/html/body/div/div[2]/div/div[1]/div[1]/div/dl/dt/span')
        appNameEle = await targeAppPage.xpath('/html/body/div/div[2]/div/div[1]/div[1]/div/dl/dt/span')
        appName = await targeAppPage.evaluate('(element) => element.textContent', appNameEle[0])
        print("\t应用名:" + appName)
        worksheet.write(index, 0, index)
        worksheet.write(index, 1, appName.strip())

        ####读取首页的概述信息
        for i in range(1, 11):
            infoEle = await appInfo[i].xpath('.//td')
            name = await targeAppPage.evaluate('(element) => element.textContent', infoEle[0])
            value = await targeAppPage.evaluate('(element) => element.textContent', infoEle[1])
            name = name.strip()
            value = value.strip()
            print("\t"+name + value)
            name = name.strip(":")
            value = value.upper() if name.endswith("MD5") or name.endswith("SHA1") else value    ##### MD5 SHA1  大写
            if name in __wantedArrt:   #####添加欲获取的属性值
                worksheet.write(index, __wantedArrt.index(name), value)   ##这里算是搞定了
        print()
        ###读取首页的签名信息
        try:
            ##### 盘古的扫描的应用，有的应用居然没有签名信息
            await targeAppPage.waitForXPath('.//div[ @ id = "apk_base_info"] / div[2] / div[2] / table',
                                                       visible=True, timeout=5*1000)
            signInfo = await targeAppPage.xpath('.//div[ @ id = "apk_base_info"] / div[2] / div[2] / table / tbody / tr')
            print(r"  应用签名信息为：")
            for i in range(0, len(signInfo)):
                infoEle = await signInfo[i].xpath('.//td')
                name = await targeAppPage.evaluate('(element) => element.textContent', infoEle[0])
                value = await targeAppPage.evaluate('(element) => element.textContent', infoEle[1])
                value = value.strip()
                name = "签名MD5" if name.find("MD5") != -1 else name      ###用find要适用性强点
                name = "签名SHA1" if name.find("SHA1") != -1 else name
                name = "签名" if name.find("subjectName") != -1 else name
                value = value.upper() if name.endswith("MD5") or name.endswith("SHA1") else value
                print("\t" + name.strip() + ":" + value)
                if name in __wantedArrt:        #####添加欲获取的属性值
                    worksheet.write(index, __wantedArrt.index(name), value)
        except:
            print("当前应用未获取到签名信息")
            worksheet.write(index, 9, "未获取到")
            worksheet.write(index, 10, "未获取到")
            worksheet.write(index, 11, "未获取到")
            worksheet.write(index, 15, targeAppPage.url)    ### 未获取到的时候，把当前页面url 添加到备注栏
        finally:
            worksheet.write(index, 6, time.strftime('%Y-%m-%d %H:%M:%S'))   ###添加我们的主动扫扫描时间
            print()

       ###点击背景信息，准备读取下载链接和运营商店url
        await targeAppPage.waitForXPath('.//span[@class="padd-lr-3"]', visible=True)
        backInfoBtn = await targeAppPage.xpath('.//span[@class="padd-lr-3"]/i')
        await backInfoBtn[1].click()

        #####获取发布页面和下载链接信息
        print(r"  应用发布信息为：")
        try:
            #####当前最大等待时间为5秒，请根据网络情况更改为合适值
            await targeAppPage.waitForXPath(".//ul[@class='app-bg-ul']/li[1]/div/div", visible=True, timeout=5*1000)
            flag1 = 0
            backPageList = await targeAppPage.xpath(".//ul[@class='app-bg-ul']/li[3]/div/span")
            if len(backPageList) == 0:
                print("未获取到发布页面，或没有发布页面\n")
                worksheet.write(index, 12, "未获取到奥")
                worksheet.write(index, 13, "未获取到奥")
                worksheet.write(index, 15, targeAppPage.url) 
                flag1 += 1
            else:
                for pageUrlEle in backPageList:
                    pageUrlList = await pageUrlEle.xpath(".//a[1]")
                    pageUrlName = await targeAppPage.evaluate('(element) => element.textContent', pageUrlList[0])
                    pageUrl = await targeAppPage.evaluate('(element) => element.href', pageUrlList[0])
                    print("\t获取到的发布商店及页面为: " + pageUrlName + ": " + pageUrl)
                    worksheet.write(index+flag1, 12, pageUrlName.strip())
                    worksheet.write(index+flag1, 13, pageUrl.strip())
                    flag1 += 1

            backInfoList = await targeAppPage.xpath(".//ul[@class='app-bg-ul']/li[1]/div/div")
            flag2 = 0
            if len(backInfoList) == 0:
                print("未获取到下载链接")
                worksheet.write(index, 14, "未获取到奥")
                worksheet.write(index, 15, targeAppPage.url) 
                flag2 += 1
            else:
                for urlEle in backInfoList:
                    url = await targeAppPage.evaluate('(element) => element.textContent', urlEle)
                    print("\t获取到的下载链接为 " + url)
                    worksheet.write(index+flag2, 14, url.strip())
                    flag2 += 1
            print()
            index += flag2 if flag2 >= flag1 else flag1      ###  目前这里是，谁大听谁的
        except:
            print("当前页面没有发布信息\n")
            worksheet.write(index, 12, "未获取到")
            worksheet.write(index, 13, "未获取到")
            worksheet.write(index, 14, "未获取到")
            worksheet.write(index, 15, targeAppPage.url)    ### 未获取到的时候，把当前页面url 添加到备注栏
            index += 1

        continue

    await curPage.close()
    await targeAppPage.close()
    await browser.close()

    workbook.save("{}抓取结果.xls".format(__wanted))

asyncio.get_event_loop().run_until_complete(main())
