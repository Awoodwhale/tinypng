import json
import os
import random
import requests
import sys
import time
import threading

def list_images(path):
    images = None
    try:
        if path:
            os.chdir(path)
        full_path = os.getcwd()
        files = os.listdir(full_path)
        images = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png'):
                images.append(os.path.join(full_path, file))
    except:
        pass
    return images

def shrink_image(file_path):
    print(file_path)
    result = shrink(file_path)
    if result:
        output_path = generate_output_path(file_path)
        url = result['output']['url']
        response = requests.get(url)
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(output_path)
        print('%s %d=>%d(%f)' % (
            result['input']['type'],
            result['input']['size'],
            result['output']['size'],
            result['output']['ratio']
            ))
    else:
        print('压缩失败')

def shrink(file_path):
    url = 'https://tinypng.com/web/shrink'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'X-Forwarded-For': get_random_ip()
    }
    result = None
    try:
        file = open(file_path, 'rb')
        response = requests.post(url, headers=headers, data=file)
        result = json.loads(response.text)
    except:
        if file:
            file.close()
    if result and result['input'] and result['output']:
        return result
    else:
        return None

def generate_output_path(file_path):
    parent_path = os.path.abspath(os.path.dirname(file_path))
    output_path = os.path.join(parent_path, 'tinypng_output')
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    return os.path.join(output_path, os.path.basename(file_path))

def get_random_ip():
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)

if __name__ == '__main__':
    threads = []
    startTime = time.time()
    path = ''
    if len(sys.argv) > 1:
        path = sys.argv[1]
    images = list_images(path)
    if images is None:
        print('Path error!')
    else:
        print('-' * 80)
        print("Start!")
        print(f'Try to download {len(images)} pictures!')
        for image in images:
            print('-' * 80)
            t = threading.Thread(target=shrink_image, args=(image,))
            t.start()
            threads.append(t)
            time.sleep(0.5)
        for t in threads:
            t.join()
    endTime = time.time()
    print('-' * 80)
    print(f"Finished! It takes {endTime-startTime}s time!")