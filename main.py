import os
from pathlib import Path

import fire
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm


def save_url_as_markdown(url: str, output_filename: str):
    response = requests.get(url)
    if response.status_code != 200:
        return
    markdown_content = md(response.text)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(markdown_content)

def merge_md_files_in_order(directory: str, output_file: str):
    md_files = [f for f in Path(directory).glob("*.md")]
    md_files.sort(key=lambda f: f.stat().st_ctime)
    with open(output_file, 'w', encoding='utf-8') as output:
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                output.write(f"\n\n# {md_file.name}\n\n")
                output.write(f.read())

class Cli:
    def make(self, url: str):
        if not url.endswith("all.html") and not url.startswith("https://docs.rs/"):
            raise ValueError("러스트 공식 문서가 아닙니다.")
        lib_name = url.split("/")[3]
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        a_arr = soup.find("main").find("section").find_all("a")
        os.makedirs(lib_name, exist_ok=True)
        for a in tqdm(a_arr):
            url = f"https://docs.rs/{lib_name}/latest/{lib_name}/" + a["href"]
            name = lib_name + "/" + a["href"].split(".")[-2]
            save_url_as_markdown(url, f"{name}.md")
        merge_md_files_in_order(lib_name, f'{lib_name}.merged.md')

if __name__ == "__main__":
    fire.Fire(Cli)