import subprocess

# big margin
subprocess.Popen(
    ["python", "bitget_auto_rial/close_subaccount_futures.py"]
).wait()  # bitget subaccount(big margin)全 position クローズ
subprocess.Popen(
    ["python", "bitget_auto_rial/all_cancel_sub_account.py"]
).wait()  # bitget subaccount(big margin)オーダー全キャンセル
