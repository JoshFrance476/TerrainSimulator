function AccountWindow({ user, onLogout }) {
    return (
        <div className="account-window">
            {user ? (
                <div>
                    <p>Logged in as: {user.name}</p>
                    <p>Email: {user.email}</p>
                    <p onClick={onLogout} style={{ cursor: 'pointer', color: 'blue', textDecoration: 'underline' }}>Logout</p>
                </div>
            ) : (
                <div>
                    <p>You are not logged in.</p>
                    <a href="http://localhost:8000/api/auth/login">Login</a>
                </div>
            )}
        </div>
    )
}

export default AccountWindow