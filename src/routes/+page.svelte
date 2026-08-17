<script lang="ts">
	type Role = 'individual' | 'asha' | 'anm';
	type View = 'welcome' | 'dashboard' | 'screening' | 'result' | 'learn' | 'reports' | 'emergency' | 'profile';

	let role: Role | null = null;
	let view: View = 'welcome';
	let symptoms = new Set<string>();
	let patientName = 'Sunita Devi';
	let step = 1;
	let saved = false;

	const roleInfo = {
		individual: { title: "Personal Monitoring", subtitle: 'Self-check symptoms & get guidance', icon: '👤', name: 'Hello!', accent: '#0f8b8d' },
		asha: { title: "I'm an ASHA Worker", subtitle: 'Screen, educate & support your community', icon: '🧑🏽‍⚕️', name: 'Hello, Sunita', accent: '#d6536d' },
		anm: { title: "I'm an ANM Worker", subtitle: 'Advanced assessment, referrals & reporting', icon: '👩🏽‍⚕️', name: 'Hello, Dr. Priya', accent: '#356fd6' }
	};

	const symptomOptions = [
		['🤒', 'Fever'], ['🤧', 'Cough'], ['🫁', 'Breathing Problem'], ['❤️', 'Chest Pain'],
		['⚡', 'Weakness'], ['🧠', 'Headache'], ['💧', 'Diarrhea'], ['➕', 'Others']
	];

	const cases = [
		{ name: 'Ramesh Kumar', time: '2 min ago', status: 'High priority' },
		{ name: 'Savitri Devi', time: '1 hr ago', status: 'Medium priority' },
		{ name: 'Mohan Lal', time: '3 hr ago', status: 'Low priority' }
	];

	function chooseRole(next: Role) { role = next; }
	function start() { if (!role) role = 'individual'; view = 'dashboard'; }
	function toggleSymptom(name: string) {
		const next = new Set(symptoms);
		next.has(name) ? next.delete(name) : next.add(name);
		symptoms = next;
	}
	function severity() {
		if (symptoms.has('Chest Pain') || symptoms.has('Breathing Problem')) return 'High Priority';
		if (symptoms.has('Fever') && symptoms.has('Weakness')) return 'Medium Priority';
		return 'Low Priority';
	}
	function go(next: View) { saved = false; view = next; }
	$: current = role ? roleInfo[role] : roleInfo.individual;
</script>

<svelte:head><title>MedNexus | Triage Severity Identification System</title><meta name="theme-color" content="#071621" /></svelte:head>

<div class="app-shell">
	<header class="topbar">
		<button class="brand" on:click={() => go(role ? 'dashboard' : 'welcome')} aria-label="MedNexus home">
			<img src="/images/mednexus-logo.png" alt="MedNexus MN logo" />
			<span>Med<span>Nexus</span></span>
		</button>
		<div class="top-actions"><span class="network">● Online</span><button class="avatar" on:click={() => role && go('profile')}>{role === 'asha' ? 'S' : role === 'anm' ? 'P' : 'K'}</button></div>
	</header>

	{#if view === 'welcome'}
		<main class="welcome page">
			<section class="hero-card">
				<div class="logo-orbit"><img src="/images/mednexus-logo.png" alt="MedNexus logo" /></div>
				<p class="eyebrow">AI-ASSISTED COMMUNITY HEALTHCARE</p>
				<h1>Med<span>Nexus</span></h1>
				<h2>Triage Severity Identification System</h2>
				<p class="tagline">Right Care <b>•</b> Right Time <b>•</b> Saves Lives</p>
			</section>
			<section class="role-grid">
				{#each Object.entries(roleInfo) as [key, info]}
					<button class:active={role === key} class="role-card" on:click={() => chooseRole(key as Role)}>
						<span class="role-icon">{info.icon}</span><span><strong>{info.title}</strong><small>{info.subtitle}</small></span><i>→</i>
					</button>
				{/each}
			</section>
			<button class="primary large" on:click={start}>Get Started <span>→</span></button>
			<p class="disclaimer">MedNexus supports triage and referral decisions. It does not replace professional medical diagnosis.</p>
		</main>
	{:else if view === 'dashboard'}
		<main class="page dashboard">
			<section class="welcome-row"><div><p class="eyebrow">{role === 'individual' ? 'YOUR HEALTH COMPANION' : 'COMMUNITY HEALTH DASHBOARD'}</p><h1>{current.name}</h1><p>{role === 'individual' ? 'How can we help you today?' : current.title.replace("I'm an ", '')}</p></div><div class="profile-orb">{current.icon}</div></section>
			{#if role !== 'individual'}
				<section class="stats"><div><b>23</b><span>People screened</span></div><div><b class="danger">7</b><span>High priority</span></div><div><b class="warning">3</b><span>Referred today</span></div></section>
			{/if}
			<section><div class="section-title"><h2>Quick Actions</h2><button on:click={() => go('screening')}>Start screening →</button></div><div class="action-grid">
				<button on:click={() => go('screening')}><span>🩺</span><b>{role === 'individual' ? 'Check Symptoms' : 'Patient Screening'}</b><small>Assess symptoms safely</small></button>
				<button on:click={() => go('learn')}><span>📚</span><b>Health Education</b><small>Learn & share guidance</small></button>
				<button on:click={() => go('reports')}><span>📊</span><b>Reports</b><small>View local health data</small></button>
				<button class="emergency-action" on:click={() => go('emergency')}><span>🆘</span><b>Emergency</b><small>Quick help & referral</small></button>
			</div></section>
			{#if role !== 'individual'}<section class="recent"><div class="section-title"><h2>Recent Screenings</h2><button on:click={() => go('reports')}>View all</button></div>{#each cases as c}<article><span class="person">👤</span><div><b>{c.name}</b><small class:high={c.status === 'High priority'} class:medium-status={c.status === 'Medium priority'} class:low-status={c.status === 'Low priority'}><i class="status-light"></i>{c.status}</small></div><time>{c.time}</time></article>{/each}</section>{/if}
		</main>
	{:else if view === 'screening'}
		<main class="page screening">
			<button class="back" on:click={() => go('dashboard')}>← Back</button><div class="progress"><span style={`width:${step * 20}%`}></span></div><small>Step {step} of 5</small>
			<h1>{role === 'individual' ? 'What are you feeling?' : 'What is the main concern?'}</h1><p>Select all symptoms that apply. This information helps determine the appropriate next step.</p>
			{#if role !== 'individual'}<label class="input-label">Patient name<input bind:value={patientName} placeholder="Enter patient name" /></label>{/if}
			<div class="symptoms">{#each symptomOptions as item}<button class:selected={symptoms.has(item[1])} on:click={() => toggleSymptom(item[1])}><span>{item[0]}</span>{item[1]}<i>{symptoms.has(item[1]) ? '✓' : '+'}</i></button>{/each}</div>
			<button class="primary large" disabled={symptoms.size === 0} on:click={() => { step = 5; go('result'); }}>Analyze Symptoms →</button>
		</main>
	{:else if view === 'result'}
		<main class="page result">
			<button class="back" on:click={() => go('screening')}>← Edit symptoms</button>
			<div class:medium={severity() === 'Medium Priority'} class:low={severity() === 'Low Priority'} class="severity-card"><span>⚠</span><div><small>TRIAGE RESULT</small><h1>{severity()}</h1><p>{severity() === 'High Priority' ? 'Immediate attention is recommended.' : severity() === 'Medium Priority' ? 'Medical consultation is recommended soon.' : 'Monitor symptoms and follow the guidance.'}</p></div></div>
			<section class="result-details"><h2>Recommended next step</h2><ul>{#if severity() === 'High Priority'}<li>Visit the nearest PHC, hospital, or emergency service now.</li><li>Do not leave the person alone if symptoms worsen.</li><li>Take previous prescriptions or relevant records.</li>{:else if severity() === 'Medium Priority'}<li>Arrange a medical consultation within 24 hours.</li><li>Monitor symptoms and hydration.</li><li>Escalate immediately if red-flag symptoms appear.</li>{:else}<li>Rest, hydrate and monitor symptoms.</li><li>Use trusted health guidance for self-care.</li><li>Seek care if symptoms persist or worsen.</li>{/if}</ul></section>
			<section class="red-flags"><h2>Emergency warning signs</h2><p>Severe breathing difficulty, persistent chest pain, unconsciousness, seizures, or sudden severe weakness require urgent medical help.</p></section>
			<div class="dual"><button class="secondary" on:click={() => saved = true}>⇧ Share Report</button><button class="primary" on:click={() => saved = true}>Save Screening</button></div>{#if saved}<p class="toast">✓ Screening saved successfully</p>{/if}
		</main>
	{:else if view === 'learn'}
		<main class="page learn"><button class="back" on:click={() => go('dashboard')}>← Back</button><div class="section-title"><div><p class="eyebrow">KNOWLEDGE FOR BETTER CARE</p><h1>Learn & Educate</h1></div><button>View all</button></div><div class="topic-grid">{#each [['🤒','Fever','Causes, symptoms & when to seek help'],['💧','Diarrhea','Prevention & oral rehydration'],['🤰','Pregnancy Care','Important do’s and warning signs'],['👶','Child Nutrition','Food & healthy growth'],['🫁','Respiratory Care','Recognize danger signs'],['🧼','Hygiene','Safe daily practices']] as t}<article><span>{t[0]}</span><b>{t[1]}</b><small>{t[2]}</small><button>Open →</button></article>{/each}</div><section class="video-placeholder"><span>▶</span><div><b>Community health awareness</b><p>Short, easy-to-understand videos for rural and urban communities.</p></div></section></main>
	{:else if view === 'reports'}
		<main class="page reports"><button class="back" on:click={() => go('dashboard')}>← Back</button><div class="section-title"><div><p class="eyebrow">SCREENING INSIGHTS</p><h1>Reports</h1></div><select><option>This Month</option><option>This Week</option></select></div><section class="stats"><div><b>156</b><span>Total screened</span></div><div><b class="danger">32</b><span>High priority</span></div><div><b class="warning">18</b><span>Referred</span></div></section><section class="chart-card"><h2>Health Monitoring</h2><div class="bars">{#each [38,52,31,68,45,80,62,91,73,96,84,100] as h}<i style={`height:${h}%`}></i>{/each}</div></section><section class="conditions"><h2>Common concerns</h2>{#each [['🤒','Fever','45'],['🫁','Respiratory infection','32'],['💧','Diarrhea','21'],['➕','Others','58']] as c}<div><span>{c[0]} {c[1]}</span><b>{c[2]} cases</b></div>{/each}</section></main>
	{:else if view === 'emergency'}
		<main class="page emergency"><button class="back light" on:click={() => go('dashboard')}>← Back</button><p class="eyebrow light-text">EMERGENCY ASSISTANCE</p><h1>Need urgent help?</h1><p>Use emergency services for severe or life-threatening symptoms.</p><button class="sos" on:click={() => saved = true}>SOS</button>{#if saved}<p class="emergency-note">Emergency alert initiated. Contact your local emergency service immediately.</p>{/if}<section class="emergency-contacts"><h2>Quick contacts</h2><button><span>☎</span><div><b>112</b><small>National emergency response</small></div><i>Call →</i></button><button><span>🏥</span><div><b>Nearest PHC / Hospital</b><small>Find the closest care centre</small></div><i>→</i></button><button><span>📞</span><div><b>Health helpline</b><small>Get official health assistance</small></div><i>→</i></button></section></main>
	{:else if view === 'profile'}
		<main class="page profile"><button class="back" on:click={() => go('dashboard')}>← Back</button><div class="profile-head"><div class="big-avatar">{current.icon}</div><h1>{role === 'individual' ? 'Krishna' : role === 'asha' ? 'Sunita Devi' : 'Dr. Priya Singh'}</h1><p>{role === 'individual' ? 'MedNexus user' : current.title.replace("I'm an ", '')} · ID: MN-8214345</p></div><section class="menu">{#each ['Personal Information','My Activity','Training & Certificates','Language & Accessibility','Settings','Help & Support'] as m}<button><span>{m === 'Settings' ? '⚙' : m === 'Help & Support' ? '?' : '◈'}</span>{m}<i>›</i></button>{/each}<button class="logout" on:click={() => { role = null; go('welcome'); }}>↪ Sign out</button></section></main>
	{/if}

	{#if view !== 'welcome' && view !== 'screening' && view !== 'result' && view !== 'emergency'}
		<nav class="bottom-nav"><button class:nav-active={view === 'dashboard'} on:click={() => go('dashboard')}>⌂<span>Home</span></button><button class:nav-active={view === 'screening'} on:click={() => go('screening')}>♧<span>Screen</span></button><button class:nav-active={view === 'learn'} on:click={() => go('learn')}>▣<span>Learn</span></button><button class:nav-active={view === 'reports'} on:click={() => go('reports')}>▥<span>Reports</span></button><button class:nav-active={view === 'profile'} on:click={() => go('profile')}>♙<span>Profile</span></button></nav>
	{/if}
</div>

<style>
	:global(*){box-sizing:border-box}:global(body){margin:0;background:#eef3f4;color:#17232d}.app-shell{min-height:100vh;background:linear-gradient(180deg,#f7faf9,#edf3f4);padding:0 0 84px}.topbar{height:72px;max-width:1120px;margin:auto;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;background:rgba(247,250,249,.88);backdrop-filter:blur(14px);position:sticky;top:0;z-index:5}.brand{border:0;background:none;display:flex;align-items:center;gap:10px;font-size:22px;font-weight:800;color:#12202b;cursor:pointer}.brand img{width:42px;height:42px;border-radius:50%;object-fit:cover;box-shadow:0 3px 12px #0c1e2c30}.brand span span,h1 span{color:#b78a50}.top-actions{display:flex;align-items:center;gap:14px}.network{font-size:12px;color:#19866d}.avatar{width:40px;height:40px;border:0;border-radius:50%;background:#0f6f74;color:white;font-weight:800}.page{max-width:1120px;margin:0 auto;padding:38px 24px;animation:enter .35s ease}@keyframes enter{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}.welcome{text-align:center;max-width:850px}.hero-card{padding:10px 0 24px}.logo-orbit{width:190px;height:190px;margin:0 auto 18px;border-radius:50%;padding:7px;background:conic-gradient(from 30deg,#c79b5d 0 45%,transparent 45% 55%,#b8c1ca 55% 90%,transparent 90%);box-shadow:0 0 0 12px #0b202915}.logo-orbit img{width:100%;height:100%;border-radius:50%;object-fit:cover}.eyebrow{font-size:11px;letter-spacing:.17em;font-weight:800;color:#72808a;margin:0 0 8px}.hero-card h1{font-size:52px;margin:0;color:#eef3f3;text-shadow:0 3px 20px #0b202955}.hero-card h2{font-size:18px;margin:6px 0;color:#d5dee1}.hero-card,.emergency{border-radius:26px;background:radial-gradient(circle at 50% 25%,#173441,#071621 68%);color:white}.tagline{color:#b8c3c8}.tagline b{color:#caa164}.role-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px 0}.role-card,.action-grid button,.topic-grid article,.symptoms button,.menu button{border:1px solid #dde6e8;background:white;border-radius:18px;text-align:left;cursor:pointer;transition:.2s}.role-card{padding:18px;display:flex;align-items:center;gap:12px}.role-card:hover,.role-card.active{border-color:#188489;box-shadow:0 10px 28px #16313b15;transform:translateY(-2px)}.role-icon{font-size:30px}.role-card strong,.role-card small{display:block}.role-card small{color:#74818a;font-size:12px;margin-top:4px}.role-card i{margin-left:auto;font-style:normal;color:#9da8ad}.primary{border:0;border-radius:14px;background:linear-gradient(135deg,#137e80,#0a606b);color:white;padding:14px 22px;font-weight:750;cursor:pointer;box-shadow:0 10px 22px #08717730}.primary:disabled{opacity:.4;cursor:not-allowed}.large{width:100%;font-size:16px;padding:18px}.disclaimer{font-size:11px;color:#7e898f;margin:16px auto;max-width:620px}.welcome-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:25px}.welcome-row h1{margin:0;font-size:32px}.welcome-row p:not(.eyebrow){margin:4px 0;color:#72808a}.profile-orb,.big-avatar{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;background:#dff1ee;font-size:32px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}.stats div{padding:20px;background:white;border-radius:18px;box-shadow:0 8px 24px #152e3810}.stats b{font-size:28px;display:block;color:#126d72}.stats span{font-size:12px;color:#75828a}.danger{color:#cf4f43!important}.warning{color:#b77b28!important}.section-title{display:flex;justify-content:space-between;align-items:center;margin:30px 0 12px}.section-title h2{margin:0}.section-title button{border:0;background:none;color:#08767b;font-weight:700}.action-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.action-grid button{padding:20px;min-height:145px}.action-grid span{font-size:30px;display:block;margin-bottom:14px}.action-grid b,.action-grid small{display:block}.action-grid small{font-size:11px;color:#77838b;margin-top:5px}.emergency-action{border-color:#f2d5d2!important}.recent{background:white;border-radius:20px;padding:6px 20px;margin-top:26px}.recent article{display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid #eef1f2}.recent article:last-child{border:0}.person{font-size:25px}.recent b,.recent small{display:block}.recent small{font-size:11px;color:#168166;display:flex;align-items:center;gap:6px}.recent .high{color:#ce5548}.recent .medium-status{color:#b98222}.recent .low-status{color:#168166}.status-light{width:8px;height:8px;border-radius:50%;background:currentColor;display:inline-block;box-shadow:0 0 0 4px currentColor;opacity:.9}.recent time{margin-left:auto;font-size:11px;color:#8b969c}.back{border:0;background:none;color:#63727a;font-weight:700;margin-bottom:18px;cursor:pointer}.progress{height:5px;background:#dce5e7;border-radius:10px;margin-bottom:6px}.progress span{display:block;height:100%;background:#118287;border-radius:10px}.screening>small{color:#7a858c;font-size:11px}.screening h1{margin-bottom:6px}.screening>p{color:#738088;max-width:700px}.input-label{display:block;margin:18px 0;font-size:13px;font-weight:700}.input-label input{display:block;width:100%;padding:14px;border:1px solid #d9e3e5;border-radius:12px;margin-top:7px;font:inherit}.symptoms{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:22px 0}.symptoms button{padding:15px;display:flex;align-items:center;gap:12px}.symptoms button.selected{background:#e8f6f3;border-color:#0f8b8d}.symptoms button span{font-size:23px}.symptoms i{margin-left:auto;font-style:normal;color:#0d7c81}.severity-card{display:flex;gap:20px;padding:26px;background:#fff0ee;border:1px solid #ffd9d4;border-radius:22px}.severity-card.medium{background:#fff7e8;border-color:#f2dfad}.severity-card.low{background:#eaf8f2;border-color:#bce5d1}.severity-card>span{font-size:42px}.severity-card.medium>span{display:flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:50%;font-size:0;background:#e3a72f;box-shadow:0 0 0 7px #e3a72f25}.severity-card.medium>span:after{content:'!';font-size:30px;font-weight:900;color:white}.severity-card.low>span{color:#168166}.severity-card:not(.medium):not(.low)>span{color:#cf4f43}.severity-card h1{margin:3px 0;color:#cf4f43}.severity-card.medium h1{color:#b98222}.severity-card.low h1{color:#168166}.severity-card p{margin:0;color:#657078}.result-details,.red-flags,.chart-card,.conditions{background:white;border-radius:20px;padding:22px;margin-top:18px}.result-details h2,.red-flags h2,.chart-card h2,.conditions h2{font-size:18px;margin-top:0}.result-details li{margin:11px 0;color:#52616a}.red-flags{border-left:4px solid #d9584b}.red-flags p{color:#68757c}.dual{display:flex;gap:12px;margin-top:20px}.dual>*{flex:1}.secondary{border:1px solid #ccd9dc;border-radius:14px;background:white;font-weight:700;cursor:pointer}.toast{text-align:center;color:#0a8069;font-weight:700}.topic-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.topic-grid article{padding:18px}.topic-grid span{font-size:28px;display:block}.topic-grid b{display:block;margin:10px 0 4px}.topic-grid small{color:#718089;font-size:12px}.topic-grid button{border:0;background:none;padding:10px 0 0;color:#08777b;font-weight:700}.video-placeholder{margin-top:22px;padding:22px;border-radius:20px;background:linear-gradient(135deg,#16303b,#24576a);color:white;display:flex;gap:18px;align-items:center}.video-placeholder>span{width:50px;height:50px;border-radius:50%;background:#e5b86e;color:#17242c;display:grid;place-items:center}.video-placeholder p{color:#c7d4d7;font-size:13px}.section-title select{border:1px solid #d8e1e3;padding:9px 12px;border-radius:10px;background:white}.bars{height:180px;display:flex;align-items:flex-end;gap:8px;padding-top:15px}.bars i{flex:1;background:linear-gradient(180deg,#35a2a2,#0b6f76);border-radius:8px 8px 2px 2px}.conditions div{display:flex;justify-content:space-between;padding:13px 0;border-bottom:1px solid #edf1f2}.conditions div:last-child{border:0}.conditions b{font-size:12px;color:#68757b}.emergency{min-height:calc(100vh - 156px);text-align:center;padding-top:20px}.light{color:#d7e2e5}.light-text{color:#aebec3}.emergency h1{font-size:38px;margin:8px}.emergency>p:not(.eyebrow):not(.emergency-note){color:#bdc9ce}.sos{width:130px;height:130px;border-radius:50%;border:8px solid #ff9a9140;background:#e63f38;color:white;font-size:30px;font-weight:900;box-shadow:0 0 0 12px #e63f3818,0 15px 40px #e63f3840;margin:32px;cursor:pointer}.emergency-note{color:#ffe0dc}.emergency-contacts{max-width:700px;margin:20px auto;text-align:left;background:white;border-radius:24px;padding:20px;color:#1a2730}.emergency-contacts h2{margin-top:0}.emergency-contacts button{width:100%;border:0;border-bottom:1px solid #edf1f2;background:white;padding:15px 0;display:flex;align-items:center;gap:13px;text-align:left}.emergency-contacts button>span{font-size:24px}.emergency-contacts small{display:block;color:#7a868d;margin-top:3px}.emergency-contacts i{margin-left:auto;font-style:normal;color:#0b777d}.profile-head{text-align:center;padding:10px 0 28px}.big-avatar{margin:auto;width:88px;height:88px;font-size:44px}.profile-head h1{margin:12px 0 4px}.profile-head p{margin:0;color:#77848b}.menu{max-width:700px;margin:auto;background:white;border-radius:20px;padding:6px 18px}.menu button{width:100%;padding:17px 4px;border:0;border-bottom:1px solid #edf1f2;border-radius:0;display:flex;gap:13px;align-items:center}.menu i{margin-left:auto;font-style:normal;font-size:22px;color:#829098}.menu .logout{color:#c7483d;border:0}.bottom-nav{position:fixed;bottom:0;left:0;right:0;z-index:6;height:72px;background:#ffffffef;backdrop-filter:blur(12px);display:flex;justify-content:center;border-top:1px solid #e3eaec}.bottom-nav button{width:110px;border:0;background:none;color:#819097;font-size:19px;cursor:pointer;padding-top:9px}.bottom-nav span{display:block;font-size:10px;margin-top:3px}.bottom-nav .nav-active{color:#087a7f;font-weight:800}@media(max-width:760px){.topbar{padding:8px 16px}.page{padding:26px 16px}.network{display:none}.hero-card h1{font-size:44px}.role-grid,.action-grid,.topic-grid{grid-template-columns:1fr}.role-card{padding:14px}.action-grid{grid-template-columns:1fr 1fr}.action-grid button{min-height:125px}.stats{gap:8px}.stats div{padding:14px}.stats b{font-size:22px}.symptoms{grid-template-columns:1fr}.bottom-nav button{width:20%;font-size:16px}.emergency{margin:0;border-radius:0;min-height:calc(100vh - 72px)}.topic-grid{grid-template-columns:1fr 1fr}.logo-orbit{width:155px;height:155px}}@media(max-width:430px){.topic-grid{grid-template-columns:1fr}.welcome-row h1{font-size:27px}.role-grid{gap:9px}.role-card strong{font-size:13px}.role-card small{font-size:10px}.role-icon{font-size:24px}}
</style>
