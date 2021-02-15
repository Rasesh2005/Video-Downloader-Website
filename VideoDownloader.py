import json
from flask import Flask,request, render_template
from youtube_dl import YoutubeDL
import os

qualityToLink={}
url=None
to_be_deleted=[]
app=Flask(__name__,static_folder="media")
BASE_DIR=os.path.join(os.getcwd(),"media")



class FileCleaner:
    def __init__(self) -> None:
        pass
    def run(self):
        global to_be_deleted
        for item in to_be_deleted:
            os.remove(item)
            to_be_deleted.remove(item)


cleaner=FileCleaner()
for i in os.listdir(BASE_DIR):
    os.remove(os.path.join(BASE_DIR,i))


def make_links(link):
    global url
    ydl_opts={}
    newDict={}
    with YoutubeDL(ydl_opts) as ydl:
        url=ydl.extract_info(link, download=False)
        for i in url["formats"]:
            if i.get("height")!=None and i["ext"]=="mp4":
                newDict[str(i.get('height'))+"p"]=i['url']
    return newDict


def download_video(link,res):
    global li
    qualityToLink=make_links(link)
    s=url["title"][:15]
    filename="".join(x if x.isalnum() else '-' for x in s)
    if os.path.exists(os.path.join(BASE_DIR,filename)):
        return filename+".mp4"
    
    download_link=qualityToLink[res]
    return download_link,filename+".mp4"

@app.route('/')
def home():
    return render_template("home.html")



@app.route('/get_quality',methods=["POST"])
def get_quality():
    if request.form.get("url").strip()!="":
        res=set()
        ydl_opts={}
        with YoutubeDL(ydl_opts) as ydl:
            try:
                newDict={}
                url=ydl.extract_info(str(request.form.get("url")), download=False)
                for i in url["formats"]:
                    if i.get("height") and i["ext"]=="mp4":
                        newDict[str(i.get('height'))+"p"]=i['url']
                        res.add(i.get('height') if i.get('height') else None) 
                if None in res:
                    res.remove(None)
                    res.add(0)
            except Exception as e:
                print(e)
        return json.dumps(sorted(list(res),reverse=True))
    return "No parameters passed"



@app.route('/download',methods=["POST"])
def download():
    global to_be_deleted
    cleaner.run()
    link=request.form.get("url")
    res=request.form.get("res")
    if filename:=download_video(link,res):
        link,file=filename
        print(link)
        path=os.path.join(BASE_DIR,file)
        # print(link,file)
        print("fetching url")
        # data=base64.b64encode(requests.get(url=filename[0]).content)
        # to_be_deleted.append(path)
        title=filename[1]
        title.replace(' ','%20')
        return render_template("download.html",title=title,link=link,filename=file)
    else:
        print(filename)
        return "Link Not Found"

if __name__=='__main__':
    app.run(debug=True)
