import csv
import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
GLOBAL_CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")


class Scenario(object):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.jobs = data['jobs']
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dirname = os.path.join(RESULTS_DIR, self.timestamp)
        self.job_files = []

    def create_job_files(self):
        os.makedirs(self.dirname)
        print(GLOBAL_CONFIGS_DIR)
        for job in self.jobs:
            id = job.pop('id')
            name = job.pop('name')
            order = job.pop('order')
            global_config = job.pop('global')

            file_path = os.path.join(self.dirname, f"{order}_{name}.job")
            with open(file_path, "w") as f:
                f.write("[global]\n")
                f.write(f"include {GLOBAL_CONFIGS_DIR}/global-{global_config}.fio\n\n")
                f.write("[job1]\n")
                f.write(f"description=[{self.id}] {order}_{name}\n")
                for key in job.keys():
                    f.write(f"{key}={job[key]}\n")
            self.job_files.append(file_path)

    def run_test(self):
        for job_file in self.job_files:
            cmd = [
                f"fio {job_file}",
                "--status-interval=1 --minimal"
            ]
            print(" ".join(cmd))
            os.system(" ".join(cmd))

    def do_test(self):
        self.create_job_files()
        self.run_test()

