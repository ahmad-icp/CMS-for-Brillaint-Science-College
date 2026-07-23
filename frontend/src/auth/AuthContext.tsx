import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from 'react';

import {
  getAccessToken,
  getStoredProfile,
  login as loginRequest,
  LoginInput,
  logout as logoutRequest,
} from '../services/auth';

interface AuthContextValue {
  authenticated: boolean;
  profile: { college_id: string; username: string } | null;
  login: (input: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(Boolean(getAccessToken()));
  const [profile, setProfile] = useState(getStoredProfile());

  useEffect(() => {
    const expire = () => {
      setAuthenticated(false);
      setProfile(null);
    };
    window.addEventListener('college-erp:session-expired', expire);
    return () => window.removeEventListener('college-erp:session-expired', expire);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    authenticated,
    profile,
    login: async (input) => {
      await loginRequest(input);
      setAuthenticated(true);
      setProfile({ college_id: input.college_id, username: input.username });
    },
    logout: async () => {
      await logoutRequest();
      setAuthenticated(false);
      setProfile(null);
    },
  }), [authenticated, profile]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
