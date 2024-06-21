from __future__ import annotations

import abc
import base64
import dataclasses
import datetime
import hashlib
import json
import time
import typing

from class_registry import ClassRegistry

from compute_horde_facilitator_sdk._internal.typing import JSONType

if typing.TYPE_CHECKING:
    import bittensor


SIGNERS_REGISTRY = ClassRegistry("signature_type")
VERIFIERS_REGISTRY = ClassRegistry("signature_type")


@dataclasses.dataclass
class Signature:
    signature_type: str
    signatory: str  # identity of the signer (e.g. sa58 address if signature_type == "bittensor")
    timestamp_ns: int  # UNIX timestamp in nanoseconds
    signature: bytes


def verify_signature(
    payload: JSONType | bytes,
    signature: Signature,
    newer_than: datetime.datetime | None = None,
):
    """
    Verifies the signature of the payload

    :param payload: payload to be verified
    :param signature: signature object
    :param newer_than: if provided, checks if the signature is newer than the provided timestamp
    :return: None
    :raises SignatureInvalidException: if the signature is invalid
    """
    verifier = VERIFIERS_REGISTRY.get(signature.signature_type)
    verifier.verify(payload, signature, newer_than)


def signature_from_headers(headers: dict[str, str], prefix: str = "X-CH-") -> Signature:
    """
    Extracts the signature from the headers

    :param headers: headers dict
    :return: Signature object
    """
    try:
        return Signature(
            signature_type=headers[f"{prefix}Signature-Type"],
            signatory=headers[f"{prefix}Signatory"],
            timestamp_ns=int(headers[f"{prefix}Timestamp-NS"]),
            signature=base64.b64decode(headers[f"{prefix}Signature"]),
        )
    except (
        KeyError,
        ValueError,
        TypeError,
    ) as e:
        raise SignatureNotFound("Signature not found in headers") from e


def signature_to_headers(signature: Signature, prefix: str = "X-CH-") -> dict[str, str]:
    """
    Converts the signature to headers

    :param signature: Signature object
    :return: headers dict
    """
    return {
        f"{prefix}Signature-Type": signature.signature_type,
        f"{prefix}Signatory": signature.signatory,
        f"{prefix}Timestamp-NS": str(signature.timestamp_ns),
        f"{prefix}Signature": base64.b64encode(signature.signature).decode("utf-8"),
    }


class SignatureException(Exception):
    pass


class SignatureNotFound(SignatureException):
    pass


class SignatureInvalidException(SignatureException):
    pass


class SignatureTimeoutException(SignatureInvalidException):
    pass


def hash_message_signature(payload: bytes | JSONType, signature: Signature) -> bytes:
    """
    Hashes the message to be signed with the signature parameters

    :param payload: payload to be signed
    :param signature: incomplete signature object with Signature parameters
    :return:
    """
    if not isinstance(payload, bytes):
        payload = json.dumps(payload, sort_keys=True).encode("utf-8")

    hasher = hashlib.blake2b()
    hasher.update(signature.timestamp_ns.to_bytes(8, "big"))
    hasher.update(payload)
    return hasher.digest()


class Signer(abc.ABC):
    signature_type: typing.ClassVar[str]

    def sign(self, payload: JSONType | bytes) -> Signature:
        signature = Signature(
            signature_type=self.signature_type,
            signatory=self.get_signatory(),
            timestamp_ns=time.time_ns(),
            signature=b"",
        )
        payload_hash = hash_message_signature(payload, signature)
        signature.signature = self._sign(payload_hash)
        return signature

    @abc.abstractmethod
    def _sign(self, payload: bytes) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def get_signatory(self) -> str:
        raise NotImplementedError


class Verifier(abc.ABC):
    signature_type: typing.ClassVar[str]

    def verify(
        self,
        payload: JSONType | bytes,
        signature: Signature,
        newer_than: datetime.datetime | None = None,
    ):
        payload_hash = hash_message_signature(payload, signature)
        self._verify(payload_hash, signature)

        if newer_than is not None:
            if newer_than > datetime.datetime.fromtimestamp(signature.timestamp_ns / 1_000_000_000):
                raise SignatureTimeoutException("Signature is too old")

    @abc.abstractmethod
    def _verify(self, payload: bytes, signature: Signature) -> None:
        raise NotImplementedError


def _require_bittensor():
    try:
        import bittensor
    except ImportError as e:
        raise ImportError("bittensor package is required for BittensorWalletSigner") from e
    return bittensor


@SIGNERS_REGISTRY.register
class BittensorWalletSigner(Signer):
    signature_type = "bittensor"

    def __init__(self, wallet: bittensor.wallet | None = None):
        bittensor = _require_bittensor()

        self._keypair = (wallet or bittensor.wallet()).hotkey

    def _sign(self, payload: bytes) -> bytes:
        return self._keypair.sign(payload)

    def get_signatory(self) -> str:
        return self._keypair.ss58_address


@VERIFIERS_REGISTRY.register
class BittensorWalletVerifier(Verifier):
    signature_type = "bittensor"

    def __init__(self, *args, **kwargs):
        self._bittensor = _require_bittensor()

        super().__init__(*args, **kwargs)

    def _verify(self, payload: bytes, signature: Signature) -> None:
        try:
            keypair = self._bittensor.Keypair(ss58_address=signature.signatory)
        except ValueError:
            raise SignatureInvalidException("Invalid signatory for BittensorWalletVerifier")
        try:
            if not keypair.verify(data=payload, signature=signature.signature):
                raise SignatureInvalidException("Signature is invalid")
        except (ValueError, TypeError) as e:
            raise SignatureInvalidException("Signature is malformed") from e
