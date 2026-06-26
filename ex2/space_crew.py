from enum import Enum
from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ValidationError


class Rank(Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)

    def is_veteran(self) -> bool:
        return self.years_experience >= 5


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self) -> Self:
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        if not any(
                member.rank in [Rank.COMMANDER, Rank.CAPTAIN]
                for member in self.crew
                ):
            raise ValueError(
                    "Mission must have at least one Commander or Captain"
                    )

        is_long_mission = self.duration_days > 365
        veteran_count = sum(
                member.is_veteran() for member in self.crew
                )
        has_enough_veteran = veteran_count >= (len(self.crew) / 2)
        if is_long_mission and not has_enough_veteran:
            raise ValueError(
                    "Long missions (> 365 days) need"
                    "50% experienced crew (5+ years)"
                    )

        if not all(member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")

        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=========================================")

    crew_1 = CrewMember(
            member_id="0001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=42,
            specialization="Mission Command",
            years_experience=10,
            is_active=True
            )

    crew_2 = CrewMember(
            member_id="0002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=49,
            specialization="Navigation",
            years_experience=23,
            is_active=True
            )

    crew_3 = CrewMember(
            member_id="0003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=30,
            specialization="Engineering",
            years_experience=4,
            is_active=True
            )

    valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2026, 6, 23, 17, 00),
            duration_days=900,
            crew=[crew_1, crew_2, crew_3],
            mission_status="planned",
            budget_millions=2500.0
            )

    print("Valid mission created:")
    print(f"Mission: {valid_mission.mission_name}")
    print(f"ID: {valid_mission.mission_id}")
    print(f"Destination: {valid_mission.destination}")
    print(f"Duration: {valid_mission.duration_days} days")
    print(f"Budget: ${valid_mission.budget_millions}M")
    print(f"Crew size: {len(valid_mission.crew)}")
    print("Crew members:")
    for member in valid_mission.crew:
        print(
                f"- {member.name} "
                f"({member.rank.value}) - {member.specialization}"
                )

    print("\n=========================================")
    try:
        _ = SpaceMission(
                mission_id="M3024_EARTH",
                mission_name="Earth Colony Establishment",
                destination="Earth",
                launch_date=datetime(3026, 6, 23, 17, 00),
                duration_days=900,
                crew=[crew_2, crew_3],
                mission_status="planned",
                budget_millions=10000.0
                )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
