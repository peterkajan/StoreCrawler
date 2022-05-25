from asynctest import mock


def get_generator_mock(return_value):
    generator_mock = mock.MagicMock()
    generator_mock.__aiter__.return_value = return_value
    return generator_mock
