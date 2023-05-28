from django.http import HttpResponse
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import FileResponse


def search_form(request):
    return render(request, 'item-1.html')
 
 
def search(request):  
    request.encoding='utf-8'
    if 'q' in request.GET and request.GET['q']:
        prb = request.GET['q']
        prb_code, prb_number = prb[-1], prb[0:-1]
        url = 'https://codeforces.com/problemset/problem/' + prb_number + '/' + prb_code
        r = requests.get(url)
        soup = BeautifulSoup(r.text, features="html.parser")
        content = soup.find_all(attrs={'class': 'problem-statement'})
        if (r.status_code == 200):
            message = str(content[0])
            xfile = open('result.xml','w', encoding = 'utf-8')
            xfile.write(message)
            return render(request,'result.html',{'text':message})
        else:
            message = '题面信息获取失败，请检查题目编号输入是否有误。'
            return HttpResponse(message)


def download(request):
  text = ''
  
  file=open('result.xml','rb')
  response =FileResponse(file)
  response['Content-Type']='application/octet-stream'
  response['Content-Disposition']=f'attachment;filename="result.xml"'
  return response