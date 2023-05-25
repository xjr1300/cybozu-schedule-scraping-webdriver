import contextlib
import os
from dataclasses import dataclass
from datetime import time
from typing import Generator, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import service as chrome_service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from . import ROOT_DIR, CBSSWDException, LoginInfo, YearMonth, cybozu_page_url


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


def _str_to_time(text: str) -> Optional[time]:
    """文字列を時刻に変換する。

    引数:
        text: 時刻に変換する文字列。
    戻り値:
        文字列から変換した時刻。
        時刻に変換できない場合は`None`。
    """
    text = text.strip()
    if not text:
        return None
    splitted = text.split(":", 1)
    if len(splitted) != 2:
        return None
    return time(hour=int(splitted[0]), minute=int(splitted[1]))


def _time_to_str(time: Optional[time]) -> str:
    """時刻を文字列に変換する。

    引数:
        time: 文字列に変換する時刻。
    戻り値:
        時刻を変換した文字列。
        時刻が`None`の場合は`""`。
    """
    return time.strftime("%H:%M") if time else ""


@dataclass
class Schedule:
    # 日
    day: int
    # 開始時刻
    begin: Optional[time]
    # 終了時刻
    end: Optional[time]
    # スケジュールのタイトル
    title: Optional[str]

    def __str__(self) -> str:
        if not self.begin and not self.end:
            return f"{self.day}日 {self.title}"
        else:
            begin_str = _time_to_str(self.begin)
            end_str = _time_to_str(self.end)
            time_range = f"{begin_str}-{end_str}" if end_str else begin_str
            return f"{self.day}日 {time_range} {self.title}"


def _is_event_cell_at_month(event_cell: WebElement, month: int) -> bool:
    """td.eventcellがスケジュールを抽出したい月であるか確認する。

    引数:
        event_cell: td.eventcell要素。
        month: スケジュールを抽出したい月。

    戻り値:
        td.eventcellがスケジュールを抽出したい月の場合はTrue。それ以外はFalse。
    """
    date_span = event_cell.find_element(By.CSS_SELECTOR, "span.date")
    date_str = date_span.get_attribute("textContent")
    m, _ = date_str.split("/", 1)
    return int(m) == month


def _retrieve_event_links_in_event_cell(
    event_cell: WebElement,
) -> Tuple[WebElement, List[WebElement]]:
    """td.eventcell要素に含まれる、すべてのdiv.eventLink要素を抽出する。

    引数:
        event_cell: td.eventcell要素。
    戻り値:
        仮引数で渡されたtd.eventcell要素と、その要素内に含まれるすべてのdiv.eventLink要素を格納したリスト。
    """
    return (
        event_cell,
        event_cell.find_elements(By.CSS_SELECTOR, "div.eventLink"),
    )


def retrieve_monthly_schedules(
    driver: webdriver.Chrome, user_id: str, ym: YearMonth
) -> List[Schedule]:
    """ユーザーの個人月表示ページに遷移して、月刊スケジュールを取得して返却する。

    引数:
        driver: Chrome WebDriver。
        user_id: ユーザーID。
        ym: スケジュールを取得する月の年月。
    戻り値:
        月間のスケジュールを格納したリスト。
    """
    # ユーザーの個人月表示ページを開く
    date_str = f"da.{ym.year:04}.{ym.month:02}.01"
    driver.get(cybozu_page_url(f"page=ScheduleUserMonth&UID={user_id}&Date={date_str}"))
    # #um__body要素が表示されるまで待機
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "um__body")))
    # td.eventcell要素を取得
    event_cells = driver.find_elements(By.CSS_SELECTOR, "td.eventcell")
    # 指定された月のtd.eventcell要素のみを抽出
    event_cells = [
        event_cell
        for event_cell in event_cells
        if _is_event_cell_at_month(event_cell, ym.month)
    ]
    # div.eventLink要素を取得
    event_cell_links = [
        _retrieve_event_links_in_event_cell(event_cell) for event_cell in event_cells
    ]
    # スケジュールを抽出
    schedules: List[Schedule] = []
    for event_cell, event_links in event_cell_links:
        # td.eventcell span.date要素から日を取得
        day = int(
            event_cell.find_element(By.CSS_SELECTOR, "span.date").text.split("/", 1)[1]
        )
        # div.eventLink要素から時間帯及びタイトルを取得
        for event_link in event_links:
            begin: Optional[time] = None
            end: Optional[time] = None
            # div.eventLink div.eventInner span.eventDateTime要素から時間帯を取得
            try:
                time_range_elem = event_link.find_element(
                    By.CSS_SELECTOR, "div.eventInner span.eventDateTime"
                )
                if time_range_elem:
                    time_range_text = time_range_elem.text.removesuffix("&nbsp;")
                    splitted = time_range_text.split("-", 1)
                    begin = _str_to_time(splitted[0])
                    if len(splitted) == 2:
                        end = _str_to_time(splitted[1])
            except NoSuchElementException:
                pass
            # div.eventLink div.eventInner span.eventDetail a.event要素からタイトルを取得
            title_elem = event_link.find_element(
                By.CSS_SELECTOR, "div.eventInner a.event"
            )
            title = title_elem.get_attribute("title")
            if title:
                schedules.append(Schedule(day, begin, end, title))
    return schedules
