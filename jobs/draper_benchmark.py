import itertools
import time
import logging

from datetime import date, datetime

import sys
from qiskit import QuantumProgram, Result
import algorithms.draper as draper
from interfaces import ApiCredentials
import credentials
from models import Experiment

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


def sync_job(Q_program: QuantumProgram, experiment: Experiment):
    bits = ["0b00", "0b01", "0b10", "0b11"]

    for a,b in itertools.product(bits, bits):
        qasm, qobj, expected  = draper.create_experiment(Q_program, a, b, experiment)
        shots = 1000
        result: Result = Q_program.execute(["draper"], backend, shots=shots)

        op_length = len(qasm.split("\n"))
        computational_result = ""
        success = False
        counts = dict()
        calibrations = []

        data = result.get_data("draper")
        if "counts" in data:
            counts: dict = data["counts"]
            computational_result = max(counts.keys(), key=(lambda key: counts[key]))
            success = expected == computational_result

        log_msg = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (datetime.isoformat(datetime.now()), backend, a, b, op_length,
                                                        shots, expected, computational_result, success, counts,
                                                        calibrations, version)
        print(log_msg)


def async_job(qp: QuantumProgram, experiment: Experiment, block_missing_credits = True):
    bits = ["0b00", "0b01", "0b10", "0b11"]

    running_jobs = []
    done_jobs = []

    for a,b in itertools.product(bits, bits):
        qasm, qobj, expected = experiment.create_experiment(qp, (a, b))
        shots = 1024

        credits = qp.get_api().get_my_credits()
        backend_status = qp.get_api().backend_status(experiment.backend)
        log.debug("Current credits: %s" % credits["remaining"])
        log.debug("Current backend status: %s" % backend_status)
        while credits["remaining"] < 3 and block_missing_credits:
            time.sleep(10)
            credits = qp.get_api().get_my_credits()
            log.debug("Current credits: %s" % credits["remaining"])
            log.debug("Current backend status: %s" % backend_status)

        job_result = qp.get_api().run_job([{"qasm": qasm}], experiment.backend, shots, max_credits=3, seed=None)
        jobId = job_result["id"]

        op_length = len(qasm.split("\n"))
        job = [ experiment.backend, jobId, a, b, op_length, shots, expected, experiment.version ]
        log.debug("Added job %s (%s+%s)..." % (jobId, a, b))
        running_jobs.append(job)

    while len(running_jobs) > 0:
        for jobEntry in running_jobs:
            job_result = qp.get_api().get_job(jobEntry[1])
            log.debug("Checking job %s..." % (jobEntry[1]))
            if "status" in job_result and job_result["status"] == "COMPLETED":
                log.debug("Done job %s..." % (jobEntry[1]))
                running_jobs.remove(jobEntry)
                jobEntry.append(job_result)
                done_jobs.append(jobEntry)
        time.sleep(2)

    for jobEntry in done_jobs:
        result = jobEntry[8]
        computational_result = ""
        success = False
        counts = dict()
        calibrations = {}
        computational_result_prob = 0.0

        if "qasms" in result and len(result["qasms"]) == 1 and "data" in result["qasms"][0]:
            data = result["qasms"][0]["data"]
            if "counts" in data:
                counts: dict = data["counts"]
                computational_result = max(counts.keys(), key=(lambda key: counts[key]))
                success = jobEntry[6] == computational_result
                shots = jobEntry[5]
                computational_result_count = max(counts.values())
                computational_result_prob = float(computational_result_count)/float(shots)
            if "calibration" in result:
                calibrations = result["calibration"]

        log_msg = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (datetime.isoformat(datetime.now()), jobEntry[0], jobEntry[1],
                                                       jobEntry[2], jobEntry[3], jobEntry[4],jobEntry[5], jobEntry[6],
                                                       computational_result, computational_result_prob, success,
                                                       counts, calibrations, jobEntry[7])
        log.info(log_msg)


if __name__ == "__main__":
    credentials = ApiCredentials()
    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(credentials.GetToken(), credentials.GetApiUri())

    backend = draper.backend_online_simulator
    version = "V1.0"
    block_at_no_credits = True

    for arg in sys.argv:
        if "-real" == arg:
            backend = draper.backend_real_processor
            block_at_no_credits = True
        if "-sim" == arg:
            backend = draper.backend_online_simulator
            block_at_no_credits = False
        if "-version=" in arg:
            version = arg.replace("-version=", "")

    from algorithms import DraperExperiment
    experiment = DraperExperiment(backend, version)

    async_job(Q_program, experiment, block_at_no_credits)