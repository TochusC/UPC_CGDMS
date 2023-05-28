import pymysql
import random

from django.http import HttpResponse

from django.shortcuts import render, redirect

db = pymysql.connect(host='localhost',
                     user='root',
                     password='wue789789',
                     database='cgdms')

self_info = {}


# 通用模块
def login(request):
    return render(request, "login.html")


def index(request):
    global self_info
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM user WHERE Uno = '" + request.POST['Uno'] + "' AND Upassword = '" + request.POST['Upwd'] + "';")
    if cursor.rowcount == 1:
        username, password, role = cursor.fetchone();
        sql = "SELECT * FROM STUDENT WHERE UNO = '" + username + "';"
        cursor.execute(sql)
        if cursor.rowcount == 0:
            sql = "SELECT * FROM TEACHER WHERE UNO = '" + username + "';"
            cursor.execute(sql)
            no, name, gender, birth, fno, mno, username = cursor.fetchone();
            self_info = {
                'role': '教师',
                'uno': request.POST['Uno'],
                'no': no,
                "name": name,
                "gender": gender,
                "birth": birth,
                "fno": fno,
                "mno": mno,
                "username": username
            }
        else:
            no, name, gender, birth, fno, mno, cno, username = cursor.fetchone();
            self_info = {
                'role': '学生',
                'uno': request.POST['Uno'],
                'no': no,
                "name": name,
                "gender": gender,
                "birth": birth,
                "fno": fno,
                "mno": mno,
                "username": username
            }
        return render(request, "index.html", self_info)
    else:
        return render(request, "announce.html",
                      {'message': '登录失败！请检查您的用户名和密码。', 'name': self_info["name"]})


def reindex(request):
    return render(request, "index.html", self_info)


def showinfo(request):
    return render(request, "showinfo.html", self_info)


def account(request):
    return render(request, "account.html", self_info)


def change_password(request):
    if request.POST['new_password'] != request.POST['new_password_confirm']:
        return render(request, "announce.html", {'message': '修改失败！两次输入的密码不一致。'})
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM user WHERE Uno = '" + request.POST['uno'] + "' AND Upassword = '" + request.POST[
            'current_password'] + "';")
    if cursor.rowcount == 1:
        cursor.execute(
            "UPDATE user SET Upassword = '" + request.POST['new_password'] + "' WHERE Uno = '" + request.POST[
                'uno'] + "';")
        db.commit()
        return render(request, "announce.html", {'message': '修改成功！', 'name': self_info["name"]})
    else:
        return render(request, "announce.html",
                      {'message': '修改失败！请检查您的用户名和密码。', 'name': self_info["name"]})


# 学生模块
def student(request):
    if self_info["role"] == "学生":
        return render(request, "student/student_index.html", self_info)
    else:
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': self_info["name"]})


def project_selection(request):
    if not checkRole("学生"):
        return render(request, "announce.html", {'message': '老师，这里是学生中心哦！', 'name': self_info["name"]})
    project_list = []
    pre_select_list = []
    pre_select_names = []
    tmp = {}

    cursor = db.cursor()
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SNO = '" + self_info["no"] + "'")
    # 如果选题表中有记录
    if cursor.rowcount == 1:
        # 获取项目名称
        pname = cursor.fetchone()[1]
        # 获取项目信息
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM PROJECT WHERE Pname = '" + pname + "'");
        project_info = cursor1.fetchone()
        # 获取老师信息
        no = project_info[5]
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
        teacher_info = cursor2.fetchone()
        # 构造项目字典
        project = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": teacher_info[1],
        }

        tmp.update({"selected": True})
        tmp.update({"selected_project": project})
    else:
        # 获取预选表中的项目
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Pre_Select WHERE SNO = '" + self_info["no"] + "'")
        for num in range(cursor.rowcount):
            # 获取项目名称
            pre_select_project = cursor.fetchone()
            pname = pre_select_project[1]
            # 获取项目信息
            cursor1 = db.cursor()
            cursor1.execute("SELECT * FROM PROJECT WHERE Pname = '" + pname + "'");
            selected_project_info = cursor1.fetchone()
            # 获取老师信息
            no = selected_project_info[5]
            cursor2 = db.cursor()
            cursor2.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
            teacher_info = cursor2.fetchone()
            # 构造项目字典
            project = {
                "name": selected_project_info[0],
                "type": selected_project_info[1],
                "supervisor": teacher_info[1],
                "selected_by_me": False
            }
            pre_select_names.append(pname)
            pre_select_list.append(project)

        tmp.update({"pre_select_list": pre_select_list})
        tmp.update({"selected": False})
    # 获取所有发布的项目
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE Pstatus = '已发布'")
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        no = project_info[5]
        # 获取项目被选次数
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Pre_Select WHERE Pname = '" + project_info[0] + "'")
        # 获取教师信息
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
        teacher_info = cursor2.fetchone()
        # 构造项目字典
        if project_info[0] in pre_select_names:
            project = {
                "name": project_info[0],
                "type": project_info[1],
                "supervisor": teacher_info[1],
                "selected_times": -1,
            }
        else:
            project = {
                "name": project_info[0],
                "type": project_info[1],
                "supervisor": teacher_info[1],
                "selected_times": cursor1.rowcount
            }
        project_list.append(project)

    tmp.update({"project_list": project_list})
    tmp.update(self_info)

    return render(request, "student/project_selection.html", tmp)


def select_project(request):
    project_name = request.POST["project_name"]
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Pre_Select WHERE SNO = '" + self_info["no"] + "'")
    if cursor.rowcount == 3:
        return render(request, "announce.html", {'message': '您已选满三个预选项目！', 'name': self_info["name"]})

    cursor.execute("INSERT INTO Pre_Select VALUES ('" + self_info["no"] + "','"
                   + project_name + "','" + str(cursor.rowcount + 1) + "');")
    # cursor.execute("UPDATE PROJECT SET PSTATUS = '已选' WHERE PNAME = '" + project_name + "';")
    db.commit()
    return redirect("/student/project_selection")


def cancel_project(request):
    cursor = db.cursor()
    pname = request.POST["project_name"]
    cursor.execute("DELETE FROM Pre_Select WHERE SNO = '" + self_info["no"] + "' AND PNAME = '" + pname + "';")
    return redirect("/student/project_selection")


# 教师模块
def teacher(request):
    if self_info["role"] == "教师":
        return render(request, "teacher/teacher_index.html", self_info)
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': self_info["name"]})


def checkRole(role):
    if self_info["role"] == role:
        return True
    return False


def role(request):
    userRole = request.POST["role"]
    curse = db.cursor()
    curse.execute("SELECT * FROM ROLE WHERE TNO = '" + self_info["no"] + "' AND is_" + userRole + "= '是'" + ";")
    if curse.rowcount == 1:
        return render(request, "teacher/" + userRole + "/" + userRole + ".html", self_info)
    else:
        return render(request, "announce.html",
                      {'message': '您没有' + userRole + '权限，无法访问。', 'name': self_info["name"]})


# 指导教师模块
def supervisor(request):
    if checkRole("教师"):
        curse = db.cursor()
        curse.execute("SELECT * FROM ROLE WHERE TNO = '" + self_info["no"] + "' AND is_supervisor = '是';")
        if curse.rowcount == 1:
            return render(request, "teacher/supervisor/supervisor.html", self_info)
        else:
            return render(request, "announce.html",
                          {'message': '您没有指导教师权限，无法访问。', 'name': self_info["name"]})
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': self_info["name"]})


def project_proposal(request):
    return render(request, "teacher/supervisor/project_proposal.html", self_info)


def propose_project(request):
    project_name = request.POST["project_name"]
    project_type = request.POST["project_type"]
    project_info = request.POST["project_info"]
    cursor = db.cursor()
    cursor.execute("INSERT INTO PROJECT VALUES ('" + project_name + "','" +
                   project_type + "','" + project_info + "','" + "','申报中" + "','" + self_info["no"] + "');")
    db.commit()
    return render(request, "teacher/supervisor/announce.html",
                  {'message': '毕业课题申报完成！', 'name': self_info["name"]})


# 确认选题页面
def project_confirmation(request):
    pre_selection_info = []
    # 获取该老师所有的已发布课题
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE TNO = '" + self_info["no"] + "' AND Pstatus = '已发布';")
    # 对每一个课题，遍历该课题的选题情况
    for project_index in range(cursor.rowcount):
        # 获取当前课题信息
        project_info = cursor.fetchone()
        pname = project_info[0]
        # 获取当前课题的预选情况
        cursor1 = db.cursor()
        cursor1.execute("SELECT * FROM Pre_Select WHERE PNAME = '" + pname + "';")
        for pre_index in range(cursor1.rowcount):
            select_info = cursor1.fetchone()
            # 获取学生姓名
            cursor2 = db.cursor()
            cursor2.execute("SELECT * FROM STUDENT WHERE SNO = '" + select_info[0] + "';")
            student_info = cursor2.fetchone()
            # 构造预选信息字典
            pre_selection = {
                "project_name": pname,
                "project_type": project_info[1],
                "student_name": student_info[1],
                "student_no": select_info[0],
            }
            pre_selection_info.append(pre_selection)
    tmp = {}
    tmp.update({"pre_selection_info": pre_selection_info})
    tmp.update(self_info)
    return render(request, "teacher/supervisor/project_confirmation.html", tmp)


# 确认选题操作
def confirm_project(request):
    # 获取学生学号和课题名称
    pname = request.POST["project_name"]
    sno = request.POST["student_no"]
    # 删除该学生的所有预选课题
    cursor = db.cursor()
    cursor.execute("DELETE FROM Pre_Select WHERE SNO = '" + sno + "';")
    # 将该课题的状态改为已选
    cursor.execute("UPDATE PROJECT SET Pstatus = '已选' WHERE PNAME = '" + pname + "';")
    # 在选题表中插入该选题记录
    cursor.execute("INSERT INTO Select_Project(SNO, PNAME) VALUES ('" + sno + "','" + pname + "');")
    # 提交事务
    db.commit()
    # 重定向至确认选题页面
    return redirect("/teacher/supervisor/project_confirmation")


# 取消预选选题操作
def cancel_pre_selection(request):
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


def task_issue(request):
    return render(request, "teacher/supervisor/task_issue.html", self_info)


def issue_task(request):
    return None


def report_review(request):
    return render(request, "teacher/supervisor/report_review.html", self_info)


def translation_review(request):
    return render(request, "teacher/supervisor/translation_review.html", self_info)


def mid_term_check(request):
    return render(request, "teacher/supervisor/mid_term_check.html", self_info)


def weekly_review(request):
    return render(request, "teacher/supervisor/weekly_review.html", self_info)


def final_review(request):
    return render(request, "teacher/supervisor/final_review.html", self_info)


def draft_review(request):
    return render(request, "teacher/supervisor/draft_review.html", self_info)


def project_recommendation(request):
    return render(request, "teacher/supervisor/project_recommendation.html", self_info)


# 毕设负责人模块
def manager(request):
    if checkRole("教师"):
        curse = db.cursor()
        curse.execute("SELECT * FROM ROLE WHERE TNO = '" + self_info["no"] + "' AND is_manager = '是';")
        if curse.rowcount == 1:
            return render(request, "teacher/manager/manager.html", self_info)
        else:
            return render(request, "announce.html",
                          {'message': '您没有毕设负责人权限，无法访问。', 'name': self_info["name"]})
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': self_info["name"]})


def project_review(request):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE Pstatus = '申报中'")
    project_list = []
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        no = project_info[5]
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
        teacher_info = cursor2.fetchone()
        project = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": teacher_info[1],
        }
        project_list.append(project)
    tmp = {}
    tmp.update({"project_list": project_list})
    tmp.update(self_info)
    return render(request, "teacher/manager/project_review.html", tmp)


def pass_project(request):
    project_name = request.POST["project_name"]
    cursor = db.cursor()
    cursor.execute("UPDATE PROJECT SET Pstatus = '审核通过' WHERE Pname = '" + project_name + "';")
    return project_review(request)


def task_review(request):
    return render(request, "teacher/manager/task_review.html", self_info)


def defense_assignment(request):
    return render(request, "teacher/manager/defense_assignment.html", self_info)


def group_assignment(request):
    return render(request, "teacher/manager/group_assignment.html", self_info)


def information_summary(request):
    return render(request, "teacher/manager/information_summary.html", self_info)


# 教学院长模块
def dean(request):
    if checkRole("教师"):
        curse = db.cursor()
        curse.execute("SELECT * FROM ROLE WHERE TNO = '" + self_info["no"] + "' AND is_dean = '是';")
        if curse.rowcount == 1:
            return render(request, "teacher/dean/dean.html", self_info)
        else:
            return render(request, "announce.html",
                          {'message': '您没有教学院长权限，无法访问。', 'name': self_info["name"]})
    else:
        return render(request, "announce.html",
                      {'message': '同学，请不要随便进入教师的页面哦！', 'name': self_info["name"]})


def project_announcement(request):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM PROJECT WHERE Pstatus = '审核通过'")
    project_list = []
    for num in range(cursor.rowcount):
        project_info = cursor.fetchone()
        no = project_info[5]
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM TEACHER WHERE Tno = '" + no + "'")
        teacher_info = cursor2.fetchone()
        project = {
            "name": project_info[0],
            "type": project_info[1],
            "supervisor": teacher_info[1],
        }
        project_list.append(project)
    tmp = {}
    tmp.update({"project_list": project_list})
    tmp.update(self_info)

    return render(request, "teacher/dean/project_announcement.html", tmp)


def announce_project(request):
    project_name = request.POST["project_name"]
    cursor = db.cursor()
    cursor.execute("UPDATE PROJECT SET Pstatus = '已发布' WHERE Pname = '" + project_name + "';")
    db.commit()
    return project_announcement(request)


def result_announcement(request):
    # 获取选题表信息
    cursor = db.cursor()
    selection_info_list = []
    cursor.execute("SELECT * FROM SELECT_PROJECT WHERE SPrecommend = '0'")
    # 遍历所有选题信息
    for num in range(cursor.rowcount):
        selection_info = cursor.fetchone()
        # 获取学生信息
        sno = selection_info[0]
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM STUDENT WHERE Sno = '" + sno + "'")
        student_info = cursor2.fetchone()
        # 获取课题信息
        project_name = selection_info[1]
        cursor3 = db.cursor()
        cursor3.execute("SELECT * FROM PROJECT WHERE Pname = '" + project_name + "'")
        project_info = cursor3.fetchone()
        # 获取教师信息
        tno = project_info[5]
        cursor4 = db.cursor()
        cursor4.execute("SELECT * FROM TEACHER WHERE Tno = '" + tno + "'")
        teacher_info = cursor4.fetchone()
        # 构造双选信息字典
        selection_info = {
            "project_name": project_info[0],
            "project_type": project_info[1],
            "project_supervisor": teacher_info[1],
            "student_name": student_info[1],
            "student_no": student_info[0],
        }
        selection_info_list.append(selection_info)
    tmp = {}
    tmp.update({"selection_info_list": selection_info_list})
    tmp.update(self_info)
    return render(request, "teacher/dean/result_announcement.html", tmp)


def announce_result(request):
    # 获取双选信息
    project_name = request.POST["project_name"]
    student_no = request.POST["student_no"]
    # 更新选题表
    cursor = db.cursor()
    cursor.execute(
        "UPDATE SELECT_PROJECT SET SPrecommend = '1' WHERE Pname = '" + project_name + "' AND Sno = '" + student_no + "';")
    db.commit()
    # 重定向至发布双选结果页面
    return redirect("/teacher/dean/result_announcement/")
