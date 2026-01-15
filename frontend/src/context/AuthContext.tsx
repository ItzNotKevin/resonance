import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Simple storage for web (use localStorage)
const storage = {
  async getItem(key: string): Promise<string | null> {
    if (typeof window !== 'undefined' && window.localStorage) {
      return window.localStorage.getItem(key);
    }
    return null;
  },
  async setItem(key: string, value: string): Promise<void> {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem(key, value);
    }
  },
  async removeItem(key: string): Promise<void> {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.removeItem(key);
    }
  },
};

interface User {
  id: number;
  username: string;
  token: string;
}

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(null);

  useEffect(() => {
    // Load user from storage on mount
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await storage.getItem('user');
      if (userData) {
        setUserState(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error loading user:', error);
    }
  };

  const setUser = async (userData: User | null) => {
    setUserState(userData);
    if (userData) {
      try {
        await storage.setItem('user', JSON.stringify(userData));
      } catch (error) {
        console.error('Error saving user:', error);
      }
    } else {
      try {
        await storage.removeItem('user');
      } catch (error) {
        console.error('Error removing user:', error);
      }
    }
  };

  const logout = async () => {
    await setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

