from youtube_dl import YoutubeDL

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



