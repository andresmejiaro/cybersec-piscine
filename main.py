from pydantic import BaseModel
import argparse
import requests


def parse_args():
    parser = argparse.ArgumentParser(
        description="Arachnida")
    parser.add_argument("url", help="target url")
    parser.add_argument("-l", type=int,
                        help="recursion depth", default=5,)
    parser.add_argument("-p", type=str,
                        help="target path for download", default="./data/")
    parser.add_argument("-r", action="store true",)
    return parser.parse_args()






class Craw(BaseModel):
    addr: str = None
    depth: int 
    path: str







def main():
    parse_args()





if __name__ == "___main___":
    main()