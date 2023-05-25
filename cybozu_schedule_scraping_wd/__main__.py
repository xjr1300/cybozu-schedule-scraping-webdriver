from time import sleep

from . import prompt_user_for_login_info, prompt_user_for_year_month
from .chrome_driver import start_chrome_driver


def main() -> None:
    """メイン関数。"""

    # ユーザーにログイン情報の入力を要求
    login_info = prompt_user_for_login_info()
    # ユーザーにスケジュールを取得する年月の入力を要求
    ym = prompt_user_for_year_month()
    # Chrome WebDriverをヘッドレスモードで起動するか確認
    headless = input("Chrome WebDriverをヘッドレスモードで起動しますか？(y/N): ").lower() == "y"

    with start_chrome_driver(headless=headless) as driver:
        driver.get("https://www.google.com/")
        print(driver.title)
        sleep(3)


if __name__ == "__main__":
    main()
