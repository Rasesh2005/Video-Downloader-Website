import json
from flask import Flask,request, render_template
from youtube_dl import YoutubeDL

qualityToLink={}
url=None
to_be_deleted=[]
app=Flask(__name__,static_folder="media")

def get_playlist(link):
    ydl_conf={}
    with YoutubeDL(ydl_conf) as ydl:
        url=ydl.extract_info(link, download=False)
        download_links=[]
        download_titles=[]
        for entry in url["entries"]:
            download_titles.append(entry["title"])
            download_links.append(entry["formats"][-1]["url"])
        return zip(download_titles,download_links)

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
    
    download_link=qualityToLink[res]
    return download_link,filename+".mp4"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/playlist')
def playlist():
    return render_template("playlist.html")


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
    link=request.form.get("url")
    res=request.form.get("res")
    if filename:=download_video(link,res):
        link,file=filename
        print(link)
        print("fetching url")
        title=filename[1]
        title.replace(' ','%20')
        return render_template("download.html",title=title,link=link,filename=file)
    else:
        print(filename)
        return "Link Not Found"

@app.route("/download_playlist",methods=["POST"])
def download_playlist():
    print("WELCOME TO PLAYLIST DOWNLOADER")
    link=request.form.get("link")
    print(link)
    print(type(link))
    zipped=get_playlist(link)
    return render_template("download_playlist.html",zipped_list=zipped)
if __name__=='__main__':
    app.run(debug=True)
