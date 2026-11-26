from pydantic import BaseModel
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Arachnida")
    parser.add_argument("url", help="target url")
    parser.add_argument("-l", type=int,
                        help="recursion depth", default=5,)
    parser.add_argument("-p", type=str,
                        help="target path for download", default="./data/")
    parser.add_argument("-r", action="store_true",)
    return parser.parse_args()



class Craw(BaseModel):
    addr: str = None
    depth: int 
    path: str
    referer_host: str



def resolve_name(url, target_dir):
    parsed_url = urlparse(url)
    name = Path(parsed_url.path).name
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    prop_name = Path(target_dir) / name 
    if prop_name.suffix not in [".jpg",".jpeg",".png",".gif",".bmp"]:
        raise ValueError("not valid extension")
    if prop_name.exists():
        for i in range (10000):
            new_name = Path(target_dir) / (prop_name.stem + f"{i}"+ prop_name.suffix)
            if new_name.exists():
                continue
            else:
                break
        else:
            raise ValueError("Limit img same name reached")
    else:
        new_name = prop_name
    return new_name


def get_image(url: str,target_dir: str)-> None:
    target_name = resolve_name(url, target_dir)
    with requests.get(url) as rq:
        if rq.status_code != 200:
            raise ValueError(f"Could not download img http_status: {rq.status_code} ")
        with open(target_name,"wb") as f:
            print(f"Writing {target_name} from {url}")
            f.write(rq.content)



def crawl(actual:Craw)-> None:
    if actual.depth < 0 or actual.addr is None:
        return
    out = requests.get(actual.addr)
    if out.status_code != 200:
        raise ValueError(f"Error {out.status_code} opening {out.url}")
    current_host = urlparse(out.url).hostname 
    if (current_host != actual.referer_host) and not actual.referer_host == "user":
        return
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
                imgroute = urljoin(out.url,src)                 
                get_image(imgroute,actual.path)
            except ValueError as e:
                print(f"Error getting {urljoin(out.url,src)}, {e} skipping")
    target_addr = soup.select("a[href]")
    targets = [Craw(addr = urljoin(out.url,x.get("href")) , depth=actual.depth - 1 ,path = actual.path, 
                    referer_host= current_host) for x in target_addr if urlparse(urljoin(out.url,x.get("href"))).hostname == current_host]
    for w in targets:
        try:
            crawl(w)
        except Exception as e:
            print(f"Could not out process {w.addr} {e} Skipping")

visited = {}



def main():
    args = parse_args()
    if not args.url:
        print("an url is required")
        exit(1)
    if not args.r:
        args.l = 0
    if args.l < 0:
        print("Error: recursion should be non negative")
        exit(1)
    crawler = Craw(addr= args.url, depth=args.l,path=args.p ,referer_host="user")
    crawl(crawler)


if __name__ == "__main__":
    main()