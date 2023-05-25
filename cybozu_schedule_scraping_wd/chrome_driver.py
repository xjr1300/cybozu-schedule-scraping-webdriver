import contextlib
import os
from typing import Generator

from selenium import webdriver
from selenium.webdriver.chrome import service as chrome_service
from webdriver_manager.chrome import ChromeDriverManager

from cybozu_schedule_scraping_wd import ROOT_DIR, CBSSWDException


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
    except Exception as e:
        raise CBSSWDException(f"Chrome WebDriverの起動に失敗しました。{e}")
    finally:
        driver.close()
