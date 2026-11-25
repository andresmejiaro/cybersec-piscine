#%%
from pydantic import BaseModel
import argparse
import requests
from bs4 import BeautifulSoup
import urllib.parse import urljoin, urlparse
from pathlib import Path



#%%


url = "https://www.google.com"

out = requests.get(url)



#%%
class Craw(BaseModel):
    addr: str = None
    depth: int 
    path: str

#%%

soup = BeautifulSoup(out.text, "html.parser")

# %%

images = soup.find_all("img")




# %%
im= images[0]
# %%
suf = im.get("src")

# %%

img = requests.get(f"{url}{suf}")

# %%

img.content

# %%

imgname = suf.split("/")[-1]

#%%
imgname

#%%
with open(imgname,"wb") as f:
    f.write(img.content)
# %%

def resolve_name(url, target_dir):
    parsed_url = urlparse(url)
    name = Path(parsed_url.path).name
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    return Path(target_dir) / name


def get_image(url: str,target_dir: str)-> None:
    target_name = resolve_name(url, target_dir)
    with requests.get(url) as rq:
        if rq.status_code != 200:
            raise ValueError(f"Could not download img http_status: {rq.status_code} ")
        with open(target_name,"wb") as f:
            print(f"Writing {target_name} from {url}")
            f.write(rq.content)
# %%

visited = {}



def crawl(actual:Craw)-> None:
    if actual.depth < 0 or actual.addr is None:
        return
    out = requests.get(actual.addr)
    if out.status_code != 200:
        raise ValueError(f"Error {out.status_code} opening {out.url}")
    images = False
    if out.url not in visited:
        images = True 
    if out.url in visited and visited[out.url] >= actual.depth:
        return
    else:
        visited[out.url] = actual.depth
   
    soup = BeautifulSoup(out.content,"html.parser")
    if images:
        images = soup.select("img[src]")
        for img in images:
            try:
                src = img.get("src")
                get_image(urljoin(out.url,src),actual.path)
            except ValueError as e:
                print(f"Error getting {urljoin(out.url,src)}, {e} skipping")
    target_addr = soup.select("a[href]")
    targets = [Craw(addr = urljoin(out.url,x.get("href")) , depth=actual.depth - 1 ,path = actual.path) for x in target_addr]
    for w in targets:
        try:
            crawl(w)
        except Exception as e:
            print(f"Could not out process {w.addr} {e} Skipping")