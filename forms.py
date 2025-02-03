from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

class KeyForm(FlaskForm):
    profile_name = StringField(
        "Profile Name",
        validators=[DataRequired(), Length(min=3, message="Profile name must be at least 3 characters long.")]
    )
    snowflake_url = TextAreaField(
        "Snowflake URL",
        validators=[DataRequired(), Length(min=5, message="Please enter a valid URL.")]
    )
    username = TextAreaField(
        "Username",
        validators=[DataRequired(), Length(min=3, message="Username must be at least 3 characters long.")]
    )
    private_key = TextAreaField(
        "Private Key",
        validators=[DataRequired(), Length(min=10, message="Private key seems too short.")]
    )
    public_key = TextAreaField(
        "Public Key",
        validators=[DataRequired(), Length(min=10, message="Public key seems too short.")]
    )
    password = PasswordField(
        "Password (For Encryption/Editing)",
        validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters long.")]
    )
    submit = SubmitField("Save/Update Keys")

class JWTForm(FlaskForm):
    profile = SelectField("Select Key Profile", coerce=int, validators=[DataRequired()])
    access_lifetime = SelectField(
        "Access Lifetime (in minutes)",
        choices=[(str(x), f"{x} minutes") for x in range(1, 901)],
        default='60',
        validators=[DataRequired()]
    )
    password = PasswordField(
        "Password (For JWT Generation)",
        validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters long.")]
    )
    submit = SubmitField("Generate JWT")

