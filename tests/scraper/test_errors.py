from scraper.errors import CookieExpiredError


class TestCookieExpiredError:
    def test_with_expiry(self):
        err = CookieExpiredError("01/01/2024 00:00")
        assert err.expiry_date == "01/01/2024 00:00"
        assert isinstance(str(err), str)

    def test_without_expiry(self):
        err = CookieExpiredError()
        assert err.expiry_date is None

    def test_with_none(self):
        err = CookieExpiredError(None)
        assert err.expiry_date is None
