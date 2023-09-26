import logging
import time
TEST_TMP_DIR = "./tmp"
time_stamp = time.time()
test_fotos_base_dir = '~/tmp/fotos 2007'
logging.basicConfig(level=logging.DEBUG,filename=f"{TEST_TMP_DIR}/test_debug_{time_stamp}.log",filemode='w')