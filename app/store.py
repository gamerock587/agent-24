import hashlib
import json
import sqlite3
import time
import uuid
from .config import DATA

def uid(): return uuid.uuid4().hex[:16]
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def fingerprint(value): return hashlib.sha256(canonical(value).encode()).hexdigest()

class Store:
    def __init__(self,path=None):
        self.db=sqlite3.connect(path or DATA/'agent24.sqlite3',check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,domain TEXT,url TEXT,status TEXT,spec TEXT,created REAL,updated REAL,summary TEXT DEFAULT '',requests INTEGER DEFAULT 0,next_due REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,kind TEXT,message TEXT,data TEXT,created REAL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY,run_id TEXT,worker TEXT,tool TEXT,url TEXT,fingerprint TEXT,status TEXT,result TEXT,created REAL,duration REAL);
        CREATE TABLE IF NOT EXISTS memory(fingerprint TEXT PRIMARY KEY,domain TEXT,tool TEXT,status TEXT,result TEXT,last_test REAL,attempts INTEGER DEFAULT 0,lease_run TEXT,lease_until REAL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS findings(id TEXT PRIMARY KEY,run_id TEXT,title TEXT,status TEXT,severity TEXT,endpoint TEXT,detail TEXT,evidence TEXT);
        CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,run_id TEXT,name TEXT,sha256 TEXT,path TEXT,bytes INTEGER,created REAL);
        CREATE TABLE IF NOT EXISTS metrics(id INTEGER PRIMARY KEY AUTOINCREMENT,created REAL,data TEXT);
        CREATE TABLE IF NOT EXISTS captured_files(id TEXT PRIMARY KEY,run_id TEXT,url TEXT,status INTEGER,mime TEXT,bytes INTEGER,sha256 TEXT,truncated INTEGER,relative_path TEXT,tested_url TEXT);
        CREATE INDEX IF NOT EXISTS events_run ON events(run_id,seq);
        CREATE INDEX IF NOT EXISTS actions_run ON actions(run_id);
        CREATE TABLE IF NOT EXISTS model_turns(id TEXT PRIMARY KEY,run_id TEXT,model TEXT,purpose TEXT,status TEXT,input TEXT,output TEXT,created REAL,finished REAL);
        CREATE INDEX IF NOT EXISTS model_turns_run ON model_turns(run_id,created);
        CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,mission_id TEXT,run_id TEXT,role TEXT,content TEXT,created REAL);
        CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,domain TEXT,url TEXT,spec TEXT,active_run TEXT,status TEXT,next_due REAL,cycles INTEGER,summary TEXT,updated REAL);
        CREATE TABLE IF NOT EXISTS agent_state(mission_id TEXT PRIMARY KEY,state TEXT,updated REAL);
        ''')
        self.db.commit()
    def execute(self,sql,args=()):
        result=self.db.execute(sql,args);self.db.commit();return result
    def rows(self,sql,args=()):return [dict(r) for r in self.db.execute(sql,args).fetchall()]
    def run(self,ident):
        rows=self.rows('SELECT * FROM runs WHERE id=?',(ident,))
        if not rows:raise KeyError(ident)
        row=rows[0];row['spec']=json.loads(row['spec']);return row
    def create(self,url,domain,spec):
        ident=uid();now=time.time()
        self.execute('INSERT INTO runs(id,domain,url,status,spec,created,updated) VALUES(?,?,?,?,?,?,?)',(ident,domain,url,'queued',canonical(spec),now,now))
        self.event(ident,'queued','Assessment queued',{'url':url});return self.run(ident)
    def update(self,ident,**fields):
        allowed={'status','summary','requests','next_due'}
        if not set(fields)<=allowed:raise ValueError('Invalid run field')
        fields['updated']=time.time()
        self.execute('UPDATE runs SET '+','.join(k+'=?' for k in fields)+' WHERE id=?',(*fields.values(),ident))
    def event(self,ident,kind,message,data=None):
        self.execute('INSERT INTO events(run_id,kind,message,data,created) VALUES(?,?,?,?,?)',(ident,kind,message,canonical(data or {}),time.time()))
    def artifact(self,ident,name,content):
        raw=content.encode() if isinstance(content,str) else content
        aid=uid();folder=DATA/'evidence'/ident;folder.mkdir(parents=True,exist_ok=True)
        path=folder/(aid+'.json');path.write_bytes(raw)
        self.execute('INSERT INTO artifacts VALUES(?,?,?,?,?,?,?)',(aid,ident,name,hashlib.sha256(raw).hexdigest(),str(path),len(raw),time.time()))
        return aid
    def claim(self,key,domain,tool,run,force=False,ttl=86400):
        # Transaction makes identical-action leases atomic even with concurrent workers.
        now=time.time();self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT * FROM memory WHERE fingerprint=?',(key,)).fetchone()
            if row and row['lease_until']>now:
                self.db.commit();return 'leased',None
            if row and row['status']=='completed' and not force and now-row['last_test']<ttl:
                self.db.commit();return 'cached',json.loads(row['result'])
            if row:self.db.execute('UPDATE memory SET lease_run=?,lease_until=? WHERE fingerprint=?',(run,now+180,key))
            else:self.db.execute('INSERT INTO memory(fingerprint,domain,tool,status,result,last_test,attempts,lease_run,lease_until) VALUES(?,?,?,?,?,?,?,?,?)',(key,domain,tool,'pending','{}',0,0,run,now+180))
            self.db.commit();return 'claimed',None
        except Exception:self.db.rollback();raise
    def remember(self,key,status,result):
        self.execute('UPDATE memory SET status=?,result=?,last_test=?,attempts=attempts+1,lease_run=NULL,lease_until=0 WHERE fingerprint=?',(status,canonical(result),time.time(),key))
    def recover(self):
        self.execute("UPDATE model_turns SET status='interrupted',finished=? WHERE status='running'",(time.time(),))
        active=self.rows("SELECT id FROM runs WHERE status IN ('running','queued','stopping')")
        for row in active:
            self.update(row['id'],status='interrupted',summary='Process restarted; transient work was discarded. Resume re-observes the target.')
            self.event(row['id'],'recovery','Interrupted assessment preserved; no external action replayed.')
        self.execute('UPDATE memory SET lease_run=NULL,lease_until=0')
    def detail(self,ident):
        result=self.run(ident)
        for key,table in [('events','events'),('actions','actions'),('findings','findings'),('artifacts','artifacts')]:
            result[key]=self.rows(f'SELECT * FROM {table} WHERE run_id=?',(ident,))
        for e in result['events']:e['data']=json.loads(e['data'])
        for a in result['actions']:a['result']=json.loads(a['result'])
        for f in result['findings']:f['evidence']=json.loads(f['evidence'])
        for a in result['artifacts']:a.pop('path',None)
        result['coverage']=next((e['data'] for e in reversed(result['events']) if e['kind']=='coverage'),None)
        return result

