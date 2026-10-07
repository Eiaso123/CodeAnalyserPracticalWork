import { useEffect, useState } from 'react'
import { ArrowDownLeft, ArrowRight, BookOpen, Braces, Check, ChevronDown, CircleHelp, ClipboardList, Code2, FilePlus2, GraduationCap, LogOut, Plus, Send, ShieldCheck, Sparkles, UserRound } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

async function api(path, { token, ...options } = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(payload.message || payload.msg || payload.error || 'Something went wrong. Please try again.')
  return payload
}

function getSavedSession() {
  try {
    return JSON.parse(localStorage.getItem('atelier-session') || 'null')
  } catch {
    return null
  }
}

function App() {
  const [session, setSession] = useState(getSavedSession)
  const [profile, setProfile] = useState(null)
  const [modules, setModules] = useState([])
  const [tps, setTps] = useState([])
  const [responses, setResponses] = useState([])
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [authMode, setAuthMode] = useState('login')
  const [activeView, setActiveView] = useState('overview')
  const [dialog, setDialog] = useState('')

  async function loadWorkspace(token) {
    const [profileData, moduleData, tpData] = await Promise.all([
      api('/user', { token }),
      api('/modules', { token }),
      api('/tp/all', { token }),
    ])
    setProfile(profileData)
    setModules(moduleData.modules || [])
    setTps(tpData.tps || [])
    if (profileData.role === 'etudiant') {
      const responseData = await api('/etudiant/reponses', { token })
      setResponses(responseData.reponses || [])
    } else {
      setResponses([])
    }
  }

  useEffect(() => {
    if (!session?.token) return
    loadWorkspace(session.token).catch(() => {
      localStorage.removeItem('atelier-session')
      setSession(null)
    })
  }, [session?.token])

  async function submitAuth(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    const payload = Object.fromEntries(form.entries())
    try {
      const result = await api(authMode === 'login' ? '/login' : '/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      const nextSession = { token: result.token, user: result.user }
      localStorage.setItem('atelier-session', JSON.stringify(nextSession))
      setSession(nextSession)
      setNotice(authMode === 'login' ? 'Welcome back.' : 'Your account is ready.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  function signOut() {
    localStorage.removeItem('atelier-session')
    setSession(null)
    setProfile(null)
    setModules([])
    setTps([])
    setResponses([])
    setNotice('')
  }

  async function submitResponse(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    try {
      await api('/reponses', {
        token: session.token,
        method: 'POST',
        body: JSON.stringify({ id_tp: form.get('id_tp'), reponse: form.get('reponse') }),
      })
      await loadWorkspace(session.token)
      setDialog('')
      setNotice('Your work was submitted.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  async function createModule(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    form.set('id_professeur', String(profile.id))
    try {
      const response = await fetch(`${API_BASE}/module/create`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${session.token}` },
        body: form,
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.msg || 'Could not create module.')
      await loadWorkspace(session.token)
      setDialog('')
      setNotice('Module created.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  async function createTp(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    const payload = Object.fromEntries(form.entries())
    try {
      await api('/tp', { token: session.token, method: 'POST', body: JSON.stringify(payload) })
      await loadWorkspace(session.token)
      setDialog('')
      setNotice('Practical work created.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  if (!session?.token) {
    return <AuthScreen mode={authMode} setMode={setAuthMode} onSubmit={submitAuth} busy={busy} error={error} />
  }

  const isProfessor = profile?.role === 'professeur'
  const activeTps = tps.filter((tp) => tp.statut === 'Ouvert').length
  const displayName = profile?.full_name || session.user?.full_name || 'Member'

  return (
    <div className="app-frame">
      <aside className="sidebar">
        <a className="brand-lockup" href="#home" onClick={() => setActiveView('overview')}>
          <span className="brand-mark"><Braces size={20} strokeWidth={2.5} /></span>
          <span>atelier<span className="brand-period">.</span></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="side-nav" aria-label="Main navigation">
          <button className={`nav-item ${activeView === 'overview' ? 'active' : ''}`} onClick={() => setActiveView('overview')}>
            <BookOpen size={17} /> Overview
          </button>
          <button className={`nav-item ${activeView === 'practicals' ? 'active' : ''}`} onClick={() => setActiveView('practicals')}>
            <ClipboardList size={17} /> Practical work
            <span className="nav-count">{tps.length}</span>
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="help-link"><CircleHelp size={16} /> Help center <ArrowRight size={14} /></div>
          <button className="profile-button" onClick={signOut} title="Sign out">
            <span className="avatar">{displayName.slice(0, 1).toUpperCase()}</span>
            <span className="profile-copy"><strong>{displayName}</strong><small>{isProfessor ? 'Professor' : 'Student'}</small></span>
            <LogOut size={16} className="logout-icon" />
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><ArrowRight size={13} /><strong>{activeView === 'overview' ? 'Overview' : 'Practical work'}</strong></div>
          <div className="topbar-right"><span className="live-status"><i /> All systems operational</span><span className="topbar-date">{new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(new Date())}</span></div>
        </header>

        <div className="content-wrap">
          {notice && <div className="alert alert-success alert-dismissible py-2" role="status">{notice}<button className="btn-close" aria-label="Dismiss" onClick={() => setNotice('')} /></div>}
          {error && <div className="alert alert-danger alert-dismissible py-2" role="alert">{error}<button className="btn-close" aria-label="Dismiss" onClick={() => setError('')} /></div>}

          <section className="welcome-row">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> YOUR LEARNING DESK</div>
              <h1>{activeView === 'overview' ? <>Good to see you, <em>{displayName.split(' ')[0]}.</em></> : <>Practical <em>work.</em></>}</h1>
              <p>{isProfessor ? 'Shape the next challenge. Keep your classes moving.' : 'Pick up where you left off and keep your momentum.'}</p>
            </div>
            <div className="welcome-actions">
              {isProfessor ? <>
                <button className="btn btn-outline-dark action-secondary" onClick={() => { setDialog('module'); setError('') }}><Plus size={16} /> New module</button>
                <button className="btn btn-primary action-primary" onClick={() => { setDialog('tp'); setError('') }}><FilePlus2 size={16} /> Create practical</button>
              </> : <button className="btn btn-primary action-primary" onClick={() => { setDialog('response'); setError('') }}><Send size={16} /> Submit work</button>}
            </div>
          </section>

          <section className="metric-grid" aria-label="Workspace summary">
            <Metric icon={<BookOpen size={17} />} label="Modules" value={modules.length} note={isProfessor ? 'Under your guidance' : 'Available to you'} tone="mint" />
            <Metric icon={<ClipboardList size={17} />} label="Practical work" value={tps.length} note={`${activeTps} currently open`} tone="coral" />
            <Metric icon={isProfessor ? <GraduationCap size={18} /> : <Check size={18} />} label={isProfessor ? 'Your role' : 'Submissions'} value={isProfessor ? 'Guide' : responses.length} note={isProfessor ? 'Professor workspace' : 'Work turned in'} tone="yellow" />
          </section>

          <section className="section-heading">
            <div><span className="section-kicker">WORKSPACE</span><h2>{activeView === 'overview' ? 'Your practicals' : 'All practical work'}</h2></div>
            <button className="text-action" onClick={() => setActiveView(activeView === 'overview' ? 'practicals' : 'overview')}>{activeView === 'overview' ? 'View all practicals' : 'Back to overview'} <ArrowRight size={15} /></button>
          </section>

          {tps.length ? <section className="work-list">
            <div className="work-list-head"><span>ASSIGNMENT</span><span>MODULE</span><span>DUE DATE</span><span>STATUS</span><span /></div>
            {tps.map((tp, index) => <article className="work-row" key={tp.id_tp}>
              <div className="work-title-cell"><span className={`work-icon work-icon-${index % 3}`}><Code2 size={18} /></span><div><strong>{tp.titre}</strong><small>Practical #{String(tp.id_tp).padStart(2, '0')}</small></div></div>
              <div className="module-cell">{modules.find((module) => module.id_module === tp.id_module)?.nom || `Module ${tp.id_module}`}</div>
              <div className="due-cell">{tp.deadline || 'No deadline'}</div>
              <div><span className={`status-pill ${tp.statut === 'Ouvert' ? 'status-open' : 'status-closed'}`}><i />{tp.statut}</span></div>
              <button className="row-arrow" title={`Open ${tp.titre}`} onClick={() => setDialog(isProfessor ? '' : 'response')}><ArrowRight size={17} /></button>
            </article>)}
          </section> : <div className="empty-state"><div className="empty-glyph"><Sparkles size={21} /></div><h3>No practical work yet</h3><p>{isProfessor ? 'Create a practical assignment to get your class started.' : 'New assignments from your professors will appear here.'}</p>{isProfessor && <button className="btn btn-primary" onClick={() => setDialog('tp')}><Plus size={16} /> Create practical</button>}</div>}

          <footer className="content-footer"><span><ShieldCheck size={14} /> Secure academic workspace</span><span>ATELIER <b>·</b> 01</span></footer>
        </div>
      </main>

      {dialog && <Dialog title={dialog === 'response' ? 'Submit your work' : dialog === 'module' ? 'Create a module' : 'Create practical work'} onClose={() => setDialog('')}>
        {dialog === 'response' && <form onSubmit={submitResponse} className="dialog-form">
          <label className="form-label" htmlFor="response-tp">Practical work</label>
          <select className="form-select" id="response-tp" name="id_tp" required defaultValue=""><option value="" disabled>Select an open practical</option>{tps.filter((tp) => tp.statut === 'Ouvert').map((tp) => <option key={tp.id_tp} value={tp.id_tp}>{tp.titre}</option>)}</select>
          <label className="form-label mt-3" htmlFor="response-code">Your analysis or code</label>
          <textarea className="form-control code-input" id="response-code" name="reponse" rows="8" required placeholder="Paste your work here…" />
          <div className="dialog-actions"><button className="btn btn-light" type="button" onClick={() => setDialog('')}>Cancel</button><button className="btn btn-primary" disabled={busy || !tps.some((tp) => tp.statut === 'Ouvert')}><Send size={15} /> Submit</button></div>
        </form>}
        {dialog === 'module' && <form onSubmit={createModule} className="dialog-form">
          <label className="form-label" htmlFor="module-name">Module name</label><input className="form-control" id="module-name" name="nom" required placeholder="e.g. Data structures" />
          <label className="form-label mt-3" htmlFor="module-info">Description</label><textarea className="form-control" id="module-info" name="information" rows="3" placeholder="What will students learn?" />
          <div className="dialog-actions"><button className="btn btn-light" type="button" onClick={() => setDialog('')}>Cancel</button><button className="btn btn-primary" disabled={busy}><Plus size={15} /> Create module</button></div>
        </form>}
        {dialog === 'tp' && <form onSubmit={createTp} className="dialog-form">
          <label className="form-label" htmlFor="tp-title">Assignment title</label><input className="form-control" id="tp-title" name="titre" required placeholder="e.g. Sorting algorithms" />
          <div className="row g-3 mt-0"><div className="col-7"><label className="form-label" htmlFor="tp-module">Module</label><select className="form-select" id="tp-module" name="id_module" required defaultValue=""><option value="" disabled>Select module</option>{modules.map((module) => <option key={module.id_module} value={module.id_module}>{module.nom}</option>)}</select></div><div className="col-5"><label className="form-label" htmlFor="tp-deadline">Due date</label><input className="form-control" id="tp-deadline" name="deadline" type="date" required /></div></div>
          <div className="dialog-actions"><button className="btn btn-light" type="button" onClick={() => setDialog('')}>Cancel</button><button className="btn btn-primary" disabled={busy || !modules.length}><FilePlus2 size={15} /> Create practical</button></div>
        </form>}
      </Dialog>}
    </div>
  )
}

function AuthScreen({ mode, setMode, onSubmit, busy, error }) {
  const registering = mode === 'register'
  return <main className="auth-shell">
    <div className="auth-art" aria-hidden="true"><div className="art-topline"><span>ATELIER / 01</span><span>LEARN BY MAKING</span></div><div className="art-grid" /><div className="art-code"><span>01</span><code>function <b>understand</b>(problem) {'{'}</code><code className="indent">return build(problem)</code><code>{'}'}</code><span className="art-cursor" /></div><div className="art-caption"><span className="caption-mark"><Braces size={18} /></span><span>Make ideas<br /><em>work.</em></span></div><div className="art-bottom"><span>FIELD NOTES FOR THE CURIOUS</span><span>EST. 2025</span></div></div>
    <div className="auth-panel"><div className="auth-panel-inner"><a className="brand-lockup auth-brand" href="#home"><span className="brand-mark"><Braces size={19} strokeWidth={2.5} /></span><span>atelier<span className="brand-period">.</span></span></a><div className="auth-form-wrap"><div className="eyebrow"><span className="eyebrow-line" /> YOUR LEARNING DESK</div><h1>{registering ? 'Start building.' : 'Welcome back.'}</h1><p className="auth-subtitle">{registering ? 'Create your workspace account and get to work.' : 'Sign in to continue your practical work.'}</p>
      {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
      <form onSubmit={onSubmit} className="auth-form">
        {registering && <><label className="form-label" htmlFor="full-name">Full name</label><input className="form-control" id="full-name" name="full_name" autoComplete="name" required placeholder="Your name" /></>}
        <label className="form-label" htmlFor="email">Email address</label><input className="form-control" id="email" name="email" type="email" autoComplete="email" required placeholder="you@example.com" />
        <div className="password-label"><label className="form-label" htmlFor="password">Password</label>{!registering && <span>Use your account password</span>}</div><input className="form-control" id="password" name="password" type="password" autoComplete={registering ? 'new-password' : 'current-password'} minLength={6} required placeholder="At least 6 characters" />
        {registering && <><label className="form-label mt-3" htmlFor="role">I am a</label><select className="form-select" id="role" name="role"><option value="etudiant">Student</option><option value="professeur">Professor</option></select></>}
        <button className="btn btn-primary auth-submit" disabled={busy}>{busy ? 'Please wait…' : registering ? 'Create account' : 'Sign in'} <ArrowRight size={17} /></button>
      </form>
      <div className="auth-switch">{registering ? 'Already have an account?' : 'New to Atelier?'} <button onClick={() => setMode(registering ? 'login' : 'register')}>{registering ? 'Sign in' : 'Create account'} <ArrowDownLeft size={14} /></button></div>
      <div className="auth-security"><ShieldCheck size={15} /> Your academic workspace, kept private.</div>
    </div><div className="auth-foot"><span>ATELIER · PRACTICAL WORK</span><span>HELP <ChevronDown size={12} /></span></div></div></div>
  </main>
}

function Metric({ icon, label, value, note, tone }) {
  return <article className="metric-card"><div className={`metric-icon metric-${tone}`}>{icon}</div><div className="metric-label">{label}</div><div className="metric-bottom"><strong>{value}</strong><span>{note}</span></div></article>
}

function Dialog({ title, onClose, children }) {
  useEffect(() => {
    function onKeyDown(event) { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])
  return <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><section className="dialog-panel" role="dialog" aria-modal="true" aria-labelledby="dialog-title"><div className="dialog-header"><div><span className="section-kicker">ATELIER / WORKSPACE</span><h2 id="dialog-title">{title}</h2></div><button className="dialog-close" onClick={onClose} aria-label="Close dialog">×</button></div>{children}</section></div>
}

export default App