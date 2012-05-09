import unittest


TEST_CASE_LIST = (
    'test.webserver_test',
    #'test.queues_test',
    'test.tempfile_test',
    'test.multifetcher_test'
)


def main():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(TEST_CASE_LIST)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
