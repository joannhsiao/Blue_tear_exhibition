from detection import *
from flask import Flask, render_template, Response, request, make_response, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

sun_angle = 0
sun_idx = 0
blue_tear_end = False

def detect():
    global blue_tear_end, sun_idx, sun_angle
    while True:
        frame, blue_tear_end, sun_idx = get_frame(sun_angle)
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/get_end', methods=['GET'])
def clock_return():
    global blue_tear_end, sun_idx
    return str(blue_tear_end), str(sun_idx)
"""
@app.route('/get_json', methods=['POST'])
    #sun_angle
"""
@app.route("/video_feed", methods=['GET'])
def video_feed():
    return Response(detect(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6200, debug=True, threaded=True)
