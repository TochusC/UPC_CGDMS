import requests
import csv
import pyecharts.options as opts
from bs4 import BeautifulSoup
from pyecharts.render import make_snapshot
from pyecharts.charts import Line
from django.http import HttpResponse
from django.shortcuts import render


def init(request):
    return render(request, 'item-2.html')


date_trans = {'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8',
              'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'}


def read_data(users):
    name_list = users
    headers = ['time', 'score']
    for i in name_list:
        url = f'https://codeforces.com/contests/with/{i}'
        resp = requests.get(url)
        page = BeautifulSoup(resp.text, 'html.parser')
        tr_list = page.find('table', class_="tablesorter user-contests-table").find('tbody').find_all('tr')
        f = open(i + '.csv', mode='w', encoding='utf-8', newline='')
        csvwriter = csv.writer(f)
        csvwriter.writerow(headers)
        for tr in tr_list:
            tds = tr.find_all('td')
            dic = {
                "time": tds[2].text.split('\n\n')[1], 'score': tds[6].text.split('\r\n')[1].split(' ')[-1]
            }
            csvwriter.writerow(dic.values())
        resp.close()


def process_data(user, date, score):
    file = open(user + '.csv', 'r')
    for line in file.readlines()[1:]:
        score.append(line.strip().split(',')[1])
        year = line.split(',')[0].split(' ')[0].split('/')[2]
        month = date_trans[line.split(',')[0].split(' ')[0].split('/')[0]]
        day = line.split(',')[0].split(' ')[0].split('/')[1]
        date.append(year + '-' + month + '-' + day)
    score.reverse()
    date.reverse()


def visualize(users):
    chart = Line(init_opts=opts.InitOpts(page_title='用户积分可视化',width='1600px', height = '800px'))
    for user in users:
        score, date = [], []
        process_data(user, date, score)
        chart.add_xaxis(date).add_yaxis(user, score,
                                        label_opts=opts.LabelOpts(rotate=45,
                                                                  font_size=8,
                                                                  ),
                                        is_connect_nones=True)
    chart.set_global_opts(yaxis_opts=opts.AxisOpts(name='积分'),
                          xaxis_opts=opts.AxisOpts(name='日期'),
                          toolbox_opts=opts.ToolboxOpts(is_show=True),
                          datazoom_opts=opts.DataZoomOpts(is_show=True,
                                                          range_start=0,
                                                          range_end=100
                                                          )
                          ).render('积分变化图.html')


def visual(request):
    request.encoding = 'utf-8'
    if 'q' in request.GET and request.GET['q']:
        usernames = request.GET['q'].split(',')
        read_data(usernames)
        visualize(usernames)
        return render(request, '.\积分变化图.html')
    else:
        return HttpResponse('发生错误！请检查用户名输入是否有误。')
