import subprocess
import os
import androguard.core.bytecodes.apk as apk
import androguard.core.bytecodes.axml as axl
from androguard.util import get_certificate_name_string
import hashlib
from asn1crypto import x509
from lxml import etree
from mainPcroess import rawFile

ComponentsSet = {}
targeApk = ""
def getInfo():
    global targeApk
    #### 用列表搜集需要的信息
    cell_List = []
    targeApk = apk.APK(rawFile,True)
    targeDex = targeApk.get_dex()
    apkMd5 = hashlib.md5(rawFile).hexdigest().upper()
    ##文件名称、文件MD5、DEX MD5、文件大小
    fileName = apkMd5 + ".apk"
    cell_List.append(fileName)
    cell_List.append(apkMd5)
    dexMd5 = hashlib.md5(targeDex).hexdigest().upper()
    cell_List.append(dexMd5)
    fileSize = format(os.path.getsize(f.name),',') + " 字节"
    cell_List.append(fileSize.lstrip())
    ##app名称、包名、签名（issuer）、证书串号、公钥MD5、公钥SHA1、
    apkName = targeApk.get_app_name()
    cell_List.append(apkName)
    apkPackageName = targeApk.get_package()
    cell_List.append(apkPackageName)
    apkSign  = getSign()  ###一段蹩脚的签名获取方法，后去可用keytool工具直接获取
    cell_List.append(apkSign["Issuer"])
    cell_List.append(apkSign["SerialNumber"])
    cell_List.append(apkSign["signMd5"])
    cell_List.append(apkSign["signSha1"])

    ###  操作word
    doc = Document("test.docx")
    table = doc.tables[0]
    #table.rows[1].cells[2].text = fileName    这种方式废弃
    #table.rows[2].cells[2].text = apkMd5
    #table.rows[3].cells[2].text = dexMd5


    for i in range(1, 11):
        run = table.rows[i].cells[2].paragraphs[0].add_run(cell_List[i-1])  ###或者写成  table.rows(i, 2)
        run.font.name = '仿宋_GB2312'
        run.font.size = 175000

    doc.save("test1.docx")
    ###是否结束？清理工作
    print("everything is done, exit?")
    _ = input()
    f.close()
    return



#### 获取 签名信息的部分
def getSign():
    certs = set(targeApk.get_certificates_der_v2() + [targeApk.get_certificate_der(x) for x in targeApk.get_signature_names()])
    for cert in certs:
        x509_cert = x509.Certificate.load(cert)
        Issuer = get_certificate_name_string(x509_cert.issuer.native, short=True)
        SerialNumber = hex(x509_cert.serial_number).upper().strip("0X")
        signMd5 = hashlib.md5(cert).hexdigest().upper()
        signSha1 = hashlib.sha1(cert).hexdigest().upper()
        return {"Issuer":Issuer,"SerialNumber":SerialNumber,"signMd5":signMd5,"signSha1":signSha1}

####获取 组件、权限信息
def getComponentInfo():
    with open("si.apk", "rb") as f:
        rawFile = f.read()

    if rawFile is None:
        print("打开apk文件失败")
        f.close()
        return
    global targeApk
    targeApk = apk.APK(rawFile,True)
    f.close()
    manifestXml = targeApk.get_android_manifest_xml()
    Components = ["activity","receiver","service","uses-permission"]
    global ComponentsSet
    #获取四大组件：
    for Component in Components:
        # 使用 xpath 获取组件元素列表
        ComElementList = manifestXml.xpath("//"+ Component)
        ComponentsSet[Component] = ""
        # 每个元素列表需要做一下格式优化，去掉名称空间，去掉 \t 等特殊字符：
        for ComElement in ComElementList:
            comStr = etree.tostring(ComElement, pretty_print=True, encoding="utf-8").decode("utf-8")    # byte出现了，就是带了编码的，需要 decode一下；
            comStr = comStr.replace(apk.NS_ANDROID_URI,"").replace("\t",r" ").rstrip("\n")   #把多余的回车去掉
            ComponentsSet[Component] += comStr

def getIcon():
    icon = targeApk.get_app_icon()
    icon = targeApk.get_main_activity()
    n = 3

def getRunImage():
    apkPackageName = targeApk.get_package()
    cmds = ["adb uninstall " + apkPackageName,
           "adb install "+ os.getcwd()+r"\si.apk",
           "adb shell am start " + apkPackageName + r"/"+ targeApk.get_main_activity()]

    subProcess = subprocess.Popen(r"adb devices", shell=True, stdout=subprocess.PIPE)
    subProcess.wait()
    shellRes = subProcess.stdout.readlines()[1].decode("utf-8").partition("\t")[0]
    print(shellRes)
    subProcess.kill()
    #cmd = r"adb -s "+ shellRes +" install test.apk"
    cmd = "adb install si.apk"
    subProcess = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE)
    subProcess.wait()
    shellRes = subProcess.stdout.read().decode("utf-8")
    print(shellRes)

    for cmd in cmds:
        print(cmd)
        subProcess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        subProcess.wait()
        res = subProcess.stdout.read()
        print(res)
        subProcess.kill()



if __name__ == '__main__':
    getComponentInfo()
    #getIcon()
    getRunImage()
