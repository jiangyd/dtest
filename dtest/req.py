import requests
import jmespath
from jinja2 import Template
from dtest.syslog import log
from dtest.report import report


class req():
    def __init__(self, project, module, suite, case, var, name, method, url, headers, body, validate, extract=None):
        self.project = project
        self.module = module
        self.suite = suite
        self.case = case
        self.var = var
        log.debug(self.var)
        self.name = name
        self.url = self.safe(url)
        self.method = self.safe(method)
        self.headers = self.safe(headers)
        self.body = self.safe(body)
        self.validate = validate
        self.extract = extract
        self.resp = None

    def safe(self, data):
        """
        :param data: 如果数据不是字符串就不需要渲染
        :return:
        """
        if isinstance(data, str):
            t = Template(data)
            return t.render(self.var)
        elif isinstance(data, dict):
            for k, v in data.items():
                data[k] = self.safe(v)
        elif isinstance(data, list):
            for i, v in enumerate(data):
                data[i] = self.safe(v)

        return data

    def run(self):
        try:
            resp = requests.request(method=self.method, url=self.url, headers=self.headers, data=self.body,timeout=5)
            log.debug("响应状态码:%d", resp.status_code)
            log.debug("响应json: %s", resp.json())
            self.resp = resp

            result = self.check(resp=resp, validate=self.validate)
            rep = report(project=self.project, module=self.module, suite=self.suite, case=self.case, msg=result,
                     method=self.method, url=self.url, headers=self.headers, body=self.body,
                     resp_code=resp.status_code, resp_body=resp.json(),
                     validate=self.validate)
            rep.save()
        except Exception as e:
            rep = report(project=self.project, module=self.module, suite=self.suite, case=self.case, error=str(e),
                         method=self.method, url=self.url, headers=self.headers, body=self.body,
                         validate=self.validate)
            rep.save()


    def extract_value(self):
        try:
            xx = {}
            for key, value in self.extract.items():
                xx[key] = jmespath.search(value, self.resp.json())
            return xx
        except Exception as e:
            log.error(e)
            return {}

    def check(self, resp, validate):
        for item in validate.get("status_code", []):
            left = resp.status_code
            expr = item.get("expr")
            right = self.safe(item.get("right"))
            msg = item.get("msg")
            result = self.action(left=left, expr=expr, right=right, msg=msg)
            if len(result) > 0:
                log.info(result)
                return result

        for item in validate.get("duration", []):
            left = resp.elapsed.seconds
            expr = item.get("expr")
            right = self.safe(item.get("right"))
            msg = item.get("msg")
            result = self.action(left=left, expr=expr, right=right, msg=msg)
            if len(result) > 0:
                log.info(result)
                return result

        for item in validate.get("body", []):
            left = jmespath.search(item["left"], resp.json())
            right = self.safe(item.get("right"))
            expr = item.get("expr")
            msg = self.safe(item.get("msg"))
            result = self.action(left=left, expr=expr, right=right, msg=msg)
            if len(result) > 0:
                log.info(result)
                return result
        return None

    def action(self, left=None, expr=None, right=None, msg=None):
        expr = expr.lower()
        try:
            if expr == "==":
                assert left == right, msg
            elif expr == "!=":
                assert left != right, msg
            elif expr == "<=":
                assert left <= right, msg
            elif expr == ">=":
                assert left >= right, msg
            elif expr == "<":
                assert left < right, msg
            elif expr == ">":
                assert left > right, msg
            elif expr == "in":
                assert left in right, msg
            elif expr == "not in":
                assert left not in right, msg
        except AssertionError as e:
            return str(e)
        return ""
