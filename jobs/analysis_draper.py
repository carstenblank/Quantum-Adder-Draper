import re

from qiskit import QuantumProgram

from interfaces import ApiCredentials


def map_2_meaning(row):
    date = row["date"]
    backend = row["backend"]
    m = re.search("// draper\\((.+),(.+)\\)->(\\d+)", row["target"])
    a = m.group(1)
    b = m.group(2)
    counts = row["result"]["data"]["counts"]
    shots = row["shots"]
    expected_result = m.group(3)
    computational_result = max(counts.keys(), key=(lambda key: counts[key]))
    hint_result = "2_1__"
    success = computational_result == expected_result
    computational_result_prob = counts[computational_result] / float(shots)
    expected_result_prob = counts[expected_result] / float(shots)

    calibration = row["calibration"]

    return str([date, success, backend, a, b, expected_result, expected_result_prob,
                computational_result, computational_result_prob, hint_result])


def flatten_data(x):
    return {
        'date': x["creationDate"],
        'target': x["qasms"][0]["qasm"].split('\n')[0],
        'backend': x["backend"]["name"],
        'result': x["qasms"][0]["result"],
        'calibration': x["calibration"],
        'shots': x["shots"]
    }


if __name__ == "__main__":
    import credentials
    credentials = ApiCredentials()

    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(credentials.GetToken(), credentials.GetApiUri())
    jobs = Q_program.get_api().get_jobs(limit=10000000)

    data = filter(lambda x: x["status"] == "COMPLETED",jobs)
    data = map(flatten_data, data)
    data = filter(lambda x: len(x["target"]) > 0, data)
    data = map(map_2_meaning, data)

    print(list(data))