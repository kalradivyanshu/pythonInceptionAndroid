from flask import Flask, request
import base64
import sys
from time import time
from server import run_inference_on_image
import os
app = Flask(__name__)

@app.route("/", methods=['POST'])
def index():
	if request.method == 'POST':
		image_raw = request.form.get('image', '')
		#print(image_raw)
		try:
			try:
				image = base64.b64decode(image_raw).strip()
				print(type(image))
			except Exception as ex:
				s = str(ex)
				e = sys.exc_info()[0]
				ERROR = str((e,s))
				print(ERROR)
				return "DecodeError: "+ERROR
			#image = image.decode('utf-8')
			name = str(int(time()))+"_image.png"
			name = "./uploads/"+name

			file_ = open(name, 'wb')
			file_.write(image)
			file_.close()
			result = run_inference_on_image(os.path.abspath(name))
			print(result)
			return result
		except Exception as ex:
			s = str(ex)
			e = sys.exc_info()[0]
			ERROR = str((e,s))
			print(ERROR)
			return ERROR



if __name__ == '__main__':
	app.run(host= '0.0.0.0', debug=True)