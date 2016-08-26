from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField    #
from wtforms.validators import Required, Length               #

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(Form):                          #
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class PostForm(Form):
    body = TextAreaField('What is on your mind?', validators=[Required()])
    submit = SubmitField('Submit')

class CommentForm(Form):
    body = StringField('Write down your comment:', validators=[Required()])
    submit = SubmitField('Submit')