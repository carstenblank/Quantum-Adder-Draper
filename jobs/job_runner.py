import sys
import logging
import time
from datetime import datetime
from typing import List

from qiskit import QuantumProgram

import models
from interfaces import ApiCredentials
from models import Experiment

import credentials

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

logging.getLogger().handlers.clear()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logging.getLogger().addHandler(ch)

log = logging.getLogger("draper")
log.setLevel(10)


class RunningExperimentData(object):

    def __init__(self, job_id, executing_backend, shots, input, output, experiment: Experiment):
        self.job_id = job_id
        self.executing_backend = executing_backend
        self.backend = experiment.backend
        self.shots = shots
        self.input = input
        self.output = output
        self.name = experiment.name
        self.version = experiment.version
        self.qubit_mapping = experiment.qubit_mapping
        self.algorithm = experiment.algorithm
        self.success: bool = False
        self.counts: dict = {}
        self.computational_result: int = ""
        self.computational_result_prob: float = 0.0
        self.calibrations: dict = {}

    def complete_job(self, result: dict):
        if "qasms" in result and len(result["qasms"]) == 1 and "data" in result["qasms"][0]:
            data = result["qasms"][0]["data"]
            if "counts" in data:
                self.counts = data["counts"]
                self.computational_result = max(self.counts.keys(), key=(lambda key: self.counts[key]))
                self.success = self.output == self.computational_result
                computational_result_count = max(self.counts.values())
                self.computational_result_prob = float(computational_result_count)/float(self.shots)
            if "calibration" in result:
               self. calibrations = result["calibration"]

    def to_log(self):
        fields = [
            datetime.isoformat(datetime.now()),
            self.job_id,
            self.executing_backend,
            self.backend,
            self.shots,
            self.input,
            self.output,
            self.name,
            self.version,
            self.qubit_mapping,
            self.algorithm,
            self.success,
            self.computational_result,
            self.computational_result_prob,
            self.counts,
            self.calibrations
        ]
        stringified_fields = map(lambda f: str(f), fields)
        return ";".join(stringified_fields)


def async_job(qp: QuantumProgram, experiment: Experiment, block_missing_credits=True, use_sim=True):

    running_jobs: List[RunningExperimentData] = []
    done_jobs: List[RunningExperimentData] = []

    for algorithm_input in experiment.get_inputs():
        qasm, qobj, expected = experiment.create_experiment(qp, algorithm_input)

        executing_backend = models.backend_online_simulator if use_sim else experiment.backend

        my_credits = qp.get_api().get_my_credits()
        backend_status = qp.get_api().backend_status(executing_backend)

        log.debug("Current credits: %s" % my_credits["remaining"])
        log.debug("Current executing backend status: %s" % backend_status)

        while my_credits["remaining"] < 3 and block_missing_credits:
            time.sleep(10)
            my_credits = qp.get_api().get_my_credits()

            log.debug("Current credits: %s" % my_credits["remaining"])
            log.debug("Current executing backend status: %s" % backend_status)

        job_result = qp.get_api().run_job([{"qasm": qasm}], executing_backend, experiment.get_shots(), max_credits=3, seed=None)
        job_id = job_result["id"]

        job = RunningExperimentData(job_id, executing_backend, experiment.get_shots(), algorithm_input, expected, experiment)
        running_jobs.append(job)

        log.debug("Added job %s (%s)..." % (job_id, str(algorithm_input)))

    while len(running_jobs) > 0:
        for job_entry in running_jobs:
            job_result = qp.get_api().get_job(job_entry.job_id)

            log.debug("Checking job %s..." % (job_entry.job_id))
            if "status" in job_result and job_result["status"] == "COMPLETED":
                log.debug("Done job %s..." % (job_entry.job_id))
                running_jobs.remove(job_entry)
                job_entry.complete_job(job_result)
                done_jobs.append(job_entry)
        time.sleep(2)

    for job_entry in done_jobs:
        log.info(job_entry.to_log())

    commands.update_config_file()


class Commands(object):
    def __init__(self):
        self.backend = models.backend_online_simulator
        self.is_sim = True
        self.experiment: Experiment = None
        self.version = "V1.0"
        self.block_at_no_credits = True
        self.experiment_name = ""
        self.configfile = None
        self.config_index = -1

    def load(self, args):
        for arg in args:
            if "-ibmqx5" == arg:
                self.backend = models.backend_online_ibmqx5
            if "-ibmqx4" == arg:
                self.backend = models.backend_online_ibmqx4
            if "-ibmqx2" == arg:
                self.backend = models.backend_online_ibmqx2
            if "-sim" == arg:
                self.block_at_no_credits = False
                self.is_sim = True
            if "-real" == arg:
                self.block_at_no_credits = True
                self.is_sim = False
            if "-version=" in arg:
                self.version = arg.replace("-version=", "")
            if "-config=" in arg:
                self.configfile = arg.replace("-config=", "")
            if "-experiment=" in arg:
                self.experiment_name = arg.replace("-experiment=", "")

    def update_config_file(self):
        import io
        programs: list
        with io.open(self.configfile, newline='\n') as file:
            programs = [[index] + line.split(";") for index, line in enumerate(file.readlines())]

        [index, args, count] = programs[self.config_index]
        lines = []
        for prg in programs:
            if prg[0] != index:
                lines.append(";".join([ prg[1], prg[2].replace("\n","") ]))
            else:
                lines.append(";".join([args, str(int(count) + 1)]))

        with io.open(self.configfile, mode='w', newline="\n") as file:
            file.write("\n".join(lines))

    @staticmethod
    def load_from_config_file(config_file, qc: QuantumProgram):
        import io
        with io.open(config_file) as file:
            programs = [ [index] + line.split(";") for index,line in enumerate(file.readlines())]
            sorted_programs = list(sorted(programs, key=lambda k: k[2]))
            for prg in sorted_programs:
                [index, args, count] = prg
                commands = Commands()
                commands.load(args.split(" "))
                status = qc.get_api().backend_status(commands.backend)
                if "available" in status and status["available"] and status["pending_jobs"] < 15:
                    commands.config_index = index
                    commands.configfile = config_file
                    return commands
        return None

    def experiment_lookup(self):
        if len(self.experiment_name) == 0:
            raise Exception("Experiment not given!")

        if self.experiment_name == "draper":
            from algorithms import DraperExperiment
            self.experiment = DraperExperiment(self.version, self.backend)


if __name__ == "__main__":
    credentials = ApiCredentials()
    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(credentials.GetToken(), credentials.GetApiUri())

    commands = Commands()
    commands.load(sys.argv)
    if commands.configfile is not None:
        commands = Commands.load_from_config_file(commands.configfile, Q_program)
    # command line arguments have precedence, hence load them again
    commands.load(sys.argv)
    commands.experiment_lookup()

    async_job(Q_program, commands.experiment, commands.block_at_no_credits, commands.is_sim)