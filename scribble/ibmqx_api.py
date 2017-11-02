import json

from qiskit import QuantumProgram, QuantumRegister, QuantumCircuit

token = "a6c65f024279c033c9368bd14e6f9079b71fdfd00625b1f3d3573475c97d84d429c8b4316aa572709dd2670e9a069e735f127342360a7ec6bd8f17f82a997ba2"
url = 'https://quantumexperience.ng.bluemix.net/api'

if __name__ == '__main__':
    # Creating Programs create your first QuantumProgram object instance.
    Q_program: QuantumProgram = QuantumProgram()
    Q_program.set_api(token, url)

    api = Q_program.get_api()
    try:
        response: list = api.get_jobs(limit=1000)
        last_result = response[-1]
        print(last_result['status'])

        if last_result['status'] == "COMPLETED":
            last_result_counts = last_result["qasms"][0]["result"]["data"]["counts"]
            print(last_result_counts)

        print("Result Dump:")
        print(json.dumps(response[-1]))
    except Exception as err:
        print("Error %s(%s)" % (type(err), err))