function AccountWindow({ user, onLogout }) {
    return (
        <div className="account-window">
            {user ? (
                <div>
                    <p>Logged in as: {user.name}</p>
                    <p>Email: {user.email}</p>
                    <button type="button" className="link-btn" onClick={onLogout}>Logout</button>
                </div>
            ) : (
                <div>
                    <p>You are not logged in.</p>
                    <a href="/api/auth/login">Login</a>
                </div>
            )}
        </div>
    )
}

export default AccountWindow