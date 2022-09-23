import os
import sys
import json
import random
import requests
import time
import threading
from rich.console import Console
from rich import print as rprint


class Log:
    """
    Log uitl
    """

    __console = Console()

    def info(self, data, emoji="face_with_monocle") -> None:
        self.__console.print(
            f"[bold blue][Info] :{emoji}: {data}[/bold blue]", emoji=True
        )

    def error(self, data, emoji="hot_face") -> None:
        self.__console.print(
            f"[bold red][Error] :{emoji}: {data}[/bold red]", emoji=True)

    def success(self, data, emoji="face_savoring_food") -> None:
        self.__console.print(
            f"[bold green][Success] :{emoji}: {data}[/bold green]",
            emoji=True,
        )

    def warning(self, data, emoji="grinning_face_with_sweat") -> None:
        self.__console.print(
            f"[bold yellow][Warning] :{emoji}: {data}[/bold yellow]", emoji=True
        )

    def print(self, data) -> None:
        rprint(data)

    def log(self, data) -> None:
        self.__console.log(data)

    def console(self) -> Console:
        return self.__console


log = Log()


def list_images(path: str) -> list:
    """
    Get a list of your input path contains images.

    :param path: images' path
    :type path: str
    :return: list of images
    :rtype: list
    """
    if not os.path.exists(path):
        return []
    if os.path.isfile(path):
        return [os.path.abspath(path)]
    else:
        images = []
        os.chdir(path)
        full_path = os.getcwd()
        files = os.listdir(full_path)
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png'):
                images.append(os.path.join(full_path, file))
    return images


def shrink_image(file_path: str) -> None:
    """
    Shrink your image by method 'shrink' and write to your current path.

    :param file_path: absolut path of your image
    :type file_path: str
    """
    result = shrink(file_path)
    if result:
        output_path = generate_output_path(file_path)
        url = result['output']['url']
        response = requests.get(url)
        try:
            with open(output_path, 'wb') as file:
                file.write(response.content)
        except:
            log.error("Write Image Error!")
        log.success(
            f"{output_path}: {result['input']['type']} {result['input']['size']} => { result['output']['size']}({result['output']['ratio']})")
    else:
        log.error("Shrinking Error!")


def shrink(file_path: str) -> dict:
    """
    Shrink your file path contains images by TinyPNG Web Api!

    :param file_path: absoult path of your image
    :type file_path: str
    :return: api resoult
    :rtype: dict
    """
    url = 'https://tinypng.com/web/shrink'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'X-Forwarded-For': get_random_ip()
    }
    result = None
    file = None
    try:
        file = open(file_path, 'rb')
        response = requests.post(url, headers=headers, data=file)
        result = json.loads(response.text)
    except:
        if file:
            file.close()
        log.error("File Open Error!")
    if result and result['input'] and result['output']:
        return result
    else:
        return {}


def generate_output_path(file_path: str, out_path="tinypng_output") -> str:
    """
    Generate a output paht of your image.

    :param file_path: absolut pat of your image
    :type file_path: str
    :param out_path: your output images path, defaults to "tinypng_output"
    :type out_path: str, optional
    :return: after shrinking's images path
    :rtype: str
    """
    parent_path = os.path.abspath(os.path.dirname(file_path))
    output_path = os.path.join(parent_path, out_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    return os.path.join(output_path, os.path.basename(file_path))


def get_random_ip() -> str:
    """
    Get a random ip.

    :return: random ip
    :rtype: str
    """
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)


def list_equally_split(list_data: list, num: int) -> list:
    """
    A useful util to handle list spilt

    :param list_data: input list
    :type list_data: list
    :param num: every list len
    :type num: int
    :return: spilted list
    :rtype: list
    """
    return [
        list_data[i * num: (i + 1) * num]
        for i in range(int(len(list_data) / num) + 1)
        if list_data[i * num: (i + 1) * num]
    ]


def thread_shrink(file_path: str, threads_cnt=8) -> None:
    start_time = time.time()
    img_list = list_images(file_path)
    if not img_list:
        log.error("Please Input Correct Path!")
        return
    if len(img_list) == 1:
        # Only one image
        shrink_image(img_list[0])
    else:
        # Get min thread count
        threads_cnt = min(len(img_list), threads_cnt)
        handle_img_list = list_equally_split(
            img_list,  round(len(img_list) / threads_cnt))
        threads = []
        log.print(f"[bold cyan]Threads Count --> {threads_cnt}[/bold cyan] ")

        def cyclic_shrink(img_list: list):
            for img in img_list:
                shrink_image(img)
        with log.console().status("[bold blue]Shrinking Your Images...", spinner="earth") as s:
            for i in range(len(handle_img_list)):
                new_thread = threading.Thread(
                    target=cyclic_shrink, args=(handle_img_list[i],))
                threads.append(new_thread)
                new_thread.start()
            for i in threads:
                i.join()
    end_time = time.time()
    log.success(
        f"Shrink Images Successfully! It Takes {end_time - start_time}s")


if __name__ == '__main__':
    # thread_shrink("D:\\图片\\background", 8)
    thread_shrink(sys.argv[1:][0], threads_cnt=8)
        
