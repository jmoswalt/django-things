from things.forms import ThingForm
from .models import Article


class ArticleForm(ThingForm):
    model = Article
