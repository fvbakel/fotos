from test.config import *

import pathlib
import shutil


def make_test_file(filename:str):
    with open(filename,'w') as f:
        f.write('Test File')


def make_test_files():
    tmp_dir = pathlib.Path(TEST_TMP_DIR)
    test_files_dir = tmp_dir / pathlib.Path('data_dir')
    test_files_dir_str = str(test_files_dir)
    if test_files_dir.exists():
        shutil.rmtree(test_files_dir_str)
    test_files_dir.mkdir(parents=True, exist_ok=True)

    for j in range(2):
        test_files_dir_j = test_files_dir / pathlib.Path(f'sub_dir_{j}')
        test_files_dir_j.mkdir(parents=True, exist_ok=True)
        test_files_dir_j_str = str(test_files_dir_j)
        for i in range(2):
            make_test_file(f'{test_files_dir_j_str}/test_file_{i}.JPEG')
            make_test_file(f'{test_files_dir_j_str}/test_file_{i}.jpg')
    return test_files_dir_str