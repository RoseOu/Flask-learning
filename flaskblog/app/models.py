from . import db
from werkzeug.security import generate_password_hash, check_password_hash  
from flask.ext.login import UserMixin, current_app, AnonymousUserMixin
from . import login_manager   


class Permission:            #
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):      
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)   #
    permissions = db.Column(db.Integer)                 #
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod            ##
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):          
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)  
    password_hash = db.Column(db.String(128))                    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property                 
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter                
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):        
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):          #
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):        #
        return self.can(Permission.ADMINISTER)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):        #
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))