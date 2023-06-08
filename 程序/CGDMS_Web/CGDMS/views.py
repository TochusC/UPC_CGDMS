import datetime
import os

import pymysql
from django.shortcuts import render, redirect

db = pymysql.connect(host='localhost',
                     user='root',
                     password='wue789789',
                     database='cgdms')


# 通用模块
# 登录页面，网站的初始页面
def login_page(request):
    """
    登录页面，网站的初始页面
    :param request:HTTP请求
    :return render:渲染登录页面
    """
    return render(request, "login_page.html")


# 登录功能，验证用户名和密码，并把用户信息存入session
def login(request):
    """
    登录功能，验证用户名和密码，并把用户信息存入session
    :param request: HTTP请求
    :return redirect:重定向至主页
    """
    # 从数据库中验证用户名和密码
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM user WHERE Uno = '" + request.POST['Uno'] + "' AND Upassword = '" + request.POST['Upwd'] + "';")
    # 如果查询到结果
    if cursor.rowcount == 1:
        # 获取账号信息
        account_info = cursor.fetchone()
        uno = account_info[0]
        user_role = account_info[2]
        # 依据账户身份的不同，分别从不同的表中查询信息
        if user_role == '学生':
            cursor.execute("SELECT * FROM STUDENT WHERE UNO = '" + uno + "';")
        else:
            cursor.execute("SELECT * FROM TEACHER WHERE UNO = '" + uno + "';")
        # 获取个人信息
        self_info = cursor.fetchone()
        # 将个人信息存入session
        request.session['uno'] = uno
        request.session['role'] = role
        request.session['no'] = self_info[0]
        request.session['name'] = self_info[1]
        # 重定向到主页
        redirect('/index/')
    # 如果查询不到结果,则说明用户名或密码错误
    else:
        # 返回页面，并提示错误信息
        return render(request, "announce.html",
                      {'message': '登录失败！请检查您的用户名和密码。'})


# 注册页面（未实装）//TODO
def register_page(request):
    pass


# 注册功能（未实装）//TODO
def register(request):
    pass


# 退出登录功能，清除session
def logout(request):
    """
    退出登录功能，清除session，并重定向至登录页面
    :param request: HTTP请求
    :return redirect: 重定向至登录界面
    """
    request.session.flush()
    return redirect('/login_page/')


# 主页
def index(request):
    """
    主页，显示登录用户的个人信息
    :param request: HTTP请求
    :return render: 渲染主页
    """
    # 如果没有登录，则重定向到登录页面
    if 'uno' not in request.session:
        return redirect('')
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no']
    }
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
    # 获取表中的个人信息
    cursor = db.cursor()
    if request.session['role'] == '教师':
        # 从教师表中获取个人信息
        cursor.execute("SELECT * FROM TEACHER WHERE UNO = '" + request.session['uno'] + "';")
        no, name, gender, birth, fname, mname, cname, username = cursor.fetchone()
        # 构造个人信息字典
        self_info = {
            "gender": gender,
            "birth": birth,
            "fname": fname,
            "mname": mname,
            "cname": cname
        }
    else:
        # 从学生表中获取个人信息
        cursor.execute("SELECT * FROM STUDENT WHERE UNO = '" + request.session['uno'] + "';")
        no, name, gender, birth, fname, mname, tittle, username = cursor.fetchone()
        # 构造个人信息字典
        self_info = {
            "gender": gender,
            "birth": birth,
            "fname": fname,
            "mname": mname,
            "tittle": tittle,
        }
    # 获取session中的用户信息
    info_dict = {
        'uno': request.session['uno'],
        'role': request.session['role'],
        'name': request.session['name'],
        'no': request.session['no']
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
        'no': request.session['no']
    }
    # 获取账户的注册时间
    cursor = db.cursor()
    cursor.execute("SELECT Utime FROM USER WHERE UNO = '" + request.session['uno'] + "';")
    info_dict['time'] = cursor.fetchone()[0]
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
        'no': request.session['no']
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
        'no': request.session['no']
    }
    # 检查用户的身份
    if info_dict["role"] == "学生":
        # 如果是学生，则渲染学生主页
        return render(request, "student/student_index.html", info_dict)
    else:
        # 如果不是学生，则返回错误信息
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': info_dict})


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
        'no': request.session['no']
    }
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
    cursor.execute("SELECT * FROM PUBLISHED_PROJECT WHERE Pstatus = '已发布'")
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        # 构造课题字典
        project = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": project_info[2],
            "selected_times": project_info[3],
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
        'no': request.session['no']
    }
    # 获取POST表单中的课题名称
    project_name = request.POST["project_name"]
    # 查询学生的预选课题数量
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Pre_Select WHERE SNO = '" + info_dict["no"] + "'")
    # 如果预选课题数量已达到3个，则返回错误信息
    if cursor.rowcount == 3:
        return render(request, "announce.html", {'message': '您已选满三个预选项目！', 'name': info_dict["name"]})
    # 否则，将该课题加入预选表
    cursor.execute("INSERT INTO Pre_Select VALUES ('" + info_dict["no"] + "','"
                   + project_name + "','" + str(cursor.rowcount + 1) + "');")
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
    cursor.execute("DELETE FROM Pre_Select WHERE SNO = '" + self_info["no"] + "' AND PNAME = '" + pname + "';")
    # 提交事务
    db.commit()
    # 重定向至选题界面
    return redirect("/student/project_selection")


# 功能函数，实现课题所处阶段的检查功能，用于判断相关操作是否可进行
def status_check(status, stage):
    """
    实现课题所处阶段的检查功能，用于判断相关操作是否可进行
    :param status: 字符串，表示课题所处状态
    :param stage: 字符串，相关操作所处阶段
    :return string: 返回字符串，表示操作是否可进行
    """
    status_dict = {
        "选题已被确认": 0,
        "双选结果已被公布": 1,
        "已下达任务书": 2,
        "任务书已审核": 3,
        "已提交开题报告": 4,
        "开题报告已被审核": 5,
        "已提交中期检查": 6,
        "中期检查已被审核": 7,
        "已提交论文草稿": 8,
        "论文草稿已被审核": 9,
        "已提交论文定稿": 10,
        "论文定稿已被审核": 11,
        "已进行答辩": 12,
        "已完成": 13
    }
    stage_dict = {
        "任务书": 1,
        "开题报告": 2,
        "中期检查": 3,
        "论文草稿": 4,
        "论文定稿": 5,
        "答辩": 6
    }
    status_index = status_dict[status]
    if status_index < stage_dict[stage]:
        if status_index == 0:
            return '''访问拒绝，课题正处于'指导教师确认'阶段。'''
        elif status_index == 1:
            return '''访问拒绝，课题正处于'双选结果公布'阶段。'''
        elif status_index == 2:
            return '''访问拒绝，课题正处于'任务书下达'阶段。'''
        elif status_index == 3:
            return '''访问拒绝，课题正处于'任务书审核'阶段。'''
        elif status_index == 4:
            return '''访问拒绝，课题正处于'开题报告提交'阶段。'''
        elif status_index == 5:
            return '''访问拒绝，课题正处于'开题报告审核'阶段。'''
        elif status_index == 6:
            return '''访问拒绝，课题正处于'中期检查提交'阶段。'''
        elif status_index == 7:
            return '''访问拒绝，课题正处于'中期检查审核'阶段。'''
        elif status_index == 8:
            return '''访问拒绝，课题正处于'论文草稿提交'阶段。'''
        elif status_index == 9:
            return '''访问拒绝，课题正处于'论文草稿审核'阶段。'''
        elif status_index == 10:
            return '''访问拒绝，课题正处于'论文定稿提交'阶段。'''
        elif status_index == 11:
            return '''访问拒绝，课题正处于'论文定稿审核'阶段。'''
        elif status_index == 12:
            return '''访问拒绝，课题正处于'答辩'阶段。'''
    else:
        return "操作允许"


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
        'no': request.session['no']
    }
    # 获取该学生的选题信息,检查该学生是否选题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果查询到结果，则程序继续进行，否则则该学生未选题，返回错误信息
    if cursor.rowcount == 1:
        # 获取选题信息
        select_info = cursor.fetchone()
        # 检查选题的所处阶段，是否已经到达任务书阶段
        status = select_info[3]
        message = status_check(status, "任务书")
        # 如果不允许操作，则返回错误信息
        if not message == "操作允许":
            return render(request, 'student/announce.html', {'message': message, 'name': info_dict['name']})
        # 获取项目名称
        pname = select_info[1]
        # 从任务书表中，获取项目的任务书信息
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Task_Book WHERE PNAME = '" + pname + "'")
        # 如果任务书存在,则程序继续进行，获取任务书信息，否则返回错误信息
        if cursor1.rowcount == 1:
            # 获取任务书信息
            task_book_info = cursor1.fetchone()
            # 如果任务书已审核
            if task_book_info[7] == "通过":
                # 构造任务书字典
                task_book = {
                    'name': task_book_info[0],
                    "content": task_book_info[1],
                    "requirement": task_book_info[2],
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
                # 如果任务书未审核，则返回错误信息
                return render(request, "announce.html",
                              {'message': '指导教师下达的任务书正在审核中...', 'name': info_dict["name"]})
        else:
            # 如果任务书不存在，则返回错误信息
            return render(request, "announce.html", {'message': '指导教师尚未下达任务书...', 'name': info_dict["name"]})
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
        'no': request.session['no']
    }
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[3]
        message = status_check(selected_project_info[3], "开题报告")
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
            open_report_info = cursor.fetchone()
            open_report_dict = {
                'content': open_report_info[1],
                'file': open_report_info[2],
                'time': open_report_info[3],
                'status': open_report_info[4],
                'comment': open_report_info[5],
                'comment_time': open_report_info[6],
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
        'no': request.session['no']
    }
    # 初始化附件路径
    path = ""
    # 获取课题名称
    project_name = request.POST["project_name"]
    # 获取开题报告内容
    report_content = request.POST["report_content"]
    attachment = request.FILES["attachment"]
    # 获取当前时间
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    # 初始化数据库游标，准备修改数据
    cursor = db.cursor()
    # 检查用户是提交开题报告还是修改开题报告
    if request.POST["status"] == "未提交":
        cursor.execute("INSERT INTO OPEN_REPORT VALUES ('" + project_name + "', '" + report_content +
                       "', '" + path + "', '" + now + "', '待审核', '', '')")
    else:
        # 删除原有附件
        cursor.execute("SELECT * FROM OPEN_REPORT WHERE PNAME = '" + project_name + "'")
        open_report_info = cursor.fetchone()
        if open_report_info[2] is not "":
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "open_report",
                                open_report_info[2])
            os.remove(path)
        # 更新开题报告信息
        cursor.execute("UPDATE OPEN_REPORT SET ORcontent = '" + report_content + "', ORfile = '" + path
                       + "', ORtime = '" + now + "', ORstatus = '待审核' WHERE PNAME = '" + project_name + "'")
    # 如果含有附件，则写入附件
    if attachment is not "":
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
        'no': request.session['no']
    }
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[3]
        message = status_check(selected_project_info[3], "开题报告")
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
                'time': middle_check_info[3],
                'status': middle_check_info[4],
                'comment': middle_check_info[5],
                'comment_time': middle_check_info[6],
            }
            # 更新信息字典
            info_dict['status'] = "已提交"
            info_dict['open_report'] = middle_check_dict
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
        'no': request.session['no']
    }
    # 初始化附件路径
    path = ""
    # 获取课题名称
    project_name = request.POST["project_name"]
    # 获取中期检查内容
    progress_info = request.POST["middle_check"]
    attachment = request.FILES["attachment"]
    # 获取当前时间,并格式化为时间戳
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    # 初始化数据库游标，准备修改数据
    cursor = db.cursor()
    # 检查用户是提交开题报告还是修改开题报告
    if request.POST["status"] == "未提交":
        # 插入开题报告信息
        cursor.execute("INSERT INTO Middle_CHECK VALUES ('" + project_name + "', '" + progress_info + "', '"
                       + path + "', '" + now + "', '待审核', NULL, NULL)")
    else:
        # 删除原有附件
        cursor.execute("SELECT * FROM OPEN_REPORT WHERE PNAME = '" + project_name + "'")
        middle_check_info = cursor.fetchone()
        if middle_check_info[2] is not "":
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "open_report",
                                middle_check_info[2])
            os.remove(path)
        # 更新开题报告信息
        cursor.execute("UPDATE OPEN_REPORT SET MCcontent = '" + progress_info + "', MCfile = '" + path
                       + "', MCtime = '" + now + "', MCstatus = '待审核' WHERE PNAME = '" + project_name + "'")
    # 如果含有附件，则写入附件
    if attachment is not "":
        path = os.path.join("static", "upload", "student" + info_dict['no'] + "middle_check")
        write_attachment(attachment, path)
    # 提交修改
    db.commit()
    # 重定向至开题报告页面
    return redirect('/student/open_report/')


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
        'no': request.session['no']
    }
    # 获取该学生的选题信息，检查学生是否已选题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 检查选题状态，是否允许操作
        status = selected_project_info[3]
        message = status_check(selected_project_info[3], "开题报告")
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
            # 构造周进度报告信息字典
            weekly_report_dict = {
                'content': weekly_report_info[1],
                'file': weekly_report_info[2],
                'time': weekly_report_info[3],
                'status': weekly_report_info[4],
                'comment': weekly_report_info[5],
                'comment_time': weekly_report_info[6],
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
        'no': request.session['no']
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
                       + "','" + path + "','" + now + "','审核中','','')")
    elif action == "修改":
        # 获取当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 获取要修改的周进度报告的提交时间
        submit_time = request.POST.get('submit_time')
        # 获取原有附件路径，并删除原有附件
        cursor = db.cursor()
        cursor.execute("SELECT ATTACHMENT FROM Weekly_Report WHERE PNAME = '" + project_name +
                       "' AND WRtime = '" + submit_time + "'")
        attachment_path = cursor.fetchone()[2]
        # 如果原有附件不为空，则删除原有附件
        if not attachment_path == "":
            os.remove(attachment_path)
        # 如果含有附件，则写入附件
        if report_attachment is not None:
            path = os.path.join("static", "upload", "student" + info_dict['no'] + "weekly_report")
            write_attachment(report_attachment, path)
        # 更新周进度报告信息
        cursor = db.cursor()
        cursor.execute("UPDATE Weekly_Report SET CONTENT = '" + report_content + "', ATTACHMENT = '" + path
                       + "', TIME = '" + now + "', WRstatus = '审核中' WHERE PNAME = '" + project_name + "'")
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
        'no': request.session['no']
    }
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息
        selected_project_info = cursor.fetchone()
        # 获取毕业论文草稿信息
        cursor = db.cursor()
        cursor.execute("SELECT * FROM THESIS_DRAFT WHERE PNAME = '" + selected_project_info[1] + "'")
        # 检查学生是否已提交毕业论文（草稿）
        if cursor.rowcount == 1:
            # 如果查询到结果，则说明学生已提交毕业论文（草稿）,此时获取论文草稿信息
            thesis_draft_info = cursor.fetchone()
            # 构造毕业论文字典，以供修改
            thesis_draft_dict = {
                'content': thesis_draft_info[1],
                'time': thesis_draft_info[2],
                'status': thesis_draft_info[3],
                'comment': thesis_draft_info[4],
                'comment_time': thesis_draft_info[5],
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
        'no': request.session['no']
    }
    # 获取论文草稿相关信息
    project_name = request.POST('project_name')
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
                       path + "','" + now + "','审核中','','')")
    else:
        # 获取原有附件路径，如果路径不为空，删除原有附件
        cursor = db.cursor()
        cursor.execute("SELECT ATTACHMENT FROM THESIS_DRAFT WHERE PNAME = '" + project_name + "'")
        path = cursor.fetchone()[0]
        if path is not "":
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
        'no': request.session['no']
    }
    # 获取该学生的选题信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" +
                   info_dict["no"] + "'")
    # 如果学生已选题
    if cursor.rowcount == 1:
        # 获取选题信息，并从中获取学生所选课题名称
        selected_project_info = cursor.fetchone()
        pname = selected_project_info[1]
        # 尝试获取该学生的毕业论文定稿信息，检查该学生是否提交论文定稿
        cursor.execute("SELECT * FROM THESIS_FINAL WHERE PNAME = '" + pname + "'")
        # 如果查询到结果，则学生已提交论文定稿
        if cursor.rowcount == 1:
            # 更新信息字典，将状态改为已提交
            info_dict['status'] = "已提交"
            # 获取毕业论文定稿信息
            thesis_final_info = cursor.fetchone()
            # 获取评阅教师信息
            cursor.execute("SELECT * FROM TEACHER WHERE TNO = '" + thesis_final_info[7] + "'")
            teacher_info = cursor.fetchone()
            # 构造毕业论文定稿字典，以便在页面中显示，供学生修改
            thesis_final_dict = {
                "content": thesis_final_info[1],
                "file": thesis_final_info[2],
                "time": thesis_final_info[3],
                "status": thesis_final_info[4],
                "comment": thesis_final_info[5],
                "comment_time": thesis_final_info[6],
                "reviewer": teacher_info[1],
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
        'no': request.session['no']
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
        cursor.execute("SELECT FILE FROM THESIS_FINAL WHERE PNAME = '" + project_name + "'")
        thesis_final_info = cursor.fetchone()
        if thesis_final_info[2] != "":
            os.remove(thesis_final_info[2])
        # 初始化游标，向数据库中插入毕业论文定稿数据
        cursor = db.cursor()
        cursor.execute("UPDATE THESIS_FINAL SET CONTENT = '" + content + "', FILE = '" +
                       path + "','" + now + "' WHERE PNAME = '" + project_name + "'")
    # 如果附件不为空，则将附件保存至指定路径
    if attachment is not None:
        write_attachment(path, attachment)
    # 提交事务
    db.commit()
    # 重定向至提交论文定稿页面
    return redirect("/student/thesis_final/")


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
        'no': request.session['no']
    }
    # 检查用户身份是否是教师
    if info_dict["role"] == "教师":
        return render(request, "teacher/teacher_index.html", info_dict)
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})


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
        'no': request.session['no']
    }
    # 检查用户身份是否是教师
    if info_dict["role"] == "教师":
        # 检查用户是否有指导教师权限
        curse = db.cursor()
        curse.execute("SELECT * FROM ROLE WHERE TNO = '" + info_dict["no"] + "' AND is_supervisor = '是';")
        if curse.rowcount == 1:
            return render(request, "teacher/supervisor/supervisor.html", info_dict)
        else:
            return render(request, "announce.html",
                          {'message': '您没有指导教师权限，无法访问。', 'name': info_dict["name"]})
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})


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
        'no': request.session['no']
    }
    # 检查用户身份是否是教师
    if info_dict["role"] == "教师":
        # 初始化课题列表
        project_list = []
        # 获取教师所有已申报课题
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "';")
        for project in cursor.fetchall():
            # 构造课题信息字典
            project_info = {
                'name': project[0],
                'type': project[1],
                'info': project[2],
                'file': project[3],
                'status': project[4],
                'comment': project[5],
                'comment_time': project[6],
                'time': project[8]
            }
            # 将课题信息字典添加至课题列表
            project_list.append(project_info)
        # 将课题列表添加至信息字典
        info_dict["project_list"] = project_list
        # 渲染申报课题页面
        return render(request, "teacher/supervisor/project_proposal.html", info_dict)
    else:
        # 如果用户角色不是老师，则渲染通知页面
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})


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
        'no': request.session['no']
    }
    # 从POST表单中获取课题相关信息
    project_name = request.POST["project_name"]
    project_type = request.POST["project_type"]
    project_info = request.POST["project_info"]
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
        # 更新课题信息
        cursor.execute("UPDATE PROJECT SET Pname = '" + project_name + "', Ptype = '" + project_type + "', Pinfo = '" +
                       project_info + "', Ptime = '" + now + "', Pstatus = '待审核'"
                                                             " WHERE Pname = '" + old_project_name + "';")
        return redirect('/teacher/supervisor/project_proposal/')
    else:
        cursor.execute("INSERT INTO PROJECT VALUES ('" + project_name + "','" +
                       project_type + "','" + project_info + "','" + "','待审核" + "','" + info_dict["no"] + "');")
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
        'no': request.session['no']
    }
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
    return render(request, "teacher/supervisor/project_confirmation.html", pre_selection_info)


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
    cursor.execute("CALL CONFIRM_SELECT('" + sno + "','" + pname + "');")
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
    cursor.execute("CALL CANCEL_CONFIRM('" + sno + "','" + pname + "');")
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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
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
        'no': request.session['no']
    }
    # 从POST表单中获取课题名称
    pname = request.POST["project_name"]
    # 从POST表单中获取课题任务书信息
    content = request.POST["content"]
    requirements = request.POST["requirements"]
    goal = request.POST["goal"]
    management = request.POST["management"]
    attachment = request.FILES.get("attachment")
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
                       "', '" + goal + "', '" + management + "', '" + path + "', '', '审核中', '', '');")
    # 如果用户操作类型为修改，则将课题任务书信息更新至数据库中
    else:
        # 将课题任务书信息更新至数据库中
        cursor.execute("UPDATE Task_Book SET Content = '" + content + "', Requirements = '" + requirements +
                       "', Goal = '" + goal + "', Management = '" + management + "', File = '" + path +
                       "', Status = '审核中' WHERE PNAME = '" + pname + "';")
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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 从开题报告表中查找该课题的开题报告信息
        cursor.execute("SELECT * FROM Open_Report WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则开题报告已存在，构造开题报告信息字典，以供教师查看审阅
        if cursor.rowcount == 1:
            # 获取开题报告信息
            open_report_info = cursor.fetchone()
            # 构造开题报告信息字典
            open_report_dict = {
                "content": open_report_info[1],
                "file": open_report_info[2],
                "time": open_report_info[3],
                "status": open_report_info[4],
                "comment": open_report_info[5],
                "comment_time": open_report_info[6]
            }
            project_info_dict["status"] = open_report_info[4]
            # 将开题报告信息字典添加至已选课题信息字典中
            project_info_dict["open_report"] = open_report_dict
        else:
            # 如果未查找到结果，则开题报告未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list[project_index] = project_info_dict
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
    cursor.execute("UPDATE Open_Report SET Status = '" + result + "', Comment = '"
                   + comment + "', Comment_Time = '" + comment_time + "' WHERE PNAME = '" + pname + "';")
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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")

    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
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
            mid_term_dict = {
                "content": mid_term_info[1],
                "file": mid_term_info[2],
                "time": mid_term_info[3],
                "status": mid_term_info[4],
                "comment": mid_term_info[5],
                "comment_time": mid_term_info[6]
            }
            project_info_dict["status"] = mid_term_info[4]
            # 将开题报告信息字典添加至已选课题信息字典中
            project_info_dict["mid_term_info"] = mid_term_dict
        else:
            # 如果未查找到结果，则开题报告未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list[project_index] = project_info_dict
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
        'no': request.session['no']
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
    cursor.execute("UPDATE Middle_Check SET Status = '" + result + "', Comment = '"
                   + comment + "', Comment_Time = '" + comment_time + "' WHERE PNAME = '" + pname + "';")
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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 初始化周进度列表
        weekly_list = []
        # 从周进度表中查找该课题的周进度信息
        cursor.execute("SELECT * FROM Weekly_Progress WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则周进度已存在，构造周进度信息字典，以供教师查看审阅
        project_info_dict["status"] = "已审核"
        if cursor.rowcount >= 1:
            # 获取周进度信息
            weekly_info = cursor.fetchone()
            if weekly_info[4] == "审核中":
                project_info_dict["status"] = "待审核"
            # 构造周进度信息字典
            weekly_dict = {
                "content": weekly_info[1],
                "file": weekly_info[2],
                "time": weekly_info[3],
                "status": weekly_info[4],
                "comment": weekly_info[5],
                "comment_time": weekly_info[6]
            }
            project_info_dict["status"] = weekly_info[4]
            # 将周进度信息字典添加至周进度列表中
            weekly_list.append(weekly_dict)
        else:
            # 如果未查找到结果，则周进度未提交
            project_info_dict["status"] = "未提交"
        # 将周进度列表添加至课题信息字典中
        project_info_dict["weekly_list"] = weekly_list
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染周进度审阅页面
    return render(request, "teacher/supervisor/weekly_review.html", info_dict)


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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 初始化论文草稿列表
        draft_list = []
        # 从论文草稿表中查找该课题的论文草稿信息
        cursor.execute("SELECT * FROM Draft WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则论文草稿已存在，构造论文草稿信息字典，以供教师查看审阅
        if cursor.rowcount >= 1:
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
            # 将论文草稿信息字典添加至论文草稿列表中
            draft_list.append(draft_dict)
        else:
            # 如果未查找到结果，则论文草稿未提交
            project_info_dict["status"] = "未提交"
        # 将论文草稿列表添加至课题信息字典中
        project_info_dict["draft_list"] = draft_list
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染论文草稿审阅页面
    return render(request, "teacher/supervisor/draft_review.html", info_dict)


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
        'no': request.session['no']
    }
    # 从课题-学生视图中查找该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Project_Student WHERE TNO = '" +
                   info_dict["no"] + "'AND Pstatus = '已选';")
    # 获取该老师的所有已选课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + info_dict["no"] + "' AND Pstatus = '已选';")
    # 初始化课题列表
    project_list = []
    # 遍历已选课题信息，构造课题列表
    for project_index in range(cursor.rowcount):
        project_info = cursor.fetchone()
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "student_name": project_info[2],
        }
        # 从论文定稿表中查找该课题的论文定稿信息
        cursor.execute("SELECT * FROM Final WHERE PNAME = '" + project_info[0] + "';")
        # 如果查找到结果，则论文定稿已存在，构造论文定稿信息字典，以供教师查看审阅
        if cursor.rowcount >= 1:
            # 获取论文定稿信息
            final_info = cursor.fetchone()
            # 构造论文定稿信息字典
            final_dict = {
                "content": final_info[1],
                "file": final_info[2],
                "time": final_info[3],
                "status": final_info[4],
                "comment": final_info[5],
                "comment_time": final_info[6]
            }
            # 将论文定稿信息字典添加至课题信息字典中
            project_info_dict["final_dict"] = final_dict
            project_info_dict["status"] = final_info[4]
        else:
            # 如果未查找到结果，则论文定稿未提交
            project_info_dict["status"] = "未提交"
        # 将课题信息字典添加至课题列表中
        project_list.append(project_info_dict)
    # 将课题列表添加至信息字典中
    info_dict["project_list"] = project_list
    # 渲染论文定稿审阅页面
    return render(request, "teacher/supervisor/final_review.html", info_dict)


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
        'no': request.session['no']
    }
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
        'no': request.session['no']
    }
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
            "project_name": project_info[0],
            "project_type": project_info[1],
            "project_intro": project_info[2],
            "project_file": project_info[3],
            "project_time": project_info[4],
            "project_status": project_info[5],
            "project_comment": project_info[6],
            "project_comment_time": project_info[7],
            "teacher_name": teacher_info[1],
            "teacher_no": teacher_info[0]
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
    project_name = request.POST.get("project_name")
    # 获取课题状态
    result = request.POST.get("result")
    # 获取课题评语
    project_comment = request.POST.get("project_comment")
    # 获取课题评语时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新课题表中的课题状态
    cursor = db.cursor()
    cursor.execute("UPDATE PROJECT SET Pstatus = '" + result + "', Pcomment = '" + project_comment +
                   "', Pcomment_time = '" + now + "' WHERE Pname = '" + project_name + "';")
    db.commit()
    # 重定向至申报课题审核页面
    return redirect('/teacher/project_review/')


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
        'no': request.session['no']
    }
    # 获取任务书表中待审核的任务书信息
    cursor = db.cursor()
    cursor.execute("SELECT * FROM TASK_BOOK WHERE TBstatus = '审核中';")
    project_list = []
    # 遍历任务书
    for num in range(cursor.rowcount):
        # 获取任务书信息
        task_info = cursor.fetchone()
        # 构造任务书信息字典
        task_info_dict = {
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
        cursor2.execute("SELECT * FROM PROJECT WHERE Pname = '" + project_name + "';")
        project_info = cursor2.fetchone()
        # 获取指导教师信息
        no = project_info[8]
        cursor2.execute("SELECT * FROM TEACHER WHERE TNO = '" + no + "';")
        teacher_info = cursor2.fetchone()
        # 构造课题信息字典
        project_info_dict = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "teacher_name": teacher_info[1],
            "teacher_no": teacher_info[0],
            "task_book": task_info_dict
        }
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
    project_name = request.POST.get("project_name")
    # 获取任务书状态
    result = request.POST.get("result")
    # 获取任务书评语
    task_comment = request.POST.get("task_comment")
    # 获取任务书评语时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 更新任务书表中的任务书状态
    cursor = db.cursor()
    cursor.execute("UPDATE TASK_BOOK SET TBstatus = '" + result + "', TBcomment = '" + task_comment +
                   "', TBcomment_time = '" + now + "' WHERE name = '" + project_name + "';")
    db.commit()
    # 重定向至审核任务书页面
    return redirect('/teacher/task_review/')


# TODO 答辩组创建页面
def defense_assignment(request):
    pass


# TODO 答辩组分配页面
def group_assignment(request):
    pass


# TODO 过程信息总结页面
def information_summary(request):
    pass


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
        'no': request.session['no']
    }
    # 检查用户身份是否为老师
    if info_dict['role'] != '教师':
        # 如果不是，则渲染通知页面
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': info_dict["name"]})
    # TODO 检查用户是否为教学院长
    # 渲染教学院长模块主页
    return render(request, "teacher/dean/dean.html", info_dict)


# TODO 发布双选结果页面
def project_announcement(request):
    pass

# TODO 发布课题功能
def announce_project(request):
    project_name = request.POST["project_name"]
    cursor = db.cursor()
    cursor.execute("UPDATE PROJECT SET Pstatus = '已发布' WHERE Pname = '" + project_name + "';")
    db.commit()
    return project_announcement(request)


# TODO 公布双选结果页面
def result_announcement(request):
    pass
    # 获取选题表信息
    # cursor = db.cursor()
    # cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SPrecommend = '0'")
    # select_list = []
    # for num in range(cursor.rowcount):
    #     select_info = cursor.fetchone()
    #     # 获取学生信息
    #     no = select_info[0]
    #     cursor2 = db.cursor()
    #     cursor2.execute("SELECT * FROM STUDENT WHERE Sno = '" + no + "'")
    #     student_info = cursor2.fetchone()
    #     # 获取教师信息
    #     no = select_info[2]
    #     cursor3 = db.cursor()
    #     cursor3.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
    #     teacher_info = cursor3.fetchone()
    #     # 获取课题信息
    #     project_name = select_info[1]
    #     cursor4 = db.cursor()
    #     cursor4.execute("SELECT * FROM PROJECT WHERE Pname = '" + project_name + "'")
    #     project_info = cursor4.fetchone()
    #     project = {
    #         "project_name": project_info[0],
    #         "project_type": project_info[1],
    #         "project_supervisor": teacher_info[1],
    #         "student_name": student_info[1],
    #         "student_no": student_info[0],
    #     }
    #     select_list.append(project)
    # return render(request, "teacher/dean/result_announcement.html", tmp)
    #

# TODO 公布双选结果功能
def announce_result(request):
    pass
    # 获取双选信息
    # project_name = request.POST["project_name"]
    # student_no = request.POST["student_no"]
    # 更新选题表
    # cursor = db.cursor()
    # cursor.execute(
    #     "UPDATE SELECT_PROJECT SET SPrecommend = '1' WHERE Pname = '" +
    #     project_name + "' AND Sno = '" + student_no + "';")
    # db.commit()
    # # 重定向至发布双选结果页面
    # return redirect("/teacher/dean/result_announcement/")
