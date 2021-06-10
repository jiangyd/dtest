# coding=utf-8
import os



def loadSuiteFiles(path, start="test_", end=".yaml"):
    """加载用例文件"""
    f = []
    if os.path.exists(path):
        print(path)
        if os.path.isfile(path) and os.path.basename(path).startswith(start) and os.path.basename(path).endswith(end):
            f.append(path)
            return f

        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for i in files:
                    if i.startswith(start) and i.endswith(end):
                        f.append(os.path.join(root, i))
    else:
        raise FileNotFoundError(path)
    f.sort()
    return f



