import csv
import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")


class TestCase(object):
    def __init__(self, config):
        name = config['name']
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.order = config.pop('order')
        self.dirname = os.path.join(RESULTS_DIR, self.timestamp)
        self.config_file_path = os.path.join(self.dirname, f"{self.order}_{name}.job")
        self.result_file_path = os.path.join(self.dirname, f"{self.order}_{name}.result")
        self.file_prefix = os.path.join(self.dirname, f"{self.order}_{name}")
        self.config = config

    def create_config_file(self):
        os.makedirs(self.dirname)

        with open(self.config_file_path, "w") as f:
            f.write(f"[job{self.order}]\n")
            for key in self.config.keys():
                f.write(f"{key}={self.config[key]}\n")
            # for key in ['bw', 'lat', 'iops']:
            #     f.write(f"write_{key}_log={self.file_prefix}\n")

    def run_test(self):
        cmd = [
            f"fio {self.config_file_path}",
            f"--write_bw_log={self.file_prefix}",
            f"--write_lat_log={self.file_prefix}",
            f"--write_iops_log={self.file_prefix}",
            "--status-interval=1 --minimal"
        ]
        print(" ".join(cmd))
        os.system(" ".join(cmd))

    def parse_result_file(self):
        results = {}
        fieldnames = ['time', 'value', 'dir', 'bs']
        for type in ['bw', 'iops', 'lat']:
            csvfile = open(f"{self.file_prefix}_{type}.1.log", 'r')
            reader = csv.DictReader(csvfile, fieldnames, skipinitialspace=True)
            for line in reader:
                key = str(int(int(line['time']) / 1000))
                if key not in results:
                    results[key] = {}
                results[key][type] = {'value': line['value'], 'dir': line['dir']}
        return json.dumps(results)

    def do_test(self):
        self.create_config_file()
        self.run_test()
        return self.parse_result_file()
