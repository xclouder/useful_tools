import argparse
import subprocess

blackList = [
'/Assets/Scripts/Systems/DollInGame/',
'/Assets/Scripts/Systems/EntitySys/',
'/Assets/Scripts/Framework/Event/DollEventDefine',
'/Assets/Scripts/Framework/GameRoot/GameRootCfg/',
'/Assets/Scripts/Framework/GameRoot/GameSystemConfig',
'/Assets/Scripts/UICtrl/DollUI/'
]

def is_in_blacklist(line):
    for b in blackList:
        if (line.find(b) >= 0):
            return True

    return False


def get_version_list(rawVersionList):
    lst = []

    for versionStr in rawVersionList:
        if (versionStr.find('-') != -1):
            splited = versionStr.split('-')
            assert len(splited) == 2, "invalid version with '-'"

            fromVer = int(splited[0])
            toVer = int(splited[1])

            for v in range(fromVer, toVer + 1):
                lst.append(v)
        else:
            lst.append(int(versionStr))

    return lst

'''
svn diff的结果会是这个样子：
M       http://tc-svn.tencent.com/wepop/wepop_client_proj/trunk/WePop/Assets/Scripts/Framework/Event/DollEventDefine.cs

svn diff:296026
D       http://tc-svn.tencent.com/wepop/wepop_client_proj/trunk/WePop/Assets/Scripts/Systems/DollInGame/DollSkillSystem/Buffs/SpeedBuff.cs
D       http://tc-svn.tencent.com/wepop/wepop_client_proj/trunk/WePop/Assets/Scripts/Systems/DollInGame/DollSkillSystem/Buffs/SpeedBuff.cs.meta

此函数从svn diff结果里找出具体文件，过滤掉‘D’,‘M’空格等

输出:
/Assets/Scripts/Framework/Event/DollEventDefine.cs
/Assets/Scripts/Systems/DollInGame/DollSkillSystem/Buffs/SpeedBuff.cs
/Assets/Scripts/Systems/DollInGame/DollSkillSystem/Buffs/SpeedBuff.cs.meta
'''
def get_files_from_output(output, url):
    strList = output.splitlines()

    ls = []
    urlLen = len(url)
    for s in strList:
        index = s.find(url)
        
        if (index >= 0):
            ls.append(s[index + urlLen:])
        else:
            ls.append(s)

    return ls
        


'''
获得svn描述的版本号的开始和结束版本，方便diff
比如:
3566版本，得到3566和3565
'''
def get_diff_versions(ver):
    return ver, ver - 1

def make_diff_url(projUrl, newver, oldver):
    return "svn diff --summarize {0}@{1} {0}@{2}".format(projUrl, newver, oldver)


def run_cmd(cmdStr):
    ret = subprocess.run(cmdStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout = 10)
    if (ret.returncode == 0):
        return True, ret.stdout
    else:
        return False, ret.stderr

    # p = subprocess.Popen(cmdStr, stdout=subprocess.PIPE, shell=True)
    # (output, err) = p.communicate()

    # if (err != None):
    #     return False, err.decode('utf-8')
    # else:
    #     outputStr = output.decode('utf-8')
    #     return True, outputStr

def is_files_need_merge(files):
    
    for line in files:
        if (len(line) > 0):
            isInBlackList = is_in_blacklist(line)
                
            if (not isInBlackList):
                print (line)
                print ("isInBlackList:" + str(isInBlackList))

                return True

    return False

def main():
    
    url = "http://tc-svn.tencent.com/wepop/wepop_client_proj/trunk/WePop"
    parser = argparse.ArgumentParser(description='do some filter work')
    parser.add_argument('versionFile', help='the versions.txt')
    
    args = parser.parse_args()
    print("url:")
    print(url)
    print("versions:")
    print(args)

    # version list
    originVersionArr = []
    with open(args.versionFile, mode = 'r') as f:

        versionsStr = f.read()
        originVersionArr = versionsStr.split(',')

    # get versions to diff
    versionArr = get_version_list(originVersionArr)


    resultDict = {}

    # do diff work
    for ver in versionArr:
        ver1, ver2 = get_diff_versions(ver)
        # print(ver + "," + str(ver1) + "," + str(ver2))
        #print (make_diff_url(url, ver1, ver2))
        print ("svn diff:" + str(ver))
        svnDiffCmd = make_diff_url(url, ver1, ver2)
        succ, output = run_cmd(svnDiffCmd)


        if (succ):
            #print (output)
            files = get_files_from_output (output, url)
            if (is_files_need_merge(files)):
                resultDict[ver] = files

        else:
            error(output)

    
    #print result
    finalVersions = []
    for ver in resultDict:
        finalVersions.append(str(ver))

    if (len(finalVersions) > 0):
        finalVerStr = ','.join(finalVersions)
        print (finalVerStr)    
    else:
        print ("no version need to merge")
    
    
    # result = []




    # print result
    # for r in result:
    #     print(r.strip())


if __name__ == "__main__":
    main()