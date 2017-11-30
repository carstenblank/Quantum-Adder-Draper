import itertools
import time
import logging

from datetime import date, datetime

import sys
from qiskit import QuantumProgram, Result
import algorithms.draper as draper
from interfaces import ApiCredentials
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


def sync_job(Q_program: QuantumProgram, backend: str):
    bits = ["0b00", "0b01", "0b10", "0b11"]

    for a,b in itertools.product(bits, bits):
        qasm, expected, qobj = draper.create_experiment(Q_program, a, b, "draper",
                                                        draper.backend_real_processor,
                                                        draper.algorithm_prime)
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

        log_msg = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (datetime.isoformat(datetime.now()), backend, a, b, op_length, shots, expected, computational_result, success, counts, calibrations)
        print(log_msg)


def async_job(Q_program: QuantumProgram, backend: str, block_missing_credits = True):
    bits = ["0b00", "0b01", "0b10", "0b11"]

    running_jobs = []
    done_jobs = []

    for a,b in itertools.product(bits, bits):
        qasm, expected, qobj = draper.create_experiment(Q_program, a, b, "draper",
                                           draper.backend_real_processor, draper.algorithm_prime)
        shots = 1024
        qasm_alt = qobj["circuits"][0]["compiled_circuit_qasm"]

        credits = Q_program.get_api().get_my_credits()
        log.debug("Current credits: %s" % credits["remaining"])
        while credits["remaining"] < 3 and block_missing_credits:
            time.sleep(10)
            credits = Q_program.get_api().get_my_credits()
            log.debug("Current credits: %s" % credits["remaining"])

        job_result = Q_program.get_api().run_job([ {"qasm": qasm_alt} ], backend, shots, max_credits=3, seed=None)
        jobId = job_result["id"]

        op_length = len(qasm.split("\n"))
        job = [ backend, jobId, a, b, op_length, shots, expected ]
        log.debug("Added job %s (%s+%s)..." % (jobId, a, b))
        running_jobs.append(job)

    while len(running_jobs) > 0:
        for jobEntry in running_jobs:
            job_result = Q_program.get_api().get_job(jobEntry[1])
            log.debug("Checking job %s..." % (jobEntry[1]))
            if job_result["status"] == "COMPLETED":
                log.debug("Done job %s..." % (jobEntry[1]))
                running_jobs.remove(jobEntry)
                jobEntry.append(job_result)
                done_jobs.append(jobEntry)
        time.sleep(2)

    for jobEntry in done_jobs:
        result = jobEntry[7]
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

        log_msg = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (datetime.isoformat(datetime.now()), jobEntry[0], jobEntry[1],
                                                       jobEntry[2], jobEntry[3], jobEntry[4],jobEntry[5], jobEntry[6],
                                                       computational_result, computational_result_prob, success,
                                                       counts, calibrations)
        log.info(log_msg)


def real(Q_program):
    backend = draper.backend_real_processor
    bits = ["0b01"] #["0b00", "0b01", "0b10", "0b11"]

    for a,b in itertools.product(bits, bits):
        qasm, expected, _ = draper.create_experiment(Q_program, a, b, "draper",
                                           draper.backend_real_processor, draper.algorithm_regular)
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

        log = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (backend, a, b, op_length, shots, expected, computational_result, success, counts, calibrations)
        print(log)


if __name__ == "__main__":
    credentials = ApiCredentials()
    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(credentials.GetToken(), credentials.GetApiUri())
    async_job(Q_program, draper.backend_online_simulator, False)
    #async_job(Q_program, draper.backend_real_processor, True)
