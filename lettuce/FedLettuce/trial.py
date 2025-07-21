import numpy as np

wrong_terms = ['Memantine HCL', 'Ppaliperidone (3-month)']
joined_terms = "\n".join(wrong_terms)
byte_data = joined_terms.encode('utf-8')
param_array = np.frombuffer(byte_data, dtype=np.uint8)
print(param_array)
print(param_array.dtype)
print(param_array.tobytes().decode('utf-8'))
