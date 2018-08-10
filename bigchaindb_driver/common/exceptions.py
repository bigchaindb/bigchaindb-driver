# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

###############################################################################
# DO NOT CHANGE THIS FILE.                                                    #
#                                                                             #
# This is a copy of the `bigchaindb.common` module, any change you want to do #
# here should be done in the original module, located in the BigchainDB       #
# repository at <https://github.com/bigchaindb/bigchaindb>.                   #
#                                                                             #
# We decided to copy the module here to avoid having the whole BigchainDB     #
# package as a dependency. This is a temporary solution until BEP-9 is        #
# implemented.                                                                #
###############################################################################

"""Custom exceptions used in the `bigchaindb` package.
"""


class BigchainDBError(Exception):
    """Base class for BigchainDB exceptions."""


class ConfigurationError(BigchainDBError):
    """Raised when there is a problem with server configuration"""


class DatabaseAlreadyExists(BigchainDBError):
    """Raised when trying to create the database but the db is already there"""


class DatabaseDoesNotExist(BigchainDBError):
    """Raised when trying to delete the database but the db is not there"""


class StartupError(BigchainDBError):
    """Raised when there is an error starting up the system"""


class CyclicBlockchainError(BigchainDBError):
    """Raised when there is a cycle in the blockchain"""


class KeypairMismatchException(BigchainDBError):
    """Raised if the private key(s) provided for signing don't match any of the
    current owner(s)
    """


class OperationError(BigchainDBError):
    """Raised when an operation cannot go through"""


##############################################################################
# Validation errors
#
# All validation errors (which are handleable errors, not faults) should
# subclass ValidationError. However, where possible they should also have their
# own distinct type to differentiate them from other validation errors,
# especially for the purposes of testing.


class ValidationError(BigchainDBError):
    """Raised if there was an error in validation"""


class DoubleSpend(ValidationError):
    """Raised if a double spend is found"""


class InvalidHash(ValidationError):
    """Raised if there was an error checking the hash for a particular
    operation
    """


class SchemaValidationError(ValidationError):
    """Raised if there was any error validating an object's schema"""


class InvalidSignature(ValidationError):
    """Raised if there was an error checking the signature for a particular
    operation
    """


class TransactionNotInValidBlock(ValidationError):
    """Raised when a transfer transaction is attempting to fulfill the
    outputs of a transaction that is in an invalid or undecided block
    """


class AssetIdMismatch(ValidationError):
    """Raised when multiple transaction inputs related to different assets"""


class AmountError(ValidationError):
    """Raised when there is a problem with a transaction's output amounts"""


class InputDoesNotExist(ValidationError):
    """Raised if a transaction input does not exist"""


class TransactionOwnerError(ValidationError):
    """Raised if a user tries to transfer a transaction they don't own"""


class DuplicateTransaction(ValidationError):
    """Raised if a duplicated transaction is found"""


class ThresholdTooDeep(ValidationError):
    """Raised if threshold condition is too deep"""


class GenesisBlockAlreadyExistsError(ValidationError):
    """Raised when trying to create the already existing genesis block"""


class MultipleValidatorOperationError(ValidationError):
    """Raised when a validator update pending but new request is submited"""
