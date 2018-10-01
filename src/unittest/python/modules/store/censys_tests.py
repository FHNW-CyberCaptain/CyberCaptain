import unittest, os, shutil, requests, responses, censys
from unittest.mock import patch, MagicMock                                       

from cybercaptain.store.censys import store_censys
from cybercaptain.utils.exceptions import ValidationError

TEST_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../assets/output')
TEST_INPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')

TESTDATA_UNCOMPRESSED_FILE = os.path.join(TEST_INPUT_FOLDER, 'uncompressed_file.json')
TESTDATA_COMPRESSED_FILE = os.path.join(TEST_INPUT_FOLDER, 'uncompressed_file.json.lz4')
TESTDATA_DOWNLOADED_FILE = os.path.join(TEST_INPUT_FOLDER, "test_censys_download_method.txt")
TESTDATA_DOWNLOADED_COMPRESSED_FILE = os.path.join(TEST_INPUT_FOLDER, "test_censys_run_method_compressed.txt.lz4")
TESTDATA_DOWNLOADED_UNCOMPRESSED_FILE = os.path.join(TEST_INPUT_FOLDER, "test_censys_run_method_uncompressed.txt")

TESTDATA_OUTPUT_UNCOMPRESSED = os.path.join(TEST_OUTPUT_FOLDER, "test_censys_decompress_lz4_method.json")
TESTDATA_OUTPUT_DOWNLOAD = os.path.join(TEST_OUTPUT_FOLDER, "test_censys_download_method.txt")
TESTDATA_OUTPUT_DOWNLOADED_COMPRESSED_FILE = os.path.join(TEST_OUTPUT_FOLDER, "test_censys_run_method_compressed.txt.lz4")
TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE = os.path.join(TEST_OUTPUT_FOLDER, "test_censys_run_method_uncompressed.txt")

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot':os.path.join(os.path.dirname(__file__), '../assets/output'), 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}


# Mocked censys data api
class _mock_censys_data_api():
    def __init__(self, api_id, api_secret):
        self.api_id = api_id
        self.api_secret = api_secret
        if "NEEDS_TO_FAIL" == api_secret or "NEEDS_TO_FAIL" == api_id: raise Exception
    
    def view_series(self, series_id):
        if "NEEDS_TO_FAIL" == series_id: return {"error_code":404, "error":"page not found"}

        return {"protocol": "https", "description": "This dataset is composed of the DNS lookups for each domain on the Alexa Top\r\nMillion and a TLS handshake with responsive hosts that only offers\r\nexport-grade RSA ciphers.", "destination": "alexa_top1mil", "results": {"historical": [{"timestamp": "20180414T141007", "id": "20180414T1410", "details_url": "https://www.censys.io/api/v1/data/443-https-rsa_export-alexa_top1mil/20180414T1410"}], "latest": {"timestamp": "20180414T141007", "id": "20180414T1410", "details_url": "https://www.censys.io/api/v1/data/443-https-rsa_export-alexa_top1mil/20180414T1410"}}, "port": 443, "subprotocol": "rsa_export", "id": "443-https-rsa_export-alexa_top1mil", "name": "443-https-rsa_export-alexa_top1mil"}

    def view_result(self, series_id, dataset_id):
        if "NEEDS_TO_FAIL" == dataset_id or "NEEDS_TO_FAIL" == series_id or "NEEDS_TO_FAIL_RESULT" == series_id: return {"error_code":404, "error":"page not found"}


        return {"files": {"ztee-zgrab-updates": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztee-zgrab-updates.csv.lz4", "sha256_fingerprint": "0899df4fa52368936fa3ba3b6101a0ab17de43eba79014ed02d2be58ffc28a57", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztee-zgrab-updates.csv.lz4", "file_type": "csv", "schema": None, "compression_type": None, "size": 0}, "ztee-alexa-updates": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztee-alexa-updates.csv.lz4", "sha256_fingerprint": "3d7901589e92bd0476e4a40d14b5cbfdc862745a92af8658a1c1709eb57dfb14", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztee-alexa-updates.csv.lz4", "file_type": "csv", "schema": None, "compression_type": None, "size": 0}, "zgrab-results": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4", "sha256_fingerprint": "8328400a3b86918d11661d7c80b5f2fb01d71db62414f3b34e5169d7951f4769", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4", "file_type": "json", "schema": None, "compression_type": None, "size": 197}, "zgrab-metadata": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-metadata.json.lz4", "sha256_fingerprint": "6f566f06d22b6dd7132544e1900f3b8be2055658d888228d970c9f04ccc2dac9", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-metadata.json.lz4", "file_type": "json", "schema": None, "compression_type": None, "size": 0}, "alexa-results": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-alexa-results.csv.lz4", "sha256_fingerprint": "498f1c7a398fb311ebdc7eaf3de76393cb8a9fd0c2a4968e76f15c6232330ff7", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-alexa-results.csv.lz4", "file_type": "csv", "schema": None, "compression_type": None, "size": 22}, "zgrab-log": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-log.log.lz4", "sha256_fingerprint": "3aac03410c36045a3609c7017d58ad21367734a203e25e5e484d20459e33d8c4", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-log.log.lz4", "file_type": "log", "schema": None, "compression_type": None, "size": 97}, "ztag-metadata": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztag-metadata.json.lz4", "sha256_fingerprint": "2c150a227e4f5d1ffbbd7d052809de1efbe5294100e9823f322bf429c887caab", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztag-metadata.json.lz4", "file_type": "json", "schema": None, "compression_type": None, "size": 0}, "ztag-log": {"compressed_size": None, "compressed_sha256_fingerprint": None, "compressed_download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztag-log.log.lz4", "sha256_fingerprint": "89ac42fcad10ad9f0a076aa3517c335e896cd1084ef8adc8216d5e2bbca37873", "download_path": "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-ztag-log.log.lz4", "file_type": "log", "schema": None, "compression_type": None, "size": 0}}, "task_id": None, "series": {"id": "443-https-rsa_export-alexa_top1mil", "name": "443-https-rsa_export-alexa_top1mil"}, "timestamp": "20180414T141007", "id": "20180414T1410", "metadata": None}

# Censys Tests
class StoreCensysTest(unittest.TestCase):
    """
    Test the store processing censys module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()

        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":1000,
            "chunkSizeDecomp":1000,
            "target":"."
        })

        self.censys_module = store_censys(**arguments)


    def setUp(self):
        if not os.path.exists(TEST_OUTPUT_FOLDER):
            os.makedirs(TEST_OUTPUT_FOLDER)

    def tearDown(self):
        shutil.rmtree(TEST_OUTPUT_FOLDER)

    def test_censys_decompress_lz4_method(self):
        # Tests the lz4 decompress method
        self.censys_module.decompress_lz4(TESTDATA_COMPRESSED_FILE, TESTDATA_OUTPUT_UNCOMPRESSED, 1)

        with open(TESTDATA_UNCOMPRESSED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_UNCOMPRESSED,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

    @responses.activate
    def test_censys_download_file_method(self):
        # MOCK STREAM DOWNLOAD
        with open(TESTDATA_DOWNLOADED_FILE, 'rb') as dl_file:
            responses.add(
                responses.GET, 'http://unittest.test',
                body=dl_file.read(), status=200, headers={"content-length": str(os.path.getsize(TESTDATA_DOWNLOADED_FILE))},
                stream=True
            )
        self.censys_module.download_file('http://unittest.test', TESTDATA_OUTPUT_DOWNLOAD, 400)

        with open(TESTDATA_DOWNLOADED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_DOWNLOAD,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

    @responses.activate
    def test_censys_run_via_api(self):
        # Mock: Setup custom censys data class
        old_censys_class = censys.data.CensysData
        censys.data.CensysData = _mock_censys_data_api

        # Via API with getByLatest False
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":1000,
            "chunkSizeDecomp":1000,
            "target":TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE
        })

        sc1 = store_censys(**arguments)
        # Download file mocked
        dataset_wanted_file_url = "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4"
        with open(TESTDATA_DOWNLOADED_COMPRESSED_FILE, 'rb') as dl_file:
            responses.add(
                responses.GET, dataset_wanted_file_url,
                body=dl_file.read(), status=200, headers={"content-length": str(os.path.getsize(TESTDATA_DOWNLOADED_COMPRESSED_FILE))},
                stream=True
            )
        sc1.run()

        with open(TESTDATA_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Via API with getByLatest True
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByLatest":True,
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":1000,
            "chunkSizeDecomp":1000,
            "target":TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE
        })

        sc2 = store_censys(**arguments) 
        # Download file mocked
        dataset_wanted_file_url = "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4"
        with open(TESTDATA_DOWNLOADED_COMPRESSED_FILE, 'rb') as dl_file:
            responses.add(
                responses.GET, dataset_wanted_file_url,
                body=dl_file.read(), status=200, headers={"content-length": str(os.path.getsize(TESTDATA_DOWNLOADED_COMPRESSED_FILE))},
                stream=True
            )
        sc2.run()

        with open(TESTDATA_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Via API with getByLatest True
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByLatest":True,
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":1000,
            "chunkSizeDecomp":1000,
            "target":TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE
        })

        sc2 = store_censys(**arguments) 
        # Download file mocked
        dataset_wanted_file_url = "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4"
        with open(TESTDATA_DOWNLOADED_COMPRESSED_FILE, 'rb') as dl_file:
            responses.add(
                responses.GET, dataset_wanted_file_url,
                body=dl_file.read(), status=200, headers={"content-length": str(os.path.getsize(TESTDATA_DOWNLOADED_COMPRESSED_FILE))},
                stream=True
            )
        sc2.run()

        with open(TESTDATA_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Via API with get_by_date True
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDate":"14042018",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":1000,
            "chunkSizeDecomp":1000,
            "target":TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE
        })

        sc3 = store_censys(**arguments) 
        # Download file mocked
        dataset_wanted_file_url = "https://scans.io/zsearch/ir028m5ucemb5ahq-443-https-rsa_export-alexa_top1mil-20180414T140001-zgrab-results.json.lz4"
        with open(TESTDATA_DOWNLOADED_COMPRESSED_FILE, 'rb') as dl_file:
            responses.add(
                responses.GET, dataset_wanted_file_url,
                body=dl_file.read(), status=200, headers={"content-length": str(os.path.getsize(TESTDATA_DOWNLOADED_COMPRESSED_FILE))},
                stream=True
            )
        sc3.run()

        with open(TESTDATA_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_DOWNLOADED_UNCOMPRESSED_FILE,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Reset Mock
        censys.data.CensysData = old_censys_class

    def test_censys_run_via_api_error_code(self):
        # Mock: Setup custom censys data class
        old_censys_class = censys.data.CensysData
        censys.data.CensysData = _mock_censys_data_api

        # Run method with certain invalid series ids and datasets ids
        # API will return an error code

        # Set the datasetid to something not existing, api should return error (mocked censys api)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs1 = store_censys(**arguments)
        cs1.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs1.get_by_datasetId = "NEEDS_TO_FAIL"

        self.assertEquals(cs1.run(), False)

        # Set the series_id to something not existing, api should return error (mocked censys api)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"TEST",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs2 = store_censys(**arguments)
        cs2.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs2.series_id = "NEEDS_TO_FAIL"

        self.assertEquals(cs2.run(), False)

        # Remove all valid methods just in case validation would be passed without any valid method
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"TEST",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs3 = store_censys(**arguments)
        cs3.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs3.get_by_datasetId = None

        self.assertEquals(cs3.run(), False)

        # Mock wrong api_id - api would throw an exception
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":"NEEDS_TO_FAIL",
            "apiSecret":".",
            "seriesId":"TEST",
            "getByDatasetId":"20180410T1408",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs4 = store_censys(**arguments)
        cs4.download_file = None # Better be safe than sorry, do not download anything in those tests

        self.assertEquals(cs4.run(), False)

        # GetByDate - Series Not found
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDate":"14042018",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs5 = store_censys(**arguments)
        cs5.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs5.series_id = "NEEDS_TO_FAIL"
        self.assertEquals(cs5.run(), False)

        # GetByDate - Dataset Not found Via Date
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDate":"14042999",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs6 = store_censys(**arguments)
        cs6.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs6.series_id = "NEEDS_TO_FAIL_RESULT"
        self.assertEquals(cs6.run(), False)

        # GetByDate - Dataset Not found Via Id From API (Should acutally not happen)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByDate":"14042018",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs6_1 = store_censys(**arguments)
        cs6_1.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs6_1.series_id = "NEEDS_TO_FAIL_RESULT"
        self.assertEquals(cs6_1.run(), False)

        # GetByLatest - Series Not found
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByLatest":"yes",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs7 = store_censys(**arguments)
        cs7.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs7.series_id = "NEEDS_TO_FAIL"
        self.assertEquals(cs7.run(), False)

        # GetByLatest - Dataset Not found (Shouldnt really happen)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByLatest":"yes",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "chunkSizeDownload":400,
            "chunkSizeDecomp":400,
            "target":"."
        })

        cs8 = store_censys(**arguments)
        cs8.download_file = None # Better be safe than sorry, do not download anything in those tests
        cs8.series_id = "NEEDS_TO_FAIL_RESULT"
        self.assertEquals(cs8.run(), False)

        # Check To Use Default Chunk Sizes
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":"443-https-rsa_export-alexa_top1mil",
            "getByLatest":"yes",
            "getMissingDatasets":False,
            "fileId":"zgrab-results",
            "target":"."
        })

        cs9 = store_censys(**arguments)

        # Reset Mock
        censys.data.CensysData = old_censys_class

    def test_censys_validate_method(self):

        # ------------------
        # Via API
        # ------------------

        # Via API ALL parameters set 
        arguments9 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "getMissingDatasets":False,
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        sc9 = store_censys(**arguments9)

        # apiSecret not set
        arguments10 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "seriesId":".",
            "getByLatest":True,
            "getMissingDatasets":".",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc10 = store_censys(**arguments10)

        # apiId not set
        arguments11 = append_needed_args({
            "viaApi":True,
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "getMissingDatasets":".",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc11 = store_censys(**arguments11)

        # seriesId not set
        arguments11_2 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "getByLatest":True,
            "getMissingDatasets":".",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc11_2 = store_censys(**arguments11_2)

        # seriesId not set
        arguments11_3 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "getByLatest":True,
            "getMissingDatasets":".",
            "seriesId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc11_3 = store_censys(**arguments11_3)

        # getByLatest not set
        arguments12 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getMissingDatasets":".",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc12 = store_censys(**arguments12)

        # getByLatest true
        arguments13 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        sc13 = store_censys(**arguments13)

        # getByDate true and getByDate wrong format
        arguments14 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDate":"04042018MORE",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc14 = store_censys(**arguments14)

        # getByDate true and getByDate not cybercaptain date format
        arguments15 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDate":"20180404",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc15 = store_censys(**arguments15)

        # getByDatasetId true and getByDatasetId wrong format
        arguments16 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDatasetId":"20180410T1408TEST",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc16 = store_censys(**arguments16)

        # chunkSizeDownload not an integer
        arguments17 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDatasetId":"20180410T1408",
            "fileId":".",
            "chunkSizeDownload":"TEST",
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc17 = store_censys(**arguments17)

        # chunkSizeDecomp not an integer
        arguments18 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByDatasetId":"20180410T1408",
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":"TEST",
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc18 = store_censys(**arguments18)

        # Via API getMissingDatasets and getAllMissingDatasets both set
        arguments9 = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "getMissingDatasets":True,
            "getAllMissingDatasets":True,
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            sc = store_censys(**arguments9)

    def test_censys_inject_additional_tasks_method(self):
        # Mock Censys
        old_censys_class = censys.data.CensysData
        censys.data.CensysData = _mock_censys_data_api

        # Test injecting addiitonal tasks found via API (get datasets between last run and newest)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "getMissingDatasets":True,
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        ss = store_censys(**arguments)
        additional_tasks = ss.inject_additional_tasks()
        self.assertEquals(len(additional_tasks), 0)

        # Test injecting addiitonal tasks found via API (get all datasets from start)
        arguments = append_needed_args({
            "viaApi":True,
            "apiId":".",
            "apiSecret":".",
            "seriesId":".",
            "getByLatest":True,
            "getAllMissingDatasets":True,
            "fileId":".",
            "chunkSizeDownload":100,
            "chunkSizeDecomp":100,
            "target":"."
        })

        ss = store_censys(**arguments)
        additional_tasks = ss.inject_additional_tasks()
        self.assertEquals(len(additional_tasks), 1)

        # Reset Mock
        censys.data.CensysData = old_censys_class
