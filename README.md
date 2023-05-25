# cybozu-schedule-scraping-webdriver

## システム要件

- Python 3.11
- [Poetry](https://python-poetry.org/)

## インストール方法

```bash
git clone git@github.com:xjr1300/cybozu-schedule-scraping-webdriver.git
cd cybozu-schedule-scraping-webdriver
poetry install
```

## 使用方法

```bash
source .venv/bin/activate
python -m cybozu_schedule_scraping_webdriver
```

## Chrome WebDriver

本プログラムは、`Chrome WebDriver`を自動的にダウンロードして使用します。
Chrome WebDriverは、パッケージ内の`drivers`ディレクトリに保存されます。
