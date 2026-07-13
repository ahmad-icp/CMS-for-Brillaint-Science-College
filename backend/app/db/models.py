"""Central SQLAlchemy model registry imports.

Import this module before calling ``Base.metadata.create_all`` so every ORM model is
registered exactly once through the canonical ``app.*`` package path.
"""

# Import modules for their mapper/table side effects. Keep this list explicit so
# model ownership stays clear and circular imports are easier to spot.
from app.modules.academic import models as academic_models  # noqa: F401
from app.modules.admissions import models as admissions_models  # noqa: F401
from app.modules.attendance import models as attendance_models  # noqa: F401
from app.modules.certificates import models as certificates_models  # noqa: F401
from app.modules.examination import models as examination_models  # noqa: F401
from app.modules.fees import models as fees_models  # noqa: F401
from app.modules.marks_entry import models as marks_entry_models  # noqa: F401
from app.modules.notifications import models as notifications_models  # noqa: F401
from app.modules.reporting import models as reporting_models  # noqa: F401
from app.modules.results import gazette_models  # noqa: F401
from app.modules.results import gpa_models  # noqa: F401
from app.modules.results import merit_models  # noqa: F401
from app.modules.results import models as results_models  # noqa: F401
from app.modules.results import report_card_models  # noqa: F401
from app.modules.results import transcript_models  # noqa: F401
from app.modules.students import models as students_models  # noqa: F401
from app.modules.timetable import models as timetable_models  # noqa: F401

from app.modules.authentication import models as authentication_models  # noqa: F401
