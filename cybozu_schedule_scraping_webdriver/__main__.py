import sys
from typing import IO, List

from selenium import webdriver

from . import YearMonth, prompt_user_for_login_info, prompt_user_for_year_month
from .chrome_driver import (
    Schedule,
    login,
    retrieve_division_code,
    retrieve_monthly_schedules,
    start_chrome_driver,
)


def write_monthly_schedules(
    writer: IO, name: str, ym: YearMonth, schedules: List[Schedule]
) -> None:
    """ユーザーの月間のスケジュールを書き込む。

    引数:
        writer: ユーザーの月間スケジュールを書き込むライター。
        name: ユーザーの名前。
        ym: ユーザーのスケジュールを出力する年月。
        schedules: ユーザーの月間スケジュールを格納したリスト。
    """
    print(f"{name}さんの{ym.text_jp}のスケジュールは次の通りです。", file=writer)
    for schedule in schedules:
        print(schedule, file=writer)


def main(driver: webdriver.Chrome) -> None:
    """メイン関数。"""

    # 組織選択ページに移動して、ユーザーが入力した部署の組織コードを取得
    division_code = retrieve_division_code(driver, login_info.division_name)

    # ログインページに遷移して、ログイン
    user_id = login(driver, division_code, login_info)

    # ユーザーの月間スケジュールを取得
    schedules = retrieve_monthly_schedules(driver, user_id, ym)

    # ユーザーの月間スケジュールを出力
    write_monthly_schedules(sys.stdout, login_info.name, ym, schedules)


if __name__ == "__main__":
    # ユーザーにログイン情報の入力を要求
    login_info = prompt_user_for_login_info()
    # ユーザーにスケジュールを取得する年月の入力を要求
    ym = prompt_user_for_year_month()
    # Chrome WebDriverをヘッドレスモードで起動するか確認
    headless = input("Chrome WebDriverをヘッドレスモードで起動しますか？(y/N): ").lower() == "y"
    # Chrome WebDriverを起動
    with start_chrome_driver(headless=headless) as driver:
        main(driver)
