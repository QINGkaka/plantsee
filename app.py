from flask import Flask, request, jsonify, render_template
import khandy
import plantid
import os
import time

app = Flask(__name__)

plant_identifier = plantid.PlantIdentifier()

@app.route('/api/identify', methods=['POST'])
def identify():
    print('request.form:', request.form)
    print('request.files:', request.files)
    # 优先处理 image 文件
    if 'image' in request.files:
        file = request.files['image']
        image = khandy.imread_cv(file.stream)
        if image is None:
            return jsonify({'status': 2, 'msg': 'Invalid image'}), 400
    # 如果没有 image 文件，尝试处理 image_url
    elif 'image_url' in request.form:
        image_url = request.form['image_url']
        print('收到 image_url:', image_url)
        try:
            import requests
            resp = requests.get(image_url, timeout=10)
            print('下载图片状态码:', resp.status_code)
            if resp.status_code != 200:
                print('status 3: Failed to download image')
                return jsonify({'status': 3, 'msg': 'Failed to download image'}), 400
            import numpy as np
            image = khandy.imread_cv(resp.content)
            print('image is None:', image is None)
            if image is None:
                print('status 2: Invalid image (from url)')
                return jsonify({'status': 2, 'msg': 'Invalid image'}), 400
        except Exception as e:
            print(f'status 4: Error downloading image: {str(e)}')
            return jsonify({'status': 4, 'msg': f'Error downloading image: {str(e)}'}), 400
    else:
        return jsonify({'status': 1, 'msg': 'No image or image_url provided'}), 400
    start = time.time()
    outputs = plant_identifier.identify(image, topk=5)
    duration = time.time() - start
    print("识别耗时：", duration)
    outputs['duration'] = duration
    return jsonify(outputs)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
