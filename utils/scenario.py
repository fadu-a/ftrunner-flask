import csv
import datetime
import json
import os
import ast
import subprocess
from subprocess import Popen, PIPE
import time
import threading
from flask import request, Flask, Response, redirect, url_for
import requests
import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
GLOBAL_CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")


class Scenario(object):
    def __init__(self, data):
        #print(data)
        self.id = data['id']
        self.name = data['name']
        self.testcases = data['testcases']
        #print(self.testcases)
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dirname = os.path.join(RESULTS_DIR, self.timestamp)
        self.job_files = []
        self.job_ids = []

    def create_job_files(self):
        os.makedirs(self.dirname)
        print(GLOBAL_CONFIGS_DIR)
        for job in self.testcases:
            print(job)
            id = job.pop('id')
            name = job.pop('name')
            order = job.pop('order')
            configs = job.pop('configs')
            # configs_list = []
            # configs = configs.replace("'","")
            # configs_list = configs
            # configs_list.insert(0,"{")
            # configs_list.insert(-1,"}")
            # print(configs)
            # configs_list = json.loads(configs_list)
            # configs = json.dumps(configs_list)
            print(configs)
            global_config = configs.pop('global')


            file_path = os.path.join(self.dirname, f"{order}_{name}.job")
            with open(file_path, "w") as f:
                f.write("[global]\n")
                f.write(f"include {GLOBAL_CONFIGS_DIR}/global-{global_config}.fio\n\n")
                f.write("[job1]\n")
                f.write(f"description=[{self.id}] {order}_{name}\n")
                for key in configs.keys():
                    f.write(f"{key}={configs[key]}\n")
            self.job_files.append(file_path)
            self.job_ids.append(id)

    def run_test(self):
        global fio_process, fio_thread

        for index, job_file in enumerate(self.job_files):
            cmd = [
                "fio",
                f"{job_file}",
                "--status-interval=1",
                "--minimal"
            ]
            fio_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setpgrp)
            fio_thread = threading.Thread(target=self.read_test_log(self.job_ids[index]), args=())
            fio_thread.daemon = True
            fio_thread.start()
        fio_status = {'status': 1}
        requests.patch("http://192.168.0.16:8000/api/fio/results/{}/".format(self.id), data=fio_status)

    def read_test_log(self, job_id):
        print("Test")
        while fio_process.poll() == None:
            std_line = fio_process.stdout.readline()
            print(std_line)
            headers = {'Content-type':'application/json'}
            re = requests.put("http://192.168.0.16:8000/api/fio/io_logs/{}/append/".format(job_id), json="{}".format(std_line), headers=headers)
            re.text
            re.status_code
            print(re.text)

    def do_test(self):
        self.create_job_files()
        self.run_test()




