
from mongoengine import Document, EmbeddedDocument, fields

# Create your models here.
class Comment(EmbeddedDocument):

    author = fields.StringField(verbose_name="Name", max_length=255)
    email  = fields.EmailField(verbose_name="Email")
    body = fields.StringField(verbose_name="Comment")

class Post(Document):

    title = fields.StringField(max_length=255)
    slug = fields.StringField(max_length=255, primary_key=True)
    comments = fields.ListField(
        fields.EmbeddedDocumentField('Comment'), blank=True,
    )