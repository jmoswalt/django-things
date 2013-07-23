# Django-things

Django Things is a framework designed around making quick models for a CMS. Django Things stores everything in one of two tables: Things and Values. This makes schema changes very easy since the schema isn't really kept in the database.

## Installation

Django Things works out of your virtual environment using virtualenv. If you aren't using `virtualenv`, you probably should be.

First, you should make a new folder for your things project and cd into it:

    mkdir my-things
    cd my-things`

To install, first make your virtualenv with a command like:

    virtualenv venv

Then, activate the environment with:

    source venv/bin/activate

Next, we install Django Things:

    pip install django-things

This will install some dependencies like Django itself. Once this has completed, we run a command to build our basic project:

    create-things-project

This will build a Django project in the current directory. It builds your `settings.py` and `urls.py` files, both in the `conf` directory. Additionally, there is a requirements directory that we will use to install more requirements. We can install the additional requirements with:

    pip install -r requirements/dev.txt

This will install all of the common requirements, along with the django debug toolbar for local debugging. If you are installing for production on your own server or a host like Heroku, you can simply use `pip install -r requirements.txt` to get the production dependencies.

When running locally or on your own server, Environment Variables can be set in the `.env` file that has been created. You will want to modify the database setting below with your database location and credentials:

    DATABASE_URL='postgres://localhost/django_things'

You may also want to uncomment things like the `DEBUG` setting and change your `SECRET_KEY` to something unique to you.

Next, we run the initial sync to create the database tables. This is a great time to add a superuser when prompted.

    python manage.py syncdb

If DEBUG is not set to true in the `.env` file, you should also run `python manage.py collectstatic` so the styles come through.

Finally, you are ready to view the site at [http://127.0.0.1:8000/]()
   

## Theming

Custom themes can be created for django things websites. Themes go in the `themes` directory in the root of the project. By default, there is a theme called `default_theme` that can be used as an example.

The theme for the site is set in the `.env` file like below:

    THEME='default_theme'
    
Only one theme can be used at a time.

Inside the individual theme folder, there are two directories: **static** and **templates**

#### Static folder

The static folder as you may have guessed contains static assets like CSS, JS, and fonts that are to be used in the theme. These files are collected when running `collectstatic`

#### Templates folder

Inside the templates folder, only two files are required: **home.html** and **interior.html**

`home.html`: This template is used only for the homepage of the website.

`interior.html`: This template is used for all pages that aren't the homepage.

Both template files should extend base.html with this at the top:

    {% extends 'base.html' %}

#### Template blocks

Content should be added within `{% block %}` tags. The following blocks are available to be used by the base template:

`title`: This is rendered as the html title in the document head.

`head`: This is added to the end of the document head. It's where you should add fonts, stylesheets, and other meta elements.

`body`: This is the main content area of the template. It loads in the document body.

`js`: This is loaded at the end of the document. It's where you should add your javascript files. jQuery is included by default, so you don't need to include it.

Below are some less common blocks that you may also use:

`x_ua_compatible`: This by default adds `<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">` to the top of the document. If you need to override this,  please override the block.

`description`: This is the meta description. It can be populated within custom apps, or just in a template like homepage.html

`bootstrap_css_link`: This includes bootstrap CSS by default. You can override this to remove the default bootstrap CSS.

`jquery`: This includes jquery by default (currently 1.8.3). You can override this block with a different version of jquery. If you remove jquery all together, it will affect some of the site's functions.

## Custom Apps

The apps that are used with Django Things are a bit different than the models and views you might normally use with Django. The default comes with an `articles` app that is explained below.

#### Articles models.py

Our class `Articles` inherits `models.Thing` from the things package, and sets a Meta property as a proxy model:

    from things import models
    class Article(models.Thing):

        class Meta:
            proxy = True

The Thing class is packed with functionality to automatically map fields using and EAV type architecture. It handles different field types that can be imported from `things.types`. Things also comes with some basic attributes (like fields) that can be imported from `things.attrs`.

All `Thing` models include these fields by default:

`title`: Title is a simple charfield.

`slug`: Slug is a slugfield which is unique across all apps.

`creator`: Creator is a foregin key to the User table

`created_at`: This is an automated timestamp when the record is created

`updated_at`: This is an automated timestamp that updates whenever a record is changed.

We don't actually put our fields in our model. Instead, we set them in a dictionary, in this case named `ARITCLE_ATTRIBUTES`. In articles, you will see some default attrs used, as well as a custom attr defined:

    from things import attrs, types

    ARITCLE_ATTRIBUTES = (
        attrs.CONTENT,
        attrs.AUTHOR,
        attrs.PUBLISHED_AT,
        attrs.FEATURED,
        {
            "name": "Category",
            "key": "category",
            "description": "Add a Category to the {{ model }}.",
            "datatype": types.TYPE_TEXT,
            "required": False
        },
    )

The different attrs used above have different functionality. CONTENT has a WYSIWYG field that supports file uploads, AUTHOR is a text field, PUBLISHED_AT is a date/time field, and FEATURED is a boolean field. The Category field is defined, set as text and not required.

The `Articles` class has some properties set instead of the normal fields, which we've seen are attrs in a dictionary. Below are the different types of properties that are used on a Things class.

`public_filter_out`: This is a **dictionary** that includes query-style filters that will block certain content from showing publicly. For example, with the `Articles` class, we set a key for `published_at__gte` and a value of `0`. This means if there is no Published At date/time value, then that article won't be accessible publicly. Similarly, we have a key `published_at__lte` with a value of `datetime.now().replace(second=0, microsecond=0)`. This says anything that is published in the future should also not be publicly accessible.

`super_user_order`: This is a **list** that contains attrs with their asc/desc order. It controls what order the articles are displayed to superusers. For articles, we have an order of `['-published_at', '-created_at']`, meaning newest published followed by newest created.

`public_order`: This is a **string** that controls the order for publicly viewable content. For articles, we use `"-published_at"`, so the newest published items are shown first.

Finally, we register our class `Articles` and our attributes dictionary `ARITCLE_ATTRIBUTES` with things using the following:

    models.register_thing(Article, ARITCLE_ATTRIBUTES)

This automatically adds our app to the django admin, as well as includes it in the site RSS feed, sitemap, and includes it's urls with the site.


#### Article forms.py

We don't need a forms.py with Articles. Instead, we automatically inherit the form from the things package.


#### Article feeds.py

A `feeds.py` file is traditionally used to define a class for an RSS feed. We don't have to add this file because it is automatically inherited from the things package.


#### Article views.py

We don't need a `views.py` file if all we have are a list view and a detail view. We instead inherit views from the things package in the `urls.py` file.


#### Article admin.py

Things comes with an admin class that we can inherit from. We register our admin class and our model with the django admin as normal:

    class ArticleAdmin(ThingAdmin):
        list_display = ['name', 'link', 'content', 'author', 'published_at']

    admin.site.register(Article, ArticleAdmin)

The `list_display` is commonly used in django-things apps. The default list_display is the title and url of the content, along with all of your attrs. If you are ok with this, you can just register your model with the `ThingAdmin` class, like:

    admin.site.register(Article, ThingAdmin)



#### Article urls.py

In our urls.py, we can define a list view and a detail view with their respective patterns. For the views assigned to these URLs, we use ThingListView and ThingDetailView, respectively.

We simply pass in our model to these URLs, along with a slug kwarg for the DetailView.


#### Article Templates

There are some default templates that come out-of-the-box, which include displaying all of the fields in the list and detail view, along with the updated_at timestamp.

To define custom templates, create a directory called `templates` in the app directory, and then add a directory inside templates with the name of the app, like `apps/articles/templates/articles`. Inside this directory, we can add the following templates:

`article_detail.html`: This is the template for the detail view. The article object is passed into the context as the variable `object`. We can reference the title field with `object.title`, and any of the attrs with the lowercase of their name, like `object.content` or `object.published_at`.

`article_list.html`: This template get's `object_list`. A common pattern is to define an `_article_list_item.html` and use that template as an include to display the list items. For example:

    {% for object in object_list %}
        {% include "articles/_article_list_item.html" %}
    {% endfor %}

We can also use `autopaginate` in our article_list to paginate our list, and we can use `paginate` to display page-number links.

