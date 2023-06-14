import datetime
import os
import pymysql
from django.shortcuts import render, redirect

db = pymysql.connect(host='localhost',
                     user='root',
                     password='wue789789',
                     database='cgdms')


# 功能函数，获得所有留言
def get_comment_list():
    # 从留言表中获取所有留言
    cursor = db.cursor()
    cursor.execute("SELECT * FROM MESSAGE ORDER BY UTIME DESC;")
    # 构造留言表
    comment_list = []
    maximum = 5
    if cursor.rowcount < 5:
        maximum = cursor.rowcount
    for num in range(maximum):
        comment = cursor.fetchone()
        comment_time = comment[2].strftime("%Y-%m-%d %H:%M:%S")
        comment_dict = {
            "user": comment[0],
            "role": comment[1],
            "time": comment_time,
            "content": comment[3],
        }
        comment_list.append(comment_dict)
    return comment_list


# 通用模块
# 登录页面，网站的初始页面
def login_page(request):
    """
    登录页面，网站的初始页面
    :param request:HTTP请求
    :return render:渲染登录页面
    """
    message_list = get_comment_list()
    return render(request, "login_page.html", {"message_list": message_list})


# 登录功能，验证用户名和密码，并把用户信息存入session
def login(request):
    """
    登录功能，验证用户名和密码，并把用户信息存入session
    :param request: HTTP请求
    :return redirect:重定向至主页
    """
    # 从POST表单中获取账号密码
    uno = request.POST['uno']
    upwd = request.POST['upwd']
    # 从数据库中验证用户名和密码
    cursor = db.cursor()
    cursor.execute("CALL GET_USER('" + uno + "','" + upwd + "');");
    # 如果查询到结果
    if cursor.rowcount == 1:
        # 获取个人信息
        self_info = cursor.fetchone()
        # 将个人信息存入session
        request.session['uno'] = uno
        request.session['role'] = self_info[0]
        request.session['no'] = self_info[1]
        request.session['name'] = self_info[2]
        request.session.set_expiry(0)
        # 重定向到主页
        return redirect('/index/')
    # 如果查询不到结果,则说明用户名或密码错误
    else:
        # 返回页面，并提示错误信息
        return render(request, "announce.html",
                      {'message': '登录失败！请检查您的用户名和密码。'
                          , 'name': '用户'})


# 注册功能
def register(request):
    """
    注册功能，将注册信息存入数据库
    :param request: HTTP请求
    :return redirect: 重定向至登录页面
    """
    # 从POST表单中获取注册信息
    uno = request.POST['uno']
    upwd = request.POST['upwd']
    user_role = request.POST['role']
    # 获取个人信息
    no = request.POST['no']
    name = request.POST['name']
    gender = request.POST['gender']
    birth = request.POST['birth']
    fname = request.POST['faculty']
    mname = request.POST['major']
    # 获得当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 将注册信息存入数据库
    cursor = db.cursor()
    cursor.execute("INSERT INTO USER VALUES ('" + uno + "','" + upwd + "','" + user_role + "','" + now + "');")
    # 检查用户身份，依身份不同，将个人信息存入不同的表中
    if user_role == '学生':
        # 获取班级信息
        cno = request.POST['last']
        # 将学生信息存入数据库
        cursor.execute("INSERT INTO STUDENT VALUES ('" + no + "','" + name
                       + "','" + gender + "','" + birth + "','" + fname + "','" +
                       mname + "','" + cno + "','" + uno + "');")
    else:
        # 获取职称信息
        title = request.POST['last']
        # 将教师信息存入数据库
        cursor.execute("INSERT INTO TEACHER VALUES ('" + no + "','" + name +
                       "','" + gender + "','" + birth + "','" + fname + "','" +
                       mname + "','" + title + "','" + uno + "');")
        # 将教师权限信息存入数据库
        cursor.execute("INSERT INTO ROLE VALUES ('" + no + "','是','是','是','是','是');")
    # 提交数据库操作
    db.commit()
    # 重定向至登录页面
    return redirect('/')


# 退出登录功能，清除session
def logout(request):
    """
    退出登录功能，清除session，并重定向至登录页面
    :param request: HTTP请求
    :return redirect: 重定向至登录界面
    """
    request.session.flush()
    return redirect('/')


# 主页
def index(request):
    """
    主页，显示登录用户的个人信息
    :param request: HTTP请求
    :return render: 渲染主页
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('/')
    # 获取session中的用户信息, 构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'no': request.session['no'],
        'name': request.session['name'],
        'comment_list': get_comment_list()
    }
    # 渲染主页
    return render(request, "index.html", info_dict)


# 个人信息页面
def showinfo(request):
    """
    个人信息页面，显示登录用户的个人信息
    :param request: HTTP请求
    :return render: 渲染个人信息页面
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息, 构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'no': request.session['no'],
        'name': request.session['name'],
        'comment_list': get_comment_list()
    }
    # 获取表中的个人信息
    cursor = db.cursor()
    if request.session['role'] == '教师':
        # 从教师表中获取个人信息
        cursor.execute("SELECT * FROM TEACHER WHERE Uno = '" + info_dict['uno'] + "';")
        no, name, gender, birth, fname, mname, title, username = cursor.fetchone()
        # 构造个人信息字典
        self_info = {
            "gender": gender,
            "birth": birth,
            "fname": fname,
            "mname": mname,
            "title": title,
        }
    else:
        # 从学生表中获取个人信息
        cursor.execute("SELECT * FROM STUDENT WHERE UNO = '" + request.session['uno'] + "';")
        no, name, gender, birth, fname, mname, cname, username = cursor.fetchone()
        # 构造个人信息字典
        self_info = {
            "gender": gender,
            "birth": birth,
            "fname": fname,
            "mname": mname,
            "cname": cname
        }
    # 将个人信息添加到信息字典中
    info_dict.update(self_info)
    # 渲染个人信息页面
    return render(request, "show_info.html", info_dict)


# 账户信息页面
def account(request):
    """
    账户信息页面，显示登录用户的账户信息
    :param request: HTTP请求
    :return render: 渲染账户信息页面
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 获取账户的注册时间
    cursor = db.cursor()
    cursor.execute("SELECT Utime FROM USER WHERE UNO = '" + request.session['uno'] + "';")
    info_dict['time'] = cursor.fetchone()[0].strftime("%Y-%m-%d %H:%M:%S")
    # 渲染账户信息页面
    return render(request, "account.html", info_dict)


# 修改密码功能
def change_password(request):
    """
    修改密码功能，修改登录用户的密码
    :param request: HTTP请求
    :return render: 渲染通知页面
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 检查两次输入的密码是否一致
    if request.POST['new_password'] != request.POST['new_password_confirm']:
        return render(request, "announce.html", {'message': '修改失败！两次输入的密码不一致。'})
    # 检查当前密码是否正确
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM user WHERE Uno = '" + request.POST['uno'] + "' AND Upassword = '" + request.POST[
            'current_password'] + "';")
    if cursor.rowcount == 1:
        # 如果正确，则修改密码
        cursor.execute(
            "UPDATE user SET Upassword = '" + request.POST['new_password'] + "' WHERE Uno = '" + request.POST[
                'uno'] + "';")
        db.commit()
        return render(request, "announce.html", {'message': '修改成功！', 'name': info_dict["name"]})
    else:
        # 如果不正确，则返回错误信息
        return render(request, "announce.html",
                      {'message': '修改失败！请检查您的用户名和密码。', 'name': info_dict["name"]})


# 评论功能
def comment(request):
    # 从session中获取用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取评论信息
    comment = request.POST['comment']
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 将数据插入到评论表中
    cursor = db.cursor()
    cursor.execute("INSERT INTO MESSAGE VALUES ('" + info_dict['uno'] + "', '" +
                   info_dict['role'] + "', '" + now + "', '" + comment + "');")
    db.commit()
    # 重定向至用户访问的上一个页面
    return redirect(request.META['HTTP_REFERER'])


# 学生模块
# 学生主页
def student(request):
    """
    学生中心主页
    :param request: HTTP请求
    :return render: 渲染学生主页
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 检查用户的身份
    if info_dict["role"] == "学生":
        # 如果是学生，则渲染学生主页
        return render(request, "student/student_index.html", info_dict)
    else:
        # 如果不是学生，则返回错误信息
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})


# 选题页面
def project_selection(request):
    """
    选题页面，显示所有的选题信息，学生可以在这里查看所有的已发布选题及自己的选题情况，
    或选择自己感兴趣的选题，选择成功后，选题信息会被添加到学生的选题表中
    :param request: HTTP请求
    :return render: 渲染选题页面
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 初始化已发布课题列表、学生已预选课题列表、学生已选课题名称列表
    project_list = []
    pre_select_list = []
    pre_select_names = []
    # 获取选题表中的项目，检查该学生的选题是否已被老师确认
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果选题表中有记录，说明该学生的选题已被确认
    if cursor.rowcount == 1:
        # 获取项目名称
        pname = cursor.fetchone()[1]
        # 获取项目及老师信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PROJECT_TEACHER WHERE Pname = '" + pname + "'")
        info = cursor.fetchone()
        # 构造项目字典
        project = {
            "name": info[0],
            "type": info[1],
            "supervisor": info[2],
        }
        # 更新信息字典，将学生选题情况selected设为True，选题名称selected_project设为该项目
        info_dict["selected"] = True
        info_dict["selected_project"] = project
    else:
        # 如果选题表中无记录，则说明该同学的选题未被老师确认
        # 从预选表中获取自己选择的所有课题
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Pre_Select WHERE SNO = '" + info_dict["no"] + "'")
        for num in range(cursor.rowcount):
            # 获选预选信息
            pre_select_project = cursor.fetchone()
            # 从预选信息中获取项目名称
            pname = pre_select_project[1]
            # 获取项目及老师信息
            cursor.execute("SELECT * FROM PROJECT_TEACHER WHERE Pname = '" + pname + "'")
            info = cursor.fetchone()
            # 构造项目字典
            project = {
                "name": info[0],
                "type": info[1],
                "supervisor": info[2],
            }
            # 将被自己选择的课题加入列表
            pre_select_names.append(pname)
            pre_select_list.append(project)
        # 更新信息字典
        info_dict.update({"pre_select_list": pre_select_list})
        info_dict.update({"selected": False})
    # 获取所有已发布的项目
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PUBLISHED_PROJECT")
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        # 从预选表中该课题的预选次数
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Pre_Select WHERE Pname = '" + project_info[0] + "';")
        selected_times = cursor1.rowcount
        # 构造课题字典
        project = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": project_info[2],
            "selected_times": selected_times
        }
        # 如果该课题已被自己选择，则将selected属性设置为True
        if project_info[0] in pre_select_names:
            project["selected"] = True
        else:
            project["selected"] = False
        project_list.append(project)
    # 将已发布课题列表加入信息字典
    info_dict.update({"project_list": project_list})
    # 渲染选题页面
    return render(request, "student/project_selection.html", info_dict)


# 预选功能
def select_project(request):
    """
    实现预选功能，当学生预选题目时，检查学生是否已经预选了3个课题，
    如果没有，则将课题加入预选表中，并重定向至选题页面
    :param request: HTTP请求
    :return: redirect: 重定向至选题页面
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 查询学生的预选课题数量
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Pre_Select WHERE SNO = '" + info_dict["no"] + "'")
    # 如果预选课题数量已达到3个，则返回错误信息
    if cursor.rowcount == 3:
        return render(request, "announce.html", {'message': '您已选满三个预选项目！', 'name': info_dict["name"]})
    # 获取课题名称
    project_name = request.POST["project_name"]
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 否则，将该课题加入预选表
    cursor.execute("INSERT INTO Pre_Select VALUES ('" + info_dict["no"] + "','"
                   + project_name + "'," + "NULL" + ",'" + now + "');")
    # 提交事务
    db.commit()
    # 重定向到选题页面
    return redirect("/student/project_selection")


# 取消预选
def cancel_select(request):
    """
    实现取消预选功能，当学生取消预选时，将该课题从预选表中删除
    :param request: HTTP请求
    :return redirect: 重定向至选题界面
    """
    # 如果未登录，则重定向至登录界面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    self_info = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no']
    }
    # 获取POST表单中的课题名称
    pname = request.POST["project_name"]
    # 从预选表中删除该课题
    cursor = db.cursor()
    cursor.execute("DELETE FROM Pre_Select WHERE SNO = '" + self_info["no"] +
                   "' AND PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至选题界面
    return redirect("/student/project_selection")


# 功能函数，实现提交时附件的写入功能
def write_attachment(attachment, path):
    if attachment is not None:
        if not os.path.exists(path):
            os.makedirs(path)
            path = os.path.join(path, attachment.name)
            file = open(path, "wb")
            for chunk in attachment.chunks():
                file.write(chunk)
            file.close()

# 功能函数，实现课题所处阶段的检查功能，用于判断相关操作是否可进行
def check_status(status, stage):
    """
    实现课题所处阶段的检查功能，用于判断相关操作是否可进行
    :param status: 字符串，表示课题所处状态
    :param stage: 字符串，相关操作所处阶段
    :return string: 返回字符串，表示操作是否可进行
    """
    status_dict = {
        "选题已被确认": 0,
        "双选结果已公布": 1,
        "已下达任务书": 2,
        "任务书已审核": 3,
        "已提交开题报告": 4,
        "开题报告已审核": 5,
        "已提交中期检查": 6,
        "中期检查已审核": 7,
        "已提交论文草稿": 8,
        "论文草稿已审核": 9,
        "已提交论文定稿": 10,
        "论文定稿已审核": 11,
        "论文定稿已评阅": 12,
        "已分配答辩组": 13,
        "已录入答辩成绩": 14,
        "已完成": 15
    }
    stage_dict = {
        "下达任务书": 1,
        '审核任务书': 2,
        '查看任务书': 3,
        "提交开题报告": 3,
        "审核开题报告": 4,
        "填写周进度报告": 5,
        "审核周进度报告": 5,
        "提交中期检查": 5,
        "审核中期检查": 6,
        "提交论文草稿": 7,
        "审核论文草稿": 8,
        "提交论文定稿": 9,
        "审核论文定稿": 10,
        "评阅论文定稿": 11,
        "查看答辩信息": 13,
    }
    status_index = status_dict[status]
    if status_index < stage_dict[stage]:
        if status_index == 0:
            return '''访问拒绝，课题正处于'双选结果公布'阶段。'''
        elif status_index == 1:
            return '''访问拒绝，课题正处于'任务书下达'阶段。'''
        elif status_index == 2:
            return '''访问拒绝，课题正处于'任务书审核'阶段。'''
        elif status_index == 3:
            return '''访问拒绝，课题正处于'开题报告提交'阶段。'''
        elif status_index == 4:
            return '''访问拒绝，课题正处于'开题报告审核'阶段。'''
        elif status_index == 5:
            return '''访问拒绝，课题正处于'中期检查提交'阶段。'''
        elif status_index == 6:
            return '''访问拒绝，课题正处于'中期检查审核'阶段。'''
        elif status_index == 7:
            return '''访问拒绝，课题正处于'论文草稿提交'阶段。'''
        elif status_index == 8:
            return '''访问拒绝，课题正处于'论文草稿审核'阶段。'''
        elif status_index == 9:
            return '''访问拒绝，课题正处于'论文定稿提交'阶段。'''
        elif status_index == 10:
            return '''访问拒绝，课题正处于'论文定稿审核'阶段。'''
        elif status_index == 11:
            return '''访问拒绝，课题正处于'答辩'阶段。'''
    else:
        return "操作允许"


# 浏览任务书
def browse_task(request):
    """
    实现浏览任务书功能，当学生点击任务书按钮时，根据自己的学号，查询自己选择的课题的任务书，
    如果任务书已审核，则将任务书信息发送至前端页面，如果任务书未审核，则返回错误信息
    :param request: HTTP请求
    :return: render: 渲染任务书页面
    """
    # 如果未登录，则重定向至登录界面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息,检查该学生是否选题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果查询到结果，则程序继续进行，否则则该学生未选题，返回错误信息
    if cursor.rowcount == 1:
        # 获取选题信息
        select_info = cursor.fetchone()
        # 检查选题的所处阶段，是否已经到达任务书阶段
        status = select_info[2]
        message = check_status(status, "查看任务书")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html', {'message': message, 'name': info_dict['name']})
        # 获取项目名称
        pname = select_info[1]
        # 从项目-学生-教师视图上获得课题的进一步信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PROJECT_STUDENT_TEACHER WHERE PNAME = '" + pname + "'")
        project_info = cursor.fetchone()
        # 从任务书表中，获取项目的任务书信息
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Task_Book WHERE PNAME = '" + pname + "'")
        # 获取任务书信息
        task_book_info = cursor1.fetchone()
        # 构造任务书字典
        task_book = {
            'name': task_book_info[0],
            "type": project_info[1],
            "supervisor": project_info[3],
            "content": task_book_info[1],
            "requirements": task_book_info[2],
            "goal": task_book_info[3],
            "management": task_book_info[4],
            "file": task_book_info[5],
            "time": task_book_info[6],
        }
        # 更新信息字典,将任务书信息加入字典
        info_dict["task_book"] = task_book
        # 渲染任务书页面
        return render(request, "student/browse_task.html", info_dict)
    else:
        # 如果学生未选题，则返回错误信息
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...', 'name': info_dict["name"]})


# 开题报告页面
def open_report(request):
    """
    实现开题报告页面，学生可在此提交或修改开题报告，
    当学生点击提交按钮时，将开题报告信息存入数据库中
    :param request: HTTP请求
    :return: render: 渲染开题报告页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[2]
        message = check_status(status, "提交开题报告")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html', {'message': message, 'name': info_dict['name']})
        # 获取课题信息
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM PROJECT_TEACHER WHERE PNAME = '" + selected_project_info[1] + "'")
        project_info = cursor1.fetchone()
        # 更新信息字典
        info_dict['project'] = {
            'name': project_info[0],
            'type': project_info[1],
            'supervisor': project_info[2],
        }
        # 获取开题报告信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM OPEN_REPORT WHERE PNAME = '" + selected_project_info[1] + "'")
        # 如果开题报告存在，则进行构造开题报告信息，以供修改
        if cursor.rowcount == 1:
            # 获取开题报告信息
            open_report_info = cursor.fetchone()
            if open_report_info[6] is None:
                comment_time = ""
            else:
                comment_time = open_report_info[6].strftime("%Y-%m-%d %H:%M:%S")
            # 构造开题报告字典
            open_report_dict = {
                'content': open_report_info[1],
                'file': open_report_info[2],
                'time': open_report_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                'status': open_report_info[4],
                'comment': open_report_info[5],
                'comment_time': comment_time,
            }
            # 更新信息字典
            info_dict['status'] = "已提交"
            info_dict['open_report'] = open_report_dict
        else:
            # 如果开题报告不存在，则更新信息字典
            info_dict['status'] = "未提交"
        # 渲染开题报告页面
        return render(request, "student/open_report.html", info_dict)
    else:
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...', 'name': info_dict["name"]})


# 开题报告提交功能
def submit_report(request):
    """
    实现开题报告提交功能，学生可在此提交或修改开题报告，
    当学生点击提交按钮时，将开题报告信息存入数据库中，并重定向至开题报告页面
    :param request: HTTP请求
    :return: redirect: 重定向至开题报告页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 初始化附件路径
    path = ""
    # 获取课题名称
    project_name = request.POST["project_name"]
    # 获取开题报告内容
    report_content = request.POST["report_content"]
    attachment = request.FILES.get("attachment", None)
    # 获取当前时间
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    # 初始化数据库游标，准备修改数据
    cursor = db.cursor()
    # 检查用户是提交开题报告还是修改开题报告
    if request.POST["status"] == "未提交":
        cursor.execute("INSERT INTO OPEN_REPORT VALUES ('" + project_name + "', '" + report_content +
                       "', '" + path + "', '" + now + "', '审核中', '', NULL)")
    else:
        # 删除原有附件
        cursor.execute("SELECT * FROM OPEN_REPORT WHERE PNAME = '" + project_name + "'")
        open_report_info = cursor.fetchone()
        if open_report_info[2] != "":
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "open_report",
                                open_report_info[2])
            os.remove(path)
        # 更新开题报告信息
        cursor.execute("UPDATE OPEN_REPORT SET ORcontent = '" + report_content + "', ORfile = '" + path
                       + "', ORtime = '" + now + "', ORstatus = '审核中' WHERE PNAME = '" + project_name + "'")
    # 如果含有附件，则写入附件
    if attachment is not None:
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "open_report")
        write_attachment(attachment, path)
    # 提交修改
    db.commit()
    # 重定向至开题报告页面
    return redirect('/student/open_report/')


# 中期检查页面
def mid_term_check(request):
    """
    实现学生中期检查页面，学生可在此页面提交、查看、修改自己的中期检查信息
    :param request: HTTP请求
    :return: render: 渲染中期检查页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 初始化信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html",
                      {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[2]
        message = check_status(status, "提交开题报告")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html', {'message': message, 'name': info_dict['name']})
        # 获取项目名称
        project_name = selected_project_info[1]
        # 获取项目信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PROJECT_TEACHER WHERE PNAME = '" + project_name + "'")
        project_info = cursor.fetchone()
        # 更新信息字典
        info_dict['project'] = {
            'name': project_info[0],
            'type': project_info[1],
            'supervisor': project_info[2],
        }
        # 获取中期检查信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Middle_CHECK WHERE PNAME = '" + project_name + "'")
        # 如果中期检查存在，则进行构造开题报告信息，以供修改
        if cursor.rowcount == 1:
            middle_check_info = cursor.fetchone()
            middle_check_dict = {
                'content': middle_check_info[1],
                'file': middle_check_info[2],
                'time': middle_check_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                'status': middle_check_info[4],
                'comment': middle_check_info[5],
                'comment_time': middle_check_info[6],
            }
            # 更新信息字典
            info_dict['status'] = "已提交"
            info_dict['middle_check'] = middle_check_dict
        else:
            # 如果开题报告不存在，则更新信息字典
            info_dict['status'] = "未提交"
        # 渲染中期检查页面
        return render(request, "student/mid_term_check.html", info_dict)
    else:
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...',
                                                 'name': info_dict['name']})


# 中期检查提交
def submit_progress(request):
    """
    实现中期检查提交功能，学生可在此提交或修改开题报告，
    当学生点击提交按钮时，将中期检查信息存入数据库中，并重定向至中期检查页面
    :param request: HTTP请求
    :return: redirect: 重定向至开题报告页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 初始化附件路径
    path = ""
    # 获取课题名称
    project_name = request.POST["project_name"]
    # 获取中期检查内容
    progress_info = request.POST["middle_check"]
    attachment = request.FILES.get("attachment")
    # 获取当前时间,并格式化为时间戳
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    # 初始化数据库游标，准备修改数据
    cursor = db.cursor()
    # 检查用户是提交开题报告还是修改开题报告
    if request.POST["status"] == "未提交":
        # 插入开题报告信息
        cursor.execute("INSERT INTO Middle_CHECK VALUES ('" + project_name + "', '" + progress_info + "', '"
                       + path + "', '" + now + "', '审核中', NULL, NULL)")
    else:
        # 删除原有附件
        cursor.execute("SELECT * FROM Middle_CHECK WHERE PNAME = '" + project_name + "'")
        middle_check_info = cursor.fetchone()
        if middle_check_info[2] != "":
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "open_report",
                                middle_check_info[2])
            os.remove(path)
        # 更新开题报告信息
        cursor.execute("UPDATE Middle_Check SET MCcontent = '" + progress_info + "', MCfile = '" + path
                       + "', MCtime = '" + now + "', MCstatus = '审核中' WHERE PNAME = '" + project_name + "'")
    # 如果含有附件，则写入附件
    if attachment != "":
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "middle_check")
        write_attachment(attachment, path)
    # 提交修改
    db.commit()
    # 重定向至开题报告页面
    return redirect('/student/mid_term_check/')


# 周进度报告页面
def weekly_report(request):
    """
    实现周进度报告页面，学生可在此查看或修改周进度报告，
    当学生点击提交按钮时，将周进度报告信息存入数据库中，并重定向至周进度报告页面
    :param request: HTTP请求
    :return: redirect: 重定向至周进度报告页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html",
                      {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息，检查学生是否已选题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[2]
        message = check_status(status, "填写周进度报告")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html', {'message': message, 'name': info_dict['name']})
        # 获取项目名称
        project_name = selected_project_info[1]
        # 获取项目信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PROJECT_TEACHER WHERE PNAME = '" + project_name + "'")
        project_info = cursor.fetchone()
        # 更新信息字典
        info_dict['project'] = {
            'name': project_info[0],
            'type': project_info[1],
            'supervisor': project_info[2],
        }
        # 初始化周进度报告列表
        weekly_report_list = []
        # 获取周进度报告信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Weekly_Report WHERE PNAME = '" + project_name + "'")
        # 获取所有周进度报告信息
        for i in range(cursor.rowcount):
            # 获取周进度报告信息
            weekly_report_info = cursor.fetchone()
            if weekly_report_info[6] is None:
                comment_time = ""
            else:
                comment_time = weekly_report_info[6].strftime("%Y-%m-%d %H:%M:%S")
            # 构造周进度报告信息字典
            weekly_report_dict = {
                'content': weekly_report_info[1],
                'file': weekly_report_info[2],
                'time': weekly_report_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                'status': weekly_report_info[4],
                'comment': weekly_report_info[5],
                'comment_time': comment_time,
            }
            # 将周进度报告字典添加至周进度报告列表
            weekly_report_list.append(weekly_report_dict)
        # 更新信息字典
        info_dict['weekly_report_list'] = weekly_report_list
        # 渲染周进度报告页面
        return render(request, "student/weekly_report.html", info_dict)
    else:
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...',
                                                 'name': info_dict['name']})


def submit_weekly_report(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 初始化附件路径
    path = ""
    # 获取周进度报告信息
    action = request.POST.get('action')
    project_name = request.POST.get('project_name')
    report_content = request.POST.get('weekly_report')
    report_attachment = request.FILES.get('attachment')
    # 检查是新建报告还是修改报告
    if action == "新建":
        # 获取当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 如果含有附件，则写入附件
        if report_attachment is not None:
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "weekly_report")
            write_attachment(report_attachment, path)
        # 向数据库中插入周进度报告信息
        cursor = db.cursor()
        cursor.execute("INSERT INTO Weekly_Report VALUES ('" + project_name + "','" + report_content
                       + "','" + path + "','" + now + "','审核中','',NULL)")
    elif action == "修改":
        # 获取当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 获取要修改的周进度报告的提交时间
        submit_time = request.POST.get('submit_time')
        # 获取原有附件路径，并删除原有附件
        cursor = db.cursor()
        cursor.execute("SELECT WRfile FROM Weekly_Report WHERE PNAME = '" + project_name +
                       "' AND WRtime = '" + submit_time + "'")
        attachment_path = cursor.fetchone()[0]
        # 如果原有附件不为空，则删除原有附件
        if not attachment_path == "":
            os.remove(attachment_path)
        # 如果含有附件，则写入附件
        if report_attachment is not None:
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "weekly_report")
            write_attachment(report_attachment, path)
        # 更新周进度报告信息
        cursor = db.cursor()
        cursor.execute("UPDATE Weekly_Report SET WRCONTENT = '" + report_content + "', WRfile = '" + path
                       + "', WRtime = '" + now + "', WRstatus = '审核中' WHERE PNAME = '" + project_name +
                       "' AND WRtime = '" + submit_time + "'")
    # 提交事务
    db.commit()
    # 重定向至周进度报告页面
    return redirect('/student/weekly_report/')


# 毕业论文（草稿）页面
def thesis_draft(request):
    """
    毕业论文（草稿）页面，学生能在此提交或修改毕业论文草稿
    :param request:HTTP请求
    :return render:渲染毕业论文（草稿）页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html",
                      {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT_STUDENT_Teacher WHERE SName = '" + info_dict["name"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题的所处阶段，是否已经到达任务书阶段
        status = selected_project_info[4]
        message = check_status(status, "提交论文草稿")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html',
                          {'message': message, 'name': info_dict['name']})
        # 构造课题字典
        project_dict = {
            'name': selected_project_info[0],
            'type': selected_project_info[1],
            'supervisor': selected_project_info[3],
        }
        info_dict["project"] = project_dict
        # 获取毕业论文草稿信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM THESIS_DRAFT WHERE PNAME = '" + selected_project_info[0] + "'")
        # 检查学生是否已提交毕业论文（草稿）
        if cursor.rowcount == 1:
            # 如果查询到结果，则说明学生已提交毕业论文（草稿）,此时获取论文草稿信息
            thesis_draft_info = cursor.fetchone()
            # 构造毕业论文字典，以供修改
            thesis_draft_dict = {
                'content': thesis_draft_info[1],
                'file': thesis_draft_info[2],
                'time': thesis_draft_info[3],
                'status': thesis_draft_info[4],
                'comment': thesis_draft_info[5],
                'comment_time': thesis_draft_info[6],
            }
            # 更新信息字典，将状态改为已提交并添加毕业论文草稿信息
            info_dict['status'] = "已提交"
            info_dict['thesis_draft'] = thesis_draft_dict
        else:
            # 如果学生未提交论文草稿，则更新信息字典，将状态信息改为未提交
            info_dict['status'] = "未提交"
        return render(request, "student/thesis_draft.html", info_dict)
    else:
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...',
                                                 'name': info_dict['name']})


# 论文草稿提交功能
def submit_draft(request):
    """
    实现论文草稿提交功能，将学生提交或修改的毕业论文草稿信息插入或修改至数据库中
    并重定向至论文草稿页面
    :param request: HTTP请求
    :return redirect: 重定向至论文草稿页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 获取论文草稿相关信息
    project_name = request.POST.get('project_name')
    content = request.POST.get('content')
    attachment = request.FILES.get('attachment')
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 初始化附件路径
    if attachment is not None:
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "thesis_draft")
    else:
        path = ""
    # 检查用户的动作
    action = request.POST["action"]
    # 如果用户选择提交，则将论文草稿信息插入数据库中
    if action == "提交":
        # 初始化游标，向论文草稿表插入数据
        cursor = db.cursor()
        cursor.execute("INSERT INTO THESIS_DRAFT VALUES ('" + project_name + "','" + content + "','" +
                       path + "','" + now + "','审核中','',NULL)")
    else:
        # 获取原有附件路径，如果路径不为空，删除原有附件
        cursor = db.cursor()
        cursor.execute("SELECT ATTACHMENT FROM THESIS_DRAFT WHERE PNAME = '" + project_name + "'")
        path = cursor.fetchone()[0]
        if path != "":
            os.remove(path)
        # 初始化游标，准备修改论文草稿表中相关数据
        cursor = db.cursor()
        cursor.execute("UPDATE THESIS_DRAFT SET CONTENT = '" + content + "', ATTACHMENT = '" + path + "', TIME = '" +
                       now + "', TDstatus = '审核中' WHERE PNAME = '" + project_name + "'")
    # 如果有提交附件，则存储附件
    if attachment is not None:
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "thesis_draft")
        write_attachment(attachment, path)
    # 提交事务
    db.commit()
    # 重定向至论文草稿页面
    return redirect('/student/thesis_draft/')


# 毕业论文（定稿）页面,学生能在此查看、修改或提交自己的毕业论文定稿
def thesis_final(request):
    """
    毕业论文（定稿）页面，学生能在此查看、修改或提交自己的毕业论文定稿
    :param request:HTTP请求
    :return render: 渲染毕业论文定稿页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html",
                      {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT_STUDENT_Teacher WHERE SName = '" +
                   info_dict["name"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息，并从中获取学生所选课题名称
        selected_project_info = cursor.fetchone()
        # 检查选题的所处阶段，是否已经到达任务书阶段
        status = selected_project_info[4]
        message = check_status(status, "提交论文定稿")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html',
                          {'message': message, 'name': info_dict['name']})
        pname = selected_project_info[0]
        # 构造课题字典
        project_dict = {
            'name': selected_project_info[0],
            'type': selected_project_info[1],
            'supervisor': selected_project_info[3],
        }
        info_dict["project"] = project_dict
        # 尝试获取该学生的毕业论文定稿信息，检查该学生是否提交论文定稿
        cursor.execute("SELECT * FROM THESIS_FINAL WHERE PNAME = '" + pname + "'")
        # 如果查询到结果，则学生已提交论文定稿
        if cursor.rowcount == 1:
            # 更新信息字典，将状态改为已提交
            info_dict['status'] = "已提交"
            # 获取毕业论文定稿信息
            thesis_final_info = cursor.fetchone()
            # 获取评阅教师信息
            if thesis_final_info[7] is None:
                reviewer = "暂无"
                reviewer_no = "暂无"
            else:
                reviewer_no = thesis_final_info[7]
                cursor.execute("SELECT * FROM TEACHER WHERE TNO = '" + reviewer_no + "'")
                reviewer = cursor.fetchone()[1]
            # 构造毕业论文定稿字典，以便在页面中显示，供学生修改
            thesis_final_dict = {
                "content": thesis_final_info[1],
                "file": thesis_final_info[2],
                "time": thesis_final_info[3],
                "status": thesis_final_info[4],
                "comment": thesis_final_info[5],
                "comment_time": thesis_final_info[6],
                "reviewer": reviewer,
                "reviewer_no": reviewer_no,
                "score": thesis_final_info[8],
                "score_comment": thesis_final_info[9],
                "score_time": thesis_final_info[10],
            }
            # 更新信息字典，将毕业论文定稿信息添加至信息字典中
            info_dict["thesis_final"] = thesis_final_dict
        # 如果未查询到结果，则学生未提交论文定稿
        else:
            # 更新信息字典，将状态改为未提交
            info_dict['status'] = "未提交"
        return render(request, "student/thesis_final.html", info_dict)
    else:
        return render(request, "announce.html", {'message': '同学，你还尚未选题呢...',
                                                 'name': info_dict['name']})


# 提交毕业论文定稿功能
def submit_final(request):
    """
    实现毕业论文提交功能，根据POST表单中的信息，插入或修改毕业论文表中的数据，
    并在操作完成后重定向至毕业论文定稿页面
    :param request: HTTP请求
    :return redirect: 重定向至论文定稿页面
    """
    # 从session中获取用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 从表单中获取毕业论文定稿相关数据
    project_name = request.POST["project_name"]
    content = request.POST["content"]
    attachment = request.FILES.get("attachment")
    # 初始化附件路径
    if attachment is not None:
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "thesis_final")
    else:
        path = ""
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 获取学生的操作类型
    action = request.POST["action"]
    # 如果操作为提交,则向数据库中插入毕业论文数据
    if action == "提交":
        # 初始化游标，向数据库中插入毕业论文定稿数据
        cursor = db.cursor()
        cursor.execute("INSERT INTO THESIS_FINAL VALUES ('" + project_name + "', '" + content +
                       "', '" + path + "', '" + now + "', '审核中', NULL, NULL, NULL, NULL, NULL, NULL)")
    # 如果操作为修改，则修改毕业论文定稿表中相关数据
    else:
        # 获取原有附件路径，如果路径不为空，则删除原有附件
        cursor = db.cursor()
        cursor.execute("SELECT TFfile FROM THESIS_FINAL WHERE PNAME = '" + project_name + "'")
        thesis_final_info = cursor.fetchone()
        if thesis_final_info[0] != "":
            os.remove(thesis_final_info[0])
        # 初始化游标，向数据库中修改毕业论文定稿数据
        cursor = db.cursor()
        cursor.execute("UPDATE THESIS_FINAL SET TFcontent = '" + content + "', TFfile = '"
                       + path + "', TFtime = '" + now + "', TFstatus = '审核中';")
    # 如果附件不为空，则将附件保存至指定路径
    if attachment is not None:
        write_attachment(path, attachment)
    # 提交事务
    db.commit()
    # 重定向至提交论文定稿页面
    return redirect("/student/thesis_final/")


# 查看答辩信息页面
def defense_info(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "教师":
        return render(request, "announce.html",
                      {'message': '老师，这里是学生中心哦！', 'name': info_dict['name']})
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT_STUDENT_Teacher WHERE SName = '" +
                   info_dict["name"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息，并从中获取学生所选课题名称
        selected_project_info = cursor.fetchone()
        # 检查选题的所处阶段，是否已经到达任务书阶段
        status = selected_project_info[4]
        message = check_status(status, "查看答辩信息")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html',
                          {'message': message, 'name': info_dict['name']})
        # 构造课题信息字典
        project_info_dict = {
            'name': selected_project_info[0],
            'type': selected_project_info[1],
            'supervisor': selected_project_info[3]
        }
        # 将课题信息加入至信息字典
        info_dict['project'] = project_info_dict
        # 调用存储过程，获取该学生的答辩信息
        cursor = db.cursor()
        cursor.execute("CALL GET_DEFENSE_INFO('" + info_dict["no"] + "')")
        defense_info = cursor.fetchone()
        if defense_info[7] is not None:
            score_time = defense_info[7].strftime('%Y-%m-%d %H:%M:%S')
        else:
            score_time = ""
        # 构造答辩信息字典
        defense_info_dict = {
            "name": defense_info[0],
            "leader": defense_info[1],
            "secretary": defense_info[2],
            "date": defense_info[3].strftime('%Y-%m-%d'),
            "location": defense_info[4],
            "comment": defense_info[5],
            "score": defense_info[6],
            "score_time": score_time,
            "status": defense_info[8]
        }
        # 将答辩信息加入至信息字典
        info_dict['defense_info'] = defense_info_dict
        # 渲染答辩信息页面
        return render(request, 'student/defense_info.html', info_dict)
# 教师中心页面
def teacher(request):
    """
    渲染教师中心页面，教师模块的主页，教师可以在这里选择自己的功能角色，
    比如指导教师，毕设负责人等，并转至对应的角色页面。
    :param request: HTTP请求
    :return render: 渲染教师中心页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    return render(request, "teacher/teacher_index.html", info_dict)


# 切换功能角色功能
def role(request):
    """
    实现教师切换功能角色的功能，根据POST表单中的信息，
    检查用户是否有该功能角色的权限，如果有相应权限，则重定向至对应角色页面，
    如果没有相应权限，则渲染通知页面，提示用户没有该功能角色的权限
    :param request: HTTP请求
    :return redirect: 重定向至对应角色页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    self_info = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no']
    }
    # 从POST表单中获取教师要切换的功能角色
    userRole = request.POST["role"]
    # 访问数据库，检查用户是否有该功能角色的权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + self_info["no"] + "' AND is_" + userRole + "= '是'" + ";")
    if curse.rowcount == 1:
        # 查询到结果，说明用户有该功能角色的权限，重定向至对应的功能角色页面
        return render(request, "teacher/" + userRole + "/" + userRole + ".html", self_info)
    else:
        # 查询不到结果，说明用户没有该功能角色的权限，重定向至通知页面
        return render(request, "announce.html",
                      {'message': '您没有' + userRole + '权限，无法访问。', 'name': self_info["name"]})


# 信息统计页面
def information_summary(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    self_info = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list(),
    }
    return render(request, "teacher/information_summary.html", self_info)


# 指导教师模块
def supervisor(request):
    """
    渲染指导教师模块主页，指导教师可以在这里前往相应的操作页面，
    :param request: HTTP请求
    :return render: 渲染指导教师主页
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    return render(request, "teacher/supervisor/supervisor.html", info_dict)


# 申报课题页面
def project_proposal(request):
    """
    申报课题页面，指导教师可以在这里申报课题，
    在点击提交后，课题会被插入数据库中。
    :param request: HTTP请求
    :return render:
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 初始化课题列表
    project_list = []
    # 获取教师所有已申报课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "';")
    index = 0
    for project in cursor.fetchall():
        if project[7] is None:
            comment_time = ""
        else:
            comment_time = project[7].strftime("%Y-%m-%d %H:%M:%S")
        # 构造课题信息字典
        project_info = {
            'index': index,
            'name': project[0],
            'type': project[1],
            'info': project[2],
            'file': project[3],
            'time': project[4].strftime("%Y-%m-%d %H:%M:%S"),
            'status': project[5],
            'comment': project[6],
            'comment_time': comment_time
        }
        # 将课题信息字典添加至课题列表
        project_list.append(project_info)
        index += 1
    # 将课题列表添加至信息字典
    info_dict["project_list"] = project_list
    # 渲染申报课题页面
    return render(request, "teacher/supervisor/project_proposal.html", info_dict)


# 申报课题功能
def propose_project(request):
    """
    实现申报课题功能，根据POST表单中的数据，
    向数据库中插入课题信息，或修改课题信息
    :param request: HTTP请求
    :return redirect: 重定向至课题申报页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取课题相关信息
    project_name = request.POST["project_name"]
    project_type = request.POST["project_type"]
    project_info = request.POST["project_info"]
    project_file = request.FILES.get("attachment")
    # 初始化附件路径
    if project_file is not None:
        path = os.path.join("static", "upload", "project" + project_name)
    else:
        path = ""
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 获取用户操作类型
    action = request.POST["action"]
    # 初始化游标，准备更新数据库数据
    cursor = db.cursor()
    # 如果操作类型为修改课题
    if action == "修改":
        # 获取课题原名称
        old_project_name = request.POST["old_project_name"]
        # 获取原课题附加路径
        cursor = db.cursor()
        cursor.execute("SELECT Pfile From Project WHERE Pname='" + project_name + "';")
        old_file = cursor.fetchone()[0]
        if old_file != "":
            os.remove(old_file)
        # 更新课题信息
        cursor.execute("UPDATE PROJECT SET Pname = '" + project_name + "', Ptype = '" + project_type + "', Pinfo = '" +
                       project_info + "', Pfile = '" + path + "', Ptime = '" + now + "', Pstatus = '待审核'"
                                                                                     " WHERE Pname = '" + old_project_name + "';")
        return redirect('/teacher/supervisor/project_proposal/')
    else:
        cursor.execute("INSERT INTO PROJECT VALUES ('" + project_name + "','" +
                       project_type + "','" + project_info + "','" + path + "','" + now +
                       "','待审核','',NULL,'" + info_dict['no'] + "');")
    write_attachment(project_file, path)
    # 提交数据库更新
    db.commit()
    # 重定向至课题申报页面
    return redirect('/teacher/supervisor/project_proposal/')


# 确认选题页面
def project_confirmation(request):
    """
    确认选题页面，指导教师可以在这里确认学生的选题
    :param request: HTTP请求
    :return render: 渲染确认选题页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 检查用户身份是否是教师
    if not info_dict["role"] == "教师":
        #  渲染通知页面，提示用户身份错误
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 初始化预选信息列表
    pre_selection_info = []
    # 获取该老师的课题预选信息
    cursor = db.cursor()
    cursor.execute("CALL GET_PRESELECT('" + info_dict["no"] + "');")
    # 遍历课题预选信息，构造预选信息列表
    for select_index in range(cursor.rowcount):
        # 获取当前课题信息
        preselect_info = cursor.fetchone()
        # 构造预选信息字典
        pre_selection = {
            "project_name": preselect_info[0],
            "project_type": preselect_info[1],
            "student_name": preselect_info[2],
            "student_no": preselect_info[3],
            "level": preselect_info[4],
            "time": preselect_info[5]
        }
        pre_selection_info.append(pre_selection)
    # 将预选信息列表添加至信息字典
    info_dict["pre_selection_info"] = pre_selection_info
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("CALL GET_SELECTED('" + info_dict["no"] + "');")
    # 初始化已选课题列表
    selected_project_list = []
    # 遍历已选课题信息，构造已选课题列表
    for selected_index in range(cursor.rowcount):
        selected_info = cursor.fetchone()
        selected_project = {
            "project_name": selected_info[0],
            "project_type": selected_info[1],
            "student_name": selected_info[2],
            "student_no": selected_info[3],
            "status": selected_info[4],
            "time": selected_info[5],
            "update_time": selected_info[6]
        }
        selected_project_list.append(selected_project)
    # 将已选课题列表添加至信息字典
    info_dict["selected_project_list"] = selected_project_list
    # 渲染确认选题页面
    return render(request, "teacher/supervisor/project_confirmation.html", info_dict)


# 确认选题操作
def confirm_project(request):
    """
    确认选题操作，根据POST表单中的数据，将选题信息插入数据库
    :param request: HTTP请求
    :return render: 重定向至确认选题页面
    """
    # 获取学生学号和课题名称
    pname = request.POST["project_name"]
    sno = request.POST["student_no"]
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    cursor.execute("CALL CONFIRM_SELECT('" + pname + "','" + sno + "');")
    # 提交事务
    db.commit()
    # 重定向至确认选题页面
    return redirect("/teacher/supervisor/project_confirmation")


# 取消预选选题操作
def cancel_pre_selection(request):
    """
    取消学生预选选题操作，根据POST表单中的数据，将预选信息从数据库中删除
    :param request: HTTP请求
    :return redirect: 重定向至确认选题页面
    """
    # 获取学生学号和课题名称
    pname = request.POST["project_name"]
    sno = request.POST["student_no"]
    # 删除该学生的预选课题
    cursor = db.cursor()
    cursor.execute("DELETE FROM Pre_Select WHERE SNO = '" + sno + "' AND PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至确认选题页面
    return redirect("/teacher/supervisor/project_confirmation")


# 撤销确认选题操作
def cancel_confirm(request):
    """
    撤销确认选题操作，根据POST表单中的数据，将选题信息从数据库中删除
    :param request: HTTP请求
    :return redirect: 重定向至确认选题页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    # 获取学生学号和课题名称
    pname = request.POST["project_name"]
    sno = request.POST["student_no"]
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    cursor.execute("CALL CANCEL_CONFIRM('" + pname + "','" + sno + "');")
    # 提交事务
    db.commit()
    # 重定向至确认选题页面
    return redirect("/teacher/supervisor/project_confirmation")


# 下达任务书页面
def task_issue(request):
    """
    下达任务书页面，指导教师可在此为所有已选课题下达任务书
    函数将根据session中的用户信息，获取该老师的所有已选课题，
    并将数据传递给前端，渲染下达任务书页面
    :param request: HTTP请求
    :return render: 渲染下达任务书页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-老师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" + info_dict["name"] + "';")
    # 初始化课题列表
    project_list = []
    index = 0
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "index": index,
            "project_name": project_info[0],
            "project_type": project_info[1],
            "supervisor": project_info[3],
            "student_name": project_info[2],
        }
        # 获取课题任务书信息
        cursor.execute("SELECT * FROM Task_Book WHERE PNAME = '" + project_info[0] + "';")
        # 如果课题任务书已存在，则构造任务书信息字典
        if cursor.rowcount == 1:
            # 获取课题任务书信息
            task_book_info = cursor.fetchone()
            # 构造课题任务书信息字典
            task_book_dict = {
                "content": task_book_info[1],
                "requirements": task_book_info[2],
                "goal": task_book_info[3],
                "management": task_book_info[4],
                "file": task_book_info[5],
                "time": task_book_info[6],
                "status": task_book_info[7],
                "comment": task_book_info[8],
                "comment_time": task_book_info[9]
            }
            project_info_dict["status"] = task_book_info[7]
            # 将课题任务书信息字典添加至课题信息字典
            project_info_dict["task_book"] = task_book_dict
        else:
            # 将课题信息字典的status设为未发布
            project_info_dict["status"] = "未下达"
        # 将课题信息字典添加至课题列表
        project_list.append(project_info_dict)
        index += 1
    # 更新信息字典
    info_dict["project_list"] = project_list
    # 渲染课题任务书页面
    return render(request, "teacher/supervisor/task_issue.html", info_dict)


# 下达任务书操作
def issue_task(request):
    """
    下达任务书操作，根据POST表单中的数据，
    插入课题任务书信息至数据库中或修改课题任务书信息，并重定向至下达任务书页面
    :param request: HTTP请求
    :return redirect: 重定向至下达任务书页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取课题名称
    pname = request.POST["pname"]
    # 从POST表单中获取课题任务书信息
    content = request.POST["content"]
    requirements = request.POST["requirements"]
    goal = request.POST["goal"]
    management = request.POST["management"]
    attachment = request.FILES.get("attachment")
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 初始化附件路径
    path = ""
    # 如果附件不为空，则将附件保存至服务器，并将附件路径保存至数据库中
    # 初始化附件路径
    if attachment is not None:
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "thesis_final")
    else:
        path = ""
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    # 从POST表单中获取用户操作类型
    action = request.POST["action"]
    # 如果用户操作类型为下达，则将课题任务书信息插入数据库中
    if action == "下达":
        # 将课题任务书信息插入数据库中
        cursor.execute("INSERT INTO Task_Book VALUES ('" + pname + "', '" + content + "', '" + requirements +
                       "', '" + goal + "', '" + management + "', '" + path + "','" + now + "', '审核中', '', NULL);")
    # 如果用户操作类型为修改，则将课题任务书信息更新至数据库中
    else:
        # 将课题任务书信息更新至数据库中
        cursor.execute("UPDATE Task_Book SET TBcontent = '" + content + "', TBrequirements = '" + requirements +
                       "', TBgoal = '" + goal + "', TBmanagement = '" + management + "', TBfile = '" + path +
                       "', TBtime = '" + now + "', TBstatus = '审核中' WHERE PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至课题任务书页面
    return redirect("/teacher/supervisor/task_issue")


# 审阅开题报告页面
def report_review(request):
    """
    审阅开题报告页面，指导教师可在此审核学生提交的开题报告
    :param request: HTTP请求
    :return render: 渲染开题报告审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-老师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" +
                   info_dict["name"] + "';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    index = 0
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            'index': index,
            "name": project_info[0],
            "type": project_info[1],
            "student": project_info[2],
        }
        # 从开题报告表中查找该课题的开题报告信息
        cursor.execute("SELECT * FROM Open_Report WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则开题报告已存在，构造开题报告信息字典，以供教师查看审阅
        if cursor.rowcount == 1:
            # 获取开题报告信息
            open_report_info = cursor.fetchone()
            # 构造开题报告信息字典
            if open_report_info[6] is not None:
                comment_time = open_report_info[6].strftime("%Y-%m-%d %H:%M:%S")
            else:
                comment_time = "暂未审阅"
            open_report_dict = {
                "content": open_report_info[1],
                "file": open_report_info[2],
                "time": open_report_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                "status": open_report_info[4],
                "comment": open_report_info[5],
                "comment_time": open_report_info[6].strftime("%Y-%m-%d %H:%M:%S")
            }
            project_info_dict["status"] = open_report_info[4]
            # 将开题报告信息字典添加至已选课题信息字典中
            project_info_dict["open_report"] = open_report_dict
        else:
            # 如果未查找到结果，则开题报告未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
        index += 1
    # 更新信息字典
    info_dict["project_list"] = project_list
    # 渲染开题报告审阅页面
    return render(request, "teacher/supervisor/report_review.html", info_dict)


# 审阅开题报告功能
def pass_report(request):
    """
    审阅开题报告功能，根据POST表单中的数据，
    对数据库中的开题报告信息进行更新
    :param request: HTTP请求
    :return render: 渲染开题报告审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从POST表单中获取课题名称
    pname = request.POST["project_name"]
    # 从POST表单中获取开题报告审阅内容
    result = request.POST["result"]
    comment = request.POST["comment"]
    comment_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    # 更新开题报告信息
    cursor.execute("UPDATE Open_Report SET ORstatus = '" + result + "', ORcomment = '"
                   + comment + "', ORcomment_time = '" + comment_time + "' WHERE PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至开题报告审阅页面
    return redirect("/teacher/supervisor/report_review")


# TODO: 审阅外文翻译页面（未实装）
# 审阅外文翻译页面（未实装）
def translation_review(request):
    pass


# 审阅中期检查页面
def mid_term_review(request):
    """
    审阅中期检查页面，指导教师可在此审核学生提交的中期检查
    :param request: HTTP请求
    :return render: 渲染中期检查审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-老师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" +
                   info_dict["name"] + "';")
    # 初始化课题列表
    project_list = []
    index = 0
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "index": index,
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 从中期检查表中查找该课题的开题报告信息
        cursor.execute("SELECT * FROM Middle_Check WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则开题报告已存在，构造开题报告信息字典，以供教师查看审阅
        if cursor.rowcount == 1:
            # 获取中期检查信息
            mid_term_info = cursor.fetchone()
            # 构造中期检查信息字典
            if mid_term_info[6] is not None:
                comment_time = mid_term_info[6].strftime("%Y-%m-%d %H:%M:%S")
            else:
                comment_time = "暂未审阅"
            mid_term_dict = {
                "content": mid_term_info[1],
                "file": mid_term_info[2],
                "time": mid_term_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                "status": mid_term_info[4],
                "comment": mid_term_info[5],
                "comment_time": comment_time
            }
            project_info_dict["status"] = mid_term_info[4]
            # 将开题报告信息字典添加至已选课题信息字典中
            project_info_dict["mid_term_info"] = mid_term_dict
        else:
            # 如果未查找到结果，则开题报告未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        index += 1
        project_list.append(project_info_dict)
    # 更新信息字典
    info_dict["project_list"] = project_list
    # 渲染中期检查审阅页面
    return render(request, "teacher/supervisor/mid_term_review.html", info_dict)


def pass_mid_term(request):
    """
    审阅中期检查功能，根据POST表单中的数据，
    对数据库中的中期检查信息进行更新，并重定向至中期检查审阅页面
    :param request: HTTP请求
    :return redirect: 重定向至中期检查审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取课题名称
    pname = request.POST["project_name"]
    # 从POST表单中获取中期检查审阅内容
    result = request.POST["result"]
    comment = request.POST["comment"]
    comment_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    # 更新中期检查信息
    cursor.execute("UPDATE Middle_Check SET MCstatus = '" + result + "', MCcomment = '"
                   + comment + "', MCcomment_Time = '" + comment_time + "' WHERE PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至中期检查审阅页面
    return redirect("/teacher/supervisor/mid_term_review")


# 周进度审阅页面
def weekly_review(request):
    """
    周进度审阅页面，指导教师可在此审核学生提交的周进度
    :param request: HTTP请求
    :return render: 渲染周进度审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-教师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" +
                   info_dict["name"] + "';")
    # 初始化课题列表
    project_list = []
    index = 0
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "index": index,
            "name": project_info[0],
            "type": project_info[1],
            "student": project_info[2],
        }
        # 初始化周进度列表
        weekly_report_list = []
        # 从周进度表中查找该课题的周进度信息
        cursor.execute("SELECT * FROM Weekly_Report WHERE PNAME = '"
                       + project_info[0] + "' ORDER BY WRtime DESC;")
        # 如果查找到结果，则周进度已存在，构造周进度信息字典，以供教师查看审阅
        if cursor.rowcount >= 1:
            for num in range(cursor.rowcount):
                weekly_report_info = cursor.fetchone()
                if num == 0:
                    project_info_dict["time"] = weekly_report_info[3].strftime("%Y-%m-%d %H:%M:%S")
                    if weekly_report_info[4] == "审核中":
                        project_info_dict["status"] = "待审核"
                    elif weekly_report_info[4] == "未通过":
                        project_info_dict["status"] = "未通过"
                    else:
                        project_info_dict["status"] = "已审核"
                if weekly_report_info[6] is None:
                    comment_time = ""
                else:
                    comment_time = weekly_report_info[6].strftime("%Y-%m-%d %H:%M:%S")
                # 构造周进度信息字典
                weekly_report_dict = {
                    "index": num,
                    "content": weekly_report_info[1],
                    "file": weekly_report_info[2],
                    "time": weekly_report_info[3].strftime("%Y-%m-%d %H:%M:%S"),
                    "status": weekly_report_info[4],
                    "comment": weekly_report_info[5],
                    "comment_time": comment_time
                }
                print(weekly_report_info[5], weekly_report_info[6])
                # 将周进度信息字典添加至周进度列表中
                weekly_report_list.append(weekly_report_dict)
        else:
            # 如果未查找到结果，则周进度未提交
            project_info_dict["status"] = "未提交"
        # 将周进度列表添加至课题信息字典中
        project_info_dict["weekly_report_list"] = weekly_report_list
        # 将课题信息字典添加至课题列表中
        index += 1
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染周进度审阅页面
    return render(request, "teacher/supervisor/weekly_review.html", info_dict)


# 周进度审阅功能
def review_weekly(request):
    """
    周进度审阅功能，指导教师可在此审核学生提交的周进度
    :param request:
    :return redirect:
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从POST表单中获取课题名称
    pname = request.POST["project_name"]
    # 从POST表单中获取周进度报告审阅内容
    result = request.POST["result"]
    comment = request.POST["comment"]
    submit_time = request.POST["submit_time"]
    comment_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 初始化游标，准备操作数据库
    cursor = db.cursor()
    # 更新开题报告信息
    cursor.execute("UPDATE Weekly_Report SET WRstatus = '" + result + "', WRcomment = '"
                   + comment + "', WRcomment_time = '" + comment_time + "' WHERE PNAME = '" + pname
                   + "' AND WRtime = '" + submit_time + "'")
    # 提交事务
    db.commit()
    # 重定向至周进度审阅页面
    return redirect("/teacher/supervisor/weekly_review")


# 论文草稿审阅页面
def draft_review(request):
    """
    论文草稿审阅页面，指导教师可在此审核学生提交的论文草稿
    :param request: HTTP请求
    :return render: 渲染论文草稿审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-教师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" +
                   info_dict["name"] + "';")
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    index = 0
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "index": index,
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 从论文草稿表中查找该课题的论文草稿信息
        cursor.execute("SELECT * FROM Thesis_Draft WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则论文草稿已存在，构造论文草稿信息字典，以供教师查看审阅
        if cursor.rowcount == 1:
            # 获取论文草稿信息
            draft_info = cursor.fetchone()
            # 构造论文草稿信息字典
            draft_dict = {
                "content": draft_info[1],
                "file": draft_info[2],
                "time": draft_info[3],
                "status": draft_info[4],
                "comment": draft_info[5],
                "comment_time": draft_info[6]
            }
            project_info_dict["status"] = draft_info[4]
            # 将论文草稿列表添加至课题信息字典中
            project_info_dict.update(draft_dict)
        else:
            # 如果未查找到结果，则论文草稿未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
        index += 1
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染论文草稿审阅页面
    return render(request, "teacher/supervisor/draft_review.html", info_dict)


# 论文草稿审核功能
def review_draft(request):
    """
    论文草稿审核功能，指导教师可在此审核学生提交的论文草稿
    :param request: HTTP请求
    :return redirect:
    """
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取审阅信息
    project_name = request.POST.get("project_name")
    comment = request.POST.get("comment")
    result = request.POST.get("result")
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新论文草稿表中的审阅信息
    cursor = db.cursor()
    cursor.execute("UPDATE Thesis_Draft SET TDSTATUS = '" + result + "', TDCOMMENT = '" + comment +
                   "', TDCOMMENT_TIME = '" + now + "' WHERE PNAME = '" + project_name + "';")
    db.commit()
    # 重定向至论文草稿审阅页面
    return redirect("/teacher/supervisor/draft_review/")


# 论文定稿审阅页面
def final_review(request):
    """
    论文定稿审阅页面，指导教师可在此审核学生提交的论文定稿
    :param request: HTTP请求
    :return: 渲染论文定稿审阅页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    # 从课题-学生-教师视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE Tname = '" +
                   info_dict["name"] + "';")
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    index = 0
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "index": index,
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 从论文草稿表中查找该课题的论文草稿信息
        cursor.execute("SELECT * FROM Thesis_Final WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则论文草稿已存在，构造论文草稿信息字典，以供教师查看审阅
        if cursor.rowcount == 1:
            # 获取论文草稿信息
            final_info = cursor.fetchone()
            # 构造论文草稿信息字典
            final_dict = {
                "content": final_info[1],
                "file": final_info[2],
                "time": final_info[3],
                "status": final_info[4],
                "comment": final_info[5],
                "comment_time": final_info[6],
                "tno": final_info[7],
                "score": final_info[8],
                "score_comment": final_info[9],
                "score_time": final_info[10]
            }
            project_info_dict["status"] = final_info[4]
            # 将论文草稿列表添加至课题信息字典中
            project_info_dict.update(final_dict)
        else:
            # 如果未查找到结果，则论文草稿未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
        index += 1
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染论文草稿审阅页面
    return render(request, "teacher/supervisor/final_review.html", info_dict)


# 论文定稿审核功能
def review_final(request):
    """
    论文草稿审核功能，指导教师可在此审核学生提交的论文草稿
    :param request: HTTP请求
    :return redirect:
    """
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 从POST表单中获取审阅信息
    project_name = request.POST.get("project_name")
    comment = request.POST.get("comment")
    result = request.POST.get("result")
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新论文草稿表中的审阅信息
    cursor = db.cursor()
    if result == "通过":
        result = "已审核，待评阅"
    else:
        result = "未通过"
    cursor.execute("UPDATE Thesis_Final SET TFSTATUS = '" + result + "', TFCOMMENT = '" + comment +
                   "', TFCOMMENT_TIME = '" + now + "' WHERE PNAME = '" + project_name + "';")
    db.commit()
    # 重定向至论文草稿审阅页面
    return redirect("/teacher/supervisor/final_review/")


# TODO 毕设推荐页面
def project_recommendation(request):
    pass


# 毕设负责人模块
def manager(request):
    """
    毕设负责人模块，负责人可在此查看毕设进度，审核老师申报的课题及任务书
    :param request: HTTP请求
    :return: 渲染毕设负责人模块页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_manager = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有毕设负责人权限，无法访问。', 'name': info_dict["name"]})
    # 渲染毕设负责人模块页面
    return render(request, "teacher/manager/manager.html", info_dict)


# 申报课题审核页面
def project_review(request):
    """
    申报课题审核页面，负责人可在此审核老师申报的课题
    :param request: HTTP请求
    :return render: 渲染申报课题审核页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_manager = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有毕设负责人权限，无法访问。', 'name': info_dict["name"]})
    # 获取课题表中待审核的课题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE Pstatus = '待审核';")
    project_list = []
    # 遍历课题
    for num in range(cursor.rowcount):
        # 获取课题名称
        project_name = cursor.fetchone()[0]
        # 获取课题信息
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM PROJECT WHERE Pname = '" + project_name + "';")
        project_info = cursor2.fetchone()
        # 获取指导教师信息
        no = project_info[8]
        cursor2.execute("SELECT * FROM TEACHER WHERE TNO = '" + no + "';")
        teacher_info = cursor2.fetchone()
        # 构造课题信息字典
        project_info_dict = {
            "index": num,
            "name": project_info[0],
            "type": project_info[1],
            "info": project_info[2],
            "file": project_info[3],
            "time": project_info[4],
            "status": project_info[5],
            "comment": project_info[6],
            "comment_time": project_info[7],
            "supervisor": teacher_info[1],
            "tno": teacher_info[0]
        }
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染申报课题审核页面
    return render(request, "teacher/manager/project_review.html", info_dict)


# 申报项目审核功能
def pass_project(request):
    """
    申报项目审核功能，从POST表单中获取负责人审核相关信息，更新课题表中的课题状态
    :param request: HTTP请求
    :return project_review: 重定向至申报课题审核页面
    """
    # 获取课题名称
    project_name = request.POST.get("pname")
    # 获取课题状态
    result = request.POST.get("result")
    # 获取课题评语
    project_comment = request.POST.get("comment")
    # 获取课题评语时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新课题表中的课题状态
    cursor = db.cursor()
    if result == "通过":
        cursor.execute("UPDATE PROJECT SET Pstatus = '" + "待发布" + "', Pcomment = '" + project_comment +
                       "', Pcomment_time = '" + now + "' WHERE Pname = '" + project_name + "';")
    else:
        cursor.execute("UPDATE PROJECT SET Pstatus = '" + "审核未通过" + "', Pcomment = '" + project_comment +
                       "', Pcomment_time = '" + now + "' WHERE Pname = '" + project_name + "';")
    db.commit()
    # 重定向至申报课题审核页面
    return redirect('/teacher/manager/project_review/')


# 审核任务书页面
def task_review(request):
    """
    审核任务书页面，负责人可在此审核老师提交的任务书
    :param request: HTTP请求
    :return render: 渲染审核任务书页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有毕设负责人权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_manager = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有毕设负责人权限，无法访问。', 'name': info_dict["name"]})
    # 获取任务书表中待审核的任务书信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM TASK_BOOK WHERE TBstatus = '审核中';")
    project_list = []
    # 遍历任务书
    index = 0
    for num in range(cursor.rowcount):
        # 获取任务书信息
        task_info = cursor.fetchone()
        # 构造任务书信息字典
        task_info_dict = {
            "name": task_info[0],
            "content": task_info[1],
            "requirements": task_info[2],
            "goal": task_info[3],
            "management": task_info[4],
            "file": task_info[5],
            "time": task_info[6],
            "status": task_info[7],
            "comment": task_info[8],
            "comment_time": task_info[9]
        }
        # 获取课题名称
        project_name = task_info[0]
        # 获取课题信息
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM PROJECT_Student_Teacher WHERE Pname = '" + project_name + "';")
        project_info = cursor2.fetchone()
        # 构造课题信息字典
        project_info_dict = {
            "index": index,
            "name": project_info[0],
            "type": project_info[1],
            "student": project_info[2],
            "supervisor": project_info[3],
            "task_book": task_info_dict
        }
        index += 1
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染审核任务书页面
    return render(request, "teacher/manager/task_review.html", info_dict)


# 任务书审核功能
def pass_task(request):
    """
    任务书审核功能，从POST表单中获取负责人审核相关信息，更新任务书表中的任务书状态
    :param request: HTTP请求
    :return task_review: 重定向至审核任务书页面
    """
    # 获取课题名称
    project_name = request.POST.get("pname")
    # 获取任务书状态
    result = request.POST.get("result")
    # 获取任务书评语
    task_comment = request.POST.get("comment")
    # 获取任务书评语时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新任务书表中的任务书状态
    cursor = db.cursor()
    cursor.execute("UPDATE TASK_BOOK SET TBstatus = '" + result + "', TBcomment = '" + task_comment +
                   "', TBcomment_time = '" + now + "' WHERE Pname = '" + project_name + "';")
    db.commit()
    # 重定向至审核任务书页面
    return redirect('/teacher/manager/task_review/')


# 评阅教师分配页面
def reviewer_assignment(request):
    """
    评阅教师分配页面，负责人可在此为课题分配评阅教师
    :param request: HTTP请求
    :return render: 渲染评阅教师分配页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有毕设负责人权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_manager = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有毕设负责人权限，无法访问。', 'name': info_dict["name"]})
    # 从选题表中查询所有处于论文定稿已审核状态的课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT_STUDENT_TEACHER WHERE SPstatus = '论文定稿已审核';")
    project_list = []
    # 遍历课题
    for num in range(cursor.rowcount):
        # 获取论文信息
        project_info = cursor.fetchone()
        #  从毕业论文表查询评阅教师
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM THESIS_Final WHERE Pname = '" + project_info[0] + "';")
        thesis_info = cursor2.fetchone()
        if thesis_info[7] is not None:
            tno = thesis_info[7]
            status = "已分配"
        else:
            tno = ""
            status = "未分配"
        project_info_dict = {
            "index": num,
            "name": project_info[0],
            "type": project_info[1],
            "student": project_info[2],
            "supervisor": project_info[3],
            "tno": tno,
            "status": status
        }
        # 将论文信息字典添加至论文列表中
        project_list.append(project_info_dict)
    # 将论文列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 查询所有教师
    cursor3 = db.cursor()
    cursor3.execute("SELECT * FROM TEACHER;")
    teacher_list = []
    # 遍历教师
    for num in range(cursor3.rowcount):
        # 获取教师信息
        teacher_info = cursor3.fetchone()
        # 构造教师信息字典
        teacher_info_dict = {
            "no": teacher_info[0],
            "name": teacher_info[1],
            "faculty": teacher_info[4],
            "major": teacher_info[5],
            "title": teacher_info[6]
        }
        # 将教师信息字典添加至教师列表中
        teacher_list.append(teacher_info_dict)
    # 将教师列表添加至信息字典中
    info_dict["teacher_list"] = teacher_list
    # 渲染评阅教师分配页面
    return render(request, "teacher/manager/reviewer_assignment.html", info_dict)


# 评阅教师分配功能
def assign_reviewer(request):
    """
    评阅教师分配功能，从POST表单中获取课题名称和评阅教师工号，更新毕业论文表中的评阅教师字段
    :param request: HTTP请求
    :return redirect: 重定向至评阅教师分配页面
    """
    # 从POST表单中获取相关信息
    pname = request.POST.get("project_name")
    tno = request.POST.get("tno")
    # 更新毕业论文表中的评阅教师字段
    cursor = db.cursor()
    cursor.execute("UPDATE THESIS_Final SET Tno = '" + tno + "' WHERE Pname = '" + pname + "';")
    db.commit()
    # 重定向至评阅教师分配页面
    return redirect('/teacher/manager/reviewer_assignment/')


# 答辩组管理界面
def group_assignment(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有毕设负责人权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_manager = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有毕设负责人权限，无法访问。', 'name': info_dict["name"]})
    # 从答辩组表中查询所有答辩组
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Defense_Panel;")
    group_list = []
    # 遍历答辩组
    for num in range(cursor.rowcount):
        # 获取答辩组信息
        group_info = cursor.fetchone()
        # 构造答辩组信息字典
        group_info_dict = {
            "index": num,
            "name": group_info[0],
            "location": group_info[1],
            "date": group_info[2],
            "leader": group_info[3],
            "secretary": group_info[4],
            "faculty": group_info[5],
            "time": group_info[6]
        }
        # 查询答辩组的答辩学生
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM Defense_Student WHERE DPname = '" + group_info[0] + "';")
        student_list = []
        # 遍历答辩学生
        group_info_dict['count'] = cursor2.rowcount
        for num2 in range(cursor2.rowcount):
            # 获取答辩学生信息
            student_info = cursor2.fetchone()
            # 构造答辩学生信息字典
            # 从学生表中查询学生详细信息
            cursor3 = db.cursor()
            cursor3.execute("SELECT * FROM STUDENT WHERE SNO = '" + student_info[1] + "';")
            student_info2 = cursor3.fetchone()
            student_info_dict = {
                "no": student_info[1],
                "name": student_info2[1],
                "faculty": student_info2[4],
                "major": student_info2[5],
            }
            # 将答辩学生信息字典添加至答辩学生列表中
            student_list.append(student_info_dict)
        # 查询答辩组成员
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM Panel_Member WHERE DPname = '" + group_info[0] + "';")
        member_list = []
        # 遍历答辩组成员
        for num2 in range(cursor2.rowcount):
            # 获取答辩组成员信息
            member_info = cursor2.fetchone()
            # 构造答辩组成员信息字典
            # 从教师表查询成员详细信息
            cursor3 = db.cursor()
            cursor3.execute("SELECT * FROM TEACHER WHERE TNO = '" + member_info[1] + "';")
            member_info2 = cursor3.fetchone()
            member_info_dict = {
                "no": member_info[1],
                "name": member_info2[1],
                "title": member_info2[6],
                "faculty": member_info2[4],
                "major": member_info2[5],
                "time": member_info[2]
            }
            # 将答辩组成员信息字典添加至答辩组成员列表中
            member_list.append(member_info_dict)
        group_info_dict["member_list"] = member_list
        # 将答辩组信息字典添加至答辩组列表中
        group_list.append(group_info_dict)
    # 将答辩组列表添加至信息字典中
    info_dict["group_list"] = group_list
    # 从选题表中获取所有进行到论文定稿已评阅状态的课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student_Teacher WHERE SPstatus = '论文定稿已评阅';")
    student_list = []
    # 遍历所有课题
    for num in range(cursor.rowcount):
        # 构造学生信息字典
        student_info = cursor.fetchone()
        student_info_dict = {
            "project": student_info[0],
            "type": student_info[1],
            "student": student_info[2],
            "supervisor": student_info[3],
        }
        # 将学生信息字典添加至学生列表中
        student_list.append(student_info_dict)
    # 将学生列表添加至信息字典中
    info_dict["student_list"] = student_list
    # 渲染答辩组管理页面
    return render(request, "teacher/manager/group_assignment.html", info_dict)


# 建立答辩组功能
def assign_group(request):
    # 从POST请求中获取答辩组信息
    group_name = request.POST.get("group_name")
    group_location = request.POST.get("group_location")
    group_date = request.POST.get("group_date")
    group_leader = request.POST.get("group_leader")
    group_secretary = request.POST.get("group_secretary")
    group_faculty = request.POST.get("group_faculty")
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 将答辩组信息插入答辩组表中
    cursor = db.cursor()
    cursor.execute("INSERT INTO Defense_Panel VALUES ('" + group_name + "', '" + group_location + "', '" +
                   group_date + "', '" + group_leader + "', '" + group_secretary + "', '" + group_faculty + "', '" + now + "');")
    # 从POST表单中获取答辩成员信息
    id_list = request.POST.getlist("group_member_id")
    name_list = request.POST.getlist("group_member_name")
    # 遍历答辩成员列表
    for num in range(len(id_list)):
        # 将答辩成员信息插入答辩组成员表中
        cursor.execute("INSERT INTO Panel_Member VALUES ('" + group_name + "', '" + id_list[num] + "', '" + now + "');")
    # 提交数据库事务
    db.commit()
    # 重定向至答辩组管理页面
    return redirect("/teacher/manager/group_assignment/")


# 答辩组分配学生功能
def assign_student(request):
    # 从POST表单中获取分配数据
    dpname = request.POST.get("dp_name")
    sname = request.POST.get("sname")
    # 从学生表中查询学生信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM STUDENT WHERE SName = '" + sname + "';")
    sno = cursor.fetchone()[0]
    # 获取当前时间
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 往答辩学生表中插入分配数据
    cursor = db.cursor()
    cursor.execute("INSERT INTO Defense_Student(DPname,Sno,DStime) VALUES ('" + dpname
                   + "', '" + sno + "', '" + now + "');")
    # 提交数据库事务
    db.commit()
    # 重定向至答辩组管理页面
    return redirect("/teacher/manager/group_assignment/")


# 重新分配答辩组功能
def reassign_group(request):
    # 从POST请求中获取答辩组信息
    group_name = request.POST.get("group_name")
    group_location = request.POST.get("group_location")
    group_date = request.POST.get("group_date")
    group_leader = request.POST.get("group_leader")
    group_secretary = request.POST.get("group_secretary")
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 修改答辩组信息
    cursor = db.cursor()
    cursor.execute("UPDATE Defense_Panel SET DPlocation = '" + group_location + "', DPdate = '" + group_date +
                   "', DPleader = '" + group_leader + "', DPsecretary = '" + group_secretary + "', DPtime = '" + now +
                   "' WHERE DPname = '" + request.POST.get("group_name") + "';")
    # 提交数据库事务
    db.commit()
    # 重定向至答辩组管理页面
    return redirect("/teacher/manager/group_assignment/")


# 教学院长模块主页
def dean(request):
    """
    教学院长模块主页
    :param request: HTTP请求
    :return render: 渲染教学院长模块主页
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_dean = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有教学院长权限，无法访问。', 'name': info_dict["name"]})
    # 渲染教学院长模块主页
    return render(request, "teacher/dean/dean.html", info_dict)


# 发布双选结果页面
def project_announcement(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_dean = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有教学院长权限，无法访问。', 'name': info_dict["name"]})
    # 从课题表中获取所有待发布的课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE Pstatus = '待发布'")
    project_list = []
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        # 获取课题名称
        project_name = project_info[0]
        # 获取指导教师信息
        no = project_info[8]
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM TEACHER WHERE TNO = '" + no + "';")
        teacher_info = cursor2.fetchone()
        # 构造课题信息字典
        project_info_dict = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": teacher_info[1],
            "no": teacher_info[0]
        }
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染发布双选结果页面
    return render(request, "teacher/dean/project_announcement.html", info_dict)


# 发布课题功能
def announce_project(request):
    """
    发布课题功能，从POST表单中获取课题名称，更新课题表中的课题状态
    :param request: HTTP请求
    :return: 重定向至发布双选结果页面
    """
    project_name = request.POST["project_name"]
    cursor = db.cursor()
    cursor.execute("UPDATE PROJECT SET Pstatus = '已发布' WHERE Pname = '" + project_name + "';")
    db.commit()
    return project_announcement(request)


# 公布双选结果页面
def result_announcement(request):
    """
    公布双选结果页面，教学院长可在从公布双选结果
    :param request: HTTP请求
    :return: 渲染公布双选结果页面
    """
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_dean = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有教学院长权限，无法访问。', 'name': info_dict["name"]})
    # 获取课选题表中所有处于选题已被确认阶段的课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SPstatus = '选题已被确认'")
    # 初始化课题列表
    project_list = []
    # 遍历课选题表中所有处于选题已被确认阶段的课题
    for num in range(cursor.rowcount):
        # 获取课题信息
        select_project_info = cursor.fetchone()
        # 从课题-老师-学生视图中获取课题信息
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM PROJECT_STUDENT_TEACHER WHERE Pname = '" +
                        select_project_info[1] + "';")
        project_info = cursor2.fetchone()
        # 构成课题信息字典
        project_info_dict = {
            "name": project_info[0],
            "type": project_info[1],
            "student": project_info[2],
            "supervisor": project_info[3]
        }
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染公布双选结果页面
    return render(request, "teacher/dean/result_announcement.html", info_dict)


# 公布双选结果功能
def announce_result(request):
    """
    公布双选结果功能，从POST表单中获取课题名称，更新课题表中的课题状态
    :param request: HTTP请求
    :return: 重定向至公布双选结果页面
    """
    # 获取双选信息
    project_name = request.POST["project_name"]
    # 更新选题表
    cursor = db.cursor()
    cursor.execute(
        "UPDATE SELECT_PROJECT SET SPstatus = '双选结果已公布' WHERE Pname = '" +
        project_name + "';")
    db.commit()
    # 重定向至发布双选结果页面
    return redirect("/teacher/dean/result_announcement/")


# 教学秘书模块
# 教学秘书主页
def secretary_index(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有指导教师权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_teaching_secretary = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有权限，无法访问。', 'name': info_dict["name"]})
    # 渲染教学秘书主页
    return render(request, "teacher/secretary/index.html", info_dict)


# 论文评阅页面
def thesis_score(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有答辩秘书权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_teaching_secretary = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有答辩秘书权限，无法访问。', 'name': info_dict["name"]})
    # 从毕业论文表中查询所有以该老师为评阅教师的论文
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Thesis_Final WHERE TNO = '" + info_dict["no"] + "';")
    # 初始化论文列表
    thesis_list = []
    # 遍历论文信息，构造论文列表
    for thesis_index in range(cursor.rowcount):
        # 获取论文信息
        thesis_info = cursor.fetchone()
        # 从课题-学生-教师表中查询课题信息
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Project_Student_Teacher WHERE Pname = '" + thesis_info[0] + "';")
        project_info = cursor1.fetchone()
        if thesis_info[10] is None:
            comment_time = ""
        else:
            comment_time = thesis_info[10].strftime("%Y-%m-%d %H:%M:%S")
        # 构造论文信息字典
        thesis_info_dict = {
            "index": thesis_index,
            "name": thesis_info[0],
            "type": project_info[1],
            "student": project_info[2],
            "supervisor": project_info[3],
            "content": thesis_info[1],
            "file": thesis_info[2],
            "time": thesis_info[3].strftime("%Y-%m-%d %H:%M:%S"),
            "status": thesis_info[4],
            "score": thesis_info[8],
            "comment": thesis_info[9],
            "score_time": comment_time
        }
        # 将论文信息字典添加至论文列表中
        thesis_list.append(thesis_info_dict)
    # 将论文列表添加至信息字典中
    info_dict["project_list"] = thesis_list
    # 渲染论文评阅页面
    return render(request, "teacher/secretary/thesis_score.html", info_dict)


# 论文评阅功能
def score_thesis(request):
    # 从POST表单中获取相关数据
    project_name = request.POST.get("project_name")
    score = request.POST.get("score")
    comment = request.POST.get("comment")
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新毕业论文表中的评阅信息
    cursor = db.cursor()
    cursor.execute("UPDATE Thesis_Final SET TFscore = '" + score + "', TFstatus = '已评阅', TFscore_comment = '"
                   + comment + "', TFscore_time = '" + now + "' WHERE Pname = '" + project_name + "';")
    db.commit()
    # 重定向至论文评阅页面
    return redirect("/teacher/secretary/thesis_score/")


# 答辩得分录入页面
def defense_score(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有答辩秘书权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_teaching_secretary = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有答辩秘书权限，无法访问。', 'name': info_dict["name"]})
    # 调用存储过程，获取以该教师为答辩秘书的所有答辩课题信息
    cursor = db.cursor()
    cursor.execute("CALL GET_DEFENSE_PROJECT('" + info_dict['name'] + "');")
    # 初始化课题列表
    project_list = []
    # 遍历课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        # 如果课题已评阅，则将评阅时间转换为字符串
        if project_info[10] is None:
            status = "未录入"
            score_time = ""
        else:
            status = "已录入"
            score_time = project_info[10].strftime("%Y-%m-%d %H:%M:%S")
        # 构造课题信息字典
        project_dict = {
            "index": project_index,
            "name": project_info[0],
            "type": project_info[1],
            "no": project_info[2],
            "student": project_info[3],
            "supervisor": project_info[4],
            "faculty": project_info[5],
            "major": project_info[6],
            "class": project_info[7],
            "comment": project_info[8],
            "score": project_info[9],
            "score_time": score_time,
            "status": status
        }
        # 将课题信息字典添加至课题列表中
        project_list.append(project_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染答辩得分录入页面
    return render(request, "teacher/secretary/defense_score.html", info_dict)


# 答辩成绩录入功能
def score_defense(request):
    # 从POST表单中获取相关数据
    student_no = request.POST.get("student_no")
    score = request.POST.get("score")
    comment = request.POST.get("comment")
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新毕业论文表中的评阅信息
    cursor = db.cursor()
    cursor.execute("UPDATE Defense_Student SET DSscore = '" + score + "', DSstatus = '已发布', DScomment = '"
                   + comment + "', DSscore_time = '" + now + "' WHERE Sno = '" + student_no + "';")
    db.commit()
    # 重定向至论文评阅页面
    return redirect("/teacher/secretary/defense_score/")


# 总评成绩公布页面
def score_announcement(request):
    # 如果未登录，则重定向至登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 从session中获取用户信息，并构造信息字典
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no'],
        'comment_list': get_comment_list()
    }
    # 身份检查
    if info_dict["role"] == "学生":
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # 检查用户是否有答辩秘书权限
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_teaching_secretary = '是';")
    if curse.rowcount == 0:
        return render(request, "announce.html",
                      {'message': '您没有答辩秘书权限，无法访问。', 'name': info_dict["name"]})
    # 调用存储过程，获取所有以该老师为答辩秘书课题总评信息
    cursor = db.cursor()
    cursor.execute("CALL GET_SCORE('" + info_dict['name'] + "');")
    # 初始化课题列表
    project_list = []
    # 遍历课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        # 构造课题信息字典
        project_dict = {
            "index": project_index,
            "name": project_info[0],
            "type": project_info[1],
            "no": project_info[2],
            "student": project_info[3],
            "supervisor": project_info[4],
            "defense_score": project_info[5],
            "thesis_score": project_info[6],
            "status": project_info[7]
        }
        total_score = project_dict['defense_score'] * 0.6 + project_dict['thesis_score'] * 0.4
        project_dict['total_score'] = int(total_score)
        # 将课题信息字典添加至课题列表中
        project_list.append(project_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染总评成绩公布页面
    return render(request, "teacher/secretary/score_announcement.html", info_dict)


# 公布总评成绩功能
def announce_score(request):
    # 从POST表单中获取相关数据
    project_name = request.POST.get("project_name")
    # 更新选题表信息，将课题状态更改为已完成
    cursor = db.cursor()
    cursor.execute("UPDATE Select_Project SET SPstatus = '已完成' WHERE Pname = '" + project_name + "';")
    db.commit()
    # 重定向至总评成绩公布页面
    return redirect("/teacher/secretary/score_announcement/")
