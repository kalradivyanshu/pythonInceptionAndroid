from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import re
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow as tf
from flask import Flask, request
import base64
import sys
from time import time



FLAGS = tf.app.flags.FLAGS

# classify_image_graph_def.pb:
#   Binary representation of the GraphDef protocol buffer.
# imagenet_synset_to_human_label_map.txt:
#   Map from synset ID to a human readable string.
# imagenet_2012_challenge_label_map_proto.pbtxt:
#   Text representation of a protocol buffer mapping a label to synset ID.
tf.app.flags.DEFINE_string(
		'model_dir', '/tmp/imagenet',
		"""Path to classify_image_graph_def.pb, """
		"""imagenet_synset_to_human_label_map.txt, and """
		"""imagenet_2012_challenge_label_map_proto.pbtxt.""")
tf.app.flags.DEFINE_string('image_file', '',
													 """Absolute path to image file.""")
tf.app.flags.DEFINE_integer('num_top_predictions', 5,
														"""Display this many predictions.""")

# pylint: disable=line-too-long
DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
# pylint: enable=line-too-long


class NodeLookup(object):
	"""Converts integer node ID's to human readable labels."""

	def __init__(self,
							 label_lookup_path=None,
							 uid_lookup_path=None):
		if not label_lookup_path:
			label_lookup_path = os.path.join(
					FLAGS.model_dir, 'imagenet_2012_challenge_label_map_proto.pbtxt')
		if not uid_lookup_path:
			uid_lookup_path = os.path.join(
					FLAGS.model_dir, 'imagenet_synset_to_human_label_map.txt')
		self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

	def load(self, label_lookup_path, uid_lookup_path):
		"""Loads a human readable English name for each softmax node.

		Args:
			label_lookup_path: string UID to integer node ID.
			uid_lookup_path: string UID to human-readable string.

		Returns:
			dict from integer node ID to human-readable string.
		"""
		if not tf.gfile.Exists(uid_lookup_path):
			tf.logging.fatal('File does not exist %s', uid_lookup_path)
		if not tf.gfile.Exists(label_lookup_path):
			tf.logging.fatal('File does not exist %s', label_lookup_path)

		# Loads mapping from string UID to human-readable string
		proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
		uid_to_human = {}
		p = re.compile(r'[n\d]*[ \S,]*')
		for line in proto_as_ascii_lines:
			parsed_items = p.findall(line)
			uid = parsed_items[0]
			human_string = parsed_items[2]
			uid_to_human[uid] = human_string

		# Loads mapping from string UID to integer node ID.
		node_id_to_uid = {}
		proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
		for line in proto_as_ascii:
			if line.startswith('  target_class:'):
				target_class = int(line.split(': ')[1])
			if line.startswith('  target_class_string:'):
				target_class_string = line.split(': ')[1]
				node_id_to_uid[target_class] = target_class_string[1:-2]

		# Loads the final mapping of integer node ID to human-readable string
		node_id_to_name = {}
		for key, val in node_id_to_uid.items():
			if val not in uid_to_human:
				tf.logging.fatal('Failed to locate: %s', val)
			name = uid_to_human[val]
			node_id_to_name[key] = name

		return node_id_to_name

	def id_to_string(self, node_id):
		if node_id not in self.node_lookup:
			return ''
		return self.node_lookup[node_id]
def create_graph():
	"""Creates a graph from saved GraphDef file and returns a saver."""
	# Creates graph from saved graph_def.pb.
	with tf.gfile.FastGFile(os.path.join(
			FLAGS.model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
		graph_def = tf.GraphDef()
		graph_def.ParseFromString(f.read())
		_ = tf.import_graph_def(graph_def, name='')


def run_inference_on_image(image):
	"""Runs inference on an image.

	Args:
		image: Image file name.

	Returns:
		Nothing
	"""
	if not tf.gfile.Exists(image):
		tf.logging.fatal('File does not exist %s', image)
	image_data = tf.gfile.FastGFile(image, 'rb').read()

	# Creates graph from saved GraphDef.
	create_graph()

	with tf.Session() as sess:
		# Some useful tensors:
		# 'softmax:0': A tensor containing the normalized prediction across
		#   1000 labels.
		# 'pool_3:0': A tensor containing the next-to-last layer containing 2048
		#   float description of the image.
		# 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
		#   encoding of the image.
		# Runs the softmax tensor by feeding the image_data as input to the graph.
		softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
		predictions = sess.run(softmax_tensor,
													 {'DecodeJpeg/contents:0': image_data})
		predictions = np.squeeze(predictions)

		# Creates node ID --> English string lookup.
		node_lookup = NodeLookup()

		top_k = predictions.argsort()[-FLAGS.num_top_predictions:][::-1]
		results = list()
		most_likely = ""
		for node_id in top_k:
			human_string = node_lookup.id_to_string(node_id)
			score = predictions[node_id]
			results.append([human_string, score])
			most_likely = human_string
			break
			print('%s (score = %.5f)' % (human_string, score))
	return most_likely

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
			timenow = time()
			result = run_inference_on_image(os.path.abspath(name))
			print(time()-timenow)
			print(result)
			return result
		except Exception as ex:
			s = str(ex)
			e = sys.exc_info()[0]
			ERROR = str((e,s))
			print(ERROR)
			return ERROR

def main(_):
	image = (FLAGS.image_file if FLAGS.image_file else
					 os.path.join(FLAGS.model_dir, 'cropped_panda.jpg'))
	print(image)
	app.run(host= '0.0.0.0', debug=True)
	
if __name__ == '__main__':
	tf.app.run()
