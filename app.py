from flask import Flask, render_template, request, session, redirect, jsonify, Response
from utils.db import db
from flask_cors import CORS
from utils.jiami import encrypt,decrypt
from cozepy import Coze, TokenAuth, Message, ChatEventType  # 导入 cozepy 库
from cozepy import COZE_CN_BASE_URL
coze_api_token = 'pat_C3kKuLu6qD65lFYNdUbcPdpVglB7JCF30WNN8VDvW4ayEEaDNp6A1oOcU4ta0oTO'
coze_api_base = COZE_CN_BASE_URL
bot_id = '7569206391563993130'

# 初始化Coze客户端
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
import json
app = Flask(__name__)
app.secret_key = 'abc'
originsOpenTo = [
                "https://damingbai.jeffisalone.site", 
                "http://47.93.254.56"
            ]
CORS(
    app,
    resources={
        r"/coze": {  
            "origins": originsOpenTo,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],  
            "max_age": 86400, 
            "supports_credentials": False 
        },
        r"/ciyun": {
            "origins": "*",  
            "methods": ["GET", "POST", "OPTIONS"],  
            "allow_headers": ["Content-Type", "Authorization"], 
            "max_age": 86400
        }
        
    },
    intercept_exceptions=True  
)
@app.route('/test')
def test():
    return '200'
@app.route('/')
def all():
    return 'Working'
# @app.route('/success')
# def success():
#     user_info = session.get("user_info")
#     if not user_info:
#         return redirect('/login')
#     print(user_info)
#     return render_template('success.html',username='你好,'+user_info['user'])

# @app.route('/reg',methods=['GET','POST'])
# def reg():
#     if request.method == 'GET':
#         return render_template('reg.html')
#     username = request.form.get('username')
#     pwd = request.form.get('pwd')
#     age = request.form.get('age')
#     print(username,pwd,age)
#     reg_db = db()
#     reg_db.fetch_one(f'select * from jtapp_userinfo where name = "{username}"')
#     if not reg_db.data:
#         reg_db.run(f'insert into jtapp_userinfo(name,password,age) values("{username}","{pwd}","{age}")')
#         return redirect('login')
#     return render_template('reg.html',alert='用户已存在')

# @app.route('/login',methods=['POST'])
# def home():
#     if request.method == 'GET':
#         from datetime import datetime
#         time = datetime.now()
#         return render_template('login.html', nowtime=time)
#     user = request.get_json().get('mobile')
#     pwd = request.get_json().get('pwd')

#     print(user,pwd)
#     from datetime import datetime
#     time = datetime.now()
#     if user and pwd:
#         login_conn = db()
#         login_conn.fetch_one(f'select id from jtapp_userinfo where name = "{user}" and password = "{pwd}"')
#         if login_conn.data:
#             session['user_info'] = {'user':user,'id':login_conn.data[0]}
#             print(login_conn.data)
#             print('登录成功')
#             enc = encrypt('jljt',session['user_info'])
#             # 解密测试
#             print(enc)
#             denc = decrypt('jljt',enc)
#             print(denc)
#             return ({
#                 'resp_code':200,
#                 'user':user,
#                 'session':enc
#             })

#         print(login_conn.data)
#     return ('用户名或密码错误')

@app.route('/coze', methods=['POST'])
def coze_stream():
    try:
        # 获取前端发送的prompt
        data = request.get_json()
        if not data or 'prompt' not in data:
            # 返回错误信息
            error_response = json.dumps({'type': 'error', 'content': '缺少必要的prompt参数'})
            return Response(error_response, mimetype='application/json', status=400)
        
        prompt = data['prompt']
        print(f'接收到请求: {prompt}')
        
        # 生成唯一用户ID
        import uuid
        user_id = str(uuid.uuid4())
        
        # 定义生成器函数，用于流式返回数据
        def generate():
            token_count = 0
            try:
                # 调用Coze流式API
                for event in coze.chat.stream(
                    bot_id=bot_id,
                    user_id=user_id,
                    additional_messages=[
                        Message.build_user_question_text(prompt),
                    ],
                ):
                    # 处理增量响应
                    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                        chunk = {
                            'type': 'delta',
                            'content': event.message.content
                        }
                        yield json.dumps(chunk) + '\n'
                        # 立即发送数据
                        
                    # 处理完成事件
                    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                        token_count = event.chat.usage.token_count if event.chat.usage else 0
                        completed_chunk = {
                            'type': 'completed',
                            'token_usage': token_count
                        }
                        yield json.dumps(completed_chunk) + '\n'
                        break
                        
            except Exception as e:
                # 处理异常
                error_chunk = {
                    'type': 'error',
                    'content': f'Coze API调用失败: {str(e)}'
                }
                yield json.dumps(error_chunk) + '\n'
        
        # 返回流式响应
        return Response(generate(), content_type='text/plain')
        
    except Exception as e:
        # 捕获其他错误
        error_response = json.dumps({
            'type': 'error', 
            'content': f'服务器错误: {str(e)}'
        })
        return Response(error_response, mimetype='application/json', status=500)
@app.route('/ciyun',methods=['GET','POST'])
def ciyun():
    if request.method == 'GET':
        import pymysql
        conn = pymysql.connect(host='mysql2.sqlpub.com', port=3307, user='ak0nday', passwd='kqImiJJRu4r5v6Ko',
                               db='shadow')
        cursor = conn.cursor()
        cursor.execute('select word,value from ciyun')
        data = []
        while True:
            row = cursor.fetchone()
            if not row:
                break
            data.append({'word': row[0], 'value': row[1]})
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM ciyun WHERE date < DATE_SUB(CURDATE(), INTERVAL 14 DAY);")
        conn.commit()
        cursor.close()
        conn.close()
        return data
    resp = request.get_json()
    word = resp.get('word')
    if not word:
        return jsonify({"error": "请求体中缺少 'word' 字段或字段值为空"}), 400
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    import pymysql
    conn = pymysql.connect(host='mysql2.sqlpub.com', port=3307, user='ak0nday', passwd='kqImiJJRu4r5v6Ko',
                           db='shadow')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO ciyun VALUE('{word}',0,'{current_date}')")
    conn.commit()
    cursor.close()
    conn.close()
    return '200'

# 跨域中间件



if __name__ == '__main__':
    # 确保所有必要的环境变量已设置
    
    print("[INFO] Flask 服务启动中...")
    print(f"[INFO] 服务地址: 0.0.0.0")
    print(f"[INFO] 服务域: workspace.jeffisalone.site")
    print(f"[INFO] API端点: /coze (POST)")
    print(f"[/coze ===> Origins] {originsOpenTo}")
    print(f"[INFO] 健康检查端点: /test (GET)")
    
    # 启动 Flask 服务器，启用 CORS 和调试模式
    app.run()
