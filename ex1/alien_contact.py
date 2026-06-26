from enum import Enum
from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ValidationError


class ContactType(Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_contact(self) -> Self:
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        if (
                self.contact_type == ContactType.TELEPATHIC
                and self.witness_count < 3
                ):
            raise ValueError(
                    "Telepathic contact requires at least 3 witnesses"
                    )

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                    "Strong signals (> 7.0) should include received messages"
                    )

        return self


def main() -> None:
    print("Alien Contact Log Validation")
    print("======================================")

    valid_contact_report = AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime(2024, 6, 23, 11, 0),
            location="Area 51, Nevada",
            contact_type=ContactType.RADIO,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="'Greetings from Zeta Reticuli'"
            )

    print("Valid contact report:")
    print(f"ID: {valid_contact_report.contact_id}")
    print(f"Type: {valid_contact_report.contact_type}")
    print(f"Location: {valid_contact_report.location}")
    print(f"Signal: {valid_contact_report.signal_strength}/10")
    print(f"Duration: {valid_contact_report.duration_minutes} minutes")
    print(f"Witnesses: {valid_contact_report.witness_count}")
    if valid_contact_report.message_received:
        print(f"Message: {valid_contact_report.message_received}")

    print("\n======================================")

    try:
        _ = AlienContact(
                contact_id="AC_2026_001",
                timestamp=datetime(2026, 6, 23, 11, 0),
                location="Area 51, Nevada",
                contact_type=ContactType.TELEPATHIC,
                signal_strength=6.5,
                duration_minutes=45,
                witness_count=2,
                message_received="'Greetings from DoubleZeta Reticuli'"
                )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
