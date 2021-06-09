# coding=utf-8
import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dtest.suite import parseSuite
from dtest.util import loadSuiteFiles
from dtest.syslog import log

testcase = [
    {"project": "csos", "path": "/Users/jiangyd/PycharmProjects/untitled15/dtest"},
]


async def main():
    for item in testcase:
        if isinstance(item, dict):
            project = item.get("project")
            path = item.get("path")
        # 以什么开头查找
            start = item.get("start", "test_")

            casepath = os.path.abspath(os.path.join(path))
            suite = loadSuiteFiles(path=casepath, start=start)

            log.info("查找到的scenes: {0}".format(suite))
            if len(suite) > 0:
                log.info("process is starting")
                t = parseSuite(project=project)
                for i in suite:
                    log.debug(f"start test file: {i}")
                    v= asyncio.create_task(t.runTest(test_file=i))
                    await v

asyncio.run(main())