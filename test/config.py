import logging
import time
TEST_TMP_DIR = "./tmp"
TEST_PHOTO_BASE_DIR = '/home/fvbakel/tmp/test_foto'

time_stamp = time.time()
logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/test_debug_{time_stamp}.log",filemode='w')