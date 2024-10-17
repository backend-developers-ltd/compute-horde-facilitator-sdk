import base64
import dataclasses
import datetime

import freezegun
import pytest

from compute_horde_facilitator_sdk._internal.signature import (
    hash_message_signature,
    signature_payload,
)


def test_available_signers(apiver_module):
    assert list(apiver_module.SIGNERS_REGISTRY) == ["bittensor"]


def test_available_verifiers(apiver_module):
    assert list(apiver_module.VERIFIERS_REGISTRY) == ["bittensor"]


@pytest.fixture
def sample_data():
    return {
        "b": 2,
        "array": [1, 2, 3],
        "dict": {"subdict:": {"null": None}},
    }


@pytest.fixture
def sample_signature(apiver_module):
    return apiver_module.Signature(
        signature_type="bittensor",
        signatory="5FUJCuGtQPonu8B9JKH4BwsKzEdtyBTpyvbBk2beNZ4iX8sk",  # hotkey address
        timestamp_ns=1718845323456788992,
        signature=base64.b85decode("1SaAcLt*GG`2RG*@xmapXZ14m*Y`@b1MP(hAfEnwXkO5Os<30drw{`X`15JFP4GWR96T7p>rUmYA#=8Z"),
    )


def test_hash_message_signature(sample_data, sample_signature):
    assert hash_message_signature(sample_data, sample_signature) == base64.b85decode(
        "Dk7mtj^WM^#_n_!-C@$EHF*O@>;mdK%XS?515>IhxRvgxdT<nq$ImMmQ)jr-hpUSs#o+GQRX~t<q0-~1"
    )


@freezegun.freeze_time("2024-06-20T01:02:03.456789")
def test_bittensor_wallet_signer_sign(apiver_module, bittensor_wallet, sample_data):
    signer = apiver_module.BittensorWalletSigner(bittensor_wallet)
    signature = signer.sign(sample_data)

    assert signature == apiver_module.Signature(
        signature_type="bittensor",
        signatory=bittensor_wallet.hotkey.ss58_address,
        timestamp_ns=1718845323456788992,
        signature=signature.signature,
    )

    assert isinstance(signature.signature, bytes) and len(signature.signature) == 64

    # assert random nonce is always included in the signature
    signature_2 = signer.sign(sample_data)
    assert dataclasses.replace(signature_2, signature=b"") == dataclasses.replace(signature, signature=b"")
    assert signature_2.signature != signature.signature


def test_bittensor_wallet_verifier_verify(apiver_module, sample_data, sample_signature):
    verifier = apiver_module.BittensorWalletVerifier()
    verifier.verify(sample_data, sample_signature)


def test_bittensor_wallet_verifier_verify_invalid_signature(apiver_module, sample_data, sample_signature):
    verifier = apiver_module.BittensorWalletVerifier()
    sample_signature.signature = b"invalid"
    with pytest.raises(apiver_module.SignatureInvalidException):
        verifier.verify(sample_data, sample_signature)


def test_bittensor_wallet_verifier_verify_signature_timeout(apiver_module, sample_data, sample_signature):
    verifier = apiver_module.BittensorWalletVerifier()

    with pytest.raises(apiver_module.SignatureInvalidException):
        verifier.verify(sample_data, sample_signature, newer_than=datetime.datetime.now())


@pytest.mark.parametrize(
    "data",
    [
        {"b": 2, "array": [1, 2, 3], "dict": {"subdict:": {"null": None}}},
        b"test",
    ],
)
def test_bittensor_wallet__sign_n_verify(apiver_module, bittensor_wallet, data):
    signer = apiver_module.BittensorWalletSigner(bittensor_wallet)
    verifier = apiver_module.BittensorWalletVerifier()

    signature = signer.sign(data)
    verifier.verify(data, signature)


def test_signature_from_headers__not_found(apiver_module):
    with pytest.raises(apiver_module.SignatureNotFound):
        apiver_module.signature_from_headers({})


def test_signature_payload():
    assert signature_payload("get", "https://example.com/car", headers={"Date": "X"}, json={"a": 1}) == {
        "action": "GET /car",
        "json": {"a": 1},
    }
