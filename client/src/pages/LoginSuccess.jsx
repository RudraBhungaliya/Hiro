import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function LoginSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      navigate('/', { replace: true });
    } else {
      navigate('/', { replace: true });
    }
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-[#f9f5ee] flex items-center justify-center">
      <p className="text-slate-600">Signing you in…</p>
    </div>
  );
}
