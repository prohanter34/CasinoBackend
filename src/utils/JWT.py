import base64
import hashlib
import json
import hmac
import time
from datetime import datetime, timedelta



def obj_to_base64(obj):
    obj_json = json.dumps(obj)
    obj_base64 = base64.b64encode(obj_json.encode())
    return obj_base64


def base64_to_json_obj(base_str):
    base_bytes = bytes(base_str, encoding="utf8")
    bytes_str = base64.b64decode(base_bytes)
    string = bytes_str.decode()
    json_obj = json.load(string)
    return json_obj


class JWTFabric:

    def __init__(self, secret: str):
        self.secret = secret

    def generate_token(self, id, login, time_delta):
        current_time = time.mktime(datetime.now().timetuple())
        death_time = current_time + timedelta(minutes=time_delta).total_seconds()
        payload = {
            "login": login,
            "id": id
        }
        payload_base64 = obj_to_base64(payload)
        header = {
            "alg": "sha256",
            "time": death_time
        }
        header_base64 = obj_to_base64(header)
        unsigned_token = str(header_base64)[2:-1] + "." + str(payload_base64)[2:-1]
        unsigned_token_bytes = str.encode(unsigned_token, encoding="utf-8")
        secret_bytes = str.encode(self.secret, encoding="utf-8")
        hashcode = hmac.new(key=secret_bytes, msg=unsigned_token_bytes, digestmod=hashlib.sha256).digest()
        hashcode_base64 = base64.b64encode(hashcode)
        signed_token = unsigned_token + "." + str(hashcode_base64)
        return signed_token

    def check_token(self, token: str):
        list = token.split(".")
        header = list[0]
        header_json = base64_to_json_obj(header)
        payload = list[1]
        payload_json = base64_to_json_obj(payload)
        signature = list[2]
        unsigned_token = header + "." + payload
        unsigned_token_bytes = str.encode(unsigned_token, encoding="utf-8")
        secret_bytes = str.encode(self.secret, encoding="utf-8")
        hashcode = hmac.new(key=secret_bytes, msg=unsigned_token_bytes, digestmod=hashlib.sha256).digest()
        hashcode_base64 = str(base64.b64encode(hashcode))
        jtw_token = JWTToken(header_json, payload_json, signature, hashcode_base64)
        return jtw_token


class JWTToken:

    def __init__(self, header, payload, signature, check_signature):
        self.header = header
        self.payload = payload
        self.signature = signature
        self.check_signature = check_signature
