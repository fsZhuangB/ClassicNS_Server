from enum import unique
import os
from wsgiref import validate
from xml.etree.ElementTree import tostring
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'output.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# bootstrap = Bootstrap(app)
# moment = Moment(app)
db = SQLAlchemy(app)

class QueryForm(FlaskForm):
    query = StringField(" ", validators=[DataRequired()])
    submit = SubmitField('Submit')


class SamplerInfo(db.Model):
    __tablename__ = "sampler_info"
    rng_seed = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<SamplerInfo %r>' % self.rng_seed

class Particles(db.Model):
    __tablename__ = "particles"
    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(db.Text)
    log_likelihood = db.Column(db.Float(precision=15))
    tiebreaker = db.Column(db.Float)

    def __repr__(self):
        return '<Particles %r>' % self.iteration

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, SamplerInfo=SamplerInfo, Particles=Particles)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = QueryForm()
    if form.validate_on_submit():
        log_query = request.form['query']
        result = Particles.query.filter_by(log_likelihood=log_query).one()
        
        if result is None:
            print("result is none!")
        else:
            json_res = {"iterations":result.id, "params":result.params, "log_likelihood":result.log_likelihood, "tiebreaker":result.tiebreaker}
            return json_res
