import json
import os
from pony import orm
import re
import sqlite3
import sys
from Core.Directory import Directory
from Core.File import File
from Core.Framework import Framework
from Core.Msg import Msg
from Core.Text import Text

# Reference: https://www.blog.pythonlibrary.org/2014/07/21/python-101-an-intro-to-pony-orm/

class Database():
    directory = Framework.getDatabaseDir()
    name = "Cocoscats"
    path = "{0}/{1}.db".format(directory, name)
    debugFlag = False
    ORM = orm
    ODB = orm.Database()

    class Table():
        Project = NotImplemented
        Input = NotImplemented
        Analyzer = NotImplemented
        Translator = NotImplemented
        Output = NotImplemented

    @staticmethod
    def commit():
        Database.ODB.commit()

    @staticmethod
    def connect():
        try:
            Database.ODB.bind("sqlite", Database.path, create_db=True)
        except TypeError:
            pass
        else:
            Database.ODB.generate_mapping(create_tables=True)

    @staticmethod
    def create(forceDeleteIfExists=False):
        if Database.exists():
            if forceDeleteIfExists:
                Database.drop()
            else:
                return
        Directory.make(Database.directory)
        try:
            Database.ODB.bind("sqlite", Database.path, create_db=True)
        except TypeError:
            pass
        else:
            Database.ODB.generate_mapping(create_tables=True)
            Database.ODB.disconnect()

    @staticmethod
    def disconnect():
        Database.ODB.disconnect()

    @staticmethod
    def drop():
        if Database.exists():
            os.unlink(Database.path)

    @staticmethod
    def execute(sql, commit=True, asScript=False):
        conn = sqlite3.connect(Database.path)
        cur = conn.cursor()
        if not asScript:
            cur.execute(sql)
        else:
            cur.executescript(sql)
        results = cur.fetchall()
        if commit:
            conn.commit()
        conn.close()
        return results

    @staticmethod
    def exists():
        return os.path.isfile(Database.path)

    @staticmethod
    def getAnalyzerContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Analyzer.get(ProjectID=projectID)
            if result is None:
                return None
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getInputContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Input.get(ProjectID=projectID)
            if result is None:
                return None
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "Source": result.Source,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getOutputContent(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Output.get(ProjectID=projectID)
            if result is None:
                return None
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "Target": result.Target,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def getProject(projectID):
        result = {}
        result["Project"] = Database.getProjectDetails(projectID)
        result["Input"] = Database.getInputContent(projectID)
        result["Analyzer"] = Database.getAnalyzerContent(projectID)
        result["Translator"] = Database.getTranslatorContent(projectID)
        result["Output"] = Database.getOutputContent(projectID)
        return result

    @staticmethod
    def getProjectDetails(projectID):
        with Database.ORM.db_session:
            result = Database.Table.Project.get(ID=projectID)
            if result is None:
                return None
            return {
                "ID": result.ID,
                "Description": result.Description,
                "DateTime": result.DateTime,
                "Workflow": result.Workflow
            }

    @staticmethod
    def getTranslatorContent(projectID):
        with Database.ORM.db_session:
            result =  Database.Table.Translator.get(ProjectID=projectID)
            if result is None:
                return None
            return {
                "ID": result.ID,
                "ProjectID": projectID,
                "Content": result.Content,
                "ContentJson": result.ContentJson,
                "PluginName": result.PluginName,
                "PluginMethod": result.PluginMethod,
                "Plugin": result.Plugin
            }

    @staticmethod
    def sanitize(something):
        if something is str:
            something = something.replace("'", "\\'")
        return something

    @staticmethod
    def setDebug(debugFlag):
        orm.sql_debug(debugFlag)

    @staticmethod
    def setPath(path):
        Database.path = File.getAbsPath(path)
        Database.name = File.getName(Database.path)
        Database.directory = File.getDirectory(Database.path)

class Project(Database.ODB.Entity):
    ID = orm.PrimaryKey(str)
    Description = orm.Required(str)
    DateTime = orm.Required(str)
    Workflow = orm.Optional(orm.Json)
    Input = orm.Set("Input", cascade_delete=True)
    Analyzer = orm.Set("Analyzer", cascade_delete=True)
    Translator = orm.Set("Translator", cascade_delete=True)
    Output = orm.Set("Output", cascade_delete=True)

class Input(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    Source = orm.Required(str)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Analyzer(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Translator(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    ContentJson = orm.Required(orm.Json)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

class Output(Database.ODB.Entity):
    ID = orm.PrimaryKey(int, auto=True)
    ProjectID = orm.Required(Project)
    Content = orm.Required(orm.LongStr)
    Target = orm.Required(str)
    PluginName = orm.Optional(str)
    PluginMethod = orm.Optional(str)
    Plugin = orm.Optional(orm.Json)

Database.Table.Project = Project
Database.Table.Input = Input
Database.Table.Analyzer = Analyzer
Database.Table.Translator = Translator
Database.Table.Output = Output