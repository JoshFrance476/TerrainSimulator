import { useState, useEffect } from 'react'
import Header from './components/Header'
import AccountWindow from './components/AccountWindow'
import Landing from './pages/Landing'
import Play from './pages/Play'
import WorldBuilder from './pages/Worldbuilder'
import Editor from './pages/Editor'
import { useNewSessionMutation } from './queries/queries'

function App() {
	const [user, setUser] = useState(undefined); // undefined = loading, null = logged out
	const [page, setPage] = useState({name: "landing"});  // 'name' is page name, 'worldId' is optional for editor page
	const [selectedWorldId, setSelectedWorldId] = useState(null);
	const [showAccountWindow, setShowAccountWindow] = useState(false);


	useEffect(() => {
		const fetchUser = async () => {
			const res = await fetch('/api/auth/me', { credentials: 'include' })
			if (res.ok) {
				const userData = await res.json()
				setUser(userData)
			}
		}
		fetchUser()
	}, [])

	const handleLogout = async () => {
		await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
		window.location.reload()
	}

	if (user === undefined) {
		return (
			<div className="loading-screen">
				<p>Loading...</p>
			</div>
		)
	}
	
	return (
		<>
			{page.name !== "landing" && (
				<>
					<Header 
						user={user} 
						setShowAccountWindow={setShowAccountWindow} 
						onNavigate={setPage}
					/>
					{showAccountWindow && (
						<AccountWindow 
							user={user}
							onLogout={handleLogout}
						/>
					)}
				</>
			)}
			{page.name === "landing" && <Landing onLogout={handleLogout} user={user} onNavigate={setPage}/>}
			{page.name === "play" && <Play user={user}/>} 
			{page.name === "editor" && <Editor worldId={page.worldId}/>}
			{page.name === "worldbuilder" && <WorldBuilder />}
		</>
	)
}

export default App