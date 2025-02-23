from unittest.mock import Mock, patch  # , AsyncMock

# import pytest
from semantic_router.route import Route, is_valid


# Is valid test:
def test_is_valid_with_valid_json():
    valid_json = '{"name": "test_route", "utterances": ["hello", "hi"]}'
    assert is_valid(valid_json) is True


def test_is_valid_with_missing_keys():
    invalid_json = '{"name": "test_route"}'  # Missing 'utterances'
    with patch("semantic_router.route.logger") as mock_logger:
        assert is_valid(invalid_json) is False
        mock_logger.warning.assert_called_once()


def test_is_valid_with_valid_json_list():
    valid_json_list = (
        '[{"name": "test_route1", "utterances": ["hello"]}, '
        '{"name": "test_route2", "utterances": ["hi"]}]'
    )
    assert is_valid(valid_json_list) is True


def test_is_valid_with_invalid_json_list():
    invalid_json_list = (
        '[{"name": "test_route1"}, {"name": "test_route2", "utterances": ["hi"]}]'
    )
    with patch("semantic_router.route.logger") as mock_logger:
        assert is_valid(invalid_json_list) is False
        mock_logger.warning.assert_called_once()


def test_is_valid_with_invalid_json():
    invalid_json = '{"name": "test_route", "utterances": ["hello", "hi" invalid json}'
    with patch("semantic_router.route.logger") as mock_logger:
        assert is_valid(invalid_json) is False
        mock_logger.error.assert_called_once()


class TestRoute:
    @patch("semantic_router.route.llm", new_callable=Mock)
    def test_generate_dynamic_route(self, mock_llm):
        print(f"mock_llm: {mock_llm}")
        mock_llm.return_value = """
        <config>
        {
            "name": "test_function",
            "utterances": [
                "example_utterance_1",
                "example_utterance_2",
                "example_utterance_3",
                "example_utterance_4",
                "example_utterance_5"]
        }
        </config>
        """
        function_schema = {"name": "test_function", "type": "function"}
        route = Route._generate_dynamic_route(function_schema)
        assert route.name == "test_function"
        assert route.utterances == [
            "example_utterance_1",
            "example_utterance_2",
            "example_utterance_3",
            "example_utterance_4",
            "example_utterance_5",
        ]

    # TODO add async version
    # @pytest.mark.asyncio
    # @patch("semantic_router.route.allm", new_callable=Mock)
    # async def test_generate_dynamic_route_async(self, mock_llm):
    #     print(f"mock_llm: {mock_llm}")
    #     mock_llm.return_value = """
    #     <config>
    #     {
    #         "name": "test_function",
    #         "utterances": [
    #             "example_utterance_1",
    #             "example_utterance_2",
    #             "example_utterance_3",
    #             "example_utterance_4",
    #             "example_utterance_5"]
    #     }
    #     </config>
    #     """
    #     function_schema = {"name": "test_function", "type": "function"}
    #     route = await Route._generate_dynamic_route(function_schema)
    #     assert route.name == "test_function"
    #     assert route.utterances == [
    #         "example_utterance_1",
    #         "example_utterance_2",
    #         "example_utterance_3",
    #         "example_utterance_4",
    #         "example_utterance_5",
    #     ]

    def test_to_dict(self):
        route = Route(name="test", utterances=["utterance"])
        expected_dict = {
            "name": "test",
            "utterances": ["utterance"],
            "description": None,
            "function_schema": None,
        }
        assert route.to_dict() == expected_dict

    def test_from_dict(self):
        route_dict = {"name": "test", "utterances": ["utterance"]}
        route = Route.from_dict(route_dict)
        assert route.name == "test"
        assert route.utterances == ["utterance"]

    @patch("semantic_router.route.llm", new_callable=Mock)
    def test_from_dynamic_route(self, mock_llm):
        # Mock the llm function
        mock_llm.return_value = """
        <config>
        {
            "name": "test_function",
            "utterances": [
                "example_utterance_1",
                "example_utterance_2",
                "example_utterance_3",
                "example_utterance_4",
                "example_utterance_5"]
        }
        </config>
        """

        def test_function(input: str):
            """Test function docstring"""
            pass

        dynamic_route = Route.from_dynamic_route(test_function)

        assert dynamic_route.name == "test_function"
        assert dynamic_route.utterances == [
            "example_utterance_1",
            "example_utterance_2",
            "example_utterance_3",
            "example_utterance_4",
            "example_utterance_5",
        ]

    # TODO add async functions
    # @pytest.mark.asyncio
    # @patch("semantic_router.route.allm", new_callable=AsyncMock)
    # async def test_from_dynamic_route_async(self, mock_llm):
    #     # Mock the llm function
    #     mock_llm.return_value = """
    #     <config>
    #     {
    #         "name": "test_function",
    #         "utterances": [
    #             "example_utterance_1",
    #             "example_utterance_2",
    #             "example_utterance_3",
    #             "example_utterance_4",
    #             "example_utterance_5"]
    #     }
    #     </config>
    #     """

    #     def test_function(input: str):
    #         """Test function docstring"""
    #         pass

    #     dynamic_route = await Route.from_dynamic_route(test_function)

    #     assert dynamic_route.name == "test_function"
    #     assert dynamic_route.utterances == [
    #         "example_utterance_1",
    #         "example_utterance_2",
    #         "example_utterance_3",
    #         "example_utterance_4",
    #         "example_utterance_5",
    #     ]

    def test_parse_route_config(self):
        config = """
        <config>
        {
            "name": "test_function",
            "utterances": [
                "example_utterance_1",
                "example_utterance_2",
                "example_utterance_3",
                "example_utterance_4",
                "example_utterance_5"]
        }
        </config>
        """
        expected_config = """
        {
            "name": "test_function",
            "utterances": [
                "example_utterance_1",
                "example_utterance_2",
                "example_utterance_3",
                "example_utterance_4",
                "example_utterance_5"]
        }
        """
        assert Route._parse_route_config(config).strip() == expected_config.strip()
