from time import sleep

from .chrome_driver import start_chrome_driver


def main() -> None:
    """メイン関数。"""
    with start_chrome_driver(headless=False) as driver:
        driver.get("https://www.google.com/")
        print(driver.title)
        sleep(3)


if __name__ == "__main__":
    main()
