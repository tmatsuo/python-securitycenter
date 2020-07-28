# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.securitycenter_v1beta1.services.security_center import (
    SecurityCenterAsyncClient,
)
from google.cloud.securitycenter_v1beta1.services.security_center import (
    SecurityCenterClient,
)
from google.cloud.securitycenter_v1beta1.services.security_center import pagers
from google.cloud.securitycenter_v1beta1.services.security_center import transports
from google.cloud.securitycenter_v1beta1.types import finding
from google.cloud.securitycenter_v1beta1.types import finding as gcs_finding
from google.cloud.securitycenter_v1beta1.types import organization_settings
from google.cloud.securitycenter_v1beta1.types import (
    organization_settings as gcs_organization_settings,
)
from google.cloud.securitycenter_v1beta1.types import security_marks
from google.cloud.securitycenter_v1beta1.types import (
    security_marks as gcs_security_marks,
)
from google.cloud.securitycenter_v1beta1.types import securitycenter_service
from google.cloud.securitycenter_v1beta1.types import source
from google.cloud.securitycenter_v1beta1.types import source as gcs_source
from google.iam.v1 import iam_policy_pb2 as iam_policy  # type: ignore
from google.iam.v1 import options_pb2 as options  # type: ignore
from google.iam.v1 import policy_pb2 as policy  # type: ignore
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.type import expr_pb2 as expr  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert SecurityCenterClient._get_default_mtls_endpoint(None) is None
    assert (
        SecurityCenterClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        SecurityCenterClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        SecurityCenterClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        SecurityCenterClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        SecurityCenterClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [SecurityCenterClient, SecurityCenterAsyncClient]
)
def test_security_center_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "securitycenter.googleapis.com:443"


def test_security_center_client_get_transport_class():
    transport = SecurityCenterClient.get_transport_class()
    assert transport == transports.SecurityCenterGrpcTransport

    transport = SecurityCenterClient.get_transport_class("grpc")
    assert transport == transports.SecurityCenterGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (SecurityCenterClient, transports.SecurityCenterGrpcTransport, "grpc"),
        (
            SecurityCenterAsyncClient,
            transports.SecurityCenterGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_security_center_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(SecurityCenterClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(SecurityCenterClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=client_cert_source_callback,
                quota_project_id=None,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_MTLS_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (SecurityCenterClient, transports.SecurityCenterGrpcTransport, "grpc"),
        (
            SecurityCenterAsyncClient,
            transports.SecurityCenterGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_security_center_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (SecurityCenterClient, transports.SecurityCenterGrpcTransport, "grpc"),
        (
            SecurityCenterAsyncClient,
            transports.SecurityCenterGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_security_center_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
        )


def test_security_center_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.securitycenter_v1beta1.services.security_center.transports.SecurityCenterGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = SecurityCenterClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
        )


def test_create_source(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.CreateSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
        )

        response = client.create_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_create_source_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.CreateSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_source.Source(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
            )
        )

        response = await client.create_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


def test_create_source_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.CreateSourceRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_source), "__call__") as call:
        call.return_value = gcs_source.Source()

        client.create_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_source_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.CreateSourceRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_source), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_source.Source())

        await client.create_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_source_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_source(
            parent="parent_value", source=gcs_source.Source(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].source == gcs_source.Source(name="name_value")


def test_create_source_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_source(
            securitycenter_service.CreateSourceRequest(),
            parent="parent_value",
            source=gcs_source.Source(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_source_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_source.Source())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_source(
            parent="parent_value", source=gcs_source.Source(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].source == gcs_source.Source(name="name_value")


@pytest.mark.asyncio
async def test_create_source_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_source(
            securitycenter_service.CreateSourceRequest(),
            parent="parent_value",
            source=gcs_source.Source(name="name_value"),
        )


def test_create_finding(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.CreateFindingRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_finding), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding(
            name="name_value",
            parent="parent_value",
            resource_name="resource_name_value",
            state=gcs_finding.Finding.State.ACTIVE,
            category="category_value",
            external_uri="external_uri_value",
        )

        response = client.create_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == gcs_finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


@pytest.mark.asyncio
async def test_create_finding_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.CreateFindingRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_finding), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_finding.Finding(
                name="name_value",
                parent="parent_value",
                resource_name="resource_name_value",
                state=gcs_finding.Finding.State.ACTIVE,
                category="category_value",
                external_uri="external_uri_value",
            )
        )

        response = await client.create_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == gcs_finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


def test_create_finding_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.CreateFindingRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_finding), "__call__") as call:
        call.return_value = gcs_finding.Finding()

        client.create_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_finding_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.CreateFindingRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_finding), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_finding.Finding())

        await client.create_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_finding_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_finding), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_finding(
            parent="parent_value",
            finding_id="finding_id_value",
            finding=gcs_finding.Finding(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].finding_id == "finding_id_value"

        assert args[0].finding == gcs_finding.Finding(name="name_value")


def test_create_finding_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_finding(
            securitycenter_service.CreateFindingRequest(),
            parent="parent_value",
            finding_id="finding_id_value",
            finding=gcs_finding.Finding(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_finding_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_finding), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_finding.Finding())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_finding(
            parent="parent_value",
            finding_id="finding_id_value",
            finding=gcs_finding.Finding(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].finding_id == "finding_id_value"

        assert args[0].finding == gcs_finding.Finding(name="name_value")


@pytest.mark.asyncio
async def test_create_finding_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_finding(
            securitycenter_service.CreateFindingRequest(),
            parent="parent_value",
            finding_id="finding_id_value",
            finding=gcs_finding.Finding(name="name_value"),
        )


def test_get_iam_policy(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_get_iam_policy_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_get_iam_policy_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_iam_policy_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_iam_policy), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_get_iam_policy_from_dict():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


def test_get_iam_policy_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


def test_get_iam_policy_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_iam_policy(
            iam_policy.GetIamPolicyRequest(), resource="resource_value",
        )


@pytest.mark.asyncio
async def test_get_iam_policy_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


@pytest.mark.asyncio
async def test_get_iam_policy_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_iam_policy(
            iam_policy.GetIamPolicyRequest(), resource="resource_value",
        )


def test_get_organization_settings(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GetOrganizationSettingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = organization_settings.OrganizationSettings(
            name="name_value", enable_asset_discovery=True,
        )

        response = client.get_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, organization_settings.OrganizationSettings)

    assert response.name == "name_value"

    assert response.enable_asset_discovery is True


@pytest.mark.asyncio
async def test_get_organization_settings_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GetOrganizationSettingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            organization_settings.OrganizationSettings(
                name="name_value", enable_asset_discovery=True,
            )
        )

        response = await client.get_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, organization_settings.OrganizationSettings)

    assert response.name == "name_value"

    assert response.enable_asset_discovery is True


def test_get_organization_settings_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GetOrganizationSettingsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_organization_settings), "__call__"
    ) as call:
        call.return_value = organization_settings.OrganizationSettings()

        client.get_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_organization_settings_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GetOrganizationSettingsRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_organization_settings), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            organization_settings.OrganizationSettings()
        )

        await client.get_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_organization_settings_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = organization_settings.OrganizationSettings()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_organization_settings(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_organization_settings_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_organization_settings(
            securitycenter_service.GetOrganizationSettingsRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_organization_settings_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = organization_settings.OrganizationSettings()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            organization_settings.OrganizationSettings()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_organization_settings(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_organization_settings_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_organization_settings(
            securitycenter_service.GetOrganizationSettingsRequest(), name="name_value",
        )


def test_get_source(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GetSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = source.Source(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
        )

        response = client.get_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_source_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GetSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            source.Source(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
            )
        )

        response = await client.get_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


def test_get_source_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GetSourceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_source), "__call__") as call:
        call.return_value = source.Source()

        client.get_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_source_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GetSourceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_source), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(source.Source())

        await client.get_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_source_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = source.Source()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_source(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_source_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_source(
            securitycenter_service.GetSourceRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_source_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = source.Source()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(source.Source())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_source(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_source_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_source(
            securitycenter_service.GetSourceRequest(), name="name_value",
        )


def test_group_assets(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GroupAssetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_assets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.GroupAssetsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.group_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.GroupAssetsPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_group_assets_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GroupAssetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_assets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.GroupAssetsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.group_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.GroupAssetsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_group_assets_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GroupAssetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_assets), "__call__") as call:
        call.return_value = securitycenter_service.GroupAssetsResponse()

        client.group_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_group_assets_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GroupAssetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_assets), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.GroupAssetsResponse()
        )

        await client.group_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_group_assets_pager():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_assets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.group_assets(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, securitycenter_service.GroupResult) for i in results)


def test_group_assets_pages():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_assets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.group_assets(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_group_assets_async_pager():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_assets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.group_assets(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, securitycenter_service.GroupResult) for i in responses)


@pytest.mark.asyncio
async def test_group_assets_async_pages():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_assets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupAssetsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.group_assets(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_group_findings(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GroupFindingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_findings), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.GroupFindingsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.group_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.GroupFindingsPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_group_findings_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.GroupFindingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_findings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.GroupFindingsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.group_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.GroupFindingsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_group_findings_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GroupFindingsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_findings), "__call__") as call:
        call.return_value = securitycenter_service.GroupFindingsResponse()

        client.group_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_group_findings_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.GroupFindingsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_findings), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.GroupFindingsResponse()
        )

        await client.group_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_group_findings_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_findings), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.GroupFindingsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.group_findings(
            parent="parent_value", group_by="group_by_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].group_by == "group_by_value"


def test_group_findings_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.group_findings(
            securitycenter_service.GroupFindingsRequest(),
            parent="parent_value",
            group_by="group_by_value",
        )


@pytest.mark.asyncio
async def test_group_findings_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_findings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.GroupFindingsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.GroupFindingsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.group_findings(
            parent="parent_value", group_by="group_by_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].group_by == "group_by_value"


@pytest.mark.asyncio
async def test_group_findings_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.group_findings(
            securitycenter_service.GroupFindingsRequest(),
            parent="parent_value",
            group_by="group_by_value",
        )


def test_group_findings_pager():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_findings), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.group_findings(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, securitycenter_service.GroupResult) for i in results)


def test_group_findings_pages():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.group_findings), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.group_findings(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_group_findings_async_pager():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_findings),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.group_findings(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, securitycenter_service.GroupResult) for i in responses)


@pytest.mark.asyncio
async def test_group_findings_async_pages():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.group_findings),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[], next_page_token="def",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[securitycenter_service.GroupResult(),],
                next_page_token="ghi",
            ),
            securitycenter_service.GroupFindingsResponse(
                group_by_results=[
                    securitycenter_service.GroupResult(),
                    securitycenter_service.GroupResult(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.group_findings(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_list_assets(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListAssetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_assets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.ListAssetsResponse(
            next_page_token="next_page_token_value", total_size=1086,
        )

        response = client.list_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAssetsPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086


@pytest.mark.asyncio
async def test_list_assets_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListAssetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assets), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListAssetsResponse(
                next_page_token="next_page_token_value", total_size=1086,
            )
        )

        response = await client.list_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAssetsAsyncPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086


def test_list_assets_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListAssetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_assets), "__call__") as call:
        call.return_value = securitycenter_service.ListAssetsResponse()

        client.list_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_assets_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListAssetsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assets), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListAssetsResponse()
        )

        await client.list_assets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_assets_pager():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_assets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[], next_page_token="def",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="ghi",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_assets(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(
            isinstance(i, securitycenter_service.ListAssetsResponse.ListAssetsResult)
            for i in results
        )


def test_list_assets_pages():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_assets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[], next_page_token="def",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="ghi",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_assets(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_assets_async_pager():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[], next_page_token="def",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="ghi",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_assets(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, securitycenter_service.ListAssetsResponse.ListAssetsResult)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_assets_async_pages():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assets),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="abc",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[], next_page_token="def",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
                next_page_token="ghi",
            ),
            securitycenter_service.ListAssetsResponse(
                list_assets_results=[
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                    securitycenter_service.ListAssetsResponse.ListAssetsResult(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_assets(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_list_findings(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListFindingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_findings), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.ListFindingsResponse(
            next_page_token="next_page_token_value", total_size=1086,
        )

        response = client.list_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFindingsPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086


@pytest.mark.asyncio
async def test_list_findings_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListFindingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_findings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListFindingsResponse(
                next_page_token="next_page_token_value", total_size=1086,
            )
        )

        response = await client.list_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFindingsAsyncPager)

    assert response.next_page_token == "next_page_token_value"

    assert response.total_size == 1086


def test_list_findings_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListFindingsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_findings), "__call__") as call:
        call.return_value = securitycenter_service.ListFindingsResponse()

        client.list_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_findings_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListFindingsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_findings), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListFindingsResponse()
        )

        await client.list_findings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_findings_pager():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_findings), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(), finding.Finding(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[], next_page_token="def",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(),], next_page_token="ghi",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_findings(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, finding.Finding) for i in results)


def test_list_findings_pages():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_findings), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(), finding.Finding(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[], next_page_token="def",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(),], next_page_token="ghi",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_findings(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_findings_async_pager():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_findings),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(), finding.Finding(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[], next_page_token="def",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(),], next_page_token="ghi",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_findings(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, finding.Finding) for i in responses)


@pytest.mark.asyncio
async def test_list_findings_async_pages():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_findings),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(), finding.Finding(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[], next_page_token="def",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(),], next_page_token="ghi",
            ),
            securitycenter_service.ListFindingsResponse(
                findings=[finding.Finding(), finding.Finding(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_findings(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_list_sources(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListSourcesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_sources), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.ListSourcesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_sources(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSourcesPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_sources_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.ListSourcesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_sources), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListSourcesResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_sources(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSourcesAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_sources_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListSourcesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_sources), "__call__") as call:
        call.return_value = securitycenter_service.ListSourcesResponse()

        client.list_sources(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_sources_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.ListSourcesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_sources), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListSourcesResponse()
        )

        await client.list_sources(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_sources_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_sources), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.ListSourcesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_sources(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_sources_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_sources(
            securitycenter_service.ListSourcesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_sources_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_sources), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = securitycenter_service.ListSourcesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            securitycenter_service.ListSourcesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_sources(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_sources_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_sources(
            securitycenter_service.ListSourcesRequest(), parent="parent_value",
        )


def test_list_sources_pager():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_sources), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(), source.Source(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[], next_page_token="def",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(),], next_page_token="ghi",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_sources(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, source.Source) for i in results)


def test_list_sources_pages():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_sources), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(), source.Source(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[], next_page_token="def",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(),], next_page_token="ghi",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_sources(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_sources_async_pager():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_sources),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(), source.Source(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[], next_page_token="def",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(),], next_page_token="ghi",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_sources(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, source.Source) for i in responses)


@pytest.mark.asyncio
async def test_list_sources_async_pages():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_sources),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(), source.Source(),],
                next_page_token="abc",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[], next_page_token="def",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(),], next_page_token="ghi",
            ),
            securitycenter_service.ListSourcesResponse(
                sources=[source.Source(), source.Source(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page in (await client.list_sources(request={})).pages:
            pages.append(page)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_run_asset_discovery(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.RunAssetDiscoveryRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.run_asset_discovery), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.run_asset_discovery(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_run_asset_discovery_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.RunAssetDiscoveryRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.run_asset_discovery), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.run_asset_discovery(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_run_asset_discovery_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.RunAssetDiscoveryRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.run_asset_discovery), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.run_asset_discovery(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_run_asset_discovery_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.RunAssetDiscoveryRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.run_asset_discovery), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.run_asset_discovery(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_run_asset_discovery_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.run_asset_discovery), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.run_asset_discovery(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_run_asset_discovery_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.run_asset_discovery(
            securitycenter_service.RunAssetDiscoveryRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_run_asset_discovery_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.run_asset_discovery), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.run_asset_discovery(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_run_asset_discovery_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.run_asset_discovery(
            securitycenter_service.RunAssetDiscoveryRequest(), parent="parent_value",
        )


def test_set_finding_state(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.SetFindingStateRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.set_finding_state), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = finding.Finding(
            name="name_value",
            parent="parent_value",
            resource_name="resource_name_value",
            state=finding.Finding.State.ACTIVE,
            category="category_value",
            external_uri="external_uri_value",
        )

        response = client.set_finding_state(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


@pytest.mark.asyncio
async def test_set_finding_state_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.SetFindingStateRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_finding_state), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            finding.Finding(
                name="name_value",
                parent="parent_value",
                resource_name="resource_name_value",
                state=finding.Finding.State.ACTIVE,
                category="category_value",
                external_uri="external_uri_value",
            )
        )

        response = await client.set_finding_state(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


def test_set_finding_state_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.SetFindingStateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.set_finding_state), "__call__"
    ) as call:
        call.return_value = finding.Finding()

        client.set_finding_state(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_finding_state_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.SetFindingStateRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_finding_state), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(finding.Finding())

        await client.set_finding_state(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_set_finding_state_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.set_finding_state), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = finding.Finding()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.set_finding_state(
            name="name_value",
            state=finding.Finding.State.ACTIVE,
            start_time=timestamp.Timestamp(seconds=751),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].state == finding.Finding.State.ACTIVE

        assert TimestampRule().to_proto(args[0].start_time) == timestamp.Timestamp(
            seconds=751
        )


def test_set_finding_state_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_finding_state(
            securitycenter_service.SetFindingStateRequest(),
            name="name_value",
            state=finding.Finding.State.ACTIVE,
            start_time=timestamp.Timestamp(seconds=751),
        )


@pytest.mark.asyncio
async def test_set_finding_state_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_finding_state), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = finding.Finding()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(finding.Finding())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.set_finding_state(
            name="name_value",
            state=finding.Finding.State.ACTIVE,
            start_time=timestamp.Timestamp(seconds=751),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].state == finding.Finding.State.ACTIVE

        assert TimestampRule().to_proto(args[0].start_time) == timestamp.Timestamp(
            seconds=751
        )


@pytest.mark.asyncio
async def test_set_finding_state_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.set_finding_state(
            securitycenter_service.SetFindingStateRequest(),
            name="name_value",
            state=finding.Finding.State.ACTIVE,
            start_time=timestamp.Timestamp(seconds=751),
        )


def test_set_iam_policy(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_set_iam_policy_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_set_iam_policy_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_iam_policy_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_iam_policy), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_set_iam_policy_from_dict():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy.Policy(version=774),
            }
        )
        call.assert_called()


def test_set_iam_policy_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.set_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


def test_set_iam_policy_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_iam_policy(
            iam_policy.SetIamPolicyRequest(), resource="resource_value",
        )


@pytest.mark.asyncio
async def test_set_iam_policy_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.set_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.set_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


@pytest.mark.asyncio
async def test_set_iam_policy_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.set_iam_policy(
            iam_policy.SetIamPolicyRequest(), resource="resource_value",
        )


def test_test_iam_permissions(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse(
            permissions=["permissions_value"],
        )

        response = client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse(permissions=["permissions_value"],)
        )

        response = await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


def test_test_iam_permissions_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = iam_policy.TestIamPermissionsResponse()

        client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_test_iam_permissions_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse()
        )

        await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_test_iam_permissions_from_dict():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        response = client.test_iam_permissions(
            request={
                "resource": "resource_value",
                "permissions": ["permissions_value"],
            }
        )
        call.assert_called()


def test_test_iam_permissions_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.test_iam_permissions(
            resource="resource_value", permissions=["permissions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"

        assert args[0].permissions == ["permissions_value"]


def test_test_iam_permissions_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.test_iam_permissions(
            iam_policy.TestIamPermissionsRequest(),
            resource="resource_value",
            permissions=["permissions_value"],
        )


@pytest.mark.asyncio
async def test_test_iam_permissions_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.test_iam_permissions(
            resource="resource_value", permissions=["permissions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"

        assert args[0].permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.test_iam_permissions(
            iam_policy.TestIamPermissionsRequest(),
            resource="resource_value",
            permissions=["permissions_value"],
        )


def test_update_finding(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateFindingRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_finding), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding(
            name="name_value",
            parent="parent_value",
            resource_name="resource_name_value",
            state=gcs_finding.Finding.State.ACTIVE,
            category="category_value",
            external_uri="external_uri_value",
        )

        response = client.update_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == gcs_finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


@pytest.mark.asyncio
async def test_update_finding_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateFindingRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_finding), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_finding.Finding(
                name="name_value",
                parent="parent_value",
                resource_name="resource_name_value",
                state=gcs_finding.Finding.State.ACTIVE,
                category="category_value",
                external_uri="external_uri_value",
            )
        )

        response = await client.update_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_finding.Finding)

    assert response.name == "name_value"

    assert response.parent == "parent_value"

    assert response.resource_name == "resource_name_value"

    assert response.state == gcs_finding.Finding.State.ACTIVE

    assert response.category == "category_value"

    assert response.external_uri == "external_uri_value"


def test_update_finding_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateFindingRequest()
    request.finding.name = "finding.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_finding), "__call__") as call:
        call.return_value = gcs_finding.Finding()

        client.update_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "finding.name=finding.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_finding_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateFindingRequest()
    request.finding.name = "finding.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_finding), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_finding.Finding())

        await client.update_finding(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "finding.name=finding.name/value",) in kw[
        "metadata"
    ]


def test_update_finding_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_finding), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_finding(finding=gcs_finding.Finding(name="name_value"),)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].finding == gcs_finding.Finding(name="name_value")


def test_update_finding_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_finding(
            securitycenter_service.UpdateFindingRequest(),
            finding=gcs_finding.Finding(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_finding_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_finding), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_finding.Finding()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_finding.Finding())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_finding(
            finding=gcs_finding.Finding(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].finding == gcs_finding.Finding(name="name_value")


@pytest.mark.asyncio
async def test_update_finding_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_finding(
            securitycenter_service.UpdateFindingRequest(),
            finding=gcs_finding.Finding(name="name_value"),
        )


def test_update_organization_settings(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateOrganizationSettingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_organization_settings.OrganizationSettings(
            name="name_value", enable_asset_discovery=True,
        )

        response = client.update_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_organization_settings.OrganizationSettings)

    assert response.name == "name_value"

    assert response.enable_asset_discovery is True


@pytest.mark.asyncio
async def test_update_organization_settings_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateOrganizationSettingsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_organization_settings.OrganizationSettings(
                name="name_value", enable_asset_discovery=True,
            )
        )

        response = await client.update_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_organization_settings.OrganizationSettings)

    assert response.name == "name_value"

    assert response.enable_asset_discovery is True


def test_update_organization_settings_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateOrganizationSettingsRequest()
    request.organization_settings.name = "organization_settings.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_organization_settings), "__call__"
    ) as call:
        call.return_value = gcs_organization_settings.OrganizationSettings()

        client.update_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "organization_settings.name=organization_settings.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_organization_settings_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateOrganizationSettingsRequest()
    request.organization_settings.name = "organization_settings.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_organization_settings), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_organization_settings.OrganizationSettings()
        )

        await client.update_organization_settings(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "organization_settings.name=organization_settings.name/value",
    ) in kw["metadata"]


def test_update_organization_settings_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_organization_settings.OrganizationSettings()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_organization_settings(
            organization_settings=gcs_organization_settings.OrganizationSettings(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[
            0
        ].organization_settings == gcs_organization_settings.OrganizationSettings(
            name="name_value"
        )


def test_update_organization_settings_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_organization_settings(
            securitycenter_service.UpdateOrganizationSettingsRequest(),
            organization_settings=gcs_organization_settings.OrganizationSettings(
                name="name_value"
            ),
        )


@pytest.mark.asyncio
async def test_update_organization_settings_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_organization_settings), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_organization_settings.OrganizationSettings()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_organization_settings.OrganizationSettings()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_organization_settings(
            organization_settings=gcs_organization_settings.OrganizationSettings(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[
            0
        ].organization_settings == gcs_organization_settings.OrganizationSettings(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_update_organization_settings_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_organization_settings(
            securitycenter_service.UpdateOrganizationSettingsRequest(),
            organization_settings=gcs_organization_settings.OrganizationSettings(
                name="name_value"
            ),
        )


def test_update_source(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
        )

        response = client.update_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_update_source_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateSourceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_source.Source(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
            )
        )

        response = await client.update_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_source.Source)

    assert response.name == "name_value"

    assert response.display_name == "display_name_value"

    assert response.description == "description_value"


def test_update_source_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateSourceRequest()
    request.source.name = "source.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_source), "__call__") as call:
        call.return_value = gcs_source.Source()

        client.update_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "source.name=source.name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_source_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateSourceRequest()
    request.source.name = "source.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_source), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_source.Source())

        await client.update_source(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "source.name=source.name/value",) in kw["metadata"]


def test_update_source_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_source), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_source(source=gcs_source.Source(name="name_value"),)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].source == gcs_source.Source(name="name_value")


def test_update_source_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_source(
            securitycenter_service.UpdateSourceRequest(),
            source=gcs_source.Source(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_source_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_source), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_source.Source()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcs_source.Source())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_source(
            source=gcs_source.Source(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].source == gcs_source.Source(name="name_value")


@pytest.mark.asyncio
async def test_update_source_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_source(
            securitycenter_service.UpdateSourceRequest(),
            source=gcs_source.Source(name="name_value"),
        )


def test_update_security_marks(transport: str = "grpc"):
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateSecurityMarksRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_security_marks), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_security_marks.SecurityMarks(name="name_value",)

        response = client.update_security_marks(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_security_marks.SecurityMarks)

    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_update_security_marks_async(transport: str = "grpc_asyncio"):
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = securitycenter_service.UpdateSecurityMarksRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_security_marks), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_security_marks.SecurityMarks(name="name_value",)
        )

        response = await client.update_security_marks(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcs_security_marks.SecurityMarks)

    assert response.name == "name_value"


def test_update_security_marks_field_headers():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateSecurityMarksRequest()
    request.security_marks.name = "security_marks.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_security_marks), "__call__"
    ) as call:
        call.return_value = gcs_security_marks.SecurityMarks()

        client.update_security_marks(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "security_marks.name=security_marks.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_security_marks_field_headers_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = securitycenter_service.UpdateSecurityMarksRequest()
    request.security_marks.name = "security_marks.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_security_marks), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_security_marks.SecurityMarks()
        )

        await client.update_security_marks(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "security_marks.name=security_marks.name/value",
    ) in kw["metadata"]


def test_update_security_marks_flattened():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_security_marks), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_security_marks.SecurityMarks()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_security_marks(
            security_marks=gcs_security_marks.SecurityMarks(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].security_marks == gcs_security_marks.SecurityMarks(
            name="name_value"
        )


def test_update_security_marks_flattened_error():
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_security_marks(
            securitycenter_service.UpdateSecurityMarksRequest(),
            security_marks=gcs_security_marks.SecurityMarks(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_security_marks_flattened_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_security_marks), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcs_security_marks.SecurityMarks()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcs_security_marks.SecurityMarks()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_security_marks(
            security_marks=gcs_security_marks.SecurityMarks(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].security_marks == gcs_security_marks.SecurityMarks(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_update_security_marks_flattened_error_async():
    client = SecurityCenterAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_security_marks(
            securitycenter_service.UpdateSecurityMarksRequest(),
            security_marks=gcs_security_marks.SecurityMarks(name="name_value"),
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.SecurityCenterGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = SecurityCenterClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.SecurityCenterGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = SecurityCenterClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.SecurityCenterGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = SecurityCenterClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.SecurityCenterGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = SecurityCenterClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.SecurityCenterGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.SecurityCenterGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = SecurityCenterClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.SecurityCenterGrpcTransport,)


def test_security_center_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.SecurityCenterTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_security_center_base_transport():
    # Instantiate the base transport.
    transport = transports.SecurityCenterTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_source",
        "create_finding",
        "get_iam_policy",
        "get_organization_settings",
        "get_source",
        "group_assets",
        "group_findings",
        "list_assets",
        "list_findings",
        "list_sources",
        "run_asset_discovery",
        "set_finding_state",
        "set_iam_policy",
        "test_iam_permissions",
        "update_finding",
        "update_organization_settings",
        "update_source",
        "update_security_marks",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_security_center_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(auth, "load_credentials_from_file") as load_creds:
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.SecurityCenterTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_security_center_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        SecurityCenterClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


def test_security_center_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.SecurityCenterGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_security_center_host_no_port():
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="securitycenter.googleapis.com"
        ),
    )
    assert client._transport._host == "securitycenter.googleapis.com:443"


def test_security_center_host_with_port():
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="securitycenter.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "securitycenter.googleapis.com:8000"


def test_security_center_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.SecurityCenterGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_security_center_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.SecurityCenterGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_security_center_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.SecurityCenterGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=("https://www.googleapis.com/auth/cloud-platform",),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_security_center_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.SecurityCenterGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=("https://www.googleapis.com/auth/cloud-platform",),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_security_center_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.SecurityCenterGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_security_center_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.SecurityCenterGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


def test_security_center_grpc_lro_client():
    client = SecurityCenterClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_security_center_grpc_lro_async_client():
    client = SecurityCenterAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client._client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_source_path():
    organization = "squid"
    source = "clam"

    expected = "organizations/{organization}/sources/{source}".format(
        organization=organization, source=source,
    )
    actual = SecurityCenterClient.source_path(organization, source)
    assert expected == actual


def test_parse_source_path():
    expected = {
        "organization": "whelk",
        "source": "octopus",
    }
    path = SecurityCenterClient.source_path(**expected)

    # Check that the path construction is reversible.
    actual = SecurityCenterClient.parse_source_path(path)
    assert expected == actual


def test_finding_path():
    organization = "squid"
    source = "clam"
    finding = "whelk"

    expected = "organizations/{organization}/sources/{source}/findings/{finding}".format(
        organization=organization, source=source, finding=finding,
    )
    actual = SecurityCenterClient.finding_path(organization, source, finding)
    assert expected == actual


def test_parse_finding_path():
    expected = {
        "organization": "octopus",
        "source": "oyster",
        "finding": "nudibranch",
    }
    path = SecurityCenterClient.finding_path(**expected)

    # Check that the path construction is reversible.
    actual = SecurityCenterClient.parse_finding_path(path)
    assert expected == actual


def test_organization_settings_path():
    organization = "squid"

    expected = "organizations/{organization}/organizationSettings".format(
        organization=organization,
    )
    actual = SecurityCenterClient.organization_settings_path(organization)
    assert expected == actual


def test_parse_organization_settings_path():
    expected = {
        "organization": "clam",
    }
    path = SecurityCenterClient.organization_settings_path(**expected)

    # Check that the path construction is reversible.
    actual = SecurityCenterClient.parse_organization_settings_path(path)
    assert expected == actual


def test_security_marks_path():
    organization = "squid"
    asset = "clam"

    expected = "organizations/{organization}/assets/{asset}/securityMarks".format(
        organization=organization, asset=asset,
    )
    actual = SecurityCenterClient.security_marks_path(organization, asset)
    assert expected == actual


def test_parse_security_marks_path():
    expected = {
        "organization": "whelk",
        "asset": "octopus",
    }
    path = SecurityCenterClient.security_marks_path(**expected)

    # Check that the path construction is reversible.
    actual = SecurityCenterClient.parse_security_marks_path(path)
    assert expected == actual
