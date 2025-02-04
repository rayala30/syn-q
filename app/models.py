from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Organization(db.Model):
    __tablename__ = 'organization'  # Ensure this matches your table name in the DB

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    org_passcode = db.Column(db.String(255), nullable=False)
    email_domain = db.Column(db.String(255), nullable=False)

    users = db.relationship('User', backref='organization', lazy=True)  # Linking with users
    projects = db.relationship('Project', backref='organization', lazy=True)  # Linking with projects

    def __repr__(self):
        return f'<Organization {self.name}>'


class User(db.Model):
    __tablename__ = 'users'  # Ensure this matches your table name in the DB

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_number = db.Column(db.String(255), nullable=False, unique=True)
    client_name = db.Column(db.String(255), nullable=False)
    project_name = db.Column(db.String(255), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    # FIXED: Ensure the backref name matches what is used in the File model
    files = db.relationship('File', backref='project', lazy=True)

    def __repr__(self):
        return f'<Project {self.project_number}>'


class File(db.Model):
    __tablename__ = 'project_files'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project_number = db.Column(db.String(255), nullable=False)

    # FIXED: Remove the conflicting relationship definition
    # project = db.relationship('Project', backref='files', lazy=True)

    def __repr__(self):
        return f'<File {self.file_name} for project {self.project_number}>'
