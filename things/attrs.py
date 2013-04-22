from .types import *

AUTHOR = {
    "name": "Author",
    "key": "author",
    "description": "The Author of the {{ model }}.",
    "datatype": TYPE_TEXT
}

CONTENT = {
    "name": "Content",
    "key": "content",
    "description": "The main content of the {{ model }}.",
    "required": True,
    "datatype": TYPE_LONGTEXT
}

FEATURED = {
    "name": "Featured",
    "key": "featured",
    "description": "Select whether or not this is a featured {{ model }}.",
    "datatype": TYPE_BOOLEAN
}

PRIVATE = {
    "name": "Private",
    "key": "private",
    "description": "Select whether or not this is a private {{ model }}.",
    "datatype": TYPE_BOOLEAN
}

PUBLISHED_AT = {
    "name": "Publish Date",
    "key": "published_at",
    "description": "The publish date of the {{ model }}.",
    "datatype": TYPE_DATE
}

IMAGE = {
    "name": "Image",
    "key": "image",
    "description": "Add an image to the {{ model }}.",
    "datatype": TYPE_FILE
}

ORDER = {
    "name": "Order",
    "key": "order",
    "description": "The numerical order of the {{ model }}.",
    "datatype": TYPE_INT
}
