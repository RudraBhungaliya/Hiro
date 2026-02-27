import { GoogleLogin, googleLogout } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useUser } from "../context/UserContext";

function AuthBtn() {
  const { user, setUser } = useUser();

  const handleSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);
    setUser(decoded);
  };

  const handleLogout = () => {
    googleLogout();
    setUser(null);
  };

  return (
    <div style={{ 
      display: "flex",
      justifyContent: "flex-end",
      alignItems: "center"
    }}>
      {!user ? (
        <GoogleLogin
          onSuccess={handleSuccess}
          onError={() => console.log("Login Failed")}
        />
      ) : (
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "15px",
          backgroundColor: "rgba(17, 24, 39, 0.95)",
          backdropFilter: "blur(10px)",
          padding: "10px 20px",
          borderRadius: "12px",
          border: "1px solid rgba(255,255,255,0.1)"
        }}>
          <p style={{ fontWeight: "bold", margin: 0, color: "white", fontSize: "14px" }}>Welcome, {user.name}</p>
          <button
            onClick={handleLogout}
            style={{
              padding: "8px 16px",
              backgroundColor: "#dc3545",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "13px",
              fontWeight: "500"
            }}
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

export default AuthBtn;