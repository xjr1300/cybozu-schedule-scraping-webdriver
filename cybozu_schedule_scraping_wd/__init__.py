import os

# パッケージルートディレクトリ
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CBSSWDException(Exception):
    """Cybozu Schedule Scraping WebDriverの例外クラス"""
