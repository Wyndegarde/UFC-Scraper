class ScrapingException(Exception):
    """
    Exception raised for errors in the scraping process.
    """

    def __init__(self, message: str = "An error occurred during scraping."):
        self.message = message
        super().__init__(self.message)
