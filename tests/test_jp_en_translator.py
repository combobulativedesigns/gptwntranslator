import random
import unittest
from gptwntranslator.translators.jp_en_translator import _estimate_chunks, _get_translation_model, _greedy_find_max_optimal_configuration, _japanese_token_limit_worst_case, _split_text_into_chunks, initialize, JpToEnTranslatorException

class TestSplitTextIntoChunksUninitialized(unittest.TestCase):

    def test_split_text_into_chunks_uninitialized(self):
        with self.assertRaises(JpToEnTranslatorException):
            _split_text_into_chunks("Some text", 10, [2, 1, 3])

class TestEstimateChunksUninitialized(unittest.TestCase):

    def test_estimate_chunks_uninitialized(self):
        with self.assertRaises(JpToEnTranslatorException):
            _estimate_chunks(5, 10, [2, 1, 3, 2, 1])

class TestJapaneseTokenLimitWorstCaseUninitialized(unittest.TestCase):

    def test_japanese_token_limit_worst_case_uninitialized(self):
        with self.assertRaises(JpToEnTranslatorException):
            _japanese_token_limit_worst_case(100)

class TestGreedyFindMaxOptimalConfigurationUninitialized(unittest.TestCase):

    def test_greedy_find_max_optimal_configuration_uninitialized(self):
        with self.assertRaises(JpToEnTranslatorException):
            line_token_counts = [20, 15, 30, 40, 10]
            _greedy_find_max_optimal_configuration(line_token_counts)

class TestGetTranslationModelUninitialized(unittest.TestCase):

    def setUp(self):
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }

    def test_get_translation_model_uninitialized(self):
        for model in self.available_models.keys():
            with self.assertRaises(JpToEnTranslatorException):
                _get_translation_model(model)

class TestInitialize(unittest.TestCase):

    def setUp(self):
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-3.5']
        self.translation_models = ['gpt-4']
        self.summary_models = ['gpt-4-32k']

    def test_initialize_valid_input(self):
        try:
            initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_initialize_invalid_available_models_type(self):
        with self.assertRaises(TypeError):
            initialize("invalid", self.terms_models, self.translation_models, self.summary_models)

    def test_initialize_invalid_available_models_value(self):
        invalid_models = {'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002}}
        with self.assertRaises(ValueError):
            initialize(invalid_models, self.terms_models, self.translation_models, self.summary_models)

    def test_initialize_invalid_terms_models_type(self):
        with self.assertRaises(TypeError):
            initialize(self.available_models, "invalid", self.translation_models, self.summary_models)

    def test_initialize_invalid_terms_models_value(self):
        with self.assertRaises(ValueError):
            initialize(self.available_models, ["invalid"], self.translation_models, self.summary_models)

    def test_initialize_invalid_translation_models_type(self):
        with self.assertRaises(TypeError):
            initialize(self.available_models, self.terms_models, "invalid", self.summary_models)

    def test_initialize_invalid_translation_models_value(self):
        with self.assertRaises(ValueError):
            initialize(self.available_models, self.terms_models, ["invalid"], self.summary_models)

    def test_initialize_invalid_summary_models_type(self):
        with self.assertRaises(TypeError):
            initialize(self.available_models, self.terms_models, self.translation_models, "invalid")

    def test_initialize_invalid_summary_models_value(self):
        with self.assertRaises(ValueError):
            initialize(self.available_models, self.terms_models, self.translation_models, ["invalid"])

class TestSplitTextIntoChunksInitialized(unittest.TestCase):

    def setUp(self):
        self.text = "This is a sample text.\nIt has multiple lines.\nEach line has a varying number of tokens."
        self.division_size = 15
        self.line_token_counts = [6, 5, 9]
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-3.5']
        self.translation_models = ['gpt-4']
        self.summary_models = ['gpt-4-32k']
        initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)

    def test_split_text_into_chunks_valid_input(self):
        try:
            _split_text_into_chunks(self.text, self.division_size, self.line_token_counts)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_split_text_into_chunks_invalid_text_type(self):
        with self.assertRaises(TypeError):
            _split_text_into_chunks(123, self.division_size, self.line_token_counts)

    def test_split_text_into_chunks_invalid_division_size_type(self):
        with self.assertRaises(TypeError):
            _split_text_into_chunks(self.text, "invalid", self.line_token_counts)

    def test_split_text_into_chunks_invalid_division_size_value(self):
        with self.assertRaises(ValueError):
            _split_text_into_chunks(self.text, 0, self.line_token_counts)

    def test_split_text_into_chunks_invalid_line_token_counts_type(self):
        with self.assertRaises(TypeError):
            _split_text_into_chunks(self.text, self.division_size, "invalid")

    def test_split_text_into_chunks_invalid_line_token_counts_value_type(self):
        with self.assertRaises(TypeError):
            _split_text_into_chunks(self.text, self.division_size, [1, "invalid", 3])

    def test_split_text_into_chunks_invalid_line_token_counts_value_negative(self):
        with self.assertRaises(ValueError):
            _split_text_into_chunks(self.text, self.division_size, [1, -1, 3])

class TestEstimateChunks(unittest.TestCase):

    def setUp(self):
        self.total_lines = 5
        self.division_size = 10
        self.line_token_counts = [2, 1, 3, 2, 1]
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-3.5']
        self.translation_models = ['gpt-4']
        self.summary_models = ['gpt-4-32k']
        initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)

    def test_estimate_chunks_valid_input(self):
        try:
            _estimate_chunks(self.total_lines, self.division_size, self.line_token_counts)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    # Add more test cases for different types of input validation
    def test_estimate_chunks_invalid_total_lines(self):
        with self.assertRaises(ValueError):
            _estimate_chunks(0, self.division_size, self.line_token_counts)

    def test_estimate_chunks_invalid_division_size(self):
        with self.assertRaises(ValueError):
            _estimate_chunks(self.total_lines, 0, self.line_token_counts)

    def test_estimate_chunks_invalid_line_token_counts(self):
        with self.assertRaises(ValueError):
            _estimate_chunks(self.total_lines, self.division_size, [0, -1, 3, 2, 1])

    def test_estimate_chunks_mismatched_line_token_counts(self):
        with self.assertRaises(ValueError):
            _estimate_chunks(self.total_lines, self.division_size, [2, 1, 3, 2])

class TestJapaneseTokenLimitWorstCase(unittest.TestCase):

    def setUp(self):
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-3.5']
        self.translation_models = ['gpt-4']
        self.summary_models = ['gpt-4-32k']
        initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)

    def test_japanese_token_limit_worst_case_valid_input_1(self):
        try:
            _japanese_token_limit_worst_case(100)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_japanese_token_limit_worst_case_valid_input_2(self):
        try:
            _japanese_token_limit_worst_case(100, worst_case_ratio=0.5)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_japanese_token_limit_worst_case_valid_input_3(self):
        try:
            _japanese_token_limit_worst_case(100, safety_factor=2)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_japanese_token_limit_worst_case_valid_input_4(self):
        try:
            _japanese_token_limit_worst_case(100, worst_case_ratio=0.5)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_japanese_token_limit_worst_case_valid_input_5(self):
        try:
            _japanese_token_limit_worst_case(100, worst_case_ratio=1)
        except Exception as e:
            self.fail(f"Valid input should not raise an exception: {e}")

    def test_japanese_token_limit_worst_case_invalid_N(self):
        for valuetype in [None, "qwe", 0.5]:
            with self.assertRaises(TypeError):
                _japanese_token_limit_worst_case(valuetype)

    def test_japanese_token_limit_worst_case_invalid_worst_case_ratio(self):
        for valuetype in [None, "qwe"]:
            with self.assertRaises(TypeError):
                _japanese_token_limit_worst_case(100, worst_case_ratio=valuetype)

    def test_japanese_token_limit_worst_case_invalid_safety_factor(self):
        for valuetype in [None, "asd"]:
            with self.assertRaises(TypeError):
                _japanese_token_limit_worst_case(100, safety_factor=valuetype)

    def test_japanese_token_limit_worst_case_calculation_integers_1(self):
        token_limit = _japanese_token_limit_worst_case(100, worst_case_ratio=2, safety_factor=1)
        expected_limit = 33
        self.assertEqual(token_limit, expected_limit, "Incorrect token limit calculation with integers")

    def test_japanese_token_limit_worst_case_calculation_integers_2(self):
        token_limit = _japanese_token_limit_worst_case(1000, worst_case_ratio=1, safety_factor=0.5)
        expected_limit = 250
        self.assertEqual(token_limit, expected_limit, "Incorrect token limit calculation with integers")

    def test_japanese_token_limit_worst_case_calculation_integers_3(self):
        token_limit = _japanese_token_limit_worst_case(2000, worst_case_ratio=1.5, safety_factor=1)
        expected_limit = 800
        self.assertEqual(token_limit, expected_limit, "Incorrect token limit calculation with integers")

    def test_japanese_token_limit_worst_case_calculation_integers_4(self):
        token_limit = _japanese_token_limit_worst_case(10000, worst_case_ratio=1, safety_factor=1)
        expected_limit = 5000
        self.assertEqual(token_limit, expected_limit, "Incorrect token limit calculation with integers")

class TestGreedyFindMaxOptimalConfiguration(unittest.TestCase):

    def setUp(self):
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-4']
        self.translation_models = ['gpt-3.5']
        self.summary_models = ['gpt-3.5']
        initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)

    def test_greedy_find_max_optimal_configuration_invalid_input(self):
        with self.assertRaises(TypeError, msg="line_token_counts must be a list."):
            _greedy_find_max_optimal_configuration("invalid input")

        with self.assertRaises(TypeError, msg="line_token_counts must be a list of integers."):
            _greedy_find_max_optimal_configuration([1, 2, "invalid"])

        with self.assertRaises(ValueError, msg="line_token_counts must be a list of positive integers."):
            _greedy_find_max_optimal_configuration([1, 2, -3])

    def test_greedy_find_max_optimal_configuration_basic(self):
        line_token_counts = [20, 15, 30, 40, 10]
        optimal_config = _greedy_find_max_optimal_configuration(line_token_counts)
        self.assertIsNotNone(optimal_config, "Optimal configuration not found")

    def test_greedy_find_max_optimal_configuration_large(self):
        line_token_counts = [random.randint(1, 50) for _ in range(1000)]
        optimal_config = _greedy_find_max_optimal_configuration(line_token_counts)
        self.assertIsNotNone(optimal_config, "Optimal configuration not found")

    def test_greedy_find_max_optimal_configuration_small(self):
        line_token_counts = [random.randint(1, 50) for _ in range(10)]
        optimal_config = _greedy_find_max_optimal_configuration(line_token_counts)
        self.assertIsNotNone(optimal_config, "Optimal configuration not found")

class TestGetTranslationModel(unittest.TestCase):

    def setUp(self):
        # Initialize the translator before testing
        self.available_models = {
            'gpt-3.5': {'name': 'gpt-3.5-turbo', 'cost_per_1k_tokens': 0.002, 'max_tokens': 4096},
            'gpt-4': {'name': 'gpt-4', 'cost_per_1k_tokens': 0.03, 'max_tokens': 8192},
            'gpt-4-32k': {'name': 'gpt-4-32k', 'cost_per_1k_tokens': 0.06, 'max_tokens': 32768}
        }
        self.terms_models = ['gpt-4']
        self.translation_models = ['gpt-3.5']
        self.summary_models = ['gpt-3.5']
        initialize(self.available_models, self.terms_models, self.translation_models, self.summary_models)

    def test_get_translation_model_invalid_input(self):
        with self.assertRaises(TypeError, msg="Model must be a string"):
            _get_translation_model(123)

        with self.assertRaises(ValueError, msg="Model must be a valid model"):
            _get_translation_model("invalid_model")

    def test_get_translation_model_basic(self):
        for model in self.available_models.keys():
            translation_model = _get_translation_model(model)
            self.assertIsNotNone(translation_model, f"Translation model {model} not found")
            self.assertIsInstance(translation_model, dict, f"Translation model {model} should be a dictionary")




if __name__ == "__main__":
    unittest.main()


