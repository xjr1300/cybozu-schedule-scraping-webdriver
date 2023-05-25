import os
from dataclasses import dataclass
from datetime import date, time
from getpass import getpass

# パッケージルートディレクトリ
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CBSSWDException(Exception):
    """Cybozu Schedule Scraping WebDriverの例外クラス"""


@dataclass
class LoginInfo:
    """ログイン情報"""

    # サイボウズにログインするユーザーを選択するときに指定する組織
    division_name: str
    # サイボウズにログインするユーザーの名前
    name: str
    # 上記ユーザーのパスワード
    password: str


class YearMonth:
    """年月"""

    # 年
    year: int
    # 月
    month: int

    def __init__(self, year: int, month: int) -> None:
        """イニシャライザ

        引数:
            year: 年。
            month: 月。
        """
        if year < 1900 or 2100 < year:
            raise CBSSWDException("年は1900以上2100以下を指定してください。")
        if month < 1 or 12 < month:
            raise CBSSWDException("月は1以上12以下を指定してください。")
        self.year = year
        self.month = month

    def __str__(self) -> str:
        return f"{self.year:04}/{self.month:02}"

    def __repr__(self) -> str:
        return f"YearMonth(year={self.year}, month={self.month})"

    @property
    def text_jp(self) -> str:
        """年月を日本語で表現した文字列を返却する。

        戻り値:
            年月を日本語で表現した文字列。
        """
        return f"{self.year:04}年{self.month:02}月"


def prompt_user_for_login_info() -> LoginInfo:
    """ユーザーにサイボウズにログインするときに必要な情報の入力を求める。

    戻り値:
        ログイン情報。
    """

    division_name = input("サイボウズでユーザーを選択するときの組織名: ")
    name = input("サイボウズにログインするユーザーの名前: ")
    password = getpass("パスワード: ")
    return LoginInfo(division_name, name, password)


def prompt_user_for_year_month() -> YearMonth:
    """ユーザーにスケジュールを取得する年と月の入力を求める。

    戻り値:
        年月。
    """
    today = date.today()
    separator = "/"
    default_value = f"{today.year:04}{separator}{today.month:02}"
    text = input(f"スケジュールを取得する年月 [default: {default_value}]: ")
    if not text:
        text = default_value
    splitted = text.split(separator)
    if len(splitted) != 2:
        raise CBSSWDException(f"年と月を{separator}で区切って入力してください。")
    try:
        year = int(splitted[0])
    except ValueError:
        raise CBSSWDException("年を数値として認識できません。")
    try:
        month = int(splitted[1])
    except ValueError:
        raise CBSSWDException("月を数値として認識できません。")
    return YearMonth(year, month)
