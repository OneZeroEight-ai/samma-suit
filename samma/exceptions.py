"""Samma Suit exception hierarchy — one base error per layer."""


class SammaError(Exception):
    """Base exception for all Samma Suit errors."""

    def __init__(self, message: str = "", *, layer: str = "samma"):
        self.layer = layer
        super().__init__(message)


# Layer 1: SUTRA (Gateway)
class SUTRAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="sutra")


class OriginDeniedError(SUTRAError):
    pass


class RateLimitExceededError(SUTRAError):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")


class TLSRequiredError(SUTRAError):
    pass


# Layer 2: DHARMA (Permissions)
class DHARMAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="dharma")


class PermissionDeniedError(DHARMAError):
    pass


class RoleNotFoundError(DHARMAError):
    pass


# Layer 3: SANGHA (Skill Vetting)
class SANGHAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="sangha")


# Layer 4: KARMA (Cost Controls)
class KARMAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="karma")


# Layer 5: SILA (Audit Trail)
class SILAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="sila")


# Layer 6: METTA (Identity)
class METTAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="metta")


# Layer 7: BODHI (Isolation)
class BODHIError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="bodhi")


# Layer 8: NIRVANA (Recovery)
class NIRVANAError(SammaError):
    def __init__(self, message: str = ""):
        super().__init__(message, layer="nirvana")
