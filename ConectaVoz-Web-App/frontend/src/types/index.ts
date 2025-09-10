// types/index.ts
export type UserRole = 'colaborador' | 'diretoria' | 'admin';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  department?: string;
  team?: string;
  photo?: string;
  is_connecta: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

export interface ApiResponse<T> {
  results?: T[];
  count?: number;
  next?: string;
  previous?: string;
  data?: T;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  department?: string;
  team?: string;
}
