import pytest
import json

from tests.common.fixtures import test_server
from chimera.common import ErrorCode


@pytest.mark.asyncio
async def test_incorrect_json(test_server):
    client = test_server.create_client()

    faulty_msg = '{"foo": }'
    await test_server.fake_send_message(client, faulty_msg)

    assert client.num_responses == 1
    msg = next(client.responses)

    assert msg["type"] == "response"
    assert msg["error"]["code"] == ErrorCode.PARSE_ERROR.value
    assert msg["error"]["message"] == str(ErrorCode.PARSE_ERROR)
    assert msg["id"] == None


@pytest.mark.asyncio
async def test_missing_message_type(test_server):
    client = test_server.create_client()

    faulty_msg = {"foo": "bar"}
    await test_server.fake_send_message(client, json.dumps(faulty_msg))

    assert client.num_responses == 1
    msg = next(client.responses)

    assert msg["type"] == "response"
    assert msg["error"]["code"] == ErrorCode.INCORRECT_REQUEST.value
    assert msg["error"]["message"] == str(ErrorCode.INCORRECT_REQUEST)
    assert msg["id"] == None


@pytest.mark.asyncio
async def test_incorrect_message_type(test_server):
    client = test_server.create_client()

    faulty_msg = {"type": "response"}
    await test_server.fake_send_message(client, json.dumps(faulty_msg))

    assert client.num_responses == 1
    msg = next(client.responses)

    assert msg["type"] == "response"
    assert msg["error"]["code"] == ErrorCode.INCORRECT_REQUEST.value
    assert msg["error"]["message"] == str(ErrorCode.INCORRECT_REQUEST)
    assert msg["id"] == None


@pytest.mark.asyncio
async def test_missing_operation(test_server):
    client = test_server.create_client()

    faulty_msg = {"type": "request"}
    await test_server.fake_send_message(client, json.dumps(faulty_msg))

    assert client.num_responses == 1
    msg = next(client.responses)

    assert msg["type"] == "response"
    assert msg["error"]["code"] == ErrorCode.INCORRECT_REQUEST.value
    assert msg["error"]["message"] == str(ErrorCode.INCORRECT_REQUEST)
    assert msg["id"] == None


@pytest.mark.asyncio
async def test_incorrect_operation(test_server):
    client = test_server.create_client()

    faulty_msg = {"type": "request", "id": "42", "operation": "foobar"}
    await test_server.fake_send_message(client, json.dumps(faulty_msg))

    assert client.num_responses == 1
    msg = next(client.responses)

    assert msg["type"] == "response"
    assert msg["id"] == "42"
    assert msg["error"]["code"] == ErrorCode.NO_SUCH_OPERATION.value
    assert msg["error"]["message"] == str(ErrorCode.NO_SUCH_OPERATION)
