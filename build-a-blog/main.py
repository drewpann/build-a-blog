import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""Check out the blog <a href="/blog">here</a>!""")

class Blog(Handler):
    def render_blog(self):
        recent_entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
        self.render("view.html", entries=recent_entries)

    def get(self):
        self.render_blog()

class NewPost(Handler):
    def render_write(self, title="", entry="", error=""):
        self.render("write.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_write()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Entry(title = title, entry = entry)
            e.put()
            postid = str(e.key().id())
            blog_url="blog/" + postid
            self.redirect(blog_url)

        else:
            error = "Please enter both a title and an entry!"
            self.render_write(title, entry, error)

class AllPosts(Handler):
    def render_all(self):
        all_entries = db.GqlQuery("SELECT * From Entry ORDER BY created DESC")
        self.render("view.html", entries=all_entries)

    def get(self):
        self.render_all()

class ViewPostHandler(Handler):
    def render_post(self, id):
        entry = Entry.get_by_id(int(id))
        self.render("viewone.html", entry=entry)

    def get(self,id):
        if not id:
            self.error(404)
            return

        self.render_post(id)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blog),
    ('/all', AllPosts),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
