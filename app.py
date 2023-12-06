from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = '15571601'
db = SQLAlchemy(app)

class Team(db.Model):
    team_type = db.Column(db.String(64))
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    tier = db.Column(db.String(20), nullable=False)
    character = db.Column(db.String(50), nullable=False)
    play_time = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=True)
    discord_id = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(4), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

@app.route('/')
def index():
    teams = Team.query.filter(
        ((Team.team_type.in_(['용병 모집', '용병 참가']) & (Team.created_at >= datetime.now() - timedelta(hours=24))) |
        (Team.team_type.in_(['팀원 모집', '팀원 참가']) & (Team.created_at >= datetime.now() - timedelta(hours=72))))
    ).all()
    return render_template('index.html', teams=teams)

@app.route('/filter_teams', methods=['POST'])
def filter_teams():
    team_type = request.form['team_type']
    session['team_type'] = team_type
    if team_type == '':
        teams = Team.query.filter(
            ((Team.team_type.in_(['용병 모집', '용병 참가']) & (Team.created_at >= datetime.now() - timedelta(hours=24))) |
            (Team.team_type.in_(['팀원 모집', '팀원 참가']) & (Team.created_at >= datetime.now() - timedelta(hours=72))))
        ).all()
    else:
        teams = Team.query.filter_by(team_type=team_type).all()
    return render_template('index.html', teams=teams)

@app.route('/add_team', methods=['POST'])
def add_team():
    team = Team(
            team_type=request.form['team_type'],
            nickname=request.form['nickname'],
            tier=request.form['tier'],
            character=request.form['character'],
            play_time=request.form['play_time'],
            message=request.form['message'],
            discord_id=request.form['discord_id'],
            password=request.form['password'])
    db.session.add(team)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_team/<int:id>', methods=['POST'])
def edit_team(id):
    team = db.session.get(Team, id)
    if team:
        if team.password == request.form['password']:
            team.team_type = request.form['team_type']
            team.nickname = request.form['nickname']
            team.tier = request.form['tier']
            team.character = request.form['character']
            team.play_time = request.form['play_time']
            team.message = request.form['message']
            team.discord_id = request.form['discord_id']
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Incorrect password')
            return redirect(url_for('index'))
    else:
        return "Team not found", 404

@app.route('/delete_team/<int:id>', methods=['POST'])
def delete_team(id):
    password = request.form['password']
    team = db.session.get(Team, id)
    if team and (team.password == password or password == 'admin'):
        db.session.delete(team)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        flash('Incorrect password')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)