import cv2
import dlib
import main
import time
import numpy as np
import frontalization
from skimage import feature
from classifier import Classifier


def classify(args):
	start_time = time.clock()
	detector = dlib.get_frontal_face_detector()
	front = frontalization.Front(args)
	image = cv2.resize(cv2.imread(args.image, cv2.IMREAD_COLOR), (150, 150))
	detection = detector(image, 1)
	for _, detection in enumerate(detection):
		rgb_image = image[detection.top():detection.bottom(), detection.left():detection.right()]
		lbp_image = feature.local_binary_pattern(cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY).astype(np.float64), 8, 1, 'uniform').astype(np.uint8)
		frgb_image = front.frontalized(image)
		flbp_image = feature.local_binary_pattern(cv2.cvtColor(frgb_image, cv2.COLOR_BGR2GRAY).astype(np.float64), 8, 1, 'uniform')

		main.log(args, str(time.clock() - start_time) + ' Image Representations Extracted')

		classifications = []

		rgb_classifier = Classifier(args, start_time, args.classes, args.resource_dir, rgb_image.shape, 'rgb', local=False)
		classifications.append(rgb_classifier.classify(rgb_image, (args.model_name + '/rgb/')))

		lbp_classifier = Classifier(args, start_time, args.classes, args.resource_dir, lbp_image.shape, 'lbp', local=False)
		classifications.append(lbp_classifier.classify(lbp_image, (args.model_name + '/lbp/')))

		frgb_classifier = Classifier(args, start_time, args.classes, args.resource_dir, frgb_image.shape, 'frgb', local=False)
		classifications.append(frgb_classifier.classify(frgb_image, (args.model_name + '/frgb/')))

		lfrgb_classifier = Classifier(args, start_time, args.classes, args.resource_dir, frgb_image.shape, 'lfrgb', local=True)
		classifications.append(lfrgb_classifier.classify(frgb_image, (args.model_name + '/lfrgb/')))

		flbp_classifier = Classifier(args, start_time, args.classes, args.resource_dir, flbp_image.shape, 'flbp', local=False)
		classifications.append(flbp_classifier.classify(flbp_image, (args.model_name + '/flbp/')))

		lflbp_classifier = Classifier(args, start_time, args.classes, args.resource_dir, flbp_image.shape, 'lflbp', local=True)
		classifications.append(lflbp_classifier.classify(flbp_image, (args.model_name + '/lflbp/')))

		result = np.zeros(args.classes)
		for classification in classifications:
			for i in range(len(classification)):
				result[i] += classification[i] / 6

		main.log(args, '\n' + str(time.clock() - start_time) + ' ' + args.image + ' classified as ' + str(result), True)
		return True
	main.log(args, '\n' + str(time.clock() - start_time) + ' Could not detect face in inputted image', True)
