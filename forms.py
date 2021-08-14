from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import InputRequired, Email, Optional
from wtforms.widgets.core import TextArea

class RegisterForm(FlaskForm):
    """Registration form"""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    role = SelectField("Relationship with music", choices=[
        ('Student', 'Student'),
        ('Professor/Academic', 'Professor/Academic'),
        ('Music Teacher (K-12)', 'Music Teacher (K-12)'),
        ('Music Teacher (Private)', 'Music Teacher (Private)'),
        ('DJ', 'DJ'),
        ('Composer/Arranger', 'Composer/Arranger'),
        ('Music Producer', 'Music Producer'),
        ('Audio Engineer', 'Audio Engineer'),
        ('Performer (vocals)', 'Performer (vocals)'),
        ('Performer (instrument)', 'Performer (instrument)'),
        ('Label Representative', 'Label Representative'),
        ('Music Fan', 'Music Fan'),
        ('Other', 'Other')
    ], validators=[InputRequired()])
    img_url = StringField("Image URL")


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class EditRecordingForm(FlaskForm):
    """Edit recording info form"""

    comments = TextAreaField("Comments about song", validators=[Optional()])
    tags = StringField("Tags - separate with comma and a space (', ')", validators=[Optional()])


class PlaylistForm(FlaskForm):
    """Create a new playlist"""

    name = StringField("Name", validators=[InputRequired()])
    description = StringField("Describe your playlist", validators=[Optional()])
    
class AddToPlaylistForm(FlaskForm):
    """Add a song to a playlist"""

    recording = SelectField("Pick a song from your library", choices=[], coerce=int)