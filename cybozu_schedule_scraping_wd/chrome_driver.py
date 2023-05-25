import contextlib
import os
from typing import Generator

from selenium import webdriver
from selenium.webdriver.chrome import service as chrome_service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from . import ROOT_DIR, CBSSWDException, LoginInfo, cybozu_page_url


def get_chrome_driver_dir() -> str:
    """Chrome WebDriverのパスを返却する。

    戻り値:
        Chrome WebDriverのパス。
    """
    return os.path.join(ROOT_DIR, "drivers")


@contextlib.contextmanager
def start_chrome_driver(headless: bool) -> Generator[webdriver.Chrome, None, None]:
    """Chrome WebDriverを起動する。

    引数:
        headless: ヘッドレスモードでChrome WebDriverを起動する場合はTrue。それ以外はFalse。
    戻り値:
        なし。
    """
    # WebDriver ManagerがChrome WebDriverをダウンロードするときの進捗の表示を抑制
    os.environ["WDM_PROGRESS_BAR"] = "0"
    # Chrome WebDriverの更新が必要であれば更新して、Chrome WebDriverのパスを取得
    driver_dir = get_chrome_driver_dir()
    driver_path = ChromeDriverManager(path=driver_dir).install()
    # ヘッドレスモードを設定
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")

    # Chrome WebDriverを起動する。
    try:
        service = chrome_service.Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        yield driver
    finally:
        driver.close()


def retrieve_division_code(driver: webdriver.Chrome, division_name) -> str:
    """サイボウズの組織選択ページから、引数で指定された組織名と一致する組織の組織コードを取得する。

    引数:
        driver: Chrome WebDriver。
        division_name: 組織名。
    戻り値:
        組織コード。
    例外:
        CBSSWDException: 組織名が見つからなかった場合。
    """
    # 組織選択ページを開く
    driver.get(cybozu_page_url("page=LoginGroup"))
    # 組織を選択するselect要素のoption要素を取得
    options = driver.find_elements(
        By.CSS_SELECTOR, "select.select-gid[name='Group'] option"
    )
    # 部署名が一致するoption要素を抽出
    options = [option for option in options if option.text == division_name]
    if not options:
        raise CBSSWDException(f"部署名「{division_name}」が見つかりませんでした。")
    # 組織コードを返却
    return options[0].get_attribute("value")


def login(driver: webdriver.Chrome, division_code: str, login_info: LoginInfo) -> str:
    """サイボウズのログインページに遷移して、ログインする。

    引数:
        driver: Chrome WebDriver。
        division_code: 組織コード。
        login_info: ログイン情報。
    戻り値:
        ユーザーID。
    例外:
        CBSSWDException: 名前が見つからなかった場合。
    """
    # ログインページを開く
    driver.get(cybozu_page_url(f"Group={division_code}"))
    # 名前を選択するselect要素のoption要素を取得
    options = driver.find_elements(By.CSS_SELECTOR, "select[name='_ID'] option")
    # 名前が一致するoption要素を抽出
    options = [option for option in options if option.text == login_info.name]
    if not options:
        raise CBSSWDException(f"名前「{login_info.name}」が見つかりませんでした。")
    # ユーザーIDを取得
    user_id = options[0].get_attribute("value")
    # 名前を選択
    options[0].click()
    # パスワードを入力
    element = driver.find_element(By.CSS_SELECTOR, "input[name='Password']")
    element.send_keys(login_info.password)
    # ログインボタンをクリック
    element = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    element.click()
    # ページが更新されて、#header-menu-user要素が表示されるまで待機
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "header-menu-user"))
    )
    return user_id
