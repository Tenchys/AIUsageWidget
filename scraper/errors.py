# scraper/errors.py


class CookieExpiredError(Exception):
    def __init__(self, expiry_date: str | None = None):
        self.expiry_date = expiry_date
        super().__init__()
