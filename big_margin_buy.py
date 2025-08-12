import subprocess

# big margin buy

subprocess.Popen(
    ["python", "bitget_auto_rial/subaccount_futures.py"]
).wait()  # bitget subaccount(big margin)オーダー

