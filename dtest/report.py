import pymongo
from collections import defaultdict

mymongodb = pymongo.MongoClient("mongodb://172.16.5.9:27017/test")


class report(object):
    def __init__(self, project=None, module=None, suite=None, case=None, msg=None, url=None, headers=None, body=None,
                 method=None, validate=None, resp_code=None, resp_body=None,error=None):
        self.url = url
        self.headers = headers
        self.body = body
        self.method = method
        self.project = project
        self.result = True if msg is None else False
        self.module = module
        self.suite = suite
        self.case = case
        self.msg = msg
        self.validate = validate
        self.resp_code = resp_code
        self.resp_body = resp_body
        self.error=error

    def save(self):
        data = lambda: defaultdict(data)
        result_data = data()
        result_data["request"]["url"] = self.url
        result_data["assert"]["validate"] = self.validate
        result_data["assert"]["msg"] = self.msg
        result_data["request"]["headers"] = self.headers
        result_data["request"]["method"] = self.method
        result_data["request"]["body"] = self.body

        result_data["response"]["body"] = self.resp_body
        result_data["response"]["status_code"] = self.resp_code

        result_data["project"] = self.project
        result_data["module"] = self.module
        result_data["suite"] = self.suite
        result_data["case"] = self.case
        result_data["error"]=self.error


        mymongodb.list_database_names()
        db = mymongodb["jiangyd"]
        post = db.cccc
        print(post.insert_one(result_data).inserted_id)


if __name__ == "__main__":
    t = report(project="test", module="sc", suite="b", case="test", msg="ttt")
    t.save()
