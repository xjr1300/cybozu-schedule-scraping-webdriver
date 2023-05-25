from selenium import webdriver

from . import prompt_user_for_login_info, prompt_user_for_year_month
from .chrome_driver import login, retrieve_division_code, start_chrome_driver


def main(driver: webdriver.Chrome) -> None:
    """メイン関数。"""

    # 組織選択ページに移動して、ユーザーが入力した部署の組織コードを取得
    division_code = retrieve_division_code(driver, login_info.division_name)

    # ログインページに遷移して、ログイン
    user_id = login(driver, division_code, login_info)
    print(user_id)


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
    import time

    time.sleep(10)
