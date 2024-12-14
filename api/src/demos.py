"""
src/demos.py - This script contains stuff for demos such as fake data generation.

Date: December 12, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com
"""

# Third-party
from loguru import logger
from faker import Faker

# Local
from src.models import Issue
from src.enums import IssueProgressEnum

fake: Faker = Faker()

async def generate_issues() -> None:
        # Generate 500 random issues using Faker
    issues = []
    for _ in range(500):
        issue = Issue(
            id=uuid4(),
            gse_id=f"GSE-{fake.random_int(min=1000, max=9999)}",
            issue_description=fake.text(max_nb_chars=200),
            reported_by=fake.bothify(text="###"),
            progress=fake.random_element(elements=list(IssueProgressEnum)),
            reported_at=fake.date_time_between(start_date="-1y", end_date="now"),
            estimated_time=(
                fake.future_datetime(end_date="+30d") if fake.boolean(chance_of_getting_true=50) else None
            ),
        )
        issues.append(issue)

    # Bulk insert issues
    await Issue.bulk_create(issues)

    logger.success("500 issues successfully generated and inserted into the database!")