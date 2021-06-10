import yaml
import os
from dtest import req
from dtest.syslog import log
from types import FunctionType
from dtest import function
from copy import deepcopy
from jinja2 import Template
import asyncio

mapf = {}

for k, v in vars(function).items():
    if isinstance(v, FunctionType):
        mapf[k] = v


class parseSuite(object):
    def __init__(self, project=None):
        self.project = project
        self.mapf = mapf
        self.suite_mapf = deepcopy(mapf)

    def safe(self, data):
        """
        :param data: 如果数据不是字符串就不需要渲染
        :return:
        """
        if isinstance(data, str):
            t = Template(data)
            return t.render(self.suite_mapf)
        return data

    async def runTest(self,test_file):
        with open(test_file, "r") as f:
            scene_yaml = yaml.safe_load(f)

                # 遍历场景
        for s in scene_yaml.get("suites"):
            log.debug(f"start test suite: {s}")
            for k, v in scene_yaml.get("var").items():
                self.suite_mapf[k] = self.safe(v)
            self.suites(project=self.project, suite=s, module=scene_yaml.get("module", None))
                    # suites(s, var=deepcopy(var))

    def suites(self, project=None, module=None, suite=None):
        # 遍历场景下的测试
        for c in suite.get("case_files"):
            log.debug("start test step: {c}")
            if c.get("parameters", None):
                parameters = self.parameters(**c.get("parameters"))
                c["parameters"] = parameters
            self.case_file(project=project, module=module, suite=suite.get("title"), case=c, extract=c.get("extract"))

    def parameters(self, **kwargs):
        """
        接受一个字典,如果key的value是列表，那么就以最大长度列表做遍历
        其它list获取不到值就返回None
        字符串类型，数字，bool 返回同一个值
        :param kwargs:
        :return:
        """
        value_len = []
        result = []
        for k, v in kwargs.items():
            if isinstance(v, list):
                value_len.append(len(v))
        value_len.sort()

        for i in range(value_len[-1]):
            data = {}
            for k, v in kwargs.items():
                if isinstance(v, list):
                    try:
                        data[k] = v[i]
                    except IndexError as e:
                        data[k] = None
                else:
                    data[k] = v
            result.append(data)
        return result

    def case_file(self, case=None, extract=None, project=None, module=None, suite=None):
        # 读取单个case yaml文件

        path = case.get("path")
        file = os.path.join(os.path.abspath(os.path.dirname(path)), os.path.basename(path))
        with open(file, "r") as f:
            caseyaml = yaml.safe_load(f)

        for c in caseyaml["api"]:
            self.case_mapf = deepcopy(self.suite_mapf)
            for k, v in caseyaml.get("var").items():
                self.case_mapf[k] = self.safe(v)

            newvar = deepcopy(self.case_mapf)
            if case.get("parameters", None):
                for parms in case.get("parameters"):
                    for k, v in parms.items():
                        newvar[k] = self.safe(v)
                    r = req.req(project=project,
                                module=module,
                                suite=suite,
                                case=case.get("desc"),
                                name=c["test"]["name"],
                                method=c["test"]["request"]["method"],
                                url=c["test"]["request"]["url"],
                                headers=c["test"]["request"]["headers"],
                                body=c["test"]["request"]["body"],
                                validate=c["test"]["request"]["validate"],
                                var=newvar,
                                extract=extract)
                    r.run()
                    for k, v in r.extract_value().items():
                        self.suite_mapf[k] = v
                    self.case_mapf = None

            else:
                r = req.req(project=project,
                            module=module,
                            suite=suite,
                            case=case.get("desc"),
                            name=c["test"]["name"],
                            method=c["test"]["request"]["method"],
                            url=c["test"]["request"]["url"],
                            headers=c["test"]["request"]["headers"],
                            body=c["test"]["request"]["body"],
                            validate=c["test"]["request"]["validate"],
                            var=newvar,
                            extract=extract)
                r.run()
                for k, v in r.extract_value().items():
                    self.suite_mapf[k] = v
                self.case_mapf = None
