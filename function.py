from mako.template import Template
from dtest.syslog import log
import json
import traceback
import random
import string

def selectParameters(**kwargs):
    """组合参数"""
    value_len = []
    params_list = []
    for k in kwargs.keys():
        value_len.append(len(kwargs[k]))
    value_len.sort()
    for v in range(value_len[0]):
        once = {}
        for k in kwargs.keys():
            if isinstance(kwargs[k], list):
                once[k] = kwargs[k][v]
        params_list.append(once)
    return params_list




def getParame(step=None, globalvar=None):
    parame = {}
    for k in step.get("parameters"):
        if isinstance(step.get("parameters")[k], str):
            t = Template(step.get("parameters")[k]).render(**globalvar)
            try:
                t = json.loads(t)
            except Exception as e:
                traceback.format_exc(e)
            if isinstance(t, dict):
                for i in k.split(","):
                    parame[i] = t[i]
            elif isinstance(t, str):
                parame[k] = t
            elif isinstance(t, list):
                parame[k] = t
        else:
            parame[k] = step.get("parameters")[k]
    return parame

def getRandStr(str_len):
    """ generate random string with specified length
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )