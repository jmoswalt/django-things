from things.forms import ThingForm
from journals.models import Journal


class JournalForm(ThingForm):
    model = Journal
