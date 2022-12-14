from detection import *
from flask import Flask, render_template, Response, request, make_response, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

sun_angle = -1
sun_idx = 0
sun_end = False

def detect():
    global sun_end, sun_idx
    while True:
        frame, sun_end, sun_idx = get_frame()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/post_json', methods=['POST'])
def process_json():
    global sun_angle
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        POST_content = request.json
        #print(POST_content['angle'])
        sun_angle = POST_content['angle']
        return make_response(jsonify(fleid= "ok"), 200)
    else:
        return 'Content-Type not supported!'

@app.route('/get_end', methods=['GET'])
def clock_return():
    global sun_end, sun_idx
    print(sun_end)
    print(sun_idx)
    return str(sun_end) + "," + str(sun_idx)

@app.route("/video_feed", methods=['GET'])
def video_feed():
    return Response(detect(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6200, debug=True, threaded=True)
