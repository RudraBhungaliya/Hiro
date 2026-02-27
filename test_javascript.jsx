
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetchUser(userId);
    }, [userId]);
    
    const fetchUser = async (id) => {
        const response = await fetch(`/api/users/${id}`);
        const data = await response.json();
        setUser(data);
    };
    
    return (
        <div className="user-profile">
            <h1>{user?.name}</h1>
        </div>
    );
}

export default UserProfile;
