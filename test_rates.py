import sounddevice as sd

device = 9  # your mic
info = sd.query_devices(device)
print(info)
