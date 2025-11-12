import base64
import json


# 1. 加密：字典 → JSON字符串 → 异或 → base64编码
def encrypt(key: str, data: dict) -> str:
    # 字典转JSON字符串
    json_str = json.dumps(data, ensure_ascii=False)  # 确保中文等特殊字符正确处理
    # 异或运算
    xor_bytes = bytes([ord(c) ^ ord(key[i % len(key)]) for i, c in enumerate(json_str)])
    # base64编码（转为字符串，方便传输）
    return base64.b64encode(xor_bytes).decode()


# 2. 解密：base64字符串 → base64解码 → 异或 → JSON字符串 → 字典
def decrypt(key: str, encrypted_str: str) -> dict:
    try:
        # base64解码（得到异或后的bytes）
        xor_bytes = base64.b64decode(encrypted_str)
        # 异或运算（还原原始JSON字符串）
        json_str = ''.join([chr(b ^ ord(key[i % len(key)])) for i, b in enumerate(xor_bytes)])
        # JSON字符串转字典
        return json.loads(json_str)
    except Exception as e:
        print(f"解密失败：{e}，加密字符串：{encrypted_str}，解密后字符串：{json_str if 'json_str' in locals() else '无'}")
        raise  # 抛出异常，方便调试


# 测试函数是否正常工作（先在本地测试，再集成到Flask）
if __name__ == "__main__":
    key = "jljt"
    test_data = {"user": "test_user", "id": 123, "pwd": "123456"}  # 模拟session['user_info']

    # 本地测试加密解密
    encrypted = encrypt(key, test_data)
    print("加密后：", encrypted)  # 例如：bWk4Nzo4OXg5OQ==（实际值因数据而异）

    decrypted = decrypt(key, encrypted)
    print("解密后：", decrypted)  # 应输出与 test_data 完全一致的字典