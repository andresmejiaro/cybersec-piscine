import argparse
from PIL import Image, ExifTags, UnidentifiedImageError
from pathlib import Path
from datetime import datetime
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(
        description="Arachnida")
    parser.add_argument("files", nargs="+", help="target file", type=Path)
    return parser.parse_args()


def metadata_print(img):
    exif= img.getexif()
    for tag, value in exif.items():
        name = ExifTags.TAGS.get(tag,tag)
        print(f"{name}: {value}")
    metadata_print_gif(img)


def metadata_print_gif(img: Image.Image):
    for tag, value in img.info.items():
        print(f"{tag}: {value}")


def metadata_basic(img: Image.Image):
    data = {"size": f"{img.size[0]}x{img.size[1]}", \
            "format": img.format,
            "mode": img.mode}
    for tag, value in data.items():
            print(f"{tag}: {value}")
    


def img_validate(img) -> None:
    real_type = img.format
    print(real_type)
    metadata_basic(img)
    if real_type in ["JPEG", "PNG" ,"BMP"]:
        metadata_print(img)
        return
    if real_type in ["GIF"]:
        metadata_print_gif(img)
        return
    print(f"Image type {real_type} isn't supported for metadada analysis")
    



def main():
    args = parse_args()
    for file in args.files:
        try:        
            with Image.open(file) as img:
                img_validate(img)
                print(file)
                
        except UnidentifiedImageError as e:
            print(f"File {file} cannot be identified as image skipping: {e}")
            continue
        except FileNotFoundError as e:
            print(f"File {file} is not found: {e}")
            continue
        file_info = Path(file).stat()
        print(file_info)
        process = subprocess.run(["stat","-c","%w",Path(file).absolute()],text=True,capture_output=True)
        if process.returncode == 0:
            print(f"creation date: {process.stdout}")
        else:
            print("creation date could not be retrieved")

if __name__ == "__main__":
    main()