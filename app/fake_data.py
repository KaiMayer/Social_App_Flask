from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from app.main.models import Post
from app.users.models import User
from PIL import Image


def resize(img):

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 name=fake.name(),
                 username=fake.user_name(),
                 password='password',
                 description=fake.text(),
                 created=fake.past_date(),
                 )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        img = fake.image_url()
        p = Post(content=fake.text(),
             timestamp=fake.past_date(),
             image_file=img,
             author=u)
        db.session.add(p)
    db.session.commit()

