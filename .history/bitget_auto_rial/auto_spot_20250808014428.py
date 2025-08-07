#import必要なライブラリ
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient
from order_processor import place_orders  # bitget_orders → order_processor に変更

#bitgetのAPIで注文を処理するスクリプト

# config.yaml の読み込み
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)