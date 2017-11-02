import json

from IBMQuantumExperience.IBMQuantumExperience import IBMQuantumExperience

token = "a6c65f024279c033c9368bd14e6f9079b71fdfd00625b1f3d3573475c97d84d429c8b4316aa572709dd2670e9a069e735f127342360a7ec6bd8f17f82a997ba2"

qe: IBMQuantumExperience = IBMQuantumExperience(token)
print(qe.available_backends())

print(qe.check_credentials())

print(qe.backend_parameters("ibmqx2"))