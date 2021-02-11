import json
from flask import Flask,request, render_template, send_file
from youtube_dl import YoutubeDL
import os
from threading import Thread
import time


li=0
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
            itempath=os.path.join(BASE_DIR,item)
            os.remove(itempath)


cleaner=FileCleaner()
for i in os.listdir(BASE_DIR):
    os.remove(os.path.join(BASE_DIR,i))


def make_links(link):
    global url
    ydl_opts={}
    newDict={}
    with YoutubeDL(ydl_opts) as ydl:
        url=ydl.extract_info(link, download=False)
        # print(url)
        # with open("fb.json","w") as f:
        #     f.write(json.dumps(url))
        #     print(url)
        #     print("File Written")
        for i in url["formats"]:
            if i.get("height")!=None or i["ext"]!="mp4":
                newDict[str(i.get('height') if i.get('height') else "mp4")+"p"]=i['url']
    return newDict


def download_video(link,res):
    global li
    qualityToLink=make_links(link)
    s=url["title"][:15]
    filename="".join(x if x.isalnum() else '-' for x in s)
    if os.path.exists(os.path.join(BASE_DIR,filename)):
        return filename+f"{li}.mp4"
    li+=1
    ydl_opts={"outtmpl":BASE_DIR+'/'+filename+f"{li}.mp4"}
    with YoutubeDL(ydl_opts) as ydl:
        # try:
            # url=ydl.extract_info(link, download=False)

            # print("url: ",url)
            # with open("url.json","w") as f:
            #     f.write(json.dumps(url))
        download_link=qualityToLink[res]
        ydl.download([download_link])
        return filename+f"{li}.mp4"
        # except Exception as e:
            # print(e)
            # return None

@app.route('/')
def home():
    return render_template("home.html")



@app.route('/get_quality',methods=["POST"])
def get_quality():
    global qualityToLink
    if request.form.get("url").strip()!="":
        res=set()
        ydl_opts={}
        with YoutubeDL(ydl_opts) as ydl:
            try:
                newDict={}
                url=ydl.extract_info(str(request.form.get("url")), download=False)
                for i in url["formats"]:
                    if i.get("height")!=None or i["ext"]!="mp4":
                        newDict[str(i.get('height') if i.get('height') else "mp4")+"p"]=i['url']
                        res.add(i.get('height') if i.get('height') else None) 
                qualityToLink=newDict
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
        to_be_deleted.append(os.path.join(BASE_DIR,filename))
        return send_file(os.path.join(BASE_DIR,filename),mimetype="video/mp4",as_attachment=True)
    else:
        print(filename)
        return "Link Not Found"

if __name__=='__main__':
    app.run(port=80,debug=True)
