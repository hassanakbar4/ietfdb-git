
from ietf.utils.test_utils import SimpleUrlTestCase

class RedirectsUrlTestCase(SimpleUrlTestCase):
    def testUrls(self):
        self.doTestUrls(__file__)
